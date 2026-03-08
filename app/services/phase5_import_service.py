"""Servicio para importación de datos Phase 5 - Plantillas de Informes e Informes de Prueba.

Cubre los requisitos del Issue #50 (Phase 5): Plantillas de Informes
- Import 20 plantillas de informes desde Access (RM2026.accdb)
- Mapear datos al modelo PlantillaInforme
- Generar 20 informes de prueba vinculados a entradas existentes
- Validación FK pre-importación con validate_all()
- Verificación post-importación con verify_post_import()
- Reporte de validación en Markdown
- Soporte dry-run
"""
import logging
import os
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

from app import db
from app.database.models.plantilla_informe import PlantillaInforme
from app.database.models.informe import Informe, InformeStatus, TipoInforme, MedioEntrega
from app.database.models.entrada import Entrada
from app.database.models.cliente import Cliente

logger = logging.getLogger(__name__)

ACCESS_DB_PATH = os.environ.get('ACCESS_DB_PATH', r"C:\Users\ernes\datalab\utiles\RM2026.accdb")

EXPECTED_COUNTS = {
    'plantillas': 20,
    'informes': 20,
}

TIPO_INFORME_MAP = {
    "ANALISIS": TipoInforme.ANALISIS,
    "CERTIFICADO": TipoInforme.CERTIFICADO,
    "CONSULTA": TipoInforme.CONSULTA,
    "ESPECIAL": TipoInforme.ESPECIAL,
}


class ImportWarning:
    """Representa una advertencia durante la importación."""

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


class PreImportValidationReport:
    """Resultado de validación pre-importación."""

    def __init__(self):
        self.missing_entradas: List[dict] = []
        self.missing_clientes: List[dict] = []
        self.file_errors: List[str] = []

    @property
    def is_clean(self) -> bool:
        """True si no hay problemas bloqueantes."""
        return not any([
            self.file_errors,
        ])

    def to_markdown(self) -> str:
        lines = ['# Pre-Import Validation Report — Phase 5', '']
        lines.append(f'**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}')
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

        _section('Missing Entradas (bloqueante)', self.missing_entradas,
                 ['table', 'row_id', 'entrada_id'])
        _section('Missing Clientes (bloqueante)', self.missing_clientes,
                 ['table', 'row_id', 'cliente_id'])
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
        lines = ['# Post-Import Verification Report — Phase 5', '']
        lines.append(f'**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}')
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


class ImportError:
    """Representa un error de importación."""

    def __init__(self, table: str, row_id, field: str, message: str, original_value=None):
        self.table = table
        self.row_id = row_id
        self.field = field
        self.message = message
        self.original_value = original_value
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "table": self.table,
            "row_id": self.row_id,
            "field": self.field,
            "message": self.message,
            "original_value": str(self.original_value) if self.original_value is not None else None,
        }


class Phase5ImportResult:
    """Resultado completo de importación Phase 5."""

    def __init__(self):
        self.plantillas = {"total": 0, "imported": 0, "skipped": 0, "errors": []}
        self.informes = {"total": 0, "created": 0, "skipped": 0, "errors": []}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def total_created(self) -> int:
        return self.plantillas["imported"] + self.informes["created"]

    @property
    def total_errors(self) -> int:
        return len(self.plantillas["errors"]) + len(self.informes["errors"])

    def to_dict(self) -> dict:
        def _serialize_errors(errors):
            return [e.to_dict() if hasattr(e, "to_dict") else str(e) for e in errors]

        return {
            "duration_seconds": self.duration_seconds,
            "total_created": self.total_created,
            "total_errors": self.total_errors,
            "plantillas": {
                **self.plantillas,
                "errors": _serialize_errors(self.plantillas["errors"]),
            },
            "informes": {**self.informes, "errors": _serialize_errors(self.informes["errors"])},
        }


