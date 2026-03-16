"""Servicio para importación de datos Phase 4 - Detalles de Ensayos y Utilizado.

Cubre los requisitos del Issue #6 (Phase 4): Assignment & Usage Tracking
- Import Detalles de Ensayos (563 registros) desde detalles_ensayos.csv
- Import Utilizado (632 registros) desde utilizado_r.csv
- Validación FK pre-importación con reporte de referencias faltantes
- Verificación post-importación (conteos, FK integrity)
- Reporte final en Markdown
- Soporte para dry-run standalone
"""
import csv
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Set

from app import db
from app.database.models import DetalleEnsayo, Ensayo, Entrada, Utilizado
from app.database.models.detalle_ensayo import DetalleEnsayoStatus
from app.database.models.utilizado import UtilizadoStatus

logger = logging.getLogger(__name__)

EXPECTED_COUNTS = {
    'detalles_ensayos': 563,
    'utilizados': 632,
}

AREA_MAP = {
    'CantCont': 'CONT',
    'CantFQ': 'FQ',
    'CantMB': 'MB',
    'CantES': 'ES',
}


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
    """Representa una advertencia (registro importado con datos anómalos o omitido)."""

    def __init__(self, table: str, row_id, warning_type: str, message: str, value=None):
        self.table = table
        self.row_id = row_id
        self.warning_type = warning_type
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


class Phase4ImportResult:
    """Resultado completo de importación Phase 4."""

    def __init__(self):
        self.detalles_ensayos = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.utilizados = {'total': 0, 'imported': 0, 'skipped': 0, 'errors': []}
        self.utilizado_warnings: List[ImportWarning] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def total_imported(self) -> int:
        return self.detalles_ensayos['imported'] + self.utilizados['imported']

    @property
    def total_errors(self) -> int:
        return (len(self.detalles_ensayos['errors']) +
                len(self.utilizados['errors']))

    def to_dict(self) -> dict:
        def _serialize_errors(errors):
            return [e.to_dict() if hasattr(e, 'to_dict') else str(e) for e in errors]

        return {
            'duration_seconds': self.duration_seconds,
            'total_imported': self.total_imported,
            'total_errors': self.total_errors,
            'utilizado_warnings': len(self.utilizado_warnings),
            'detalles_ensayos': {**self.detalles_ensayos,
                                 'errors': _serialize_errors(self.detalles_ensayos['errors'])},
            'utilizados': {**self.utilizados,
                           'errors': _serialize_errors(self.utilizados['errors'])},
        }


class PreImportValidationReport:
    """Resultado de validación pre-importación."""

    def __init__(self):
        self.missing_entradas: List[dict] = []
        self.missing_ensayos: List[dict] = []
        self.file_errors: List[str] = []
        self.skipped_utilizados: List[dict] = []

    @property
    def is_clean(self) -> bool:
        """True si no hay problemas bloqueantes."""
        return not any([
            self.file_errors,
        ])

    def to_markdown(self) -> str:
        lines = ['# Pre-Import Validation Report — Phase 4', '']
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

        _section('Missing Entradas (FK)', self.missing_entradas,
                 ['table', 'row_id', 'entrada_id'])
        _section('Missing Ensayos (FK)', self.missing_ensayos,
                 ['table', 'row_id', 'ensayo_id'])
        _section('Skipped Utilizados (no match)', self.skipped_utilizados,
                 ['row_id', 'id_ent'])
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
        lines = ['# Post-Import Verification Report — Phase 4', '']
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


