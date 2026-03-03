# [Phase 4] Test Execution Tracking

## Description
Build the interface and workflow for technicians to execute assigned tests, record results, and track the progress of laboratory work through completion.

## Requirements

### 1. Technician Dashboard
```
┌─────────────────────────────────────────────────────┐
│ Bienvenido, [Técnico]                               │
├─────────────────────────────────────────────────────┤
│ PENDIENTES: 12    EN PROCESO: 5    COMPLETADOS: 23  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Próximos Ensayos:                                   │
│ • Muestra #1234 - pH (FQ) - Vence: 2024-01-15      │
│ • Muestra #1235 - Recuento (MB) - Vence: 2024-01-16│
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. Pending Tests View
- Filter by area (FQ, MB, ES, OS)
- Sort by priority/due date
- Sample information at a glance
- Quick "Start Test" action
- Batch selection for multiple tests

### 3. Test Execution Form
```python
class ResultadoEnsayo(models.Model):
    detalle_ensayo = ForeignKey(DetalleEnsayo)
    tecnico = ForeignKey(User)                 # Executing technician
    fecha_inicio = DateTimeField()             # When test started
    fecha_fin = DateTimeField(null=True)       # When test completed
    
    # Result fields (flexible based on test type)
    valor_numerico = DecimalField(null=True, blank=True)
    valor_texto = CharField(max_length=255, blank=True)
    valor_booleano = BooleanField(null=True)
    observaciones = TextField(blank=True)
    
    # For multi-parameter tests
    parametros_json = JSONField(default=dict, blank=True)
    
    # Approval
    revisado_por = ForeignKey(User, null=True, related_name='revisado')
    fecha_revision = DateTimeField(null=True)
```

### 4. Batch Operations
- Select multiple tests to complete
- Bulk status update
- Batch result import (from CSV/Excel)
- Duplicate test detection

### 5. Result Recording
- **FQ Tests**: Numeric inputs with units
- **MB Tests**: Colony counts, binary results
- **ES Tests**: Score sheets, panelist data
- **OS Tests**: Time tracking, completion notes

### 6. Historical View
- Completed tests archive
- Search by sample, test, date range
- Result export (PDF/Excel)
- Test revision history

## Acceptance Criteria
- [ ] Technician dashboard with stats
- [ ] Pending tests list with filtering
- [ ] Test execution form with result entry
- [ ] Batch completion capability
- [ ] Date tracking (start, completion)
- [ ] Technician assignment recording
- [ ] Historical test view with search
- [ ] Result validation per test type
- [ ] Approval workflow for results

## Workflow States

```
┌──────────┐     Start      ┌──────────┐
│ ASIGNADO │ ──────────────→│EN PROCESO│
└──────────┘                └────┬─────┘
                                 │
                Complete Results │
                                 ↓
                          ┌──────────┐
                          │COMPLETADO│
                          └────┬─────┘
                               │
               Review/Approve  │
                               ↓
                          ┌──────────┐
                          │REPORTADO │
                          └──────────┘
```

## Technical Notes
- Real-time updates using WebSockets (optional)
- Offline capability for remote testing
- Result validation rules per test type
- Integration with equipment (LIMS instruments)
- Photo upload for visual results
- Digital signature for result approval

## Labels
`phase-4`, `testing`, `laboratory`, `workflow`, `backend`, `frontend`

## Estimated Effort
**Story Points**: 13
**Time Estimate**: 5-6 days
