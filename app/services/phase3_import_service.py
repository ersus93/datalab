"""Servicio para importación de datos transaccionales Phase 3 desde Access.

Cubre los requisitos del Issue #5 (Phase 3): Transactional Data Import
- Import OT (37), Pedidos (49), Entradas (109) desde CSV
- Validación FK pre-importación con reporte de referencias faltantes
- Verificación de balances con tracking en resultado
- Validación de formato de lote con tracking en resultado
- Verificación post-importación (conteos, FK integrity, consistencia)
- Reporte final en Markdown
- Dry-run standalone (sin efectos secundarios)
"""
import csv
import logging
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app import db
from app.database.models import (
    Cliente, Entrada, Fabrica, OrdenTrabajo, Pedido, Producto, Rama, UnidadMedida,
)
from app.database.models.entrada import EntradaStatus
from app.database.models.orden_trabajo import OTStatus
from app.database.models.pedido import PedidoStatus

logger = logging.getLogger(__name__)

# Conteos esperados según Access RM2026
EXPECTED_COUNTS = {
    'ordenes_trabajo': 37,
    'pedidos': 49,
    'entradas': 109,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class ImportError:
    """Representa un error de importación (registro omitido)."""

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
            'original_value': str(self.original_value) if self.original_value is not None else None,
        }


class ImportWarning:
    """Representa una advertencia (registro importado con datos anómalos)."""

    def __init__(self, table: str, row_id, warning_type: str, message: str, value=None):
        self.table = table
        self.row_id = row_id
        self.warning_type = warning_type  # 'balance_mismatch' | 'lot_format' | 'date'
        self.message = message
        self.value = value

    def to_dict(self):
        return {
            'table': self.table,
            'row_id': self.row_id,
            'type': self.warning_type,
            'message': self.message,
            'value': str(self.value) if self.value is not None else None,
        }


class Phase3ImportResult:
    """Resultado completo de importación Phase 3."""

    def __init__(self):
        self.ordenes_trabajo = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.pedidos         = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.entradas        = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.balance_warnings: List[ImportWarning] = []
        self.lot_warnings: List[ImportWarning] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def total_imported(self) -> int:
        return (self.ordenes_trabajo['imported'] +
                self.pedidos['imported'] +
                self.entradas['imported'])

    @property
    def total_errors(self) -> int:
        return (len(self.ordenes_trabajo['errors']) +
                len(self.pedidos['errors']) +
                len(self.entradas['errors']))

    def to_dict(self) -> dict:
        def _serialize_errors(errors):
            return [e.to_dict() if hasattr(e, 'to_dict') else str(e) for e in errors]

        return {
            'duration_seconds': self.duration_seconds,
            'total_imported': self.total_imported,
            'total_errors': self.total_errors,
            'balance_warnings': len(self.balance_warnings),
            'lot_warnings': len(self.lot_warnings),
            'ordenes_trabajo': {**self.ordenes_trabajo,
                                'errors': _serialize_errors(self.ordenes_trabajo['errors'])},
            'pedidos':         {**self.pedidos,
                                'errors': _serialize_errors(self.pedidos['errors'])},
            'entradas':        {**self.entradas,
                                'errors': _serialize_errors(self.entradas['errors'])},
        }


