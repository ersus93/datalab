# [Phase 1] Import Access Data - Reference & Master

**Labels:** `phase-1`, `migration`, `access`, `etl`, `high-priority`, `data-import`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days
**Depends on:** 
- Issue #4 ([Phase 1] Database Migration Scripts)
- Issue #7 ([Phase 1] CRUD API for Reference Data)

---

## Description

Execute the complete data migration from Microsoft Access to PostgreSQL for Phase 1 scope: all reference data (73 records) and master data (729 records). This is the **final Phase 1 task** that populates the database with real production data from the legacy RM2026 system.

### Migration Scope

| Category | Tables | Records | Source Table | Complexity |
|----------|--------|---------|--------------|------------|
| **Reference Data** | 9 | **73** | Various | Low |
| Annos | 1 | 10 | Annos | Low |
| Meses | 1 | 12 | Meses | Low |
| Areas | 1 | 4 | Areas | Low |
| Organismos | 1 | 12 | Organismos | Low |
| Provincias | 1 | 4 | Provincias | Low |
| Destinos | 1 | 7 | Destinos | Low |
| Ramas | 1 | 13 | Ramas | Low |
| TipoES | 1 | 4 | Tipo ES | Low |
| UM | 1 | 3 | UM | Low |
| **Master Data** | 3 | **729** | Various | Medium |
| Clientes | 1 | 166 | Clientes | Medium |
| Fabricas | 1 | 403 | Fabricas | Medium |
| Productos | 1 | 160 | Productos | Medium |
| Test Catalogs | 2 | **172** | Various | Low-Medium |
| Ensayos | 1 | 143 | Ensayos | Medium |
| EnsayosES | 1 | 29 | EnsayosES | Low |
| **TOTAL** | **14** | **974** | | |

---

## Acceptance Criteria

### Pre-Migration Checklist

