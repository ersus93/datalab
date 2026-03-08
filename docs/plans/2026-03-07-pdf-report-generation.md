# PDF Report Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Implementar sistema completo de generación de PDFs para informes oficiales de laboratorio usando WeasyPrint con templates HTML/Jinja2.

**Architecture:** WeasyPrint como motor PDF + Jinja2 templates con headers/footers fijos via CSS @page. Arquitectura hexagonal: Service → Templates → PDF bytes.

**Tech Stack:** WeasyPrint, Jinja2, Flask, SQLAlchemy

---

## Task 1: Instalar dependencias y configurar PDFService

**Files:**
- Modify: `requirements.txt` - Añadir weasyprint
- Create: `app/services/pdf_service.py` - Motor de generación PDF
- Test: `tests/unit/test_pdf_service.py`

### Step 1.1: Añadir weasyprint a requirements.txt

Run: `grep -n "weasyprint" requirements.txt`
Expected: No output (no existe)

Edit `requirements.txt` - Añadir:
```
weasyprint>=60.0
```

### Step 1.2: Crear PDFService básico

Create `app/services/pdf_service.py`:

```python
"""Servicio de generación de PDFs usando WeasyPrint."""
import logging
from typing import Optional

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app import db
from app.database.models import Informe, TipoInforme

logger = logging.getLogger(__name__)


class PDFService:
    """Servicio para generación de PDFs de informes."""

    def __init__(self, template_dir: str = "app/templates/informes"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generar_informe(self, informe_id: int) -> bytes:
        """Genera PDF de un informe.
        
        Args:
            informe_id: ID del informe a generar.
            
        Returns:
            bytes: Contenido del PDF.
        """
        from app.database.models import Informe
        informe = db.session.get(Informe, informe_id)
        if not informe:
            raise ValueError(f"Informe {informe_id} no encontrado")
        
        template_name = self._get_template_name(informe.tipo_informe)
        return self._render_pdf(informe, template_name)

    def _get_template_name(self, tipo_informe) -> str:
        """Obtiene el nombre del template según el tipo de informe."""
        tipo = tipo_informe.value if hasattr(tipo_informe, 'value') else tipo_informe
        mapping = {
            "ANALISIS": "analisis.html",
            "CERTIFICADO": "certificado.html",
            "CONSULTA": "consulta.html",
            "ESPECIAL": "especial.html",
        }
        return mapping.get(tipo, "analisis.html")

    def _render_pdf(self, informe: Informe, template_name: str) -> bytes:
        """Renderiza el template a PDF.
        
        Args:
            informe: Instancia del modelo Informe.
            template_name: Nombre del template Jinja2.
            
        Returns:
            bytes: Contenido PDF.
        """
        template = self.env.get_template(template_name)
        
        html_string = template.render(
            informe=informe,
            cliente=informe.cliente,
            entrada=informe.entrada,
            ensayos=list(informe.ensayos),
        )
        
        html = HTML(string=html_string)
        return html.write_pdf()
```

### Step 1.3: Crear test unitario básico

Create `tests/unit/test_pdf_service.py`:

```python
"""Tests unitarios para PDFService."""
import pytest
from unittest.mock import Mock, patch, MagicMock

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
```

### Step 1.4: Ejecutar tests

Run: `pytest tests/unit/test_pdf_service.py -v`
Expected: 3 tests PASS

---

## Task 2: Crear templates HTML para informes

**Files:**
- Create: `app/templates/informes/base.html` - Layout base
- Create: `app/templates/informes/analisis.html` - Template análisis
- Create: `app/templates/informes/styles.css` - Estilos
- Test: Verificar renderizado con pytest

### Step 2.1: Crear styles.css

Create `app/templates/informes/styles.css`:

