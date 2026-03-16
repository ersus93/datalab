# [Phase 2] Master Data Import from Access

**Labels:** `phase-2`, `migration`, `database`, `etl`, `access`, `high-priority`
**Milestone:** Phase 2: Core Entities & CRUD (Weeks 3-4)
**Estimated Effort:** 3 days
**Depends on:** Issue #1-#4 (Phase 2) ([Phase 2] Core CRUD Modules)

---

## Description

Implement complete data extraction, transformation, and loading (ETL) pipeline for migrating master data from Microsoft Access to PostgreSQL. This module handles the migration of 729 master records across three core entities: Clientes (166), Fabricas (403), and Productos (160).

### Current State
- Database schema created
- Models defined
- No data migration scripts

### Target State
- Complete ETL pipeline
- Data extraction from Access
- Transformation scripts for cleaning
- Import commands with validation
- FK integrity verification
- Row count validation
- Error handling and rollback

### Data Volume Summary
| Table | Records | Source Table | Priority |
|-------|---------|--------------|----------|
| Clientes | 166 | Clientes | High |
| Fabricas | 403 | Fabricas | High |
| Productos | 160 | Productos | High |
| **Total** | **729** | - | - |

### Migration Data Flow
```
Access (.accdb)
    ↓
Extract (pyodbc / mdb-export)
    ↓
Transform (Python scripts)
    ↓
Validate (FK checks, data types)
    ↓
Load (SQLAlchemy bulk insert)
    ↓
Verify (row counts, sampling)
```

---

## Acceptance Criteria

### Data Extraction

- [ ] Create extraction script for Access database:
  - Support both `pyodbc` and `mdb-export` methods
  - Handle Access frontend/backend split
  - Export to intermediate CSV/JSON format
  - Preserve all field values exactly
- [ ] Extract Clientes table (166 rows)
  - Map IdCli → id
  - Map NomCli → nombre
  - Map IdOrg → organismo_id
  - Map IdTipoCli → tipo_cliente
  - Map CliActivo → activo
- [ ] Extract Fabricas table (403 rows)
  - Map IdFca → id
  - Map IdCli → cliente_id
  - Map Fabrica → nombre
  - Map IdProv → provincia_id
- [ ] Extract Productos table (160 rows)
  - Map IdProd → id
  - Map Producto → nombre
  - Map IdDest → destino_id

### Data Transformation

- [ ] Create transformation pipeline:
  - Clean string values (trim whitespace)
  - Handle encoding issues (UTF-8 conversion)
  - Normalize boolean values (0/1 → True/False)
  - Validate date formats
- [ ] Cliente transformations:
  - Normalize client names
  - Map organismo_id to valid references
  - Set default tipo_cliente if null
  - Ensure activo defaults to True
- [ ] Fabrica transformations:
  - Validate cliente_id exists in Clientes
  - Validate provincia_id exists in Provincias
  - Generate default names if empty
  - Flag duplicate names per client
- [ ] Producto transformations:
  - Normalize product names
  - Validate destino_id exists
  - Handle special characters
  - Classify by sector (rama) if possible

### Import Commands

- [ ] Create Flask CLI commands:
  ```bash
  flask import clientes --file data/clientes.csv
  flask import fabricas --file data/fabricas.csv
  flask import productos --file data/productos.csv
  flask import all --dry-run  # Validate without inserting
  flask import all --force    # Skip confirmations
  ```
- [ ] Interactive mode with progress bars
- [ ] Batch size configuration (default 100)
- [ ] Skip existing records option
- [ ] Update existing records option
- [ ] Transaction support (all or nothing per table)

### Validation & Verification

- [ ] Row count validation:
  - Source: 166 clients → Target: 166 clients
  - Source: 403 factories → Target: 403 factories
  - Source: 160 products → Target: 160 products
  - Total: 729 records
- [ ] Foreign key integrity:
  - All fabricas.cliente_id exist in clientes
  - All fabricas.provincia_id exist in provincias
  - All productos.destino_id exist in destinos
  - All clientes.organismo_id exist in organismos
- [ ] Data sampling verification:
  - Random sample 10% of each table
  - Manual verification of 5 records per table
  - Check critical fields match exactly