- [ ] Verify Access database files accessible (RM2026.accdb, RM2026_be.accdb)
- [ ] Verify PostgreSQL database is running and accessible
- [ ] Verify all Phase 1 models exist in database (Issue #1-3)
- [ ] Verify Alembic migrations have been applied (Issue #4)
- [ ] Create full database backup before migration
- [ ] Verify pyodbc and Access drivers installed
- [ ] Test connectivity to both databases
- [ ] Clear target tables or verify they're empty (or handle duplicates)

### Data Extraction Scripts

- [ ] Create `extract_reference_data.py` script
  - [ ] Connect to Access using pyodbc
  - [ ] Extract all 9 reference tables
  - [ ] Export to intermediate format (CSV or JSON)
  - [ ] Handle encoding issues (Windows-1252 to UTF-8)
  - [ ] Log extraction progress

- [ ] Create `extract_master_data.py` script
  - [ ] Extract Clientes (166 records)
  - [ ] Extract Fabricas (403 records)
  - [ ] Extract Productos (160 records)
  - [ ] Preserve foreign key relationships
  - [ ] Handle NULL values appropriately

- [ ] Create `extract_test_catalogs.py` script
  - [ ] Extract Ensayos (143 records)
  - [ ] Extract EnsayosES (29 records)
  - [ ] Preserve pricing information

### Data Transformation Scripts

- [ ] Create `transform_reference_data.py`
  - [ ] Map Access data types to PostgreSQL
    - [ ] COUNTER (Auto) → SERIAL/INTEGER
    - [ ] BYTE → SMALLINT
    - [ ] VARCHAR → VARCHAR
    - [ ] BIT → BOOLEAN (-1=True, 0=False)
    - [ ] CURRENCY → DECIMAL(10,2)
    - [ ] DATETIME → TIMESTAMP
  - [ ] Clean string values (trim whitespace)
  - [ ] Handle Spanish characters (accents, ñ)
  - [ ] Validate data ranges

- [ ] Create `transform_master_data.py`
  - [ ] Map foreign keys (e.g., Clientes.IdOrg → organismo_id)
  - [ ] Handle duplicate detection
  - [ ] Validate required fields
  - [ ] Transform boolean flags correctly

- [ ] Create `transform_test_catalogs.py`
  - [ ] Map test prices to DECIMAL
  - [ ] Map area IDs correctly
  - [ ] Handle optional fields

### Data Loading Scripts

- [ ] Create `load_reference_data.py`
  - [ ] Load Areas (4 records)
  - [ ] Load Organismos (12 records)
  - [ ] Load Provincias (4 records)
  - [ ] Load Destinos (7 records)
  - [ ] Load Ramas (13 records)
  - [ ] Load Meses (12 records)
  - [ ] Load Annos (10 records)
  - [ ] Load TipoES (4 records)
  - [ ] Load UnidadesMedida (3 records)
  - [ ] Verify row counts after each load
  - [ ] Log success/failure per table

- [ ] Create `load_master_data.py`
  - [ ] Load Clientes (166 records)
    - [ ] Verify Organismo FKs exist
    - [ ] Handle inactive clients
  - [ ] Load Fabricas (403 records)
    - [ ] Verify Cliente FKs exist
    - [ ] Verify Provincia FKs exist
    - [ ] Handle duplicate factory names per client
  - [ ] Load Productos (160 records)
    - [ ] Verify Destino FKs exist
    - [ ] Handle product categorization

- [ ] Create `load_test_catalogs.py`
  - [ ] Load Ensayos (143 records)
    - [ ] Verify Area FKs exist (should be FQ=1)
    - [ ] Validate prices are positive
  - [ ] Load EnsayosES (29 records)
    - [ ] Verify TipoES FKs exist
    - [ ] Verify Area FKs exist (should be ES=3)

### Migration Orchestration

- [ ] Create `run_phase1_import.py` master script
  - [ ] Execute in correct order: Reference → Master → Test Catalogs
  - [ ] Transaction wrapping (all-or-nothing per category)
  - [ ] Progress logging with record counts
  - [ ] Error handling with rollback capability
  - [ ] Dry-run mode (validate without loading)
  - [ ] Generate migration report

### Validation & Verification

- [ ] Row count validation
  - [ ] Access row count == PostgreSQL row count for each table
  - [ ] Generate comparison report

- [ ] Foreign key integrity checks
  - [ ] No orphaned Fabricas (all have valid Cliente)
  - [ ] No orphaned Productos (all have valid Destino)
  - [ ] No orphaned Clientes (all have valid Organismo)

- [ ] Data sampling validation
  - [ ] Random sample 10% of each table
  - [ ] Manual verification of field values
  - [ ] Check critical fields (names, codes, prices)

- [ ] Functional validation via API
  - [ ] Query all records via REST API
  - [ ] Verify data displays correctly in web UI
  - [ ] Test search/filter with imported data

### Migration Report

- [ ] Generate `migration_report_phase1.md` with:
  - [ ] Start and end timestamps
  - [ ] Record counts (source vs target) per table
  - [ ] Validation results
  - [ ] Any errors or warnings
  - [ ] Data quality notes
  - [ ] Recommendations for Phase 2

---

## Technical Notes

### Directory Structure

```
scripts/
├── migrations/
│   ├── __init__.py
│   ├── config.py              # Database credentials, paths
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── access_connection.py   # pyodbc utilities
│   │   ├── reference_data.py      # Extract 9 tables
│   │   ├── master_data.py         # Extract 3 tables
│   │   └── test_catalogs.py       # Extract 2 tables
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── data_cleaner.py        # Common cleaning utilities
│   │   ├── reference_transform.py
│   │   ├── master_transform.py
│   │   └── test_transform.py
│   ├── load/
│   │   ├── __init__.py
│   │   ├── postgres_connection.py
│   │   ├── reference_loader.py
│   │   ├── master_loader.py
│   │   └── test_loader.py
│   ├── validate/
│   │   ├── __init__.py
│   │   ├── row_counts.py
│   │   ├── foreign_keys.py
│   │   └── data_sampler.py
│   └── run_phase1_import.py   # Master orchestration script
└── backups/
    └── pre_migration_*.sql    # Database backups
```

### Access Connection Utility

```python
# scripts/migrations/extract/access_connection.py

import pyodbc
import os
from pathlib import Path

class AccessDatabase:
    """Connection handler for Microsoft Access databases"""
    
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Access database not found: {db_path}")
        self.connection = None
    
    def connect(self):
        """Establish connection to Access database"""
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + str(self.db_path) + ';'
        )
        self.connection = pyodbc.connect(conn_str)
        return self.connection
    
    def get_table(self, table_name):
        """Extract entire table as list of dictionaries"""
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM [{table_name}]")
        
        columns = [column[0] for column in cursor.description]
        rows = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            rows.append(row_dict)
        
        return rows
    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

### Field Mapping Configuration

```python
# scripts/migrations/config.py

"""
Field mappings from Access to PostgreSQL
Format: 'AccessColumn': ('postgres_column', transform_function)
"""

REFERENCE_MAPPINGS = {
    'Areas': {
        'table': 'areas',
        'model': 'Area',
        'fields': {
            'IdArea': ('id', int),
            'Area': ('nombre', str),
            'Sigla': ('sigla', str),
        }
    },
    'Organismos': {
        'table': 'organismos',
        'model': 'Organismo',
        'fields': {
            'IdOrg': ('id', int),
            'Organismo': ('nombre', str),
        }
    },
    # ... similar for other reference tables
}

MASTER_MAPPINGS = {
    'Clientes': {
        'table': 'clientes',
        'model': 'Cliente',
        'fields': {
            'IdCli': ('id', int),
            'NomCli': ('nombre', str),
            'IdOrg': ('organismo_id', int),
            'IdTipoCli': ('tipo_cliente', int),
            'CliActivo': ('activo', lambda x: x == -1),  # Access BIT to Boolean
        }
    },
    'Fabricas': {
        'table': 'fabricas',
        'model': 'Fabrica',
        'fields': {
            'IdFca': ('id', int),
            'IdCli': ('cliente_id', int),
            'Fabrica': ('nombre', str),
            'IdProv': ('provincia_id', int),
        }
    },
    'Productos': {
        'table': 'productos',
        'model': 'Producto',
        'fields': {
            'IdProd': ('id', int),
            'Producto': ('nombre', str),
            'IdDest': ('destino_id', int),
        }
    },
}

TEST_MAPPINGS = {
    'Ensayos': {
        'table': 'ensayos',
        'model': 'Ensayo',
        'fields': {
            'IdEns': ('id', int),
            'NomOfic': ('nombre_oficial', str),
            'NomEns': ('nombre_corto', str),
            'IdArea': ('area_id', int),
            'Precio': ('precio', float),
            'UM': ('unidad_medida', str),
            'Activo': ('activo', lambda x: x == -1),
            'EsEnsayo': ('es_ensayo', lambda x: x == -1),
        }
    },
    'EnsayosES': {
        'table': 'ensayos_es',
        'model': 'EnsayoES',
        'fields': {
            'IdEnsES': ('id', int),
            'NomOfic': ('nombre_oficial', str),
            'NomEnsES': ('nombre_corto', str),
            'IdArea': ('area_id', int),
            'IdTipoES': ('tipo_es_id', int),
            'Precio': ('precio', float),
            'UM': ('unidad_medida', str),
            'Activo': ('activo', lambda x: x == -1),
        }
    },
}
```

### Migration Script

```python
# scripts/migrations/run_phase1_import.py

#!/usr/bin/env python3
"""
Phase 1 Data Migration Script
Migrates Reference, Master, and Test Catalog data from Access to PostgreSQL
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import create_app, db
from scripts.migrations.extract.access_connection import AccessDatabase
from scripts.migrations.config import REFERENCE_MAPPINGS, MASTER_MAPPINGS, TEST_MAPPINGS

class Phase1Migration:
    """Orchestrates Phase 1 data migration"""
    
    def __init__(self, access_db_path, dry_run=False):
        self.access_db = AccessDatabase(access_db_path)
        self.dry_run = dry_run
        self.report = {
            'start_time': datetime.now(),
            'tables': {},
            'errors': []
        }
    
    def run(self):
        """Execute full Phase 1 migration"""
        print("=" * 60)
        print("DataLab Phase 1 Migration")
        print("=" * 60)
        print(f"Started: {self.report['start_time']}")
        print(f"Dry Run: {self.dry_run}")
        print()
        
        try:
            with self.access_db:
                # Migration order matters due to FK dependencies
                self.migrate_reference_data()
                self.migrate_master_data()
                self.migrate_test_catalogs()
                
                if not self.dry_run:
                    print("\nCommitting changes...")
                    db.session.commit()
                    print("Changes committed successfully!")
                else:
                    print("\nDry run - rolling back changes...")
                    db.session.rollback()
                    print("Changes rolled back.")
                
        except Exception as e:
            print(f"\nMigration failed: {e}")
            db.session.rollback()
            self.report['errors'].append(str(e))
            raise
        
        finally:
            self.report['end_time'] = datetime.now()
            self.generate_report()
    
    def migrate_reference_data(self):
        """Migrate all 9 reference tables (73 records)"""
        print("\n--- Migrating Reference Data ---")
        
        for access_table, config in REFERENCE_MAPPINGS.items():
            print(f"\nMigrating {access_table}...")
            count = self.migrate_table(access_table, config)
            print(f"  Migrated {count} records")
    
    def migrate_master_data(self):
        """Migrate 3 master tables (729 records)"""
        print("\n--- Migrating Master Data ---")
        
        for access_table, config in MASTER_MAPPINGS.items():
            print(f"\nMigrating {access_table}...")
            count = self.migrate_table(access_table, config)
            print(f"  Migrated {count} records")
    
    def migrate_test_catalogs(self):
        """Migrate 2 test catalog tables (172 records)"""
        print("\n--- Migrating Test Catalogs ---")
        
        for access_table, config in TEST_MAPPINGS.items():
            print(f"\nMigrating {access_table}...")
            count = self.migrate_table(access_table, config)
            print(f"  Migrated {count} records")
    
    def migrate_table(self, access_table, config):
        """Migrate a single table"""
        # Extract from Access
        rows = self.access_db.get_table(access_table)
        
        # Get model class
        model_class = globals()[config['model']]
        
        migrated_count = 0
        for row in rows:
            # Transform data
            data = {}
            for access_col, (pg_col, transform) in config['fields'].items():
                value = row.get(access_col)
                if value is not None:
                    value = transform(value)
                data[pg_col] = value
            
            # Check if exists
            existing = model_class.query.get(data.get('id'))
            if existing:
                continue
            
            # Create instance
            instance = model_class(**data)
            db.session.add(instance)
            migrated_count += 1
            
            if self.dry_run:
                db.session.flush()  # Get ID without committing
            
        self.report['tables'][config['table']] = {
            'source_count': len(rows),
            'migrated_count': migrated_count
        }
        
        return migrated_count
    
    def generate_report(self):
        """Generate migration report"""
        print("\n" + "=" * 60)
        print("Migration Report")
        print("=" * 60)
        
        duration = self.report['end_time'] - self.report['start_time']
        print(f"Duration: {duration}")
        print(f"\nTable Summary:")
        print(f"{'Table':<30} {'Source':<10} {'Migrated':<10}")
        print("-" * 50)
        
        total_source = 0
        total_migrated = 0
        
        for table, stats in self.report['tables'].items():
            print(f"{table:<30} {stats['source_count']:<10} {stats['migrated_count']:<10}")
            total_source += stats['source_count']
            total_migrated += stats['migrated_count']
        
        print("-" * 50)
        print(f"{'TOTAL':<30} {total_source:<10} {total_migrated:<10}")
        
        if self.report['errors']:
            print(f"\nErrors ({len(self.report['errors'])}):")
            for error in self.report['errors']:
                print(f"  - {error}")


def main():
    parser = argparse.ArgumentParser(description='Phase 1 Data Migration')
    parser.add_argument('--access-db', required=True, help='Path to RM2026_be.accdb')
    parser.add_argument('--dry-run', action='store_true', help='Validate without loading')
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        migration = Phase1Migration(args.access_db, dry_run=args.dry_run)
        migration.run()


if __name__ == '__main__':
    main()
```

### Validation Script

```python
# scripts/migrations/validate/row_counts.py

"""
Validate that row counts match between Access and PostgreSQL
"""

from app.database.models import (
    Area, Organismo, Provincia, Destino, Rama, Mes, Anno, TipoES, UnidadMedida,
    Cliente, Fabrica, Producto, Ensayo, EnsayoES
)

EXPECTED_COUNTS = {
    # Reference Data (73 total)
    'areas': 4,
    'organismos': 12,
    'provincias': 4,
    'destinos': 7,
    'ramas': 13,
    'meses': 12,
    'annos': 10,
    'tipo_es': 4,
    'unidades_medida': 3,
    
    # Master Data (729 total)
    'clientes': 166,
    'fabricas': 403,
    'productos': 160,
    
    # Test Catalogs (172 total)
    'ensayos': 143,
    'ensayos_es': 29,
}

def validate_row_counts():
    """Check actual row counts against expected"""
    results = []
    all_pass = True
    
    model_map = {
        'areas': Area,
        'organismos': Organismo,
        'provincias': Provincia,
        'destinos': Destino,
        'ramas': Rama,
        'meses': Mes,
        'annos': Anno,
        'tipo_es': TipoES,
        'unidades_medida': UnidadMedida,
        'clientes': Cliente,
        'fabricas': Fabrica,
        'productos': Producto,
        'ensayos': Ensayo,
        'ensayos_es': EnsayoES,
    }
    
    print("Row Count Validation")
    print("=" * 50)
    print(f"{'Table':<25} {'Expected':<10} {'Actual':<10} {'Status'}")
    print("-" * 50)
    
    for table, expected in EXPECTED_COUNTS.items():
        model = model_map[table]
        actual = model.query.count()
        status = "✓" if actual == expected else "✗"
        
        if actual != expected:
            all_pass = False
        
        print(f"{table:<25} {expected:<10} {actual:<10} {status}")
        results.append({
            'table': table,
            'expected': expected,
            'actual': actual,
            'match': actual == expected
        })
    
    print("-" * 50)
    total_expected = sum(EXPECTED_COUNTS.values())
    total_actual = sum(r['actual'] for r in results)
    print(f"{'TOTAL':<25} {total_expected:<10} {total_actual:<10}")
    
    return all_pass, results


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    
    with app.app_context():
        passed, results = validate_row_counts()
        sys.exit(0 if passed else 1)
```

---

## Dependencies

**Blocked by:**
- Issue #4: [Phase 1] Database Migration Scripts (need schema in place)
- Issue #7: [Phase 1] CRUD API for Reference Data (can verify via API/UI)

**Blocks:**
- Phase 2: Core Entities & CRUD (needs master data available)
- User acceptance testing (needs real data)

---

## Related Documentation

- `plans/MIGRATION_PLAN.md` Phase 1.2: Data Migration
- `docs/ACCESS_MIGRATION_ANALYSIS.md`: Source schema details
- `docs/PRD.md` Section 6.2: Data Migration Mapping

---

## Execution Plan

1. **Pre-flight checks** (30 min)
   - Verify Access files accessible
   - Verify PostgreSQL running
   - Create backup

2. **Dry run** (30 min)
   - Run with `--dry-run` flag
   - Review validation results
   - Fix any issues

3. **Production migration** (1 hour)
   - Run full migration
   - Monitor progress
   - Validate results

4. **Verification** (30 min)
   - Run validation scripts
   - Test via web UI
   - Spot-check random records

5. **Documentation** (30 min)
   - Generate migration report
   - Document any issues
   - Update runbook

---

## Rollback Plan

If migration fails:

1. Stop migration script
2. Rollback database to pre-migration backup
3. Investigate issue
4. Fix and retry

---

## Definition of Done

- [ ] All 974 records migrated successfully
- [ ] Row count validation passing (100% match)
- [ ] Foreign key integrity checks passing
- [ ] Data sampling validation complete
- [ ] Migration report generated
- [ ] Data visible in web UI
- [ ] Team notified of completion
- [ ] Phase 1 marked complete
