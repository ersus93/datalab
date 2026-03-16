# [Phase 5] Official Reports Module (Informes)

## Description
Implement the official reports module that generates laboratory certification documents. The Informe model represents official laboratory reports issued to clients containing test results and certifications.

## Data Context
- **Source Table**: Informes
- **Record Count**: 20 existing records to migrate
- **Purpose**: Generate official laboratory reports with legal validity

## Requirements

### 1. Informe Model
```python
class Informe(models.Model):
    # Report Identification
    nro_oficial = CharField(max_length=50, unique=True)  # NroOfic - Official report number
    tipo_informe = CharField(choices=[
        ('ANALISIS', 'Análisis de Muestra'),
        ('CERTIFICADO', 'Certificado de Calidad'),
        ('CONSULTA', 'Consulta Técnica'),
        ('ESPECIAL', 'Informe Especial'),
    ])

    # Relationships
    entrada = ForeignKey(Entrada, on_delete=models.CASCADE)  # Sample entry
    cliente = ForeignKey(Cliente, on_delete=models.PROTECT)  # Report recipient
    ensayos_incluidos = ManyToManyField(DetalleEnsayo)  # Tests included in report

    # Report Status
    estado = CharField(choices=[
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE_FIRMA', 'Pendiente de Firma'),
        ('EMITIDO', 'Emitido'),
        ('ENTREGADO', 'Entregado'),
        ('ANULADO', 'Anulado'),
    ], default='BORRADOR')

    # Dates
    fecha_generacion = DateTimeField(auto_now_add=True)
    fecha_emision = DateTimeField(null=True, blank=True)
    fecha_entrega = DateTimeField(null=True, blank=True)
    fecha_vencimiento = DateField(null=True, blank=True)

    # Signatures & Authorization
    emitido_por = ForeignKey(User, related_name='informes_emitidos')
    revisado_por = ForeignKey(User, related_name='informes_revisados', null=True)
    aprobado_por = ForeignKey(User, related_name='informes_aprobados', null=True)

    # Content
    resumen_resultados = TextField()  # Summary of results
    conclusiones = TextField(blank=True)
    observaciones = TextField(blank=True)
    recomendaciones = TextField(blank=True)

    # Additional Fields
    numero_paginas = IntegerField(default=1)
    copias_entregadas = IntegerField(default=1)
    medio_entrega = CharField(choices=[
        ('FISICO', 'Físico'),
        ('DIGITAL', 'Digital'),
        ('AMBOS', 'Físico y Digital'),
    ])

    # Metadata
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    anulado = BooleanField(default=False)
    motivo_anulacion = TextField(blank=True)
```

### 2. Report Number Generation (NroOfic)
- Format: `INF-{YYYY}-{NNNN}` (e.g., INF-2024-0001)
- Sequential numbering per year
- Unique constraint across all reports
- Gap-free numbering (reuse only if last number deleted)
- Prefix configurable by report type:
  - Analysis: `INF-A-{YYYY}-{NNNN}`
  - Certificate: `INF-C-{YYYY}-{NNNN}`
  - Special: `INF-E-{YYYY}-{NNNN}`

### 3. Report Templates System
```python
class PlantillaInforme(models.Model):
    nombre = CharField(max_length=100)
    tipo = CharField(choices=TIPO_INFORME_CHOICES)
    header_html = TextField()  # HTML template for header
    footer_html = TextField()  # HTML template for footer
    body_template = TextField()  # Jinja2 template for content
    css_styles = TextField()  # Custom CSS
    logo_encabezado = ImageField()
    logo_pie = ImageField()
    activa = BooleanField(default=True)
```

### 4. Report Generation Workflow
```
BORRADOR → PENDIENTE_FIRMA → EMITIDO → ENTREGADO
    ↑           ↓               ↓
    └──── ANULADO ←─────────────┘
```

**State Descriptions:**
- **BORRADOR**: Report being prepared, editable
- **PENDIENTE_FIRMA**: Awaiting technical review and approval
- **EMITIDO**: Officially issued with report number assigned
- **ENTREGADO**: Delivered to client
- **ANULADO**: Cancelled/voided (requires authorization)

### 5. Link Reports to Entries and Tests
- One-to-many: Entry → Reports (one sample can have multiple reports)
- Many-to-many: Report ↔ DetalleEnsayo (tests included)
- Validate all tests belong to same entry
- Track which tests are included in each report
- Prevent duplicate reporting of same test

### 6. Report Status Tracking
- Status change history table
- Automatic notifications on status changes
- SLA tracking (deadline alerts)
- Delivery confirmation tracking

## Acceptance Criteria
- [ ] Informe model created with all specified fields
- [ ] Automatic NroOfic generation with sequential numbering
- [ ] Report templates system implemented
- [ ] Status workflow with transitions validation
- [ ] Link to Entrada and DetalleEnsayo established
- [ ] Signature/authorization workflow
- [ ] Report status tracking and history
- [ ] Migration of 20 existing Informes records
- [ ] Prevent duplicate test reporting

## Technical Notes
- Report number generation must be atomic to prevent duplicates
- Store generated PDFs in file storage with reference in model
- Implement soft delete (anulado flag) for legal traceability
- Index on (nro_oficial, estado, fecha_emision) for lookups
- Cascade status updates when entry status changes
- Audit all status transitions with user and timestamp

## Labels
`phase-5`, `reporting`, `informes`, `pdf`, `workflow`, `legal`, `backend`, `frontend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 4-5 days
