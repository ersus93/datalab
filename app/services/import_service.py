"""Servicio para importación de datos desde Access."""
import csv
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from app import db
from app.database.models import Cliente, Fabrica, Producto, Organismo, Provincia, Destino

logger = logging.getLogger(__name__)


class ImportError:
    """Representa un error de importación."""

    def __init__(self, row_number: int, field: str, message: str, original_value):
        self.row_number = row_number
        self.field = field
        self.message = message
        self.original_value = original_value
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'row_number': self.row_number,
            'field': self.field,
            'message': self.message,
            'original_value': str(self.original_value),
            'timestamp': self.timestamp.isoformat()
        }


class ImportResult:
    """Resultado de operación de importación."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.imported = 0
        self.skipped = 0
        self.errors: List[ImportError] = []
        self.start_time = None
        self.end_time = None

    @property
    def duration_ms(self):
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return 0

    def to_dict(self):
        return {
            'table': self.table_name,
            'imported': self.imported,
            'skipped': self.skipped,
            'errors': len(self.errors),
            'duration_ms': self.duration_ms
        }


class MasterDataImportService:
    """Servicio para importar datos maestros desde CSV."""

    BATCH_SIZE = 50

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.results: List[ImportResult] = []

    def import_clientes(self, csv_path: str, skip_existing: bool = True) -> ImportResult:
        """Importar clientes desde CSV."""
        result = ImportResult('clientes')
        result.start_time = datetime.utcnow()

        # IDs válidos de organismos
        valid_organismos = {o.id for o in Organismo.query.all()}

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # Header es 1
                    try:
                        # Verificar si existe
                        existing = Cliente.query.get(int(row['id']))
                        if existing and skip_existing:
                            result.skipped += 1
                            continue

                        # Validar organismo_id
                        organismo_id = int(row['organismo_id']) if row['organismo_id'] else None
                        if organismo_id and organismo_id not in valid_organismos:
                            result.errors.append(ImportError(
                                row_num, 'organismo_id',
                                f'Organismo inválido: {organismo_id}',
                                row['organismo_id']
                            ))
                            continue

                        # Crear cliente
                        cliente = Cliente(
                            id=int(row['id']),
                            nombre=row['nombre'].strip(),
                            codigo=row.get('codigo', f'CLI{row["id"]}'),
                            organismo_id=organismo_id,
                            tipo_cliente=int(row['tipo_cliente']) if row['tipo_cliente'] else 1,
                            activo=bool(int(row['activo'])) if row['activo'] else True
                        )

                        if not self.dry_run:
                            if existing:
                                db.session.merge(cliente)
                            else:
                                db.session.add(cliente)

                            # Commit cada BATCH_SIZE
                            if result.imported % self.BATCH_SIZE == 0:
                                db.session.commit()

                        result.imported += 1

                    except Exception as e:
                        result.errors.append(ImportError(
                            row_num, 'general', str(e), row
                        ))

            if not self.dry_run:
                db.session.commit()

        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {csv_path}")
            raise

        result.end_time = datetime.utcnow()
        self.results.append(result)
        return result

    def import_fabricas(self, csv_path: str, skip_existing: bool = True) -> ImportResult:
        """Importar fábricas desde CSV."""
        result = ImportResult('fabricas')
        result.start_time = datetime.utcnow()

        # IDs válidos
        valid_clientes = {c.id for c in Cliente.query.all()}
        valid_provincias = {p.id for p in Provincia.query.all()}

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Verificar si existe
                        existing = Fabrica.query.get(int(row['id']))
                        if existing and skip_existing:
                            result.skipped += 1
                            continue

                        # Validar FKs
                        cliente_id = int(row['cliente_id'])
                        if cliente_id not in valid_clientes:
                            result.errors.append(ImportError(
                                row_num, 'cliente_id',
                                f'Cliente inválido: {cliente_id}',
                                row['cliente_id']
                            ))
                            continue

                        provincia_id = int(row['provincia_id']) if row['provincia_id'] else None
                        if provincia_id and provincia_id not in valid_provincias:
                            result.errors.append(ImportError(
                                row_num, 'provincia_id',
                                f'Provincia inválida: {provincia_id}',
                                row['provincia_id']
                            ))
                            continue

                        # Crear fábrica
                        fabrica = Fabrica(
                            id=int(row['id']),
                            cliente_id=cliente_id,
                            nombre=row['nombre'].strip() or f'Fábrica {row["id"]}',
                            provincia_id=provincia_id,
                            activo=True
                        )

                        if not self.dry_run:
                            if existing:
                                db.session.merge(fabrica)
                            else:
                                db.session.add(fabrica)

                            if result.imported % self.BATCH_SIZE == 0:
                                db.session.commit()

                        result.imported += 1

                    except Exception as e:
                        result.errors.append(ImportError(
                            row_num, 'general', str(e), row
                        ))

            if not self.dry_run:
                db.session.commit()

        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {csv_path}")
            raise

        result.end_time = datetime.utcnow()
        self.results.append(result)
        return result

    def import_productos(self, csv_path: str, skip_existing: bool = True) -> ImportResult:
        """Importar productos desde CSV."""
        result = ImportResult('productos')
        result.start_time = datetime.utcnow()

        # IDs válidos
        valid_destinos = {d.id for d in Destino.query.all()}

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Verificar si existe
                        existing = Producto.query.get(int(row['id']))
                        if existing and skip_existing:
                            result.skipped += 1
                            continue

                        # Validar FK
                        destino_id = int(row['destino_id']) if row['destino_id'] else None
                        if destino_id and destino_id not in valid_destinos:
                            result.errors.append(ImportError(
                                row_num, 'destino_id',
                                f'Destino inválido: {destino_id}',
                                row['destino_id']
                            ))
                            continue

                        # Crear producto
                        producto = Producto(
                            id=int(row['id']),
                            nombre=row['nombre'].strip(),
                            destino_id=destino_id,
                            activo=True
                        )

                        if not self.dry_run:
                            if existing:
                                db.session.merge(producto)
                            else:
                                db.session.add(producto)

                            if result.imported % self.BATCH_SIZE == 0:
                                db.session.commit()

                        result.imported += 1

                    except Exception as e:
                        result.errors.append(ImportError(
                            row_num, 'general', str(e), row
                        ))

            if not self.dry_run:
                db.session.commit()

        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {csv_path}")
            raise

        result.end_time = datetime.utcnow()
        self.results.append(result)
        return result

    def validate_all(self) -> Dict:
        """Validar importación completa."""
        validations = {
            'clientes': {
                'expected': 166,
                'actual': Cliente.query.count(),
                'passed': Cliente.query.count() == 166
            },
            'fabricas': {
                'expected': 403,
                'actual': Fabrica.query.count(),
                'passed': Fabrica.query.count() == 403
            },
            'productos': {
                'expected': 160,
                'actual': Producto.query.count(),
                'passed': Producto.query.count() == 160
            }
        }

        # Verificar integridad FK
        orphan_fabricas = Fabrica.query.filter(
            ~Fabrica.cliente_id.in_(db.session.query(Cliente.id))
        ).count()

        validations['fk_integrity'] = {
            'orphan_fabricas': orphan_fabricas,
            'passed': orphan_fabricas == 0
        }

        return validations

    def generate_report(self) -> str:
        """Generar reporte JSON."""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'dry_run': self.dry_run,
            'tables': [r.to_dict() for r in self.results],
            'validations': self.validate_all()
        }
        return json.dumps(report, indent=2)
