"""Rutas API para generación de PDFs de informes."""
from flask import Blueprint, send_file, current_app, abort

from app.services.pdf_service import PDFService
from app import db
from app.database.models import Informe

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")


@reportes_bp.route("/informes/<int:informe_id>/pdf", methods=["GET"])
def descargar_informe_pdf(informe_id: int):
    """Genera y descarga el PDF de un informe.

    Args:
        informe_id: ID del informe.

    Returns:
        Response con archivo PDF.
    """
    try:
        service = PDFService()
        pdf_bytes = service.generar_informe(informe_id)

        informe = db.session.get(Informe, informe_id)

        filename = f"{informe.nro_oficial}.pdf" if informe else f"informe_{informe_id}.pdf"

        return send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except ValueError as e:
        abort(404, description=str(e))
    except Exception as e:
        current_app.logger.error(f"Error generando PDF: {e}")
        abort(500, description="Error al generar PDF")


@reportes_bp.route("/informes/<int:informe_id>/preview", methods=["GET"])
def preview_informe_pdf(informe_id: int):
    """Genera preview de PDF con marca de agua.

    Args:
        informe_id: ID del informe.

    Returns:
        Response con archivo PDF preview.
    """
    try:
        service = PDFService()
        pdf_bytes = service.generar_informe(informe_id, preview=True)

        informe = db.session.get(Informe, informe_id)

        filename = f"preview_{informe.nro_oficial}.pdf" if informe else f"preview_{informe_id}.pdf"

        return send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=False,
            download_name=filename,
        )
    except ValueError as e:
        abort(404, description=str(e))
    except Exception as e:
        current_app.logger.error(f"Error generando preview PDF: {e}")
        abort(500, description="Error al generar preview PDF")