class Phase5ImportService:
    """Servicio para importar datos Phase 5 - Plantillas de Informes e Informes de Prueba."""

    BATCH_SIZE = 50

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.result = Phase5ImportResult()
        self._valid_entradas: Optional[Set[int]] = None
        self._valid_clientes: Optional[Set[int]] = None

    def import_all(self) -> Phase5ImportResult:
        """Importar todos los datos Phase 5."""
        self.result.start_time = datetime.now(timezone.utc)

        logger.info("Cargando cachés de FKs...")
        self._load_fk_cache()

        logger.info("=== Importando Plantillas de Informes desde Access ===")
        self._import_plantillas_from_access()

        logger.info("=== Generando Informes de Prueba ===")
        self._generate_informes_prueba()

        self.result.end_time = datetime.now(timezone.utc)
        return self.result

    def _load_fk_cache(self):
        """Cargar sets de IDs válidos para validación FK rápida."""
        self._valid_entradas = {e.id for e in Entrada.query.all()}
        self._valid_clientes = {c.id for c in Cliente.query.all()}

    def _connect_to_access(self):
        """Establecer conexión a la base de datos Access."""
        try:
            import pyodbc

            conn_str = (
                f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
                f"DBQ={ACCESS_DB_PATH};"
            )
            conn = pyodbc.connect(conn_str)
            logger.info(f"Conexión a Access establecida: {ACCESS_DB_PATH}")
            return conn
        except ImportError:
            logger.error("pyodbc no está instalado. Instalar con: pip install pyodbc")
            raise
        except Exception as e:
            logger.error(f"Error conectando a Access: {e}")
            raise

    def _import_plantillas_from_access(self):
        """Importar plantillas de informes desde la tabla Informes de Access."""
        try:
            conn = self._connect_to_access()
            cursor = conn.cursor()

            cursor.execute("SELECT IdInf, NomInf, Parametro, Activo FROM Informes")
            rows = cursor.fetchall()

            self.result.plantillas["total"] = len(rows)

            tipos_disponibles = list(TipoInforme)
            tipo_index = 0
            batch_count = 0

            for row in rows:
                try:
                    id_inf = row.IdInf
                    nom_inf = row.NomInf
                    activo = bool(row.Activo) if row.Activo is not None else True

                    tipo_informe = tipos_disponibles[tipo_index % len(tipos_disponibles)]
                    tipo_index += 1

                    nombre_plantilla = nom_inf if nom_inf else f"Plantilla_{id_inf}"

                    existing = PlantillaInforme.query.filter_by(nombre=nombre_plantilla).first()
                    if existing:
                        logger.debug(f"Plantilla {nombre_plantilla} ya existe, saltando")
                        self.result.plantillas["skipped"] += 1
                        continue

                    plantilla = PlantillaInforme(
                        nombre=nombre_plantilla,
                        tipo=tipo_informe,
                        header_html="",
                        footer_html="",
                        body_template="",
                        css_styles="",
                        logo_encabezado=None,
                        logo_pie=None,
                        activa=activo,
                    )

                    if not self.dry_run:
                        db.session.add(plantilla)
                        batch_count += 1
                        if batch_count % self.BATCH_SIZE == 0:
                            db.session.commit()
                            logger.debug(f"Commit batch Plantilla ({batch_count})")

                    self.result.plantillas["imported"] += 1

                except Exception as e:
                    logger.error(f"Error importando plantilla {id_inf}: {e}")
                    self.result.plantillas["errors"].append(
                        ImportError("plantillas", id_inf, "general", str(e), {"IdInf": id_inf})
                    )

            cursor.close()
            conn.close()

            if not self.dry_run:
                db.session.commit()

            logger.info(
                f"Plantillas: {self.result.plantillas['imported']} importadas, "
                f"{self.result.plantillas['skipped']} omitidas, "
                f"{len(self.result.plantillas['errors'])} errores"
            )

        except Exception as e:
            logger.error(f"Error crítico en importación de plantillas: {e}")
            self.result.plantillas["errors"].append(
                ImportError("plantillas", "CONNECTION", "access", str(e))
            )

    def _generate_informes_prueba(self):
        """Generar 20 informes de prueba vinculados a entradas existentes."""
        try:
            entradas = Entrada.query.order_by(Entrada.id).limit(20).all()

            if not entradas:
                logger.warning("No hay entradas disponibles para generar informes de prueba")
                self.result.informes["errors"].append(
                    ImportError("informes", "NO_DATA", "entradas", "No hay entradas disponibles")
                )
                return

            clientes = Cliente.query.limit(10).all()
            if not clientes:
                logger.warning("No hay clientes disponibles")
                self.result.informes["errors"].append(
                    ImportError("informes", "NO_DATA", "clientes", "No hay clientes disponibles")
                )
                return

            self.result.informes["total"] = 20

            estados = [
                InformeStatus.BORRADOR,
                InformeStatus.PENDIENTE_FIRMA,
                InformeStatus.EMITIDO,
            ]

            tipos = list(TipoInforme)
            year = 2026
            batch_count = 0

            for i in range(20):
                try:
                    entrada = entradas[i % len(entradas)]
                    cliente_id = entrada.cliente_id if entrada.cliente_id else clientes[i % len(clientes)].id

                    if entrada.cliente_id is None:
                        entrada.cliente_id = clientes[0].id
                        if not self.dry_run:
                            db.session.add(entrada)

                    nro_oficial = f"INF-{year:04d}-{i+1:03d}"

                    existing = Informe.query.filter_by(nro_oficial=nro_oficial).first()
                    if existing:
                        logger.debug(f"Informe {nro_oficial} ya existe, saltando")
                        self.result.informes["skipped"] += 1
                        continue

                    tipo = tipos[i % len(tipos)]
                    estado = estados[i % len(estados)]

                    informe = Informe(
                        nro_oficial=nro_oficial,
                        tipo_informe=tipo,
                        entrada_id=entrada.id,
                        cliente_id=cliente_id,
                        estado=estado,
                        resumen_resultados=f"Resultados del análisis de prueba #{i+1}",
                        conclusiones="",
                        observaciones="",
                        recomendaciones="",
                        numero_paginas=1,
                        copias_entregadas=1,
                        medio_entrega=MedioEntrega.FISICO,
                        anulado=False,
                        motivo_anulacion="",
                    )

                    if estado == InformeStatus.EMITIDO:
                        informe.fecha_emision = datetime.now(timezone.utc)

                    if not self.dry_run:
                        db.session.add(informe)
                        batch_count += 1
                        if batch_count % self.BATCH_SIZE == 0:
                            db.session.commit()

                    self.result.informes["created"] += 1

                except Exception as e:
                    logger.error(f"Error generando informe {i+1}: {e}")
                    self.result.informes["errors"].append(
                        ImportError("informes", i + 1, "general", str(e))
                    )

            if not self.dry_run:
                db.session.commit()

            logger.info(
                f"Informes: {self.result.informes['created']} creados, "
                f"{self.result.informes['skipped']} omitidos, "
                f"{len(self.result.informes['errors'])} errores"
            )

        except Exception as e:
            logger.error(f"Error crítico en generación de informes: {e}")
            self.result.informes["errors"].append(
                ImportError("informes", "GENERATION", "general", str(e))
            )

    def validate_all(self) -> PreImportValidationReport:
        """
        Validación pre-importación completa SIN modificar la base de datos.

        Verifica que existan entradas y clientes válidos para la importación.

        Returns:
            PreImportValidationReport con todos los problemas encontrados.
        """
        report = PreImportValidationReport()

        self._load_fk_cache()

        if not self._valid_entradas:
            report.file_errors.append("No hay entradas disponibles en la base de datos")

        if not self._valid_clientes:
            report.file_errors.append("No hay clientes disponibles en la base de datos")

        return report

    def verify_post_import(self) -> PostImportVerification:
        """
        Verificación post-importación: conteos, FK integrity y consistencia de datos.

        Returns:
            PostImportVerification con resultado de cada chequeo.
        """
        v = PostImportVerification()

        v.count_checks['Plantillas de Informes'] = {
            'expected': EXPECTED_COUNTS['plantillas'],
            'actual': PlantillaInforme.query.count(),
            'passed': PlantillaInforme.query.count() >= EXPECTED_COUNTS['plantillas'],
        }

        v.count_checks['Informes'] = {
            'expected': EXPECTED_COUNTS['informes'],
            'actual': Informe.query.count(),
            'passed': Informe.query.count() >= EXPECTED_COUNTS['informes'],
        }

        informes_sin_entrada = Informe.query.filter(
            ~Informe.entrada_id.in_(db.session.query(Entrada.id))
        ).count()
        v.fk_checks['Informes → Entradas'] = {
            'expected': 0, 'actual': informes_sin_entrada,
            'passed': informes_sin_entrada == 0,
        }

        informes_sin_cliente = Informe.query.filter(
            ~Informe.cliente_id.in_(db.session.query(Cliente.id))
        ).count()
        v.fk_checks['Informes → Clientes'] = {
            'expected': 0, 'actual': informes_sin_cliente,
            'passed': informes_sin_cliente == 0,
        }

        informes_anulados = Informe.query.filter(Informe.anulado == True).count()
        v.consistency_checks['Informes anulados'] = {
            'expected': 'N/A', 'actual': informes_anulados,
            'passed': True,
        }

        return v

    def validate_fk(self) -> Dict[str, dict]:
        """Validar integridad de FKs post-importación."""
        results = {}

        try:
            plantillas_count = PlantillaInforme.query.count()
            results["plantillas"] = {
                "total": plantillas_count,
                "valid": plantillas_count > 0,
            }
        except Exception as e:
            results["plantillas"] = {"error": str(e), "valid": False}

        try:
            informes_count = Informe.query.count()
            informes_con_entrada = (
                Informe.query.filter(Informe.entrada_id.in_(self._valid_entradas)).count()
                if self._valid_entradas
                else 0
            )
            informes_con_cliente = (
                Informe.query.filter(Informe.cliente_id.in_(self._valid_clientes)).count()
                if self._valid_clientes
                else 0
            )
            results["informes"] = {
                "total": informes_count,
                "con_entrada": informes_con_entrada,
                "con_cliente": informes_con_cliente,
                "valid": informes_con_entrada > 0 and informes_con_cliente > 0,
            }
        except Exception as e:
            results["informes"] = {"error": str(e), "valid": False}

        return results

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generar reporte de importación en formato Markdown."""
        r = self.result

        fk_validation = self.validate_fk()

        lines = [
            "# Reporte de Importación Phase 5 — DataLab",
            "",
            f"**Generado:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Modo:** {'DRY-RUN (sin cambios en BD)' if self.dry_run else 'IMPORTACIÓN REAL'}",
            f"**Duración:** {r.duration_seconds:.2f} segundos",
            "",
            "---",
            "",
            "## Resumen",
            "",
            "| Entidad | Total | Creados | Omitidos | Errores |",
            "| --- | --- | --- | --- | --- |",
            f"| Plantillas de Informes | {r.plantillas['total']} | {r.plantillas['imported']} | {r.plantillas['skipped']} | {len(r.plantillas['errors'])} |",
            f"| Informes de Prueba | {r.informes['total']} | {r.informes['created']} | {r.informes['skipped']} | {len(r.informes['errors'])} |",
            "",
            f"**Total creados:** {r.total_created}",
            f"**Total errores:** {r.total_errors}",
            "",
            "---",
            "",
            "## Validación de FK",
            "",
            "| Entidad | Total Registros | Estado |",
            "| --- | --- | --- |",
        ]

        for entity, data in fk_validation.items():
            if "error" in data:
                status = "❌ Error"
            elif data.get("valid"):
                status = "✅ Válido"
            else:
                status = "⚠️ Advertencia"

            total = data.get("total", 0)
            lines.append(f"| {entity.title()} | {total} | {status} |")

        lines.extend(["", "---", ""])

        all_errors = r.plantillas["errors"] + r.informes["errors"]
        lines.append(f"## Errores ({len(all_errors)})")
        if not all_errors:
            lines.append("_Sin errores_")
        else:
            lines.append("| Tabla | ID Fila | Campo | Mensaje |")
            lines.append("| --- | --- | --- | --- |")
            for e in all_errors:
                if hasattr(e, "to_dict"):
                    d = e.to_dict()
                    lines.append(
                        f"| {d['table']} | {d['row_id']} | {d['field']} | {d['message']} |"
                    )

        lines.extend(["", "---", ""])
        lines.append("_Generado por DataLab Phase 5 Import Service_")

        report_md = "\n".join(lines)

        if output_path:
            Path(output_path).write_text(report_md, encoding="utf-8")
            logger.info(f"Reporte guardado en: {output_path}")

        return report_md


def run_import(dry_run: bool = False, output_report: Optional[str] = None) -> Phase5ImportResult:
    """Función de conveniencia para ejecutar la importación."""
    logger.info(f"Iniciando importación Phase 5 (dry_run={dry_run})")
    service = Phase5ImportService(dry_run=dry_run)
    result = service.import_all()

    if output_report:
        service.generate_report(output_report)

    return result