```css
/* Estilos para informes PDF - DataLab */

:root {
    --primary: #003366;
    --secondary: #F5F5F5;
    --text: #000000;
    --border: #CCCCCC;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
}

@page {
    size: A4;
    margin: 3cm 2cm 2.5cm 2cm;
    @top {
        content: element(header);
    }
    @bottom {
        content: element(footer);
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.5;
    color: var(--text);
    margin: 0;
    padding: 0;
}

.header {
    position: running(header);
    border-bottom: 2px solid var(--primary);
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    width: 150px;
}

.certifications {
    width: 80px;
}

h1 {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 14pt;
    font-weight: bold;
    color: var(--primary);
    margin: 0 0 10px 0;
}

h2 {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 12pt;
    font-weight: bold;
    color: var(--primary);
    margin: 15px 0 10px 0;
}

h3 {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    font-weight: bold;
    margin: 10px 0 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
}

th, td {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9pt;
    border: 1px solid var(--border);
    padding: 6px;
    text-align: left;
}

th {
    background-color: var(--primary);
    color: white;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: var(--secondary);
}

.footer {
    position: running(footer);
    border-top: 1px solid var(--border);
    padding-top: 10px;
    margin-top: 20px;
    font-size: 8pt;
    font-style: italic;
}

.disclaimer {
    font-size: 8pt;
    color: #666;
    text-align: center;
    margin-bottom: 10px;
}

.firmas {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
}

.firma-box {
    width: 45%;
    text-align: center;
}

.firma-line {
    border-top: 1px solid var(--text);
    margin-top: 40px;
    padding-top: 5px;
}

.page-number::after {
    content: "Página " counter(page) " de " counter(pages);
}

.info-grid {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 5px;
    margin: 10px 0;
}

.info-label {
    font-weight: bold;
}

.resultado-cumple {
    color: var(--success);
    font-weight: bold;
}

.resultado-no-cumple {
    color: var(--danger);
    font-weight: bold;
}

.status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 8pt;
    font-weight: bold;
}

.status-borrador { background: #ffc107; color: #000; }
.status-pendiente { background: #17a2b8; color: #fff; }
.status-emitido { background: #28a745; color: #fff; }
.status-entregado { background: #6c757d; color: #fff; }
.status-anulado { background: #dc3545; color: #fff; }
```

### Step 2.2: Crear base.html

Create `app/templates/informes/base.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Informe DataLab{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='informes/styles.css') }}">
    {% if false %}<style>{% include "styles.css" %}</style>{% endif %}
    <style>
        {% include "styles.css" %}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo-section">
                {% if informe %}
                <strong>LABORATORIO DATALAB</strong>
                {% else %}
                <strong>LABORATORIO DATALAB</strong>
                {% endif %}
                <br>
                <small>Tucumán, Argentina</small>
            </div>
            <div class="certifications">
                <!-- Placeholder para certificación ISO -->
                <small>CERT. ISO 9001</small>
            </div>
        </div>
    </div>

    <div class="content">
        {% block content %}{% endblock %}
    </div>

    <div class="footer">
        <div class="disclaimer">
            Este informe no debe ser reproducido parcialmente sin autorización escrita del laboratorio.
            Los resultados se refieren exclusivamente a la muestra analizada.
        </div>
        <div class="page-number"></div>
    </div>
</body>
</html>
```

### Step 2.3: Crear template analisis.html

Create `app/templates/informes/analisis.html`:

