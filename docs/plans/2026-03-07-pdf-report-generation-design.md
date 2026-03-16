# PDF Report Generation - Design Document

> **For Claude:** Use writing-plans skill to create implementation plan.

**Goal:** Implementar sistema completo de generación de PDFs para informes oficiales de laboratorio usando WeasyPrint con templates HTML/Jinja2.

**Architecture:** 
- WeasyPrint como motor de generación PDF
- Templates Jinja2 para separación contenido/estilo
- Headers/footers fijos con CSS `@page`
- Arquitectura hexagonal: Service → Templates → PDF

**Tech Stack:** WeasyPrint, Jinja2, Flask, SQLAlchemy

---

## Design Decisions

### 1. Motor de Generación
- **WeasyPrint** seleccionado por facilidad de modificación de templates
- Templates HTML/CSS permiten cambios sin código Python
- Soporte nativo para headers/footers en todas las páginas

### 2. Estructura de Templates

```
templates/informes/
├── base.html          # Layout con header/footer fijo
├── analisis.html     # Template informe análisis
├── certificado.html  # Template certificado
├── consulta.html     # Template consulta técnica
├── especial.html     # Template informe especial
└── styles.css        # Estilos profesionales
```

### 3. Colores y Tipografía
- Primario: #003366 (Azul institucional)
- Secundario: #F5F5F5 (Gris claro)
- Texto: #000000
- Encabezados: Arial 14pt bold
- Cuerpo: Times New Roman 11pt
- Tablas: Arial 9pt

### 4. Datos del Issue #46 (dependencia)
- Modelo Informe existente con todos los campos
- Relación Informe → Entrada → Cliente
- Relación Informe → DetalleEnsayo
- Workflow de estados completo

---

## Components

### PDFService
```python
class PDFService:
    - generar_informe(informe_id, template) -> bytes
    - generar_resumen(entrada_id) -> bytes
    - generar_uso(cliente_id, desde, hasta) -> bytes
```

### Routes API
- `GET /api/informes/<id>/pdf` - Descargar PDF
- `POST /api/informes/<id>/preview` - Preview con watermark

### Templates
- Header fijo: Logo, nombre laboratorio, certificación ISO
- Footer fijo: Legal disclaimer, firmas
- Body dinámico: Datos del informe según tipo
