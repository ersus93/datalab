# [Phase 1] Database Migration Scripts

**Labels:** `phase-1`, `database`, `alembic`, `migration`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days
**Depends on:** 
- Issue #1 ([Phase 1] Create Reference Data Models)
- Issue #2 ([Phase 1] Create Master Data Models)
- Issue #3 ([Phase 1] Create Test Catalog Models)

---

## Description

Create comprehensive database migration infrastructure using Alembic (Flask-Migrate) to manage the PostgreSQL schema. This includes:

1. **Schema Migration Scripts**: Auto-generated and hand-tuned Alembic migrations for all new models
2. **Data Migration Scripts**: Custom Python scripts to extract, transform, and load data from Access to PostgreSQL
3. **Rollback Procedures**: Documented steps and scripts to revert migrations if needed
4. **Migration Commands**: Documented CLI commands for development and production use

This is a **critical infrastructure task** - all database changes for Phase 1 must be managed through migrations.

### Migration Scope

| Category | Tables | Records | Priority |
|----------|--------|---------|----------|
| Reference Data | 9 | 73 | High |
| Master Data | 3 | 729 | High |
| Test Catalogs | 3 | 172 | High |
| **Total Phase 1** | **15** | **974** | **Critical** |

---

## Acceptance Criteria

### Alembic Schema Migrations

#### Initial Migration Setup
- [ ] Verify Flask-Migrate is properly configured in `app/__init__.py`
- [ ] Ensure `migrations/` directory exists and is tracked in git
- [ ] Verify `alembic.ini` configuration for PostgreSQL
- [ ] Document initial migration baseline