- [ ] Orphan detection:
  - Report any factories without valid clients
  - Report any products without valid destinations
  - Report any clients without organism

### Error Handling

- [ ] Comprehensive error logging:
  - Log file with timestamps
  - Row numbers for errors
  - Field-level error details
  - Stack traces for exceptions
- [ ] Continue on error option
- [ ] Stop on first error option
- [ ] Retry failed rows option
- [ ] Generate error report CSV:
  - Row number
  - Error type
  - Error message
  - Original data (JSON)

### Rollback Capability

- [ ] Pre-import backup:
  - Export existing data before import
  - Store in timestamped file
- [ ] Rollback command:
  ```bash
  flask import rollback --backup-file backup_20260302.sql
  ```
- [ ] Transaction per table:
  - Rollback entire table on error
  - Preserve data consistency

### Import Report

- [ ] Generate import report:
  ```json
  {
    "timestamp": "2026-03-02T10:30:00",
    "tables": {
      "clientes": {
        "source_count": 166,
        "imported": 166,
        "errors": 0,
        "duration_ms": 1250
      },
      "fabricas": {
        "source_count": 403,
        "imported": 403,
        "errors": 0,
        "duration_ms": 2100
      },
      "productos": {
        "source_count": 160,
        "imported": 160,
        "errors": 0,
        "duration_ms": 980
      }
    },
    "total_duration_ms": 4330,
    "validation_passed": true
  }
  ```

---

## Technical Notes

### Project Structure

```
app/
├── commands/
│   ├── __init__.py
│   └── import_access.py       # CLI commands
├── services/
│   ├── __init__.py
│   └── import_service.py      # Import logic
├── utils/
│   ├── __init__.py
│   └── data_validators.py     # Validation helpers
└── migrations/
    └── data/                  # Migration data files
        ├── clientes.csv
        ├── fabricas.csv
        └── productos.csv
```

### Access Extraction Script

```python
# scripts/extract_access.py

import pyodbc
import csv
import json
from pathlib import Path

ACCESS_DB_PATH = "data/RM2026_be.accdb"
OUTPUT_DIR = "app/migrations/data"

def extract_table(conn, table_name, columns):
    """Extract table from Access to CSV"""
    cursor = conn.cursor()
    
    # Build SELECT query
    cols_str = ', '.join(columns.keys())
    query = f"SELECT {cols_str} FROM [{table_name}]"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Write to CSV
    output_file = Path(OUTPUT_DIR) / f"{table_name.lower()}.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns.values())
        writer.writeheader()
        
        for row in rows:
            row_dict = {}
            for i, (source_col, target_col) in enumerate(columns.items()):
                value = row[i]
                # Transformations
                if isinstance(value, str):
                    value = value.strip()
                row_dict[target_col] = value
            writer.writerow(row_dict)
    
    print(f"Extracted {len(rows)} rows from {table_name} to {output_file}")
    return len(rows)

def main():
    # Connect to Access
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={ACCESS_DB_PATH}"
    conn = pyodbc.connect(conn_str)
    
    # Extract Clientes
    extract_table(conn, 'Clientes', {
        'IdCli': 'id',
        'NomCli': 'nombre',
        'IdOrg': 'organismo_id',
        'IdTipoCli': 'tipo_cliente',
        'CliActivo': 'activo'
    })
    
    # Extract Fabricas
    extract_table(conn, 'Fabricas', {
        'IdFca': 'id',
        'IdCli': 'cliente_id',
        'Fabrica': 'nombre',
        'IdProv': 'provincia_id'
    })
    
    # Extract Productos
    extract_table(conn, 'Productos', {
        'IdProd': 'id',
        'Producto': 'nombre',
        'IdDest': 'destino_id'
    })
    
    conn.close()
    print("Extraction complete!")

if __name__ == '__main__':
    main()
```

### Import Service