```html
{% extends "base.html" %}

{% block title %}Informe de Análisis - {{ informe.nro_oficial }}{% endblock %}

{% block content %}
<div class="report-header">
    <h1>Informe de Análisis</h1>
    <p><strong>Nro:</strong> {{ informe.nro_oficial }}</p>
    <p><strong>Fecha:</strong> {{ informe.fecha_generacion.strftime('%d/%m/%Y') if informe.fecha_generacion else 'N/A' }}</p>
    <p><strong>Página:</strong> <span class="page-number"></span></p>
</div>

<section class="cliente-info">
    <h2>Datos del Cliente</h2>
    <div class="info-grid">
        <span class="info-label">Cliente:</span>
        <span>{{ cliente.nombre if cliente else 'N/A' }}</span>
        
        <span class="info-label">Dirección:</span>
        <span>{{ cliente.direccion if cliente else 'N/A' }}</span>
        
        <span class="info-label">Teléfono:</span>
        <span>{{ cliente.telefono if cliente else 'N/A' }}</span>
        
        <span class="info-label">Email:</span>
        <span>{{ cliente.email if cliente else 'N/A' }}</span>
    </div>
</section>

<section class="muestra-info">
    <h2>Datos de la Muestra</h2>
    <div class="info-grid">
        <span class="info-label">Código:</span>
        <span>{{ entrada.codigo if entrada else 'N/A' }}</span>
        
        <span class="info-label">Producto:</span>
        <span>{{ entrada.producto.nombre if entrada and entrada.producto else 'N/A' }}</span>
        
        <span class="info-label">Lote:</span>
        <span>{{ entrada.lote if entrada else 'N/A' }}</span>
        
        <span class="info-label">Fecha Recepción:</span>
        <span>{{ entrada.fech_entrada.strftime('%d/%m/%Y') if entrada and entrada.fech_entrada else 'N/A' }}</span>
    </div>
</section>

<section class="resultados">
    <h2>Resultados de Ensayos</h2>
    <table>
        <thead>
            <tr>
                <th>Ensayo</th>
                <th>Método</th>
                <th>Resultado</th>
                <th>Unidad</th>
                <th>Límites</th>
                <th>Cumple</th>
            </tr>
        </thead>
        <tbody>
            {% for detalle in ensayos %}
            <tr>
                <td>{{ detalle.ensayo.nombre_corto if detalle.ensayo else 'N/A' }}</td>
                <td>{{ detalle.ensayo.nombre_oficial[:50] if detalle.ensayo else 'N/A' }}</td>
                <td>{{ detalle.valor_numerico if detalle.valor_numerico is not none else (detalle.valor_texto or 'N/A') }}</td>
                <td>{{ detalle.ensayo.unidad_medida if detalle.ensayo else 'N/A' }}</td>
                <td>
                    {% if detalle.ensayo and detalle.ensayo.especificacion_min and detalle.ensayo.especificacion_max %}
                        {{ detalle.ensayo.especificacion_min }} - {{ detalle.ensayo.especificacion_max }}
                    {% elif detalle.ensayo and detalle.ensayo.especificacion_min %}
                        > {{ detalle.ensayo.especificacion_min }}
                    {% elif detalle.ensayo and detalle.ensayo.especificacion_max %}
                        < {{ detalle.ensayo.especificacion_max }}
                    {% else %}
                    N/A
                    {% endif %}
                </td>
                <td>
                    {% if detalle.resultado_cumple is not none %}
                        <span class="{% if detalle.resultado_cumple %}resultado-cumple{% else %}resultado-no-cumple{% endif %}">
                            {{ 'Sí' if detalle.resultado_cumple else 'No' }}
                        </span>
                    {% else %}
                    N/A
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="6" style="text-align: center;">No hay ensayos asociados</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</section>

{% if informe.resumen_resultados %}
<section class="resumen">
    <h2>Resumen de Resultados</h2>
    <p>{{ informe.resumen_resultados }}</p>
</section>
{% endif %}

{% if informe.conclusiones %}
<section class="conclusiones">
    <h2>Conclusiones</h2>
    <p>{{ informe.conclusiones }}</p>
</section>
{% endif %}

{% if informe.observaciones %}
<section class="observaciones">
    <h2>Observaciones</h2>
    <p>{{ informe.observaciones }}</p>
</section>
{% endif %}

<div class="firmas">
    <div class="firma-box">
        <div class="firma-line">Emitido por</div>
        <p>{{ informe.emitidos_por.nombre_completo if informe.emitidos_por else '_______________' }}</p>
    </div>
    <div class="firma-box">
        <div class="firma-line">Revisado por</div>
        <p>{{ informe.revisados_por.nombre_completo if informe.revisados_por else '_______________' }}</p>
    </div>
</div>
{% endblock %}
```

---

## Task 3: Crear endpoint API para descarga de PDF

**Files:**
- Create: `app/features/reportes/infrastructure/web/routes.py` - Rutas API
- Modify: `app/features/reportes/__init__.py` - Registrar blueprint
- Test: Verificar endpoint con pytest