#### Schema Migration Generation
- [ ] Generate migration for all 9 reference tables (Issue #1)
  - [ ] Verify all CREATE TABLE statements present
  - [ ] Verify foreign key constraints defined
  - [ ] Verify indexes created
- [ ] Generate migration for 3 master data tables (Issue #2)
  - [ ] Verify Cliente model changes captured
  - [ ] Verify Fabrica CREATE TABLE
  - [ ] Verify Producto CREATE TABLE
- [ ] Generate migration for test catalog tables (Issue #3)
  - [ ] Verify Ensayo CREATE TABLE
  - [ ] Verify EnsayoES CREATE TABLE
  - [ ] Verify linking table CREATE TABLE

#### Migration Quality Checks
- [ ] Review auto-generated migrations for correctness
- [ ] Add hand-tuned optimizations if needed
- [ ] Ensure migration files have descriptive comments
- [ ] Verify migrations are reversible (downgrade functions)

### Data Migration Scripts

#### Script Infrastructure
- [ ] Create `scripts/migrations/` directory structure
- [ ] Create `config.py` for migration settings (Access DB path, PostgreSQL credentials)
- [ ] Set up logging for migration operations
- [ ] Create dry-run capability

#### Reference Data Migration (73 records)
- [ ] Create `migrate_reference_data.py` script
- [ ] Implement data extraction from Access (pyodbc or mdb-export)
- [ ] Implement field mapping from Access types to PostgreSQL
- [ ] Add validation: row count verification
- [ ] Add FK integrity checks
- [ ] Generate migration report (inserted/updated/failed)

#### Master Data Migration (729 records)
- [ ] Create `migrate_master_data.py` script
- [ ] Implement Clientes migration (166 records)
  - [ ] Map Access `IdOrg` to PostgreSQL `organismo_id`
  - [ ] Handle `CliActivo` to `activo` boolean conversion
- [ ] Implement Fabricas migration (403 records)
  - [ ] Map Access `IdCli` to `cliente_id`
  - [ ] Map Access `IdProv` to `provincia_id`
  - [ ] Handle duplicate factory name validation
- [ ] Implement Productos migration (160 records)
  - [ ] Map Access `IdDest` to `destino_id`
- [ ] Add referential integrity validation

#### Test Catalog Migration (172 records)
- [ ] Create `migrate_test_catalogs.py` script
- [ ] Implement Ensayos migration (143 records)
  - [ ] Map Access `Precio` (CURRENCY) to PostgreSQL DECIMAL
  - [ ] Map Access `Activo` (BIT) to PostgreSQL BOOLEAN
- [ ] Implement EnsayosES migration (29 records)
  - [ ] Map Access `IdTipoES` to `tipo_es_id`
- [ ] Add price validation (ensure non-negative)

#### Migration Orchestration
- [ ] Create `run_phase1_migration.py` master script
- [ ] Implement execution order: Reference → Master → Test Catalogs
- [ ] Add transaction wrapping (all or nothing per category)
- [ ] Generate comprehensive migration report

### Rollback Procedures

#### Schema Rollback
- [ ] Document `flask db downgrade` commands for each migration
- [ ] Create `rollback_phase1.sh` script
- [ ] Test downgrade path on development database
- [ ] Document downgrade risks and data loss potential

#### Data Rollback
- [ ] Create backup script before any data migration
- [ ] Document PostgreSQL pg_dump procedures
- [ ] Create restore script from backup
- [ ] Test restore process on development

### Migration Commands Documentation

#### Development Commands
- [ ] Document `flask db init` (one-time setup)
- [ ] Document `flask db migrate -m "message"`
- [ ] Document `flask db upgrade`
- [ ] Document `flask db downgrade`
- [ ] Document `flask db current` (show current revision)
- [ ] Document `flask db history` (show revision history)

#### Production Commands
- [ ] Document production migration checklist
- [ ] Document backup verification steps
- [ ] Document rollback triggers and procedures
- [ ] Document post-migration validation

---

## Technical Notes

### Alembic Configuration

```python
# app/__init__.py - Ensure Flask-Migrate is set up

from flask_migrate import Migrate

migrate = Migrate()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)  # This enables flask db commands
    
    return app
```

### Migration File Structure

```
migrations/
├── alembic.ini
├── env.py
├── README
├── script.py.mako
└── versions/
    ├── 001_create_reference_tables.py      # Issue #1
    ├── 002_create_master_data_tables.py    # Issue #2
    ├── 003_create_test_catalog_tables.py   # Issue #3
    └── 004_add_master_data_indexes.py      # Performance optimization
```

### Sample Migration Script

```python
# migrations/versions/001_create_reference_tables.py

"""Create reference data tables

Revision ID: 001
Revises: 
Create Date: 2026-03-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Create areas table
    op.create_table('areas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('sigla', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sigla')
    )
    op.create_index('ix_areas_sigla', 'areas', ['sigla'], unique=False)
    
    # Create organismos table
    op.create_table('organismos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )
    
    # ... (other reference tables)
    
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_areas_sigla', table_name='areas')
    op.drop_table('areas')
    # ... (reverse order)
    # ### end Alembic commands ###
```

### Data Migration Script Structure

```python
# scripts/migrations/migrate_reference_data.py

"""
Migrate reference data from Access to PostgreSQL
Phase 1: 9 reference tables, 73 records total
"""

import os
import logging
from pathlib import Path
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from app import create_app, db
from app.database.models import (
    Area, Organismo, Provincia, Destino, 
    Rama, Mes, Anno, TipoES, UnidadMedida
)

# Configuration
ACCESS_DB_PATH = os.getenv('ACCESS_DB_PATH', 'data/RM2026_be.accdb')
PG_CONNECTION = os.getenv('DATABASE_URL', 'postgresql://localhost/datalab')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Table mapping: Access table -> Model -> ID mapping
TABLE_MAPPING = {
    'Areas': {
        'model': Area,
        'fields': {
            'IdArea': 'id',
            'Area': 'nombre',
            'Sigla': 'sigla'
        }
    },
    'Organismos': {
        'model': Organismo,
        'fields': {
            'IdOrg': 'id',
            'Organismo': 'nombre'
        }
    },
    # ... other mappings
}

def extract_from_access(table_name):
    """Extract data from Access table using pyodbc"""
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + ACCESS_DB_PATH + ';'
    )
    conn = pyodbc.connect(conn_str)
    query = f"SELECT * FROM [{table_name}]"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def transform_data(df, field_mapping):
    """Transform Access data to match PostgreSQL schema"""
    # Rename columns
    df = df.rename(columns=field_mapping)
    
    # Type conversions
    if 'activo' in df.columns:
        df['activo'] = df['activo'].map({-1: True, 0: False})
    
    return df

def load_to_postgres(df, model_class):
    """Load DataFrame to PostgreSQL using SQLAlchemy"""
    records = df.to_dict('records')
    
    for record in records:
        # Check if exists
        existing = model_class.query.get(record.get('id'))
        if existing:
            logger.info(f"Skipping existing {model_class.__name__} ID {record['id']}")
            continue
        
        # Create new instance
        instance = model_class(**record)
        db.session.add(instance)
    
    db.session.commit()
    logger.info(f"Inserted {len(records)} {model_class.__name__} records")

def migrate_table(access_table_name, config):
    """Migrate a single table"""
    logger.info(f"Migrating {access_table_name}...")
    
    # Extract
    df = extract_from_access(access_table_name)
    logger.info(f"  Extracted {len(df)} rows from Access")
    
    # Transform
    df = transform_data(df, config['fields'])
    
    # Load
    load_to_postgres(df, config['model'])

def run_migration(dry_run=False):
    """Run full reference data migration"""
    app = create_app()
    
    with app.app_context():
        try:
            for access_table, config in TABLE_MAPPING.items():
                migrate_table(access_table, config)
            
            if dry_run:
                logger.info("Dry run - rolling back")
                db.session.rollback()
            else:
                logger.info("Migration complete")
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Run without committing')
    args = parser.parse_args()
    
    run_migration(dry_run=args.dry_run)
```

### Migration Validation Queries

```sql
-- Row count validation
SELECT 'areas' as table_name, COUNT(*) as count FROM areas
UNION ALL SELECT 'organismos', COUNT(*) FROM organismos
UNION ALL SELECT 'provincias', COUNT(*) FROM provincias
-- ... etc

-- Foreign key integrity check
SELECT 'Orphaned Fabricas' as check_name, COUNT(*) 
FROM fabricas f 
LEFT JOIN clientes c ON f.cliente_id = c.id 
WHERE c.id IS NULL;

-- Orphaned Products
SELECT 'Orphaned Productos' as check_name, COUNT(*) 
FROM productos p 
LEFT JOIN destinos d ON p.destino_id = d.id 
WHERE d.id IS NULL;
```

### Rollback Script

```bash
#!/bin/bash
# scripts/migrations/rollback_phase1.sh

echo "Phase 1 Migration Rollback"
echo "========================="

# Check if user is sure
echo "WARNING: This will delete all Phase 1 data!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled"
    exit 1
fi

# Restore from backup
BACKUP_FILE="backups/pre_phase1_$(date +%Y%m%d_%H%M%S).sql"
echo "Creating backup at $BACKUP_FILE..."
pg_dump $DATABASE_URL > $BACKUP_FILE

# Rollback migrations
echo "Rolling back migrations..."
flask db downgrade 003
flask db downgrade 002
flask db downgrade 001
flask db downgrade base

echo "Rollback complete"
```

---

## Dependencies

**Blocked by:**
- Issue #1: [Phase 1] Create Reference Data Models
- Issue #2: [Phase 1] Create Master Data Models
- Issue #3: [Phase 1] Create Test Catalog Models

**Blocks:**
- Issue #5: [Phase 1] Implement Authentication System (needs database ready)
- Issue #8: [Phase 1] Import Access Data - Reference & Master
- All Phase 2 work (needs schema stable)

---

## Related Documentation

- `plans/MIGRATION_PLAN.md` Phase 1.2: Data Migration - Phase 1
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Section 5: Migration Strategy
- Flask-Migrate documentation: https://flask-migrate.readthedocs.io/
- Alembic documentation: https://alembic.sqlalchemy.org/

---

## Testing Requirements

- [ ] Test migration on clean PostgreSQL database
- [ ] Test migration on database with existing data (upgrade scenario)
- [ ] Test rollback procedures
- [ ] Validate row counts match Access source
- [ ] Validate foreign key integrity
- [ ] Test dry-run mode produces no changes

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data corruption during migration | Critical | Full backup before migration; dry-run option; transaction wrapping |
| Access connection issues | Medium | Test pyodbc setup early; provide alternative CSV export method |
| Migration script bugs | High | Test on development DB first; validate row counts |
| Rollback failure | High | Test rollback procedures; maintain backups |
| Performance issues with 729 records | Low | Batch inserts; progress logging; transactions |

---

## Definition of Done

- [ ] All Alembic migrations created and tested
- [ ] Data migration scripts functional
- [ ] Rollback procedures tested
- [ ] Migration commands documented
- [ ] 974 records can be migrated from Access
- [ ] Row count validation passing
- [ ] FK integrity checks passing
- [ ] Code review completed
- [ ] Development team trained on migration procedures
