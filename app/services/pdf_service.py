"""Servicio de generación de PDFs usando WeasyPrint."""

import logging
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app import db
from app.database.models import Informe

logger = logging.getLogger(__name__)


class PDFService:
    """Servicio para generación de PDFs de informes."""

    def __init__(self, template_dir: str = "app/templates/informes"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generar_informe(self, informe_id: int, preview: bool = False) -> bytes:
        """Genera PDF de un informe.

        Args:
            informe_id: ID del informe a generar.
            preview: Si True, genera preview con marca de agua.

        Returns:
            bytes: Contenido del PDF.
        """
        informe = db.session.get(Informe, informe_id)
        if not informe:
            raise ValueError(f"Informe {informe_id} no encontrado")

        template_name = self._get_template_name(informe.tipo_informe)
        return self._render_pdf(informe, template_name, preview=preview)

    def _get_template_name(self, tipo_informe) -> str:
        """Obtiene el nombre del template según el tipo de informe."""
        tipo = tipo_informe.value if hasattr(tipo_informe, "value") else tipo_informe
        mapping = {
            "ANALISIS": "analisis.html",
            "CERTIFICADO": "certificado.html",
            "CONSULTA": "consulta.html",
            "ESPECIAL": "especial.html",
        }
        return mapping.get(tipo, "analisis.html")

    def _render_pdf(
        self, informe: Informe, template_name: str, preview: bool = False
    ) -> bytes:
        """Renderiza el template a PDF.

        Args:
            informe: Instancia del modelo Informe.
            template_name: Nombre del template Jinja2.
            preview: Si True, añade marca de agua.

        Returns:
            bytes: Contenido PDF.
        """
        try:
            template = self.env.get_template(template_name)
        except Exception:
            template = self.env.get_template("analisis.html")

        html_string = template.render(
            informe=informe,
            cliente=informe.cliente,
            entrada=informe.entrada,
            ensayos=list(informe.ensayos),
        )

        if preview:
            html_string = self._add_watermark(html_string)

        html = HTML(string=html_string)
        return html.write_pdf()

    def _add_watermark(self, html_string: str) -> str:
        """Añade marca de agua PREVIEW al HTML.

        Args:
            html_string: Contenido HTML original.

        Returns:
            HTML con marca de agua.
        """
        watermark_css = """
        <style>
            .watermark {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 80pt;
                color: rgba(200, 0, 0, 0.15);
                z-index: 9999;
                pointer-events: none;
                white-space: nowrap;
            }
        </style>
        <div class="watermark">PREVIEW</div>
        """

        if "<body>" in html_string:
            html_string = html_string.replace("<body>", f"<body>{watermark_css}")

        return html_string