```python
# app/services/import_service.py

import csv
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy import inspect
from app.database import db
from app.database.models import Cliente, Fabrica, Producto, Organismo, Provincia, Destino

class ImportError:
    """Represents an import error"""
    def __init__(self, row_number: int, field: str, message: str, original_value):
        self.row_number = row_number
        self.field = field
        self.message = message
        self.original_value = original_value
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            'row_number': self.row_number,
            'field': self.field,
            'message': self.message,
            'original_value': str(self.original_value),
            'timestamp': self.timestamp.isoformat()
        }

class ImportResult:
    """Result of import operation"""
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.imported = 0
        self.skipped = 0
        self.errors: List[ImportError] = []
        self.start_time = None
        self.end_time = None
    
    @property
    def duration_ms(self):
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return 0
    
    def to_dict(self):
        return {
            'table': self.table_name,
            'imported': self.imported,
            'skipped': self.skipped,
            'errors': len(self.errors),
            'duration_ms': self.duration_ms
        }

class MasterDataImportService:
    """Service for importing master data from Access"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.results: List[ImportResult] = []
    
    def import_clientes(self, csv_path: str, skip_existing: bool = True) -> ImportResult:
        """Import clients from CSV"""
        result = ImportResult('clientes')
        result.start_time = datetime.utcnow()
        
        # Get valid organismo IDs
        valid_organismos = {o.id for o in Organismo.query.all()}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    # Check if exists
                    existing = Cliente.query.get(int(row['id']))
                    if existing and skip_existing:
                        result.skipped += 1
                        continue
                    
                    # Validate organismo_id
                    organismo_id = int(row['organismo_id']) if row['organismo_id'] else None
                    if organismo_id and organismo_id not in valid_organismos:
                        result.errors.append(ImportError(
                            row_num, 'organismo_id',
                            f'Invalid organismo_id: {organismo_id}',
                            row['organismo_id']
                        ))
                        continue
                    
                    # Create client
                    cliente = Cliente(
                        id=int(row['id']),
                        nombre=row['nombre'].strip(),
                        organismo_id=organismo_id,
                        tipo_cliente=int(row['tipo_cliente']) if row['tipo_cliente'] else 1,
                        activo=bool(int(row['activo'])) if row['activo'] else True
                    )
                    
                    if not self.dry_run:
                        if existing:
                            db.session.merge(cliente)
                        else:
                            db.session.add(cliente)
                        
                        # Commit every 50 rows
                        if result.imported % 50 == 0:
                            db.session.commit()
                    
                    result.imported += 1
                    
                except Exception as e:
                    result.errors.append(ImportError(
                        row_num, 'general', str(e), row
                    ))
        
        if not self.dry_run:
            db.session.commit()
        
        result.end_time = datetime.utcnow()
        self.results.append(result)
        return result
    
    def import_fabricas(self, csv_path: str, skip_existing: bool = True) -> ImportResult:
        """Import factories from CSV"""
        result = ImportResult('fabricas')
        result.start_time = datetime.utcnow()
        
        # Get valid foreign keys
        valid_clientes = {c.id for c in Cliente.query.all()}
        valid_provincias = {p.id for p in Provincia.query.all()}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Check if exists
                    existing = Fabrica.query.get(int(row['id']))
                    if existing and skip_existing:
                        result.skipped += 1
                        continue
                    
                    # Validate FKs
                    cliente_id = int(row['cliente_id'])
                    if cliente_id not in valid_clientes:
                        result.errors.append(ImportError(
                            row_num, 'cliente_id',
                            f'Invalid cliente_id: {cliente_id}',
                            row['cliente_id']
                        ))
                        continue
                    
                    provincia_id = int(row['provincia_id']) if row['provincia_id'] else None
                    if provincia_id and provincia_id not in valid_provincias:
                        result.errors.append(ImportError(
                            row_num, 'provincia_id',
                            f'Invalid provincia_id: {provincia_id}',
                            row['provincia_id']
                        ))
                        continue
                    
                    # Create factory
                    fabrica = Fabrica(
                        id=int(row['id']),
                        cliente_id=cliente_id,
                        nombre=row['nombre'].strip() or f'Fábrica {row["id"]}',
                        provincia_id=provincia_id,
                        activo=True
                    )
                    
                    if not self.dry_run:
                        if existing:
                            db.session.merge(fabrica)
                        else:
                            db.session.add(fabrica)
                        
                        if result.imported % 50 == 0:
                            db.session.commit()
                    
                    result.imported += 1
                    
                except Exception as e:
                    result.errors.append(ImportError(
                        row_num, 'general', str(e), row
                    ))
        
        if not self.dry_run:
            db.session.commit()
        
        result.end_time = datetime.utcnow()
        self.results.append(result)
        return result
    
    def import_productos(self, csv_path: str, skip_existing: bool = True) -> ImportResult:
        """Import products from CSV"""
        result = ImportResult('productos')
        result.start_time = datetime.utcnow()
        
        # Get valid destinos
        valid_destinos = {d.id for d in Destino.query.all()}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Check if exists
                    existing = Producto.query.get(int(row['id']))
                    if existing and skip_existing:
                        result.skipped += 1
                        continue
                    
                    # Validate FK
                    destino_id = int(row['destino_id']) if row['destino_id'] else None
                    if destino_id and destino_id not in valid_destinos:
                        result.errors.append(ImportError(
                            row_num, 'destino_id',
                            f'Invalid destino_id: {destino_id}',
                            row['destino_id']
                        ))
                        continue
                    
                    # Create product
                    producto = Producto(
                        id=int(row['id']),
                        nombre=row['nombre'].strip(),
                        destino_id=destino_id,
                        activo=True
                    )
                    
                    if not self.dry_run:
                        if existing:
                            db.session.merge(producto)
                        else:
                            db.session.add(producto)
                        
                        if result.imported % 50 == 0:
                            db.session.commit()
                    
                    result.imported += 1
                    
                except Exception as e:
                    result.errors.append(ImportError(
                        row_num, 'general', str(e), row
                    ))
        
        if not self.dry_run:
            db.session.commit()
        
        result.end_time = datetime.utcnow()
        self.results.append(result)
        return result
    
    def validate_all(self) -> Dict:
        """Run all validations and return report"""
        validations = {
            'clientes': {
                'expected': 166,
                'actual': Cliente.query.count(),
                'passed': Cliente.query.count() == 166
            },
            'fabricas': {
                'expected': 403,
                'actual': Fabrica.query.count(),
                'passed': Fabrica.query.count() == 403
            },
            'productos': {
                'expected': 160,
                'actual': Producto.query.count(),
                'passed': Producto.query.count() == 160
            }
        }
        
        # Check FK integrity
        orphan_fabricas = Fabrica.query.filter(
            ~Fabrica.cliente_id.in_(db.session.query(Cliente.id))
        ).count()
        
        validations['fk_integrity'] = {
            'orphan_fabricas': orphan_fabricas,
            'passed': orphan_fabricas == 0
        }
        
        return validations
    
    def generate_report(self) -> str:
        """Generate JSON report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'dry_run': self.dry_run,
            'tables': [r.to_dict() for r in self.results],
            'validations': self.validate_all()
        }
        return json.dumps(report, indent=2)
```