class PreImportValidationReport:
    """Resultado de validación pre-importación."""

    def __init__(self):
        self.missing_clientes: List[dict] = []
        self.missing_productos: List[dict] = []
        self.missing_fabricas: List[dict] = []
        self.missing_ordenes_trabajo: List[dict] = []
        self.missing_unidades: List[dict] = []
        self.invalid_lots: List[dict] = []
        self.balance_mismatches: List[dict] = []
        self.date_errors: List[dict] = []
        self.file_errors: List[str] = []

    @property
    def is_clean(self) -> bool:
        """True si no hay problemas bloqueantes (solo warnings permiten continuar)."""
        return not any([
            self.missing_clientes,
            self.missing_productos,
            self.missing_fabricas,
            self.file_errors,
        ])

    def to_markdown(self) -> str:
        lines = ['# Pre-Import Validation Report — Phase 3', '']
        lines.append(f'**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}')
        lines.append('')

        status = '✅ CLEAN — Ready to import' if self.is_clean else '❌ ISSUES FOUND — Review before importing'
        lines.append(f'**Status:** {status}')
        lines.append('')

        def _section(title, items, cols):
            lines.append(f'## {title} ({len(items)})')
            if not items:
                lines.append('_None found_')
            else:
                lines.append('| ' + ' | '.join(cols) + ' |')
                lines.append('| ' + ' | '.join(['---'] * len(cols)) + ' |')
                for item in items[:50]:
                    lines.append('| ' + ' | '.join(str(item.get(c, '')) for c in cols) + ' |')
                if len(items) > 50:
                    lines.append(f'_... and {len(items) - 50} more_')
            lines.append('')

        _section('Missing Clientes (bloqueante)', self.missing_clientes,
                 ['table', 'row_id', 'cliente_id'])
        _section('Missing Productos (bloqueante)', self.missing_productos,
                 ['table', 'row_id', 'producto_id'])
        _section('Missing Fábricas (bloqueante)', self.missing_fabricas,
                 ['table', 'row_id', 'fabrica_id'])
        _section('Missing Órdenes de Trabajo (se omitirá FK)', self.missing_ordenes_trabajo,
                 ['table', 'row_id', 'ot_id'])
        _section('Lot Format Issues (advertencia)', self.invalid_lots,
                 ['table', 'row_id', 'lote'])
        _section('Balance Mismatches (advertencia)', self.balance_mismatches,
                 ['row_id', 'cant_recib', 'cant_entreg', 'stated_saldo', 'expected_saldo'])
        _section('Date Errors (advertencia)', self.date_errors,
                 ['table', 'row_id', 'field', 'value'])
        _section('File Errors (crítico)', [{'error': e} for e in self.file_errors],
                 ['error'])

        return '\n'.join(lines)


class PostImportVerification:
    """Resultado de verificación post-importación."""

    def __init__(self):
        self.count_checks: Dict[str, dict] = {}
        self.fk_checks: Dict[str, dict] = {}
        self.consistency_checks: Dict[str, dict] = {}

    @property
    def all_passed(self) -> bool:
        checks = list(self.count_checks.values()) + \
                 list(self.fk_checks.values()) + \
                 list(self.consistency_checks.values())
        return all(c.get('passed', False) for c in checks)

    def to_markdown(self) -> str:
        lines = ['# Post-Import Verification Report — Phase 3', '']
        lines.append(f'**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}')
        lines.append('')
        status = '✅ ALL CHECKS PASSED' if self.all_passed else '⚠️ SOME CHECKS FAILED'
        lines.append(f'**Status:** {status}')
        lines.append('')

        def _table(title, checks):
            lines.append(f'## {title}')
            lines.append('| Check | Expected | Actual | Status |')
            lines.append('| --- | --- | --- | --- |')
            for name, c in checks.items():
                icon = '✅' if c.get('passed') else '❌'
                lines.append(f'| {name} | {c.get("expected", "-")} | {c.get("actual", "-")} | {icon} |')
            lines.append('')

        _table('Record Counts', self.count_checks)
        _table('FK Integrity (orphaned records = 0 expected)', self.fk_checks)
        _table('Data Consistency', self.consistency_checks)
        return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