class Phase4ImportService:
    """Servicio para importar datos Phase 4 - Detalles de Ensayos y Utilizado."""

    BATCH_SIZE = 50

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.result = Phase4ImportResult()
        self._valid_entradas: Optional[Set[int]] = None
        self._valid_ensayos: Optional[Set[int]] = None

    def import_all(self, data_dir: str) -> Phase4ImportResult:
        """Importar todos los datos Phase 4 en orden correcto."""
        self.result.start_time = datetime.utcnow()
        data_path = Path(data_dir)

        logger.info("Cargando caché de FKs...")
        self._load_fk_cache()

        logger.info("=== Importando Detalles de Ensayos ===")
        self._import_detalles_ensayos(data_path / 'detalles_ensayos.csv')

        logger.info("=== Importando Utilizados ===")
        self._import_utilizados(data_path / 'utilizado_r.csv')

        self.result.end_time = datetime.utcnow()
        return self.result

    def validate_all(self, data_dir: str) -> PreImportValidationReport:
        """
        Validación pre-importación completa SIN modificar la base de datos.

        Lee todos los CSV, verifica referencias FK, y genera un reporte
        detallado de problemas encontrados.

        Args:
            data_dir: Directorio con los CSV de detalles_ensayos y utilizado_r.

        Returns:
            PreImportValidationReport con todos los problemas encontrados.
        """
        report = PreImportValidationReport()
        data_path = Path(data_dir)

        self._load_fk_cache()

        self._validate_detalles_ensayos_csv(data_path / 'detalles_ensayos.csv', report)
        self._validate_utilizados_csv(data_path / 'utilizado_r.csv', report)

        return report

    def verify_post_import(self) -> PostImportVerification:
        """
        Verificación post-importación: conteos, FK integrity y consistencia de datos.

        Returns:
            PostImportVerification con resultado de cada chequeo.
        """
        v = PostImportVerification()

        v.count_checks['Detalles de Ensayos'] = {
            'expected': EXPECTED_COUNTS['detalles_ensayos'],
            'actual': DetalleEnsayo.query.count(),
            'passed': DetalleEnsayo.query.count() == EXPECTED_COUNTS['detalles_ensayos'],
        }

        v.count_checks['Utilizados'] = {
            'expected': EXPECTED_COUNTS['utilizados'],
            'actual': Utilizado.query.count(),
            'passed': Utilizado.query.count() == EXPECTED_COUNTS['utilizados'],
        }

        detalles_sin_entrada = DetalleEnsayo.query.filter(
            ~DetalleEnsayo.entrada_id.in_(db.session.query(Entrada.id))
        ).count()
        v.fk_checks['Detalles → Entradas'] = {
            'expected': 0, 'actual': detalles_sin_entrada,
            'passed': detalles_sin_entrada == 0,
        }

        detalles_sin_ensayo = DetalleEnsayo.query.filter(
            ~DetalleEnsayo.ensayo_id.in_(db.session.query(Ensayo.id))
        ).count()
        v.fk_checks['Detalles → Ensayos'] = {
            'expected': 0, 'actual': detalles_sin_ensayo,
            'passed': detalles_sin_ensayo == 0,
        }

        utilizados_sin_entrada = Utilizado.query.filter(
            ~Utilizado.entrada_id.in_(db.session.query(Entrada.id))
        ).count()
        v.fk_checks['Utilizados → Entradas'] = {
            'expected': 0, 'actual': utilizados_sin_entrada,
            'passed': utilizados_sin_entrada == 0,
        }

        utilizados_sin_ensayo = Utilizado.query.filter(
            ~Utilizado.ensayo_id.in_(db.session.query(Ensayo.id))
        ).count()
        v.fk_checks['Utilizados → Ensayos'] = {
            'expected': 0, 'actual': utilizados_sin_ensayo,
            'passed': utilizados_sin_ensayo == 0,
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
            '# Reporte de Importación Phase 4 — DataLab',
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
            f'**Advertencias de utilizados:** {len(r.utilizado_warnings)}',
            '',
            '---',
            '',
        ]

        all_errors = r.detalles_ensayos['errors'] + r.utilizados['errors']
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

        lines.append(f'## Advertencias de Utilizados ({len(r.utilizado_warnings)})')
        if not r.utilizado_warnings:
            lines.append('_Sin advertencias_')
        else:
            lines.append('| ID Fila | Tipo | Mensaje |')
            lines.append('| --- | --- | --- |')
            for w in r.utilizado_warnings:
                lines.append(f'| {w.row_id} | {w.warning_type} | {w.message} |')
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
        lines.append('_Generado por DataLab Phase 4 Import Service_')

        report_md = '\n'.join(lines)

        if output_path:
            Path(output_path).write_text(report_md, encoding='utf-8')
            logger.info(f"Reporte guardado en: {output_path}")

        return report_md

    def _load_fk_cache(self):
        """Cargar sets de IDs válidos para validación FK rápida."""
        self._valid_entradas = {e.id for e in Entrada.query.all()}
        self._valid_ensayos = {e.id for e in Ensayo.query.all()}

    def _import_detalles_ensayos(self, csv_path: Path):
        """Importar detalles de ensayos desde CSV."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))

        self.result.detalles_ensayos['total'] = len(rows)
        batch_count = 0

        for row_num, row in enumerate(rows, start=2):
            row_id = f"{row.get('IdEnt')}-{row.get('IdEns')}"
            try:
                entrada_id = int(row['IdEnt']) if row.get('IdEnt') else None
                ensayo_id = int(row['IdEns']) if row.get('IdEns') else None

                if not entrada_id or entrada_id not in self._valid_entradas:
                    raise ValueError(f"Entrada inválida: {entrada_id}")
                if not ensayo_id or ensayo_id not in self._valid_ensayos:
                    raise ValueError(f"Ensayo inválido: {ensayo_id}")

                existing = DetalleEnsayo.query.filter_by(
                    entrada_id=entrada_id,
                    ensayo_id=ensayo_id
                ).first()
                if existing:
                    logger.debug(f"DetalleEnsayo {entrada_id}-{ensayo_id} ya existe, saltando")
                    self.result.detalles_ensayos['skipped'] += 1
                    continue

                cantidad = int(row['Cantidad']) if row.get('Cantidad') else 1

                detalle = DetalleEnsayo(
                    entrada_id=entrada_id,
                    ensayo_id=ensayo_id,
                    cantidad=cantidad,
                    estado=DetalleEnsayoStatus.PENDIENTE.value,
                    fecha_asignacion=None,
                )

                if not self.dry_run:
                    db.session.add(detalle)
                    batch_count += 1
                    if batch_count % self.BATCH_SIZE == 0:
                        db.session.commit()
                        logger.debug(f"Commit batch DetalleEnsayo ({batch_count})")

                self.result.detalles_ensayos['imported'] += 1

            except Exception as e:
                logger.error(f"Error DetalleEnsayo fila {row_num}: {e}")
                self.result.detalles_ensayos['errors'].append(
                    ImportError('detalles_ensayos', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        logger.info(
            f"Detalles de Ensayos: {self.result.detalles_ensayos['imported']} importadas, "
            f"{self.result.detalles_ensayos['skipped']} omitidas, "
            f"{len(self.result.detalles_ensayos['errors'])} errores"
        )

    def _import_utilizados(self, csv_path: Path):
        """Importar utilizados desde CSV (solo registros con entrada válida)."""
        if not csv_path.exists():
            logger.error(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))

        self.result.utilizados['total'] = len(rows)
        batch_count = 0
        imported_count = 0

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('IdEnt', row_num)
            try:
                id_ent = int(row['IdEnt']) if row.get('IdEnt') else None

                if id_ent not in self._valid_entradas:
                    warn = ImportWarning(
                        'utilizados', row_id, 'no_entry_match',
                        f"IdEnt {id_ent} no coincide con ninguna entrada existente",
                        id_ent
                    )
                    self.result.utilizado_warnings.append(warn)
                    self.result.utilizados['skipped'] += 1
                    continue

                entrada_id = id_ent

                meses = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
                mes = int(row.get('Mes', 1)) if row.get('Mes') else 1
                year = 2024
                mes_facturacion = f"{year}-{meses[mes-1]}" if 1 <= mes <= 12 else None

                created = False
                for campo, area in AREA_MAP.items():
                    cantidad = self._parse_decimal(row.get(campo, 0))
                    if cantidad > 0:
                        ensayo_id = self._get_ensayo_id_by_area(area)
                        if ensayo_id is None:
                            warn = ImportWarning(
                                'utilizados', row_id, 'no_ensayo_area',
                                f"No existe ensayo para área {area}",
                                area
                            )
                            self.result.utilizado_warnings.append(warn)
                            continue

                        utilizado = Utilizado(
                            entrada_id=entrada_id,
                            ensayo_id=ensayo_id,
                            cantidad=cantidad,
                            precio_unitario=Decimal('0'),
                            importe=Decimal('0'),
                            mes_facturacion=mes_facturacion,
                            fecha_uso=datetime.utcnow(),
                            estado=UtilizadoStatus.PENDIENTE.value,
                        )

                        if not self.dry_run:
                            db.session.add(utilizado)
                            created = True
                            batch_count += 1
                            if batch_count % self.BATCH_SIZE == 0:
                                db.session.commit()
                                logger.debug(f"Commit batch Utilizado ({batch_count})")

                        imported_count += 1

                if not created:
                    self.result.utilizados['skipped'] += 1

            except Exception as e:
                logger.error(f"Error Utilizado fila {row_num}: {e}")
                self.result.utilizados['errors'].append(
                    ImportError('utilizados', row_id, 'general', str(e), row)
                )

        if not self.dry_run:
            db.session.commit()

        self.result.utilizados['imported'] = imported_count

        logger.info(
            f"Utilizados: {self.result.utilizados['imported']} importados, "
            f"{self.result.utilizados['skipped']} omitidos, "
            f"{len(self.result.utilizados['errors'])} errores, "
            f"{len(self.result.utilizado_warnings)} advertencias"
        )

    def _validate_detalles_ensayos_csv(self, csv_path: Path, report: PreImportValidationReport):
        """Validar CSV de detalles de ensayos."""
        if not csv_path.exists():
            report.file_errors.append(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))

        for row_num, row in enumerate(rows, start=2):
            row_id = f"{row.get('IdEnt')}-{row.get('IdEns')}"

            entrada_id = int(row['IdEnt']) if row.get('IdEnt') else None
            ensayo_id = int(row['IdEns']) if row.get('IdEns') else None

            if not entrada_id or entrada_id not in self._valid_entradas:
                report.missing_entradas.append({
                    'table': 'detalles_ensayos', 'row_id': row_id, 'entrada_id': entrada_id
                })
            if not ensayo_id or ensayo_id not in self._valid_ensayos:
                report.missing_ensayos.append({
                    'table': 'detalles_ensayos', 'row_id': row_id, 'ensayo_id': ensayo_id
                })

    def _validate_utilizados_csv(self, csv_path: Path, report: PreImportValidationReport):
        """Validar CSV de utilizados."""
        if not csv_path.exists():
            report.file_errors.append(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))

        for row_num, row in enumerate(rows, start=2):
            row_id = row.get('IdEnt', row_num)

            id_ent = int(row['IdEnt']) if row.get('IdEnt') else None

            if id_ent not in self._valid_entradas:
                report.skipped_utilizados.append({
                    'row_id': row_id, 'id_ent': id_ent
                })

    def _parse_decimal(self, value) -> Decimal:
        if not value and value != 0:
            return Decimal('0')
        try:
            return Decimal(str(value).replace(',', '.'))
        except (InvalidOperation, ValueError):
            return Decimal('0')

    def _get_ensayo_id_by_area(self, area: str) -> Optional[int]:
        """Obtener ID de ensayo por área (sigla del área)."""
        from app.database.models import Ensayo, Area
        area_obj = Area.query.filter_by(sigla=area).first()
        if not area_obj:
            return None
        ensayo = Ensayo.query.filter_by(area_id=area_obj.id, activo=True).first()
        return ensayo.id if ensayo else None
