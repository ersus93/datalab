# [Phase 4] Test Assignment System (Detalles de Ensayos)

## Description
Implement the core test assignment system that links samples to specific laboratory tests. This system manages the relationship between received samples and the analytical tests that need to be performed on them.

## Data Context
- **Source Table**: Detalles de Ensayos
- **Record Count**: 563 records to migrate
- **Purpose**: Link samples with their required tests and track assignment status

## Requirements

### 1. DetalleEnsayo Model
```python
class DetalleEnsayo(models.Model):
    entrada = ForeignKey(Entrada)          # Sample reference
    ensayo = ForeignKey(Ensayo)            # Test reference
    cantidad = IntegerField(default=1)     # Number of replicates
    estado = CharField(choices=[
        ('PENDIENTE', 'Pendiente'),
        ('ASIGNADO', 'Asignado'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('REPORTADO', 'Reportado'),
    ])
    fecha_asignacion = DateTimeField(null=True)
    fecha_inicio = DateTimeField(null=True)
    fecha_completado = DateTimeField(null=True)
    tecnico_asignado = ForeignKey(User, null=True)
    observaciones = TextField(blank=True)
```

### 2. Test Assignment Interface
- Multi-select test assignment from master test catalog
- Group tests by area (FQ, MB, ES, OS)
- Search/filter tests by name or code
- Display test prices during assignment
- Default quantity = 1, editable
- Batch assign multiple tests to a single sample

### 3. Status Workflow
```
Pendiente → Asignado → En Proceso → Completado → Reportado
   ↑           ↓
   └──── Cancelado ←──
```
- **Pendiente**: Test assigned but not started
- **Asignado**: Technician assigned, ready to start
- **En Proceso**: Test execution in progress
- **Completado**: Test finished, results recorded
- **Reportado**: Results included in final report

### 4. Quantity Tracking
- Track number of replicates/test units
- Support fractional quantities where applicable
- Validate against sample quantity received

## Acceptance Criteria
- [ ] DetalleEnsayo model created with all fields
- [ ] Migration script for 563 historical records
- [ ] Assignment interface with multi-select capability
- [ ] Status workflow with state transitions
- [ ] FK validation to Entradas and Ensayos tables
- [ ] Quantity tracking with default=1
- [ ] Assignment date (FechReal) captured
- [ ] Audit trail for status changes

## Technical Notes
- Status transitions should be logged in history table
- Prevent duplicate test assignments for same sample (unless specified)
- Index on (entrada_id, estado) for performance
- Cascade delete when sample is deleted

## Labels
`phase-4`, `testing`, `laboratory`, `data-migration`, `backend`, `frontend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 3-4 days