### Flask CLI Commands

```python
# app/commands/import_access.py

import click
from flask.cli import with_appcontext
from app.services.import_service import MasterDataImportService

@click.group()
def import_cli():
    """Import commands for Access migration"""
    pass

@import_cli.command()
@click.option('--file', required=True, help='Path to CSV file')
@click.option('--dry-run', is_flag=True, help='Validate without inserting')
@click.option('--skip-existing', is_flag=True, default=True, help='Skip existing records')
@with_appcontext
def clientes(file, dry_run, skip_existing):
    """Import clients from Access CSV"""
    service = MasterDataImportService(dry_run=dry_run)
    result = service.import_clientes(file, skip_existing=skip_existing)
    
    click.echo(f"Clientes importados: {result.imported}")
    click.echo(f"Omitidos: {result.skipped}")
    click.echo(f"Errores: {len(result.errors)}")
    click.echo(f"Duración: {result.duration_ms}ms")
    
    if result.errors:
        click.echo("\nErrores:")
        for error in result.errors[:10]:  # Show first 10
            click.echo(f"  Fila {error.row_number}: {error.message}")

@import_cli.command()
@click.option('--file', required=True, help='Path to CSV file')
@click.option('--dry-run', is_flag=True, help='Validate without inserting')
@click.option('--skip-existing', is_flag=True, default=True)
@with_appcontext
def fabricas(file, dry_run, skip_existing):
    """Import factories from Access CSV"""
    service = MasterDataImportService(dry_run=dry_run)
    result = service.import_fabricas(file, skip_existing=skip_existing)
    
    click.echo(f"Fábricas importadas: {result.imported}")
    click.echo(f"Omitidas: {result.skipped}")
    click.echo(f"Errores: {len(result.errors)}")

@import_cli.command()
@click.option('--file', required=True, help='Path to CSV file')
@click.option('--dry-run', is_flag=True, help='Validate without inserting')
@click.option('--skip-existing', is_flag=True, default=True)
@with_appcontext
def productos(file, dry_run, skip_existing):
    """Import products from Access CSV"""
    service = MasterDataImportService(dry_run=dry_run)
    result = service.import_productos(file, skip_existing=skip_existing)
    
    click.echo(f"Productos importados: {result.imported}")
    click.echo(f"Omitidos: {result.skipped}")
    click.echo(f"Errores: {len(result.errors)}")

@import_cli.command()
@click.option('--data-dir', default='app/migrations/data', help='Directory containing CSV files')
@click.option('--dry-run', is_flag=True, help='Validate without inserting')
@click.option('--force', is_flag=True, help='Skip confirmation')
@with_appcontext
def all(data_dir, dry_run, force):
    """Import all master data"""
    if not force and not dry_run:
        click.confirm('This will import all master data. Continue?', abort=True)
    
    service = MasterDataImportService(dry_run=dry_run)
    
    # Import in correct order (clientes first for FKs)
    import os
    
    click.echo("Importando clientes...")
    result_clientes = service.import_clientes(
        os.path.join(data_dir, 'clientes.csv')
    )
    
    click.echo("Importando fábricas...")
    result_fabricas = service.import_fabricas(
        os.path.join(data_dir, 'fabricas.csv')
    )
    
    click.echo("Importando productos...")
    result_productos = service.import_productos(
        os.path.join(data_dir, 'productos.csv')
    )
    
    # Validate
    click.echo("\nValidating...")
    validations = service.validate_all()
    
    # Report
    click.echo("\n" + "="*50)
    click.echo("RESUMEN DE IMPORTACIÓN")
    click.echo("="*50)
    click.echo(f"Clientes: {result_clientes.imported}/166")
    click.echo(f"Fábricas: {result_fabricas.imported}/403")
    click.echo(f"Productos: {result_productos.imported}/160")
    click.echo(f"Total: {result_clientes.imported + result_fabricas.imported + result_productos.imported}/729")
    click.echo("\nValidaciones:")
    for table, check in validations.items():
        if table != 'fk_integrity':
            status = "✓" if check['passed'] else "✗"
            click.echo(f"  {status} {table}: {check['actual']}/{check['expected']}")
    
    # Save report
    report_path = 'import_report.json'
    with open(report_path, 'w') as f:
        f.write(service.generate_report())
    click.echo(f"\nReporte guardado en: {report_path}")

def init_app(app):
    app.cli.add_command(import_cli)
```

---

## Dependencies

**Blocked by:**
- Issue #1-#3 (Phase 1): All database models
- Issue #1-#3 (Phase 2): CRUD modules (to verify data after import)

**Blocks:**
- Phase 3: Sample Management (needs all master data)

---

## Related Documentation

- `docs/PRD.md` Section 6: Migration Strategy
- `docs/ACCESS_MIGRATION_ANALYSIS.md`: Complete Access schema
- `plans/MIGRATION_PLAN.md` Phase 2.2: Data Migration

---

## Testing Requirements

- [ ] Test extraction from Access database
- [ ] Test each import command
- [ ] Test dry-run mode
- [ ] Test FK validation
- [ ] Test error reporting
- [ ] Test rollback functionality
- [ ] Verify row counts match

---

## Definition of Done

- [ ] Extraction script working
- [ ] All import commands functional
- [ ] Validation passing (729 records)
- [ ] FK integrity verified
- [ ] Error handling complete
- [ ] Rollback capability tested
- [ ] Import report generated
- [ ] Code review completed
