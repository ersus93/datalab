# [Phase 3] Transactional Data Import

**Labels:** `phase-3`, `data-migration`, `import`, `backend`, `high-priority`
**Milestone:** Phase 3: Sample Management (Weeks 5-6)
**Estimated Effort:** 3 days

---

## Description

Import all transactional data from the Access database for Phase 3 entities: Ordenes de Trabajo (37 records), Pedidos (49 records), and Entradas (109 records). This migration must preserve referential integrity, validate foreign keys, verify balance calculations, and maintain lot number formats.

This is a **critical data migration** that bridges the legacy Access system with the new DataLab platform.

---

## Acceptance Criteria

### Ordenes de Trabajo Import (37 records)
- [ ] Create import script for `ordenes_trabajo` table:
  - Map Access fields to new schema
  - Link to existing `clientes` (validate FK)
  - Preserve `NroOfic` official numbers
  - Set creation dates
  - Handle missing/invalid references
- [ ] Validation rules:
  - All records must have valid `cliente_id`
  - `NroOfic` must be unique
  - Status must be valid enum value
- [ ] Import statistics report:
  - Total records processed
  - Successfully imported
  - Failed/skipped with reasons

### Pedidos Import (49 records)
- [ ] Create import script for `pedidos` table:
  - Link to `clientes` (validate FK)
  - Link to `productos` (validate FK)
  - Link to `ordenes_trabajo` (optional, validate if present)
  - Link to `unidades_medida` (optional)
  - Preserve lot numbers (Lote)
  - Preserve dates (FechFab, FechVenc)
- [ ] Validation rules:
  - Cliente and Producto are required
  - Dates must be valid
  - FechVenc > FechFab
- [ ] Cross-reference validation with OrdenesTrabajo

### Entradas Import (109 records)
- [ ] Create import script for `entradas` table:
  - Link to `pedidos` (optional, validate if present)
  - Link to `productos` (validate FK)
  - Link to `fabricas` (validate FK)
  - Link to `clientes` (validate FK)
  - Link to `ramas` (optional)
  - Link to `unidades_medida` (optional)
  - Preserve lot numbers (X-XXXX format)
  - Preserve part numbers (NroParte)
  - Import quantities (CantidadRecib, CantidadEntreg)
  - Calculate and verify balances
  - Import status flags (EnOS, Anulado, EntEntregada)
- [ ] Validation rules:
  - Producto, Fabrica, Cliente are required
  - Balance: Saldo = CantidadRecib - CantidadEntreg
  - Lot format: X-XXXX
  - Dates must be valid

### Foreign Key Validation
- [ ] Pre-import FK validation:
  - Check all referenced clients exist
  - Check all referenced products exist
  - Check all referenced factories exist
  - Generate missing reference report
- [ ] FK resolution strategies:
  - Skip records with unresolvable FKs
  - Create placeholder records for critical missing refs
  - Log all resolution actions

### Balance Verification
- [ ] Verify all balance calculations:
  ```python
  expected_saldo = cantidad_recib - cantidad_entreg
  assert entrada.saldo == expected_saldo
  ```
- [ ] Flag discrepancies for manual review
- [ ] Generate balance verification report

### Lot Number Format Validation
- [ ] Validate lot format `X-XXXX`:
  - Single uppercase letter
  - Hyphen separator
  - Exactly 4 digits
- [ ] Flag non-conforming lot numbers
- [ ] Generate lot format compliance report

### Import Process
- [ ] Implement chunked import (batch processing):
  - Process in batches of 50 records
  - Transaction per batch
  - Progress tracking
- [ ] Error handling:
  - Continue on individual record errors
  - Detailed error logging
  - Rollback on critical failures
- [ ] Dry-run capability:
  - Validate without importing
  - Generate preview report
  - Show potential issues

### Post-Import Verification
- [ ] Record count verification:
  - Source: 37 OT, 49 Pedidos, 109 Entradas
  - Destination: Match counts
- [ ] FK integrity verification:
  - All FKs resolve to valid records
  - No orphaned records
- [ ] Data consistency checks:
  - Status flags consistent
  - Dates in valid ranges
  - Quantities non-negative
- [ ] Generate final migration report

---

## Technical Notes

### Import Script Structure

