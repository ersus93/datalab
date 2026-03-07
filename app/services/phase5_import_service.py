"""Servicio para importación de datos Phase 5 - Plantillas de Informes e Informes de Prueba.

Cubre los requisitos del Issue #6 (Phase 5): Plantillas de Informes
- Import 20 plantillas de informes desde Access (RM2026.accdb)
- Mapear datos al modelo PlantillaInforme
- Generar 20 informes de prueba vinculados a entradas existentes
- Reporte de validación en Markdown
"""
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Set

from app import db
from app.database.models.plantilla_informe import PlantillaInforme
from app.database.models.informe import Informe, InformeStatus, TipoInforme, MedioEntrega
from app.database.models.entrada import Entrada
from app.database.models.cliente import Cliente

logger = logging.getLogger(__name__)

ACCESS_DB_PATH = r"C:\Users\ernes\datalab\utiles\RM2026.accdb"

TIPO_INFORME_MAP = {
    "ANALISIS": TipoInforme.ANALISIS,
    "CERTIFICADO": TipoInforme.CERTIFICADO,
    "CONSULTA": TipoInforme.CONSULTA,
    "ESPECIAL": TipoInforme.ESPECIAL,
}


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

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.result = Phase5ImportResult()
        self._valid_entradas: Optional[Set[int]] = None
        self._valid_clientes: Optional[Set[int]] = None

    def import_all(self) -> Phase5ImportResult:
        """Importar todos los datos Phase 5."""
        self.result.start_time = datetime.utcnow()

        logger.info("Cargando cachés de FKs...")
        self._load_fk_cache()

        logger.info("=== Importando Plantillas de Informes desde Access ===")
        self._import_plantillas_from_access()

        logger.info("=== Generando Informes de Prueba ===")
        self._generate_informes_prueba()

        self.result.end_time = datetime.utcnow()
        return self.result

    def _load_fk_cache(self):
        """Cargar sets de IDs válidos para validación FK rápida."""
        self._valid_entradas = {e.id for e in Entrada.query.limit(100).all()}
        self._valid_clientes = {c.id for c in Cliente.query.limit(100).all()}

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

            for i in range(20):
                try:
                    entrada = entradas[i % len(entradas)]
                    cliente = entrada.cliente_id if entrada.cliente_id else clientes[i % len(clientes)]

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
                        cliente_id=cliente,
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
                        informe.fecha_emision = datetime.utcnow()

                    if not self.dry_run:
                        db.session.add(informe)

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
            f"**Generado:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
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
