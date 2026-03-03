# Comandos de Migración

## Setup inicial
```bash
flask db init  # Una sola vez
```

## Crear migraciones
```bash
flask db migrate -m "descripción"
```

## Aplicar migraciones
```bash
flask db upgrade
```

## Migrar datos desde Access
```bash
python scripts/migrations/run_phase1_migration.py --dry-run
python scripts/migrations/run_phase1_migration.py
```

## Rollback
```bash
flask db downgrade
```

## Categorías de migración

### Datos de referencia (73 registros aprox)
```bash
python scripts/migrations/run_phase1_migration.py --category reference
```

### Datos maestros (~230 registros)
```bash
python scripts/migrations/run_phase1_migration.py --category master
```

### Catálogo de ensayos (~750 registros)
```bash
python scripts/migrations/run_phase1_migration.py --category test
```

## Variables de entorno requeridas
```bash
export ACCESS_DB_PATH="/path/to/database.accdb"
export DATABASE_URL="postgresql://user:pass@host/dbname"
export LOG_LEVEL=INFO
```