```python
# scripts/import_phase3_data.py

import pandas as pd
from app import create_app, db
from app.models import OrdenTrabajo, Pedido, Entrada, Cliente, Producto, Fabrica

class Phase3DataImporter:
    """Import Phase 3 transactional data from Access"""
    
    def __init__(self, access_db_path):
        self.access_db_path = access_db_path
        self.stats = {
            'ordenes_trabajo': {'total': 0, 'success': 0, 'failed': 0},
            'pedidos': {'total': 0, 'success': 0, 'failed': 0},
            'entradas': {'total': 0, 'success': 0, 'failed': 0}
        }
        self.errors = []
    
    def import_ordenes_trabajo(self):
        """Import 37 work orders"""
        df = self._read_access_table('ordenes_trabajo')
        self.stats['ordenes_trabajo']['total'] = len(df)
        
        for _, row in df.iterrows():
            try:
                # Validate cliente exists
                cliente = Cliente.query.get(row['IdCliente'])
                if not cliente:
                    raise ValueError(f"Cliente {row['IdCliente']} not found")
                
                # Check NroOfic uniqueness
                existing = OrdenTrabajo.query.filter_by(nro_ofic=row['NroOfic']).first()
                if existing:
                    raise ValueError(f"NroOfic {row['NroOfic']} already exists")
                
                ot = OrdenTrabajo(
                    id=row['Id'],
                    cliente_id=row['IdCliente'],
                    nro_ofic=row['NroOfic'],
                    codigo=f"OT-{row['Id']:04d}",
                    descripcion=row.get('Descripcion', ''),
                    observaciones=row.get('Observaciones', ''),
                    status=self._map_status(row.get('Status', 'PENDIENTE')),
                    fech_creacion=self._parse_datetime(row.get('FechCreacion'))
                )
                
                db.session.add(ot)
                self.stats['ordenes_trabajo']['success'] += 1
                
            except Exception as e:
                self.stats['ordenes_trabajo']['failed'] += 1
                self.errors.append({
                    'table': 'ordenes_trabajo',
                    'id': row.get('Id'),
                    'error': str(e)
                })
        
        db.session.commit()
    
    def import_pedidos(self):
        """Import 49 orders"""
        df = self._read_access_table('pedidos')
        self.stats['pedidos']['total'] = len(df)
        
        for _, row in df.iterrows():
            try:
                # Validate required FKs
                cliente = Cliente.query.get(row['IdCliente'])
                if not cliente:
                    raise ValueError(f"Cliente {row['IdCliente']} not found")
                
                producto = Producto.query.get(row['IdProducto'])
                if not producto:
                    raise ValueError(f"Producto {row['IdProducto']} not found")
                
                # Optional OT link
                ot_id = row.get('IdOrdenTrabajo')
                if ot_id and not OrdenTrabajo.query.get(ot_id):
                    raise ValueError(f"OrdenTrabajo {ot_id} not found")
                
                # Date validation
                fech_fab = self._parse_date(row.get('FechFab'))
                fech_venc = self._parse_date(row.get('FechVenc'))
                if fech_venc and fech_fab and fech_venc < fech_fab:
                    raise ValueError("FechVenc must be after FechFab")
                
                pedido = Pedido(
                    id=row['IdPedido'],
                    cliente_id=row['IdCliente'],
                    producto_id=row['IdProducto'],
                    orden_trabajo_id=ot_id,
                    codigo=f"PED-{row['IdPedido']:04d}",
                    lote=row.get('Lote'),
                    fech_fab=fech_fab,
                    fech_venc=fech_venc,
                    cantidad=row.get('Cantidad'),
                    unidad_medida_id=row.get('IdUnidadMedida'),
                    observaciones=row.get('Observaciones', ''),
                    status=self._map_pedido_status(row.get('Status', 'PENDIENTE')),
                    fech_pedido=self._parse_datetime(row.get('FechPedido'))
                )
                
                db.session.add(pedido)
                self.stats['pedidos']['success'] += 1
                
            except Exception as e:
                self.stats['pedidos']['failed'] += 1
                self.errors.append({
                    'table': 'pedidos',
                    'id': row.get('IdPedido'),
                    'error': str(e)
                })
        
        db.session.commit()
    
    def import_entradas(self):
        """Import 109 sample entries"""
        df = self._read_access_table('entradas')
        self.stats['entradas']['total'] = len(df)
        
        for _, row in df.iterrows():
            try:
                # Validate required FKs
                producto = Producto.query.get(row['IdProducto'])
                if not producto:
                    raise ValueError(f"Producto {row['IdProducto']} not found")
                
                fabrica = Fabrica.query.get(row['IdFabrica'])
                if not fabrica:
                    raise ValueError(f"Fabrica {row['IdFabrica']} not found")
                
                cliente = Cliente.query.get(row['IdCliente'])
                if not cliente:
                    raise ValueError(f"Cliente {row['IdCliente']} not found")
                
                # Verify balance
                cant_recib = row.get('CantidadRecib', 0)
                cant_entreg = row.get('CantidadEntreg', 0)
                expected_saldo = cant_recib - cant_entreg
                actual_saldo = row.get('Saldo', 0)
                
                if abs(expected_saldo - actual_saldo) > 0.01:
                    self.errors.append({
                        'table': 'entradas',
                        'id': row['Id'],
                        'warning': f'Balance mismatch: expected {expected_saldo}, got {actual_saldo}'
                    })
                
                # Validate lot format
                lote = row.get('Lote')
                if lote and not re.match(r'^[A-Z]-\d{4}$', lote):
                    self.errors.append({
                        'table': 'entradas',
                        'id': row['Id'],
                        'warning': f'Invalid lot format: {lote}'
                    })
                
                entrada = Entrada(
                    id=row['Id'],
                    pedido_id=row.get('IdPedido'),
                    producto_id=row['IdProducto'],
                    fabrica_id=row['IdFabrica'],
                    cliente_id=row['IdCliente'],
                    rama_id=row.get('IdRama'),
                    codigo=row.get('Codigo', f"ENT-{row['Id']:04d}"),
                    lote=lote,
                    nro_parte=row.get('NroParte'),
                    cantidad_recib=cant_recib,
                    cantidad_entreg=cant_entreg,
                    saldo=actual_saldo,
                    cantidad_muest=row.get('CantidadMuest'),
                    unidad_medida_id=row.get('IdUnidadMedida'),
                    fech_fab=self._parse_date(row.get('FechFab')),
                    fech_venc=self._parse_date(row.get('FechVenc')),
                    fech_muestreo=self._parse_date(row.get('FechMuestreo')),
                    fech_entrada=self._parse_datetime(row.get('FechEntrada')),
                    status=self._map_entrada_status(row.get('Status')),
                    en_os=bool(row.get('EnOS')),
                    anulado=bool(row.get('Anulado')),
                    ent_entregada=bool(row.get('EntEntregada')),
                    observaciones=row.get('Observaciones', '')
                )
                
                db.session.add(entrada)
                self.stats['entradas']['success'] += 1
                
            except Exception as e:
                self.stats['entradas']['failed'] += 1
                self.errors.append({
                    'table': 'entradas',
                    'id': row.get('Id'),
                    'error': str(e)
                })
        
        db.session.commit()
    
    def generate_report(self):
        """Generate import report"""
        report = f"""
# Phase 3 Data Import Report

## Summary
- Ordenes de Trabajo: {self.stats['ordenes_trabajo']['success']}/{self.stats['ordenes_trabajo']['total']}
- Pedidos: {self.stats['pedidos']['success']}/{self.stats['pedidos']['total']}
- Entradas: {self.stats['entradas']['success']}/{self.stats['entradas']['total']}

## Errors ({len(self.errors)})
"""
        for error in self.errors:
            report += f"- {error['table']} ID {error['id']}: {error.get('error') or error.get('warning')}\n"
        
        return report
```

