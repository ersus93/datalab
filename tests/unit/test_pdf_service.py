"""Tests unitarios para PDFService."""
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

# Mock weasyprint before importing PDFService
mock_weasyprint = MagicMock()
mock_weasyprint.HTML = MagicMock()
sys.modules["weasyprint"] = mock_weasyprint

from app.services.pdf_service import PDFService


class TestPDFService:
    """Tests del servicio de generación PDF."""

    def test_pdf_service_init(self):
        """Verifica inicialización del servicio."""
        service = PDFService()
        assert service.env is not None

    @patch("app.services.pdf_service.db.session.get")
    def test_generar_informe_not_found(self, mock_get):
        """Verifica comportamiento cuando informe no existe."""
        mock_get.return_value = None
        service = PDFService()

        with pytest.raises(ValueError, match="no encontrado"):
            service.generar_informe(999)

    @patch("app.services.pdf_service.db.session.get")
    @patch.object(PDFService, "_render_pdf")
    def test_generar_informe_success(self, mock_render, mock_get):
        """Verifica generación exitosa de PDF."""
        mock_informe = Mock()
        mock_informe.tipo_informe.value = "ANALISIS"
        mock_informe.cliente = Mock()
        mock_informe.entrada = Mock()
        mock_informe.ensayos = []
        mock_get.return_value = mock_informe
        mock_render.return_value = b"%PDF-1.4"

        service = PDFService()
        result = service.generar_informe(1)

        assert result == b"%PDF-1.4"
        mock_render.assert_called_once()

    @patch("app.services.pdf_service.db.session.get")
    @patch.object(PDFService, "_render_pdf")
    def test_generar_informe_with_preview(self, mock_render, mock_get):
        """Verifica generación de PDF con preview."""
        mock_informe = Mock()
        mock_informe.tipo_informe.value = "ANALISIS"
        mock_informe.cliente = Mock()
        mock_informe.entrada = Mock()
        mock_informe.ensayos = []
        mock_get.return_value = mock_informe
        mock_render.return_value = b"%PDF-1.4"

        service = PDFService()
        result = service.generar_informe(1, preview=True)

        assert result == b"%PDF-1.4"
        mock_render.assert_called_once_with(
            mock_informe, "analisis.html", preview=True
        )

    def test_get_template_name_analisis(self):
        """Verifica mapeo de tipo ANALISIS."""
        service = PDFService()
        tipo = Mock()
        tipo.value = "ANALISIS"
        assert service._get_template_name(tipo) == "analisis.html"

    def test_get_template_name_certificado(self):
        """Verifica mapeo de tipo CERTIFICADO."""
        service = PDFService()
        tipo = Mock()
        tipo.value = "CERTIFICADO"
        assert service._get_template_name(tipo) == "certificado.html"

    def test_get_template_name_string(self):
        """Verifica mapeo con string directo."""
        service = PDFService()
        assert service._get_template_name("ESPECIAL") == "especial.html"

    def test_add_watermark(self):
        """Verifica adición de watermark."""
        service = PDFService()
        html = "<html><body>Content</body></html>"
        result = service._add_watermark(html)

        assert "PREVIEW" in result
        assert "watermark" in result
        assert "<body>" in result

    def test_add_watermark_no_body(self):
        """Verifica comportamiento sin body tag."""
        service = PDFService()
        html = "<html><div>Content</div></html>"
        result = service._add_watermark(html)

        assert result == html