### Step 3.1: Crear routes.py

Create `app/features/reportes/infrastructure/web/routes.py`:

```python
"""Rutas API para generación de PDFs de informes."""
from flask import Blueprint, jsonify, send_file, current_app, abort

from app.services.pdf_service import PDFService

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
        
        from app.database.models import Informe
        from app import db
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
        
        from app.database.models import Informe
        from app import db
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
```

### Step 3.2: Registrar blueprint

Modify `app/features/reportes/__init__.py`:

```python
"""Módulo de reportes."""
from app.features.reportes.infrastructure.web.routes import reportes_bp

__all__ = ["reportes_bp"]
```

Modify `app/__init__.py` (buscar función que registra blueprints):

Add to register_routes():
```python
from app.features.reportes import reportes_bp
app.register_blueprint(reportes_bp)
```

### Step 3.3: Test endpoint

Create `tests/integration/test_reporte_routes.py`:

```python
"""Tests de integración para rutas de reportes."""
import pytest
from unittest.mock import Mock, patch

from app import create_app


@pytest.fixture
def client():
    """Fixture para cliente de test."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestReportesRoutes:
    """Tests de rutas de reportes."""

    @patch("app.features.reportes.infrastructure.web.routes.PDFService")
    @patch("app.features.reportes.infrastructure.web.routes.db.session.get")
    def test_descargar_informe_pdf_success(self, mock_get, mock_service_class, client):
        """Verifica descarga exitosa de PDF."""
        mock_informe = Mock()
        mock_informe.nro_oficial = "INF-2024-0001"
        mock_get.return_value = mock_informe
        
        mock_service = Mock()
        mock_service.generar_informe.return_value = b"%PDF-1.4 test"
        mock_service_class.return_value = mock_service
        
        response = client.get("/api/reportes/informes/1/pdf")
        
        assert response.status_code == 200
        assert response.content_type == "application/pdf"

    @patch("app.features.reportes.infrastructure.web.routes.db.session.get")
    def test_descargar_informe_pdf_not_found(self, mock_get, client):
        """Verifica 404 cuando informe no existe."""
        mock_get.return_value = None
        
        response = client.get("/api/reportes/informes/999/pdf")
        
        assert response.status_code == 404
```

---

## Task 4: Añadir soporte para preview con watermark

**Files:**
- Modify: `app/services/pdf_service.py` - Añadir parámetro preview
- Modify: `app/templates/informes/base.html` - Añadir marca de agua

### Step 4.1: Modificar PDFService para preview

Add to `app/services/pdf_service.py`:

```python
def generar_informe(self, informe_id: int, preview: bool = False) -> bytes:
    """Genera PDF de un informe.
    
    Args:
        informe_id: ID del informe a generar.
        preview: Si True, genera preview con marca de agua.
        
    Returns:
        bytes: Contenido del PDF.
    """
    # ... existing code ...
    
    if preview:
        html_string = self._add_watermark(html_string)
    
    # ... existing code ...

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
```

### Step 4.2: Test preview

Run: `pytest tests/unit/test_pdf_service.py -v -k preview`
Expected: tests PASS

---

## Task 5: Criterios de aceptación del Issue #47

**Verificar manualmente:**
- [ ] WeasyPrint instalado y funcionando
- [ ] Template de informe oficial con header/footer
- [ ] Tipografía y colores profesionales aplicados
- [ ] Generación de PDF funciona para tipo ANALISIS
- [ ] Endpoint /api/reportes/informes/<id>/pdf responde
- [ ] Preview con marca de agua funciona
- [ ] Soporte multi-página con números de página
- [ ] Firmas en pie de página

---

## Notes

- Dependencias de sistema para WeasyPrint (en producción):
  - Linux: `apt-get install libpango1.0-0 libcairo2 libpangocairo-1.0-0`
  - Windows/Mac: Incluidas en wheels de WeasyPrint
- Templates para otros tipos de informe (CERTIFICADO, CONSULTA, ESPECIAL) pueden crearse siguiendo el mismo patrón
