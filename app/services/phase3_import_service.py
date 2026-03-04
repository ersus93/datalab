"""Servicio para importación de datos transaccionales Phase 3 desde Access."""
import csv
import logging
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from app import db
from app.database.models import (
    OrdenTrabajo, Pedido, Entrada,
    Cliente, Producto, Fabrica, Rama, UnidadMedida
)
from app.database.models.entrada import EntradaStatus
from app.database.models.pedido import PedidoStatus
from app.database.models.orden_trabajo import OTStatus

logger = logging.getLogger(__name__)


class ImportError:
    """Representa un error de importación."""
    def __init__(self, table: str, row_id, field: str, message: str, original_value=None):
        self.table = table
        self.row_id = row_id
        self.field = field
        self.message = message
        self.original_value = original_value
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'table': self.table,
            'row_id': self.row_id,
            'field': self.field,
            'message': self.message,
            'original_value': str(self.original_value) if self.original_value else None
        }


class Phase3ImportResult:
    """Resultado de importación Phase 3."""
    def __init__(self):
        self.ordenes_trabajo = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.pedidos = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.entradas = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.start_time = None
        self.end_time = None

    @property
    def duration_seconds(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    def to_dict(self):
        return {
            'duration_seconds': self.duration_seconds,
            'ordenes_trabajo': self.ordenes_trabajo,
            'pedidos': self.pedidos,
            'entradas': self.entradas,
            'total_imported': (
                self.ordenes_trabajo['imported'] +
                self.pedidos['imported'] +
                self.entradas['imported']
            ),
            'total_errors': (
                len(self.ordenes_trabajo['errors']) +
                len(self.pedidos['errors']) +
                len(self.entradas['errors'])
            )
        }


class Phase3ImportService:
    """Servicio para importar datos transaccionales Phase 3."""

    BATCH_SIZE = 50

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.result = Phase3ImportResult()

        # Caché de FKs válidas
        self._valid_clientes = None
        self._valid_productos = None
        self._valid_fabricas = None
        self._valid_ramas = None
        self._valid_unidades = None

    def _load_fk_cache(self):
        """Cargar caché de FKs válidas."""
        self._valid_clientes = {c.id for c in Cliente.query.all()}
        self._valid_productos = {p.id for p in Producto.query.all()}
        self._valid_fabricas = {f.id for f in Fabrica.query.all()}
        self._valid_ramas = {r.id for r in Rama.query.all()}
        self._valid_unidades = {u.id for u in UnidadMedida.query.all()}

    def import_all(self, data_dir: str) -> Phase3ImportResult:
        """Importar todos los datos transaccionales."""
        self.result.start_time = datetime.utcnow()
        data_path = Path(data_dir)

        # Cargar caché de FKs
        logger.info("Cargando caché de FKs...")
        self._load_fk_cache()

        # Importar en orden correcto (OT → Pedidos → Entradas)
        logger.info("=== Importando Órdenes de Trabajo ===")
        self._import_ordenes_trabajo(data_path / 'ordenes_trabajo.csv')

        logger.info("=== Importando Pedidos ===")
        self._import_pedidos(data_path / 'pedidos.csv')

        logger.info("=== Importando Entradas ===")
        self._import_entradas(data_path / 'entradas.csv')

        self.result.end_time = datetime.utcnow()
        return self.result

    def _import_ordenes_trabajo(self, csv_path: Path):
        """Importar 37 órdenes de trabajo."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.result.ordenes_trabajo['total'] = len(rows)

        for row_num, row in enumerate(rows, start=2):
            try:
                row_id = row.get('Id', row_num)

                # Validar cliente_id
                cliente_id = int(row['IdCliente']) if row.get('IdCliente') else None
                if not cliente_id or cliente_id not in self._valid_clientes:
                    raise ValueError(f"Cliente inválido: {cliente_id}")

                # Verificar duplicados
                nro_ofic = row.get('NroOfic', '').strip()
                if not nro_ofic:
                    raise ValueError("NroOfic es obligatorio")

                existente = OrdenTrabajo.query.filter_by(nro_ofic=nro_ofic).first()
                if existente:
                    logger.info(f"OT {nro_ofic} ya existe, saltando")
                    self.result.ordenes_trabajo['skipped'] += 1
                    continue

                # Parsear fechas
                fech_creacion = self._parse_datetime(row.get('FechCreacion'))

                # Crear OT
                ot = OrdenTrabajo(
                    id=int(row['Id']),
                    nro_ofic=nro_ofic,
                    codigo=f"OT-{int(row['Id']):04d}",
                    cliente_id=cliente_id,
                    descripcion=row.get('Descripcion', ''),
                    observaciones=row.get('Observaciones', ''),
                    status=OTStatus.PENDIENTE,
                    fech_creacion=fech_creacion or datetime.utcnow()
                )

                if not self.dry_run:
                    db.session.add(ot)
                    if self.result.ordenes_trabajo['imported'] % self.BATCH_SIZE == 0:
                        db.session.commit()

                self.result.ordenes_trabajo['imported'] += 1
                logger.debug(f"OT importada: {nro_ofic}")

            except Exception as e:
                logger.error(f"Error importando OT fila {row_num}: {e}")
                self.result.ordenes_trabajo['errors'].append(
                    ImportError('ordenes_trabajo', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        logger.info(f"Órdenes de trabajo: {self.result.ordenes_trabajo['imported']} importadas, "
                   f"{self.result.ordenes_trabajo['skipped']} omitidas, "
                   f"{len(self.result.ordenes_trabajo['errors'])} errores")

    def _import_pedidos(self, csv_path: Path):
        """Importar 49 pedidos."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.result.pedidos['total'] = len(rows)

        for row_num, row in enumerate(rows, start=2):
            try:
                row_id = row.get('IdPedido', row_num)

                # Validar FKs obligatorias
                cliente_id = int(row['IdCliente']) if row.get('IdCliente') else None
                producto_id = int(row['IdProducto']) if row.get('IdProducto') else None

                if not cliente_id or cliente_id not in self._valid_clientes:
                    raise ValueError(f"Cliente inválido: {cliente_id}")
                if not producto_id or producto_id not in self._valid_productos:
                    raise ValueError(f"Producto inválido: {producto_id}")

                # OT opcional
                ot_id = int(row['IdOrdenTrabajo']) if row.get('IdOrdenTrabajo') else None
                if ot_id and ot_id not in {ot.id for ot in OrdenTrabajo.query.all()}:
                    logger.warning(f"OT {ot_id} no encontrada para pedido {row_id}")
                    ot_id = None

                # Validar fechas
                fech_fab = self._parse_date(row.get('FechFab'))
                fech_venc = self._parse_date(row.get('FechVenc'))
                if fech_fab and fech_venc and fech_venc < fech_fab:
                    raise ValueError(f"FechVenc ({fech_venc}) < FechFab ({fech_fab})")

                # Verificar duplicados
                existente = Pedido.query.get(int(row['IdPedido']))
                if existente:
                    logger.info(f"Pedido {row_id} ya existe, saltando")
                    self.result.pedidos['skipped'] += 1
                    continue

                # Crear pedido
                pedido = Pedido(
                    id=int(row['IdPedido']),
                    codigo=f"PED-{int(row['IdPedido']):04d}",
                    cliente_id=cliente_id,
                    producto_id=producto_id,
                    orden_trabajo_id=ot_id,
                    lote=row.get('Lote'),
                    cantidad=self._parse_decimal(row.get('Cantidad')),
                    unidad_medida_id=int(row['IdUnidadMedida']) if row.get('IdUnidadMedida') else None,
                    fech_fab=fech_fab,
                    fech_venc=fech_venc,
                    observaciones=row.get('Observaciones', ''),
                    status=PedidoStatus.PENDIENTE,
                    fech_pedido=self._parse_datetime(row.get('FechPedido')) or datetime.utcnow()
                )

                if not self.dry_run:
                    db.session.add(pedido)
                    if self.result.pedidos['imported'] % self.BATCH_SIZE == 0:
                        db.session.commit()

                self.result.pedidos['imported'] += 1
                logger.debug(f"Pedido importado: {pedido.codigo}")

            except Exception as e:
                logger.error(f"Error importando Pedido fila {row_num}: {e}")
                self.result.pedidos['errors'].append(
                    ImportError('pedidos', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        logger.info(f"Pedidos: {self.result.pedidos['imported']} importados, "
                   f"{self.result.pedidos['skipped']} omitidos, "
                   f"{len(self.result.pedidos['errors'])} errores")

    def _import_entradas(self, csv_path: Path):
        """Importar 109 entradas."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.result.entradas['total'] = len(rows)

        for row_num, row in enumerate(rows, start=2):
            try:
                row_id = row.get('Id', row_num)

                # Validar FKs obligatorias
                cliente_id = int(row['IdCliente']) if row.get('IdCliente') else None
                producto_id = int(row['IdProducto']) if row.get('IdProducto') else None
                fabrica_id = int(row['IdFabrica']) if row.get('IdFabrica') else None

                if not cliente_id or cliente_id not in self._valid_clientes:
                    raise ValueError(f"Cliente inválido: {cliente_id}")
                if not producto_id or producto_id not in self._valid_productos:
                    raise ValueError(f"Producto inválido: {producto_id}")
                if not fabrica_id or fabrica_id not in self._valid_fabricas:
                    raise ValueError(f"Fábrica inválida: {fabrica_id}")

                # Validar formato de lote
                lote = row.get('Lote', '').strip()
                if lote and not re.match(r'^[A-Z]-\d{4}$', lote):
                    logger.warning(f"Lote con formato incorrecto: {lote}")

                # Verificar balance
                cant_recib = self._parse_decimal(row.get('CantidadRecib', 0))
                cant_entreg = self._parse_decimal(row.get('CantidadEntreg', 0))
                expected_saldo = cant_recib - cant_entreg

                # Verificar duplicados
                existente = Entrada.query.get(int(row['Id']))
                if existente:
                    logger.info(f"Entrada {row_id} ya existe, saltando")
                    self.result.entradas['skipped'] += 1
                    continue

                # Crear entrada
                entrada = Entrada(
                    id=int(row['Id']),
                    codigo=row.get('Codigo', f"ENT-{int(row['Id']):04d}"),
                    pedido_id=int(row['IdPedido']) if row.get('IdPedido') else None,
                    producto_id=producto_id,
                    fabrica_id=fabrica_id,
                    cliente_id=cliente_id,
                    rama_id=int(row['IdRama']) if row.get('IdRama') else None,
                    unidad_medida_id=int(row['IdUnidadMedida']) if row.get('IdUnidadMedida') else None,
                    lote=lote or None,
                    nro_parte=row.get('NroParte'),
                    cantidad_recib=cant_recib,
                    cantidad_entreg=cant_entreg,
                    cantidad_muest=self._parse_decimal(row.get('CantidadMuest')),
                    fech_fab=self._parse_date(row.get('FechFab')),
                    fech_venc=self._parse_date(row.get('FechVenc')),
                    fech_muestreo=self._parse_date(row.get('FechMuestreo')),
                    fech_entrada=self._parse_datetime(row.get('FechEntrada')) or datetime.utcnow(),
                    status=row.get('Status', EntradaStatus.RECIBIDO),
                    en_os=bool(int(row.get('EnOS', 0))),
                    anulado=bool(int(row.get('Anulado', 0))),
                    ent_entregada=bool(int(row.get('EntEntregada', 0))),
                    observaciones=row.get('Observaciones', '')
                )

                if not self.dry_run:
                    db.session.add(entrada)
                    if self.result.entradas['imported'] % self.BATCH_SIZE == 0:
                        db.session.commit()

                self.result.entradas['imported'] += 1
                logger.debug(f"Entrada importada: {entrada.codigo}")

            except Exception as e:
                logger.error(f"Error importando Entrada fila {row_num}: {e}")
                self.result.entradas['errors'].append(
                    ImportError('entradas', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        logger.info(f"Entradas: {self.result.entradas['imported']} importadas, "
                   f"{self.result.entradas['skipped']} omitidas, "
                   f"{len(self.result.entradas['errors'])} errores")

    def _parse_date(self, value) -> Optional[date]:
        """Parsear fecha desde string."""
        if not value:
            return None
        try:
            # Intentar formato ISO
            return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(str(value), '%d/%m/%Y').date()
            except ValueError:
                return None

    def _parse_datetime(self, value) -> Optional[datetime]:
        """Parsear datetime desde string."""
        if not value:
            return None
        try:
            return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(str(value)[:10], '%Y-%m-%d')
            except ValueError:
                return None

    def _parse_decimal(self, value) -> Decimal:
        """Parsear decimal desde string."""
        if not value:
            return Decimal('0')
        try:
            # Manejar formato con coma como separador decimal
            clean_value = str(value).replace(',', '.')
            return Decimal(clean_value)
        except (InvalidOperation, ValueError):
            return Decimal('0')
