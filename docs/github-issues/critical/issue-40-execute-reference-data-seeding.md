# [HIGH] Execute reference data seeding - Populate 73 reference records

**Labels:** `high-priority`, `database`, `migration`, `phase-1`  
**GitHub Issue:** #40  
**Priority:** HIGH - Required for foreign key relationships to work

---

## Problem

The seed data script exists but has not been executed. The 9 reference tables need to be populated with 73 records from the legacy Access database.

## Seed Data Status

**Script exists:** `app/database/seeds/reference_data.py`

**Tables to populate:** 9

| Table | Records | Data Description |
|-------|---------|------------------|
| areas | 4 | FQ (Físico-Químico), MB (Microbiología), ES (Evaluación Sensorial), OS (Otros Servicios) |
| organismos | 12 | Ministries and enterprises |
| provincias | 4 | Geographic provinces (PR, AR, LH, MQ) |
| destinos | 7 | CF, AC, ME, CD, DE, TU, EX |
| ramas | 13 | Industry sectors (Cárnicos, Lácteos, etc.) |
| meses | 12 | Calendar months (Enero-Diciembre) |
| annos | 10 | Years 2020-2029 |
| tipos_es | 4 | Sensory evaluation types (Visual, Olfativo, Gustativo, Táctil) |
| unidades_medida | 3 | g, mg/L, mL |

**Total: 73 reference records**

## Prerequisites

⚠️ **BLOCKED BY:** Issue #38 (Create missing database migrations)

The reference tables must exist before seeding can occur.

## Execution

After migrations are applied:

### Option 1: CLI Command (recommended)
```bash
flask seed-reference
```

### Option 2: Direct execution
```bash
python app/database/seeds/reference_data.py
```

## Verification

```python
from app.database.models import Area, Organismo, Provincia
from app import create_app

app = create_app()
with app.app_context():
    print(f"Areas: {Area.query.count()}")  # Should be 4
    print(f"Organismos: {Organismo.query.count()}")  # Should be 12
    print(f"Provincias: {Provincia.query.count()}")  # Should be 4
    # ... etc
```

## Expected Output

```
=== Seeding Reference Data ===
Migrating 73 records from Access RM2026...

✓ Areas: 4 registros
✓ Organismos: 12 registros
✓ Provincias: 4 registros
✓ Destinos: 7 registros
✓ Ramas: 13 registros
✓ Meses: 12 registros
✓ Años: 10 registros
✓ Tipo ES: 4 registros
✓ Unidades de Medida: 3 registros

=== Reference Data Seeding Complete ===
Total records: 73/73
```

## Acceptance Criteria
- [ ] All 9 reference tables populated
- [ ] 73 total records inserted
- [ ] No duplicate records on re-run (idempotent)
- [ ] CLI command `flask seed-reference` works
- [ ] Data matches Access RM2026 source

## Dependencies
- Depends on: Issue #36 (Fix missing clientes module)
- Depends on: Issue #38 (Create missing database migrations)

## Related Issues
- Part of: Phase 1 implementation
- Related to: Issue #1 (Reference data models - completed)

## Created
2026-03-04