class Phase3ImportService:
    """Servicio para importar datos transaccionales Phase 3."""

    BATCH_SIZE = 50

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.result = Phase3ImportResult()
        # FK caches
        self._valid_clientes: Optional[set] = None
        self._valid_productos: Optional[set] = None
        self._valid_fabricas: Optional[set] = None
        self._valid_ramas: Optional[set] = None
        self._valid_unidades: Optional[set] = None
        self._valid_ots: Optional[set] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def import_all(self, data_dir: str) -> Phase3ImportResult:
        """Importar todos los datos transaccionales en orden correcto."""
        self.result.start_time = datetime.utcnow()
        data_path = Path(data_dir)

        logger.info("Cargando caché de FKs...")
        self._load_fk_cache()

        logger.info("=== Importando Órdenes de Trabajo ===")
        self._import_ordenes_trabajo(data_path / 'ordenes_trabajo.csv')

        logger.info("=== Importando Pedidos ===")
        self._import_pedidos(data_path / 'pedidos.csv')

        logger.info("=== Importando Entradas ===")
        self._import_entradas(data_path / 'entradas.csv')

        self.result.end_time = datetime.utcnow()
        return self.result

    def validate_all(self, data_dir: str) -> PreImportValidationReport:
        """
        Validación pre-importación completa SIN modificar la base de datos.

        Lee todos los CSV, verifica referencias FK, balances, formatos de lote
        y genera un reporte detallado de problemas encontrados.

        Args:
            data_dir: Directorio con los CSV de OT, Pedidos y Entradas.

        Returns:
            PreImportValidationReport con todos los problemas encontrados.
        """
        report = PreImportValidationReport()
        data_path = Path(data_dir)

        # Cargar FK válidas desde la BD
        self._load_fk_cache()

        # Validar cada archivo
        self._validate_ordenes_trabajo_csv(data_path / 'ordenes_trabajo.csv', report)
        self._validate_pedidos_csv(data_path / 'pedidos.csv', report)
        self._validate_entradas_csv(data_path / 'entradas.csv', report)

        return report

    def verify_post_import(self) -> PostImportVerification:
        """
        Verificación post-importación: conteos, FK integrity y consistencia de datos.

        Returns:
            PostImportVerification con resultado de cada chequeo.
        """
        v = PostImportVerification()

        # --- Conteos vs esperados ---
        v.count_checks['Órdenes de Trabajo'] = {
            'expected': EXPECTED_COUNTS['ordenes_trabajo'],
            'actual': OrdenTrabajo.query.count(),
            'passed': OrdenTrabajo.query.count() == EXPECTED_COUNTS['ordenes_trabajo'],
        }
        v.count_checks['Pedidos'] = {
            'expected': EXPECTED_COUNTS['pedidos'],
            'actual': Pedido.query.count(),
            'passed': Pedido.query.count() == EXPECTED_COUNTS['pedidos'],
        }
        v.count_checks['Entradas'] = {
            'expected': EXPECTED_COUNTS['entradas'],
            'actual': Entrada.query.count(),
            'passed': Entrada.query.count() == EXPECTED_COUNTS['entradas'],
        }

        # --- FK integrity (registros huérfanos) ---
        pedidos_sin_cliente = Pedido.query.filter(
            ~Pedido.cliente_id.in_(db.session.query(Cliente.id))
        ).count()
        v.fk_checks['Pedidos → Clientes'] = {
            'expected': 0, 'actual': pedidos_sin_cliente,
            'passed': pedidos_sin_cliente == 0,
        }

        entradas_sin_cliente = Entrada.query.filter(
            ~Entrada.cliente_id.in_(db.session.query(Cliente.id))
        ).count()
        v.fk_checks['Entradas → Clientes'] = {
            'expected': 0, 'actual': entradas_sin_cliente,
            'passed': entradas_sin_cliente == 0,
        }

        entradas_sin_producto = Entrada.query.filter(
            ~Entrada.producto_id.in_(db.session.query(Producto.id))
        ).count()
        v.fk_checks['Entradas → Productos'] = {
            'expected': 0, 'actual': entradas_sin_producto,
            'passed': entradas_sin_producto == 0,
        }

        entradas_sin_fabrica = Entrada.query.filter(
            ~Entrada.fabrica_id.in_(db.session.query(Fabrica.id))
        ).count()
        v.fk_checks['Entradas → Fábricas'] = {
            'expected': 0, 'actual': entradas_sin_fabrica,
            'passed': entradas_sin_fabrica == 0,
        }

        # --- Consistencia de datos ---
        # Cantidades negativas
        entradas_neg_recib = Entrada.query.filter(Entrada.cantidad_recib < 0).count()
        v.consistency_checks['Entradas con cantidad_recib negativa'] = {
            'expected': 0, 'actual': entradas_neg_recib,
            'passed': entradas_neg_recib == 0,
        }

        entradas_neg_entreg = Entrada.query.filter(Entrada.cantidad_entreg < 0).count()
        v.consistency_checks['Entradas con cantidad_entreg negativa'] = {
            'expected': 0, 'actual': entradas_neg_entreg,
            'passed': entradas_neg_entreg == 0,
        }

        # Saldo incorrecto (saldo != recib - entreg)
        from sqlalchemy import func, case
        bad_saldo = db.session.execute(
            db.select(func.count()).where(
                Entrada.saldo != (Entrada.cantidad_recib - Entrada.cantidad_entreg)
            )
        ).scalar()
        v.consistency_checks['Entradas con saldo incorrecto'] = {
            'expected': 0, 'actual': bad_saldo,
            'passed': bad_saldo == 0,
        }

        # Status flags consistentes con estado
        anuladas_mal = Entrada.query.filter(
            Entrada.anulado == True,
            Entrada.status != EntradaStatus.ANULADO
        ).count()
        v.consistency_checks['Anuladas con status incorrecto'] = {
            'expected': 0, 'actual': anuladas_mal,
            'passed': anuladas_mal == 0,
        }

        entregadas_mal = Entrada.query.filter(
            Entrada.ent_entregada == True,
            Entrada.status != EntradaStatus.ENTREGADO
        ).count()
        v.consistency_checks['Entregadas con status incorrecto'] = {
            'expected': 0, 'actual': entregadas_mal,
            'passed': entregadas_mal == 0,
        }

        return v

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generar reporte de importación en formato Markdown.

        Args:
            output_path: Si se provee, guarda el reporte en este archivo.

        Returns:
            Reporte en formato Markdown como string.
        """
        r = self.result
        lines = [
            '# Reporte de Importación Phase 3 — DataLab',
            '',
            f'**Generado:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}',
            f'**Modo:** {"DRY-RUN (sin cambios en BD)" if self.dry_run else "IMPORTACIÓN REAL"}',
            f'**Duración:** {r.duration_seconds:.2f} segundos',
            '',
            '---',
            '',
            '## Resumen',
            '',
            '| Entidad | Total CSV | Importados | Omitidos | Errores | Esperados |',
            '| --- | --- | --- | --- | --- | --- |',
        ]

        for key, expected in EXPECTED_COUNTS.items():
            section = getattr(r, key)
            imp = section['imported']
            total = section['total']
            skipped = section['skipped']
            errors = len(section['errors'])
            ok = '✅' if imp == expected else '⚠️'
            lines.append(
                f'| {key.replace("_", " ").title()} | {total} | {imp} | {skipped} | {errors} | {expected} {ok} |'
            )

        lines += [
            '',
            f'**Total importados:** {r.total_imported} / {sum(EXPECTED_COUNTS.values())}',
            f'**Total errores:** {r.total_errors}',
            f'**Advertencias de balance:** {len(r.balance_warnings)}',
            f'**Advertencias de lote:** {len(r.lot_warnings)}',
            '',
            '---',
            '',
        ]

        # Sección de errores
        all_errors = (
            r.ordenes_trabajo['errors'] +
            r.pedidos['errors'] +
            r.entradas['errors']
        )
        lines.append(f'## Errores ({len(all_errors)})')
        if not all_errors:
            lines.append('_Sin errores_')
        else:
            lines.append('| Tabla | ID Fila | Campo | Mensaje |')
            lines.append('| --- | --- | --- | --- |')
            for e in all_errors:
                if hasattr(e, 'to_dict'):
                    d = e.to_dict()
                    lines.append(f'| {d["table"]} | {d["row_id"]} | {d["field"]} | {d["message"]} |')
        lines.append('')

        # Advertencias de balance
        lines.append(f'## Advertencias de Balance ({len(r.balance_warnings)})')
        if not r.balance_warnings:
            lines.append('_Sin discrepancias de balance_')
        else:
            lines.append('| ID Entrada | Mensaje |')
            lines.append('| --- | --- |')
            for w in r.balance_warnings:
                lines.append(f'| {w.row_id} | {w.message} |')
        lines.append('')

        # Advertencias de lote
        lines.append(f'## Advertencias de Formato de Lote ({len(r.lot_warnings)})')
        if not r.lot_warnings:
            lines.append('_Todos los lotes tienen formato correcto_')
        else:
            lines.append('| ID Entrada | Lote | Mensaje |')
            lines.append('| --- | --- | --- |')
            for w in r.lot_warnings:
                lines.append(f'| {w.row_id} | {w.value} | {w.message} |')
        lines.append('')

        lines += [
            '---',
            '',
            '## Verificación de Conteos',
            '',
            '| Entidad | Esperados | Importados | Estado |',
            '| --- | --- | --- | --- |',
        ]
        for key, expected in EXPECTED_COUNTS.items():
            section = getattr(r, key)
            imp = section['imported']
            icon = '✅' if imp >= expected else '❌'
            lines.append(f'| {key.replace("_", " ").title()} | {expected} | {imp} | {icon} |')

        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('_Generado por DataLab Phase 3 Import Service_')

        report_md = '\n'.join(lines)

        if output_path:
            Path(output_path).write_text(report_md, encoding='utf-8')
            logger.info(f"Reporte guardado en: {output_path}")

        return report_md

    # ------------------------------------------------------------------
    # Private: import methods
    # ------------------------------------------------------------------

    def _load_fk_cache(self):
        """Cargar sets de IDs válidos para validación FK rápida."""
        self._valid_clientes  = {c.id for c in Cliente.query.all()}
        self._valid_productos  = {p.id for p in Producto.query.all()}
        self._valid_fabricas   = {f.id for f in Fabrica.query.all()}
        self._valid_ramas      = {r.id for r in Rama.query.all()}
        self._valid_unidades   = {u.id for u in UnidadMedida.query.all()}
        self._valid_ots        = {o.id for o in OrdenTrabajo.query.all()}

    def _import_ordenes_trabajo(self, csv_path: Path):
        """Importar 37 órdenes de trabajo."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        self.result.ordenes_trabajo['total'] = len(rows)
        batch_count = 0

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('Id', row_num)
            try:
                cliente_id = int(row['IdCliente']) if row.get('IdCliente') else None
                if not cliente_id or cliente_id not in self._valid_clientes:
                    raise ValueError(f"Cliente inválido: {cliente_id}")

                nro_ofic = row.get('NroOfic', '').strip()
                if not nro_ofic:
                    raise ValueError("NroOfic es obligatorio")

                if OrdenTrabajo.query.filter_by(nro_ofic=nro_ofic).first():
                    logger.debug(f"OT {nro_ofic} ya existe, saltando")
                    self.result.ordenes_trabajo['skipped'] += 1
                    continue

                ot = OrdenTrabajo(
                    id=int(row['Id']),
                    nro_ofic=nro_ofic,
                    codigo=f"OT-{int(row['Id']):04d}",
                    cliente_id=cliente_id,
                    descripcion=row.get('Descripcion', ''),
                    observaciones=row.get('Observaciones', ''),
                    status=OTStatus.PENDIENTE,
                    fech_creacion=self._parse_datetime(row.get('FechCreacion')) or datetime.utcnow(),
                )

                if not self.dry_run:
                    db.session.add(ot)
                    batch_count += 1
                    if batch_count % self.BATCH_SIZE == 0:
                        db.session.commit()
                        logger.debug(f"Commit batch OT ({batch_count})")

                self.result.ordenes_trabajo['imported'] += 1

            except Exception as e:
                logger.error(f"Error OT fila {row_num}: {e}")
                self.result.ordenes_trabajo['errors'].append(
                    ImportError('ordenes_trabajo', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()
        # Actualizar caché de OTs para que Pedidos las puedan referenciar
        self._valid_ots = {o.id for o in OrdenTrabajo.query.all()}

        logger.info(
            f"OT: {self.result.ordenes_trabajo['imported']} importadas, "
            f"{self.result.ordenes_trabajo['skipped']} omitidas, "
            f"{len(self.result.ordenes_trabajo['errors'])} errores"
        )

    def _import_pedidos(self, csv_path: Path):
        """Importar 49 pedidos."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        self.result.pedidos['total'] = len(rows)
        batch_count = 0

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('IdPedido', row_num)
            try:
                cliente_id  = int(row['IdCliente'])  if row.get('IdCliente')  else None
                producto_id = int(row['IdProducto']) if row.get('IdProducto') else None

                if not cliente_id or cliente_id not in self._valid_clientes:
                    raise ValueError(f"Cliente inválido: {cliente_id}")
                if not producto_id or producto_id not in self._valid_productos:
                    raise ValueError(f"Producto inválido: {producto_id}")

                # OT opcional: si no existe, se deja en None con advertencia
                ot_id = int(row['IdOrdenTrabajo']) if row.get('IdOrdenTrabajo') else None
                if ot_id and ot_id not in self._valid_ots:
                    logger.warning(f"OT {ot_id} no encontrada para pedido {row_id}, FK ignorada")
                    ot_id = None

                fech_fab  = self._parse_date(row.get('FechFab'))
                fech_venc = self._parse_date(row.get('FechVenc'))
                if fech_fab and fech_venc and fech_venc < fech_fab:
                    raise ValueError(f"FechVenc ({fech_venc}) < FechFab ({fech_fab})")

                if Pedido.query.get(int(row['IdPedido'])):
                    self.result.pedidos['skipped'] += 1
                    continue

                pedido = Pedido(
                    id=int(row['IdPedido']),
                    codigo=f"PED-{int(row['IdPedido']):04d}",
                    cliente_id=cliente_id,
                    producto_id=producto_id,
                    orden_trabajo_id=ot_id,
                    lote=row.get('Lote') or None,
                    cantidad=self._parse_decimal(row.get('Cantidad')),
                    unidad_medida_id=int(row['IdUnidadMedida']) if row.get('IdUnidadMedida') else None,
                    fech_fab=fech_fab,
                    fech_venc=fech_venc,
                    observaciones=row.get('Observaciones', ''),
                    status=PedidoStatus.PENDIENTE,
                    fech_pedido=self._parse_datetime(row.get('FechPedido')) or datetime.utcnow(),
                )

                if not self.dry_run:
                    db.session.add(pedido)
                    batch_count += 1
                    if batch_count % self.BATCH_SIZE == 0:
                        db.session.commit()

                self.result.pedidos['imported'] += 1

            except Exception as e:
                logger.error(f"Error Pedido fila {row_num}: {e}")
                self.result.pedidos['errors'].append(
                    ImportError('pedidos', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        logger.info(
            f"Pedidos: {self.result.pedidos['imported']} importados, "
            f"{self.result.pedidos['skipped']} omitidos, "
            f"{len(self.result.pedidos['errors'])} errores"
        )

    def _import_entradas(self, csv_path: Path):
        """Importar 109 entradas."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        self.result.entradas['total'] = len(rows)
        batch_count = 0

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('Id', row_num)
            try:
                cliente_id  = int(row['IdCliente'])  if row.get('IdCliente')  else None
                producto_id = int(row['IdProducto']) if row.get('IdProducto') else None
                fabrica_id  = int(row['IdFabrica'])  if row.get('IdFabrica')  else None

                if not cliente_id or cliente_id not in self._valid_clientes:
                    raise ValueError(f"Cliente inválido: {cliente_id}")
                if not producto_id or producto_id not in self._valid_productos:
                    raise ValueError(f"Producto inválido: {producto_id}")
                if not fabrica_id or fabrica_id not in self._valid_fabricas:
                    raise ValueError(f"Fábrica inválida: {fabrica_id}")

                # Validar y registrar formato de lote
                lote = row.get('Lote', '').strip() or None
                if lote and not re.match(r'^[A-Z]-\d{4}$', lote):
                    warn = ImportWarning('entradas', row_id, 'lot_format',
                                         f"Lote '{lote}' no cumple formato X-XXXX", lote)
                    self.result.lot_warnings.append(warn)
                    logger.warning(f"Lote incorrecto Entrada {row_id}: {lote}")

                # Verificar y registrar balance
                cant_recib  = self._parse_decimal(row.get('CantidadRecib', 0))
                cant_entreg = self._parse_decimal(row.get('CantidadEntreg', 0))
                expected_saldo = cant_recib - cant_entreg
                stated_saldo   = self._parse_decimal(row.get('Saldo', expected_saldo))

                if abs(expected_saldo - stated_saldo) > Decimal('0.01'):
                    warn = ImportWarning(
                        'entradas', row_id, 'balance_mismatch',
                        f"Saldo declarado {stated_saldo} ≠ calculado {expected_saldo} "
                        f"(recib={cant_recib}, entreg={cant_entreg})",
                        stated_saldo,
                    )
                    self.result.balance_warnings.append(warn)
                    logger.warning(f"Balance mismatch Entrada {row_id}: {warn.message}")

                if Entrada.query.get(int(row['Id'])):
                    self.result.entradas['skipped'] += 1
                    continue

                entrada = Entrada(
                    id=int(row['Id']),
                    codigo=row.get('Codigo') or f"ENT-{int(row['Id']):04d}",
                    pedido_id=int(row['IdPedido']) if row.get('IdPedido') else None,
                    producto_id=producto_id,
                    fabrica_id=fabrica_id,
                    cliente_id=cliente_id,
                    rama_id=int(row['IdRama']) if row.get('IdRama') else None,
                    unidad_medida_id=int(row['IdUnidadMedida']) if row.get('IdUnidadMedida') else None,
                    lote=lote,
                    nro_parte=row.get('NroParte') or None,
                    cantidad_recib=cant_recib,
                    cantidad_entreg=cant_entreg,
                    cantidad_muest=self._parse_decimal(row.get('CantidadMuest')) or None,
                    fech_fab=self._parse_date(row.get('FechFab')),
                    fech_venc=self._parse_date(row.get('FechVenc')),
                    fech_muestreo=self._parse_date(row.get('FechMuestreo')),
                    fech_entrada=self._parse_datetime(row.get('FechEntrada')) or datetime.utcnow(),
                    status=row.get('Status') or EntradaStatus.RECIBIDO,
                    en_os=bool(int(row.get('EnOS', 0) or 0)),
                    anulado=bool(int(row.get('Anulado', 0) or 0)),
                    ent_entregada=bool(int(row.get('EntEntregada', 0) or 0)),
                    observaciones=row.get('Observaciones', ''),
                )

                if not self.dry_run:
                    db.session.add(entrada)
                    batch_count += 1
                    if batch_count % self.BATCH_SIZE == 0:
                        db.session.commit()

                self.result.entradas['imported'] += 1

            except Exception as e:
                logger.error(f"Error Entrada fila {row_num}: {e}")
                self.result.entradas['errors'].append(
                    ImportError('entradas', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        logger.info(
            f"Entradas: {self.result.entradas['imported']} importadas, "
            f"{self.result.entradas['skipped']} omitidas, "
            f"{len(self.result.entradas['errors'])} errores, "
            f"{len(self.result.balance_warnings)} advertencias de balance, "
            f"{len(self.result.lot_warnings)} advertencias de lote"
        )

    # ------------------------------------------------------------------
    # Private: pre-import validation helpers
    # ------------------------------------------------------------------

    def _validate_ordenes_trabajo_csv(self, csv_path: Path, report: PreImportValidationReport):
        """Validar CSV de órdenes de trabajo."""
        if not csv_path.exists():
            report.file_errors.append(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('Id', row_num)

            cliente_id = int(row['IdCliente']) if row.get('IdCliente') else None
            if not cliente_id or cliente_id not in self._valid_clientes:
                report.missing_clientes.append({
                    'table': 'ordenes_trabajo', 'row_id': row_id, 'cliente_id': cliente_id
                })

    def _validate_pedidos_csv(self, csv_path: Path, report: PreImportValidationReport):
        """Validar CSV de pedidos."""
        if not csv_path.exists():
            report.file_errors.append(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('IdPedido', row_num)

            cliente_id  = int(row['IdCliente'])  if row.get('IdCliente')  else None
            producto_id = int(row['IdProducto']) if row.get('IdProducto') else None
            ot_id       = int(row['IdOrdenTrabajo']) if row.get('IdOrdenTrabajo') else None

            if not cliente_id or cliente_id not in self._valid_clientes:
                report.missing_clientes.append({
                    'table': 'pedidos', 'row_id': row_id, 'cliente_id': cliente_id
                })
            if not producto_id or producto_id not in self._valid_productos:
                report.missing_productos.append({
                    'table': 'pedidos', 'row_id': row_id, 'producto_id': producto_id
                })
            if ot_id and ot_id not in self._valid_ots:
                report.missing_ordenes_trabajo.append({
                    'table': 'pedidos', 'row_id': row_id, 'ot_id': ot_id
                })

            fech_fab  = self._parse_date(row.get('FechFab'))
            fech_venc = self._parse_date(row.get('FechVenc'))
            if fech_fab and fech_venc and fech_venc < fech_fab:
                report.date_errors.append({
                    'table': 'pedidos', 'row_id': row_id,
                    'field': 'FechVenc', 'value': f"{fech_venc} < {fech_fab}"
                })

    def _validate_entradas_csv(self, csv_path: Path, report: PreImportValidationReport):
        """Validar CSV de entradas."""
        if not csv_path.exists():
            report.file_errors.append(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('Id', row_num)

            cliente_id  = int(row['IdCliente'])  if row.get('IdCliente')  else None
            producto_id = int(row['IdProducto']) if row.get('IdProducto') else None
            fabrica_id  = int(row['IdFabrica'])  if row.get('IdFabrica')  else None

            if not cliente_id or cliente_id not in self._valid_clientes:
                report.missing_clientes.append({
                    'table': 'entradas', 'row_id': row_id, 'cliente_id': cliente_id
                })
            if not producto_id or producto_id not in self._valid_productos:
                report.missing_productos.append({
                    'table': 'entradas', 'row_id': row_id, 'producto_id': producto_id
                })
            if not fabrica_id or fabrica_id not in self._valid_fabricas:
                report.missing_fabricas.append({
                    'table': 'entradas', 'row_id': row_id, 'fabrica_id': fabrica_id
                })

            # Lote
            lote = row.get('Lote', '').strip()
            if lote and not re.match(r'^[A-Z]-\d{4}$', lote):
                report.invalid_lots.append({
                    'table': 'entradas', 'row_id': row_id, 'lote': lote
                })

            # Balance
            cant_recib     = self._parse_decimal(row.get('CantidadRecib', 0))
            cant_entreg    = self._parse_decimal(row.get('CantidadEntreg', 0))
            expected_saldo = cant_recib - cant_entreg
            stated_saldo   = self._parse_decimal(row.get('Saldo', expected_saldo))

            if abs(expected_saldo - stated_saldo) > Decimal('0.01'):
                report.balance_mismatches.append({
                    'row_id': row_id,
                    'cant_recib': str(cant_recib),
                    'cant_entreg': str(cant_entreg),
                    'stated_saldo': str(stated_saldo),
                    'expected_saldo': str(expected_saldo),
                })

            # Fechas
            fech_fab  = self._parse_date(row.get('FechFab'))
            fech_venc = self._parse_date(row.get('FechVenc'))
            if fech_fab and fech_venc and fech_venc < fech_fab:
                report.date_errors.append({
                    'table': 'entradas', 'row_id': row_id,
                    'field': 'FechVenc', 'value': f"{fech_venc} < {fech_fab}"
                })

    # ------------------------------------------------------------------
    # Private: type helpers
    # ------------------------------------------------------------------

    def _parse_date(self, value) -> Optional[date]:
        if not value:
            return None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
            try:
                return datetime.strptime(str(value)[:10], fmt).date()
            except ValueError:
                continue
        return None

    def _parse_datetime(self, value) -> Optional[datetime]:
        if not value:
            return None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(str(value)[:19], fmt)
            except ValueError:
                continue
        return None

    def _parse_decimal(self, value) -> Decimal:
        if not value and value != 0:
            return Decimal('0')
        try:
            return Decimal(str(value).replace(',', '.'))
        except (InvalidOperation, ValueError):
            return Decimal('0')