### Import Command

```python
# manage.py

@cli.command()
@click.argument('access_db_path')
@click.option('--dry-run', is_flag=True, help='Validate without importing')
@click.option('--batch-size', default=50, help='Records per batch')
def import_phase3(access_db_path, dry_run, batch_size):
    """Import Phase 3 transactional data from Access"""
    importer = Phase3DataImporter(access_db_path)
    
    if dry_run:
        click.echo("DRY RUN - Validating only...")
        importer.validate_all()
    else:
        importer.import_ordenes_trabajo()
        importer.import_pedidos()
        importer.import_entradas()
    
    click.echo(importer.generate_report())
```

### FK Validation Query

```sql
-- Pre-import check for missing references
SELECT 
    'Missing Clientes' as check_type,
    COUNT(*) as count
FROM access_entradas e
LEFT JOIN clientes c ON e.IdCliente = c.id
WHERE c.id IS NULL

UNION ALL

SELECT 
    'Missing Productos',
    COUNT(*)
FROM access_entradas e
LEFT JOIN productos p ON e.IdProducto = p.id
WHERE p.id IS NULL;
```

### File Locations

```
scripts/
├── import_phase3_data.py       # Main import script
├── validate_phase3_import.py   # Post-import validation
└── generate_import_report.py   # Report generator

docs/migration/
├── phase3_import_report.md     # Generated report
└── phase3_error_log.md         # Error details
```

---

## Dependencies

**Blocked by:**
- Issue #[Phase 1] Database Migration Scripts (base schema)
- Issue #[Phase 1] Import Access Data (reference/master data)
- Issue #[Phase 3] Sample Entry System (Entrada model)
- Issue #[Phase 3] Order Management (Pedido model)
- Issue #[Phase 3] Work Order Management (OrdenTrabajo model)

**Blocks:**
- Issue #[Phase 4] Test Results Management (requires Entradas)

---

## Related Documentation

- `docs/PRD.md` Section 4: Data Migration Strategy
- `docs/ACCESS_MIGRATION_ANALYSIS.md`: Complete field mappings
- `docs/github-issues/phase1/issue-08-import-access-data.md`

---

## Verification Checklist

- [ ] 37 Ordenes de Trabajo imported
- [ ] 49 Pedidos imported
- [ ] 109 Entradas imported
- [ ] All FKs resolve correctly
- [ ] All balances verified
- [ ] Lot formats validated
- [ ] No orphaned records
- [ ] Import report generated
- [ ] Errors documented

---

## Definition of Done

- [ ] Import script created and tested
- [ ] All 195 records imported successfully
- [ ] FK validation working
- [ ] Balance verification complete
- [ ] Lot format validation complete
- [ ] Error handling tested
- [ ] Import report generated
- [ ] Code review completed
