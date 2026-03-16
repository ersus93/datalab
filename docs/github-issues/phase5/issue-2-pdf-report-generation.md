# [Phase 5] PDF Report Generation

## Description
Implement a comprehensive PDF generation system for official laboratory reports using WeasyPrint or ReportLab. The system must produce professional, legally valid documents with proper formatting, headers, footers, and institutional branding.

## Data Context
- **Output Format**: PDF (ISO 32000 compliant)
- **Resolution**: Print-quality 300 DPI minimum
- **Language**: Spanish (with potential multi-language support)
- **Legal Requirements**: Must include signature blocks and certification text

## Requirements

### 1. PDF Generation Engine

**Option A: WeasyPrint (Recommended)**
```python
from weasyprint import HTML, CSS
from django.template.loader import render_to_string

def generar_informe_pdf(informe_id):
    informe = Informe.objects.get(id=informe_id)
    html_string = render_to_string('informes/plantilla_base.html', {
        'informe': informe,
        'resultados': informe.ensayos_incluidos.all(),
    })
    html = HTML(string=html_string)
    return html.write_pdf()
```

**Option B: ReportLab**
```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

def generar_informe_reportlab(informe):
    doc = SimpleDocTemplate("informe.pdf", pagesize=A4)
    elements = []
    # Build document elements
    doc.build(elements)
```

**Selection Criteria:**
- WeasyPrint: Better for HTML/CSS templates, easier styling
- ReportLab: More programmatic control, better for complex layouts

### 2. Official Report Template Structure

**Header (Fixed on each page):**
```
┌─────────────────────────────────────────────────────────┐
│  [LOGO]       LABORATORIO DATALAB           [CERT ISO]  │
│  [Slogan]     Tucumán, Argentina                       │
│              informe@datalab.com.ar                    │
├─────────────────────────────────────────────────────────┤
│  INFORME NRO: INF-2024-0056    Página X de Y           │
└─────────────────────────────────────────────────────────┘
```

**Body Structure:**
```html
<section class="cliente-info">
  <h2>Informe de Análisis</h2>
  <table>
    <tr><td>Cliente:</td><td>{{ informe.cliente.nombre }}</td></tr>
    <tr><td>Dirección:</td><td>{{ informe.cliente.direccion }}</td></tr>
    <tr><td>Muestra:</td><td>{{ informe.entrada.identificacion }}</td></tr>
    <tr><td>Fecha Recepción:</td><td>{{ informe.entrada.fecha_entrada }}</td></tr>
  </table>
</section>

<section class="resultados">
  <h3>Resultados de Ensayos</h3>
  <table class="tabla-resultados">
    <thead>
      <tr>
        <th>Ensayo</th>
        <th>Método</th>
        <th>Resultado</th>
        <th>Unidad</th>
        <th>Límites</th>
      </tr>
    </thead>
    <tbody>
      {% for detalle in informe.ensayos_incluidos.all %}
      <tr>
        <td>{{ detalle.ensayo.denominacion }}</td>
        <td>{{ detalle.resultado.metodo }}</td>
        <td>{{ detalle.resultado.valor }}</td>
        <td>{{ detalle.ensayo.unidad }}</td>
        <td>{{ detalle.ensayo.limites }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
```

**Footer (Fixed on each page):**
```
┌─────────────────────────────────────────────────────────┐
│  Este informe no debe ser reproducido parcialmente      │
│  sin autorización escrita del laboratorio.             │
│  Los resultados se refieren exclusivamente a la        │
│  muestra analizada.                                    │
├─────────────────────────────────────────────────────────┤
│  Emitido por: _______________  Revisado: ______________ │
│  [Firma/Timbre]                [Firma/Timbre]          │
└─────────────────────────────────────────────────────────┘
```

### 3. Test Results Summary PDF
```python
class ResumenResultadosPDF:
    """Generate summary of all tests for a sample/entry"""

    def __init__(self, entrada_id):
        self.entrada = Entrada.objects.get(id=entrada_id)

    def generar(self):
        return {
            'resumen_area': self.resumen_por_area(),
            'estadisticas': self.calcular_estadisticas(),
            'tiempos_respuesta': self.calcular_tiempos(),
        }
```

### 4. Sample Entry Detail Report
- Complete traceability chain
- Reception details
- All assigned tests
- Status history
- Technician assignments
- Timeline of activities

### 5. Usage/Consultation Report
```python
class ReporteUsoPDF:
    """Generate usage reports for billing/consultation"""

    def generar_por_cliente(self, cliente_id, fecha_desde, fecha_hasta):
        # Usage summary by client
        pass

    def generar_por_periodo(self, mes, anio):
        # Monthly usage summary
        pass

    def generar_por_tipo_ensayo(self, fecha_desde, fecha_hasta):
        # Usage by test type
        pass
```

### 6. Professional Formatting Specifications

**Typography:**
- Headers: Arial/Helvetica 14pt bold
- Body: Times New Roman 11pt
- Tables: Arial 9pt
- Footer: Arial 8pt italic

**Colors:**
- Primary: Institutional blue (#003366)
- Secondary: Light gray (#F5F5F5)
- Text: Black (#000000)
- Borders: Medium gray (#CCCCCC)

**Margins:**
- Top: 3cm (accommodates header)
- Bottom: 2.5cm (accommodates footer)
- Left/Right: 2cm

**Logo Requirements:**
- Header logo: 150px width, transparent PNG
- Footer certification marks: 80px width
- High resolution (300 DPI minimum)

## Acceptance Criteria
- [ ] PDF generation engine selected and configured (WeasyPrint/ReportLab)
- [ ] Official report template with header/footer implemented
- [ ] Professional typography and color scheme applied
- [ ] Test results summary PDF generation
- [ ] Sample entry detail report generation
- [ ] Usage/consultation reports for billing
- [ ] Logo and certification marks integration
- [ ] Multi-page support with page numbers
- [ ] Print-quality output (300 DPI)
- [ ] Digital signature placeholder support

## Technical Notes
- Install WeasyPrint: `pip install WeasyPrint`
- System dependencies: `apt-get install libpango1.0-0`
- Use `@page` CSS rules for headers/footers
- Embed fonts for cross-platform consistency
- Cache generated PDFs to avoid regeneration
- Support both preview (watermarked) and final versions
- Consider PDF/A compliance for archival

## Labels
`phase-5`, `reporting`, `pdf`, `weasyprint`, `reportlab`, `frontend`, `backend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 4-5 days
