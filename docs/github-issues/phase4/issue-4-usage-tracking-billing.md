# [Phase 4] Usage Tracking & Billing (Utilizado)

## Description
Implement the usage tracking and billing system based on the "Utilizado R" data (632 records). This system tracks actual test usage for accurate client billing.

## Data Context
- **Source Table**: Utilizado R
- **Record Count**: 632 historical usage records
- **Purpose**: Track billed quantities and calculate invoice amounts

## Requirements

### 1. Utilizado Model
```python
class Utilizado(models.Model):
    entrada = ForeignKey(Entrada)
    detalle_ensayo = ForeignKey(DetalleEnsayo, null=True)
    ensayo = ForeignKey(Ensayo)
    
    # Billing quantities
    cantidad = DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = DecimalField(max_digits=10, decimal_places=2)
    importe = DecimalField(max_digits=10, decimal_places=2)
    
    # Calculated: importe = cantidad × precio_unitario
    
    # Period
    fecha_uso = DateField()
    mes_facturacion = CharField(max_length=7)  # YYYY-MM
    
    # Status
    estado = CharField(choices=[
        ('PENDIENTE', 'Pendiente'),
        ('FACTURADO', 'Facturado'),
        ('ANULADO', 'Anulado'),
    ], default='PENDIENTE')
    
    # Invoice reference
    factura = ForeignKey(Factura, null=True, blank=True)
    
    # Audit
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### 2. Billing Calculation
```
Importe = Cantidad × Precio Unitario

Example:
- Test: pH Analysis
- Quantity: 3 samples
- Unit Price: $25.00
- Importe: 3 × $25.00 = $75.00
```

### 3. Usage Recording
- Auto-create Utilizado record when test completed
- Manual entry for corrections/adjustments
- Batch import from legacy data
- Usage validation against test assignment

### 4. Billing Reports

#### By Client
```
Cliente: [Dropdown]
Período: [Date Range]

Ensayo          | Cantidad | Precio Unit | Importe
────────────────┼──────────┼─────────────┼─────────
pH              |    15    |   $25.00    | $375.00
Densidad        |    12    |   $30.00    | $360.00
Recuento Total  |     8    |   $45.00    | $360.00
────────────────┼──────────┼─────────────┼─────────
TOTAL           |          |             | $1,095.00
```

#### By Period
- Monthly usage summary
- Quarterly reports
- Annual billing summary
- Trend analysis

#### By Test Type
- Most used tests
- Revenue by area (FQ/MB/ES/OS)
- Test popularity trends

### 5. Invoice Generation Interface
- Select unbilled usage items
- Preview invoice totals
- Generate draft invoice
- Link to external billing system
- Export billing data (CSV/XML)

### 6. Export Capabilities
- Excel export for accounting
- PDF summary reports
- XML for ERP integration
- CSV for data analysis

## Acceptance Criteria
- [ ] Utilizado model created with billing fields
- [ ] Import 632 historical records
- [ ] Auto-calculation: cantidad × precio = importe
- [ ] Usage reports by client with period filter
- [ ] Usage reports by period (month/quarter/year)
- [ ] Usage reports by test type
- [ ] Invoice generation interface
- [ ] Export billing data (Excel/PDF)
- [ ] Status tracking (Pendiente/Facturado/Anulado)
- [ ] Link to facturas table

## Technical Notes
- Trigger importe calculation on save
- Index on (entrada_id, estado, mes_facturacion)
- Soft delete for anulado records
- Currency handling (ARS/USD)
- Tax calculation hook (IVA)
- Integration with external accounting systems

## Labels
`phase-4`, `testing`, `billing`, `financial`, `data-migration`, `backend`, `frontend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 3-4 days
