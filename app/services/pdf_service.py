"""Servicio de generación de PDFs usando WeasyPrint.

Los templates PDF son standalone (no heredan de base.html) con reglas
@page CSS para headers/footers fijos y formato profesional imprimible.
"""
import logging
import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from app import db
from app.database.models import Informe

logger = logging.getLogger(__name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "informes")

# Mapeo tipo de informe → template PDF standalone
TIPO_TEMPLATE_MAP = {
    "ANALISIS": "analisis_pdf.html",
    "CERTIFICADO": "certificado_pdf.html",
    "CONSULTA": "consulta_pdf.html",
    "ESPECIAL": "especial_pdf.html",
}


class PDFService:
    """Servicio para generación de PDFs de informes usando WeasyPrint."""

    def __init__(self, template_dir: str = TEMPLATE_DIR):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generar_informe(self, informe_id: int, preview: bool = False) -> bytes:
        """Genera el PDF oficial de un informe.

        Args:
            informe_id: ID del informe a generar.
            preview: Si True, añade marca de agua BORRADOR/PREVIEW.

        Returns:
            bytes: Contenido del PDF generado.

        Raises:
            ValueError: Si el informe no existe.
        """
        informe = db.session.get(Informe, informe_id)
        if not informe:
            raise ValueError(f"Informe {informe_id} no encontrado")

        tipo = informe.tipo_informe.value if hasattr(informe.tipo_informe, "value") else informe.tipo_informe
        template_name = TIPO_TEMPLATE_MAP.get(tipo, "analisis_pdf.html")

        # Fallback si el template no existe
        try:
            self.env.get_template(template_name)
        except Exception:
            logger.warning(f"Template {template_name} no encontrado, usando analisis_pdf.html")
            template_name = "analisis_pdf.html"

        return self._render_pdf(informe, template_name, preview=preview)

    def generar_resumen_entrada(self, entrada_id: int) -> bytes:
        """Genera un PDF resumen de todos los ensayos de una entrada.

        Args:
            entrada_id: ID de la entrada a resumir.

        Returns:
            bytes: Contenido del PDF generado.
        """
        from app.database.models import Entrada, DetalleEnsayo
        entrada = db.session.get(Entrada, entrada_id)
        if not entrada:
            raise ValueError(f"Entrada {entrada_id} no encontrada")

        detalles = DetalleEnsayo.query.filter_by(entrada_id=entrada_id).all()

        try:
            template = self.env.get_template("resumen_entrada_pdf.html")
        except Exception:
            template = self.env.get_template("analisis_pdf.html")

        html_string = template.render(
            entrada=entrada,
            cliente=entrada.cliente,
            detalles=detalles,
            titulo="Resumen de Ensayos",
        )
        html = HTML(string=html_string, base_url=self.template_dir)
        return html.write_pdf()

    def _render_pdf(self, informe: Informe, template_name: str, preview: bool = False) -> bytes:
        """Renderiza el template a PDF con WeasyPrint.

        Args:
            informe: Instancia del modelo Informe.
            template_name: Nombre del template PDF standalone.
            preview: Si True, añade marca de agua.

        Returns:
            bytes: Contenido PDF.
        """
        template = self.env.get_template(template_name)

        html_string = template.render(
            informe=informe,
            cliente=informe.cliente,
            entrada=informe.entrada,
            ensayos=list(informe.ensayos) if informe.ensayos else [],
            is_preview=preview,
        )

        if preview:
            html_string = self._add_watermark(html_string)

        html = HTML(string=html_string, base_url=self.template_dir)
        return html.write_pdf()

    def _add_watermark(self, html_string: str) -> str:
        """Añade marca de agua BORRADOR al HTML antes de convertir a PDF."""
        watermark_css = """
        <style>
        .watermark-overlay {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72pt;
            font-family: Arial, sans-serif;
            font-weight: bold;
            color: rgba(200, 0, 0, 0.12);
            z-index: 9999;
            pointer-events: none;
            white-space: nowrap;
            letter-spacing: 10px;
        }
        </style>
        <div class="watermark-overlay">BORRADOR</div>
        """
        if "<body" in html_string:
            insert_pos = html_string.find(">", html_string.find("<body")) + 1
            html_string = html_string[:insert_pos] + watermark_css + html_string[insert_pos:]
        return html_string
