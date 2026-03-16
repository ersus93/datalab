# [Phase 4] Test Data Import

## Description
Execute the data migration for test-related tables: Detalles de Ensayos (563 records) and Utilizado R (632 records). Ensure data integrity and validate all foreign key relationships.

## Data Sources

### 1. Detalles de Ensayos
- **Records**: 563 test assignments
- **Source**: Legacy database table
- **Target**: `detalleensayo` table
- **Key Fields**:
  - ID (legacy ID mapping)
  - Sample reference (entrada_id)
  - Test reference (ensayo_id)
  - Quantity (cantidad)
  - Assignment date (FechReal)
  - Status (if available in source)

### 2. Utilizado R
- **Records**: 632 usage records
- **Source**: Legacy database table
- **Target**: `utilizado` table
- **Key Fields**:
  - ID (legacy ID mapping)
  - Sample reference (entrada_id)
  - Test reference (ensayo_id)
  - Quantity used (cantidad)
  - Unit price (precio)
  - Total amount (importe)
  - Usage date

## Import Process

### Step 1: Data Extraction
```bash
# Export from legacy system
python manage.py export_legacy_data --table=detalles_ensayos --format=json
python manage.py export_legacy_data --table=utilizado_r --format=json
```

### Step 2: Data Validation
```python
def validate_detalle_ensayo(record):
    errors = []
    
    # Check entrada exists
    if not Entrada.objects.filter(id=record['entrada_id']).exists():
        errors.append(f"Entrada {record['entrada_id']} not found")
    
    # Check ensayo exists
    if not Ensayo.objects.filter(id=record['ensayo_id']).exists():
        errors.append(f"Ensayo {record['ensayo_id']} not found")
    
    # Validate quantity > 0
    if record['cantidad'] <= 0:
        errors.append(f"Invalid quantity: {record['cantidad']}")
    
    # Validate date format
    try:
        parse_date(record['fecha_asignacion'])
    except:
        errors.append(f"Invalid date: {record['fecha_asignacion']}")
    
    return errors
```

### Step 3: FK Validation

#### Entrada (Sample) References
- Verify all 563 detalle records link to valid entradas
- Flag orphaned records
- Create mapping report for missing entradas

#### Ensayo (Test) References
- Verify all test assignments link to valid ensayos
- Check 143 FQ tests are mapped correctly
- Verify 29 ES tests exist
- Flag tests not in master catalog

#### Cross-Validation
- Ensure Utilizado records match Detalle assignments
- Verify cantidad in Utilizado ≤ cantidad in Detalle
- Flag inconsistencies

### Step 4: Import Execution
```python
python manage.py import_detalles_ensayos --file=detalles_ensayos.json --dry-run
python manage.py import_detalles_ensayos --file=detalles_ensayos.json

python manage.py import_utilizado --file=utilizado_r.json --dry-run
python manage.py import_utilizado --file=utilizado_r.json
```

### Step 5: Data Integrity Checks

#### Count Verification
```sql
-- Verify record counts match
SELECT COUNT(*) FROM detalleensayo;  -- Should be 563
SELECT COUNT(*) FROM utilizado;       -- Should be 632
```

#### Relationship Check
```sql
-- Find orphaned records
SELECT * FROM detalleensayo de
LEFT JOIN entradas e ON de.entrada_id = e.id
WHERE e.id IS NULL;
```

#### Financial Reconciliation
```sql
-- Verify importe = cantidad × precio
SELECT * FROM utilizado
WHERE ABS(importe - (cantidad * precio_unitario)) > 0.01;
```

## Acceptance Criteria
- [ ] Import script for Detalles de Ensayos created
- [ ] Import script for Utilizado R created
- [ ] 563 detalle records imported successfully
- [ ] 632 utilizado records imported successfully
- [ ] All FKs to entradas validated
- [ ] All FKs to ensayos validated
- [ ] Test assignments verified against samples
- [ ] Test results imported if available
- [ ] Data integrity checks passed
- [ ] Import report generated with statistics
- [ ] Rollback capability tested

## Import Report Format
```
═══════════════════════════════════════════════════════════
           PHASE 4 DATA IMPORT REPORT
═══════════════════════════════════════════════════════════

Detalles de Ensayos:
  Source Records:    563
  Imported:          558
  Failed:            5
  Orphaned:          3

Utilizado R:
  Source Records:    632
  Imported:          632
  Failed:            0
  
Foreign Key Validation:
  Entradas Found:    558/558 (100%)
  Ensayos Found:     558/558 (100%)
  
Data Integrity:
  Calculation Errors: 0
  Date Format Errors: 2
  Missing Prices:     0

═══════════════════════════════════════════════════════════
```

## Rollback Plan
- Backup before import
- Transaction-based import (all or nothing)
- Soft delete for failed imports
- Restore script ready

## Labels
`phase-4`, `testing`, `data-migration`, `database`, `backend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 3-4 days
