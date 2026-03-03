# Estrategia de Migraciones

Estrategia de versionado y condensación de migraciones de Alembic para DataLab.

## Principios

1. **Cada feature tiene su migración**: Los cambios de esquema van en migraciones dedicadas
2. **Migraciones reversibles**: Toda migración debe poder hacerse downgrade
3. **Histórico limpio**: Condensar migraciones cada 5 versiones para mantener orden

## Convenciones de Nomenclatura

| Prefijo | Uso | Ejemplo |
|---------|-----|---------|
| `add_` | Añadir tablas/columnas | `add_user_table` |
| `create_` | Crear estructuras nuevas | `create_reference_tables` |
| `update_` | Modificar existentes | `update_client_indexes` |
| `remove_` | Eliminar tablas/columnas | `remove_deprecated_field` |
| `fix_` | Correcciones | `fix_nullable_constraint` |
| `consolidated_v{N}` | Condensación | `consolidated_v1` |

## Estrategia de Condensación

### ¿Por qué condensar?

- Reduce el número de archivos en `migrations/versions/`
- Acelera el setup de nuevos entornos
- Mantiene el historial manejable
- Facilita debugging

### Proceso de Condensación

#### Cuándo condensar

Después de **5 migraciones** acumuladas:

```
001_initial.py
002_add_reference_models.py
003_add_master_data.py
004_add_test_catalogs.py
005_add_transaction_core.py
↓ CONDENSAR ↓
006_consolidated_v1.py
```

#### Cómo condensar

**Opción A: Usar alembic squash (recomendado)**

```bash
# Condensar migraciones 001-005 en una sola
flask db squash 001 005 -m "consolidated_v1"
```

**Opción B: Manual (si squash no está disponible)**

1. **Backup de base de datos**
   ```bash
   pg_dump -h localhost -U <USER> <DB> > backup.sql
   ```

2. **Crear nueva migración con esquema completo**
   ```bash
   # Exportar esquema actual
   pg_dump --schema-only -h localhost -U <USER> <DB> > schema.sql
   
   # Crear migración manual en migrations/versions/006_consolidated_v1.py
   ```

3. **Marcar migraciones antiguas como legacy**
   - Mover `001-005` a `migrations/versions/legacy/`
   - O renombrar con prefijo: `legacy_001_initial.py`

4. **Actualizar down_revision**
   ```python
   # En la nueva migración consolidada
   down_revision = None  # Es la nueva base
   ```

5. **Documentar en CHANGELOG**

### Estructura de Migración Condensada

```python
"""consolidated_v1

Combina migraciones 001-005:
- 001: initial schema (Cliente, Pedido, OrdenTrabajo)
- 002: reference data models (9 tablas)
- 003: master data (Clientes, Fabricas, Productos)
- 004: test catalogs (Ensayos, EnsayosES)
- 005: transaction core (Entradas, Detalles)

Revision ID: 006
Revises: (nada - es nueva base)
Create Date: 2026-03-03 12:00:00

"""

revision = '006'
down_revision = None  # Nueva base
branch_labels = None
depends_on = None

def upgrade():
    # Todo el esquema combinado
    op.create_table('cliente', ...)
    op.create_table('areas', ...)
    # ... etc

def downgrade():
    # Eliminar en orden inverso
    op.drop_table('areas')
    op.drop_table('cliente')
```

## Plan de Migraciones por Fase

### Fase 1: Fundamentos (Issues #4-7)

| # | Migración | Descripción | Issue |
|---|-----------|-------------|-------|
| 001 | `initial.py` | Modelos base existentes | - |
| 002 | `reference_models.py` | 9 tablas de referencia | #4 |
| 003 | `master_data.py` | Clientes, Fábricas, Productos | #5 |
| 004 | `test_catalogs.py` | Ensayos, EnsayosES | #6 |
| 005 | `transaction_core.py` | Entradas, Detalles | #10+ |
| 006 | `consolidated_v1.py` | **CONDENSACIÓN** | - |

### Fase 2: Features Principales (Post-consolidación)

| # | Migración | Descripción |
|---|-----------|-------------|
| 007 | `reporting_models.py` | Informes y reportes |
| 008 | `billing_features.py` | Facturación y uso |
| 009 | `audit_trails.py` | Auditoría de cambios |
| 010 | `user_permissions.py` | RBAC avanzado |
| 011 | `advanced_search.py` | Búsqueda y filtros |
| 012 | `consolidated_v2.py` | **CONDENSACIÓN** |

### Fase 3+: Continuar...

Repetir patrón cada 5 migraciones.

## Entornos Existentes vs Nuevos

### Entornos Nuevos (Post-condensación)

Usan solo la última consolidada:
```bash
flask db upgrade 006  # O simplemente flask db upgrade
```

### Entornos Existentes (Pre-condensación)

Ya tienen migraciones 001-005 aplicadas. Solo aplican la consolidada:
```bash
flask db upgrade 006
```

## Gestión del Directorio migrations/

```
migrations/
├── versions/
│   ├── 006_consolidated_v1.py      # Activa
│   ├── 007_reporting_models.py     # Activa
│   ├── 008_billing_features.py     # Activa
│   └── ...                         # Nuevas
├── versions_legacy/                # Migraciones condensadas
│   ├── 001_initial.py
│   ├── 002_reference_models.py
│   ├── 003_master_data.py
│   ├── 004_test_catalogs.py
│   └── 005_transaction_core.py
└── env.py
```

## Checklist de Condensación

- [ ] Backup de base de datos realizado
- [ ] 5 migraciones acumuladas
- [ ] Nueva migración creada con esquema completo
- [ ] Migraciones antiguas movidas a legacy/
- [ ] down_revision actualizado
- [ ] Test en entorno de desarrollo
- [ ] Documentación actualizada
- [ ] Team notificado

## Referencias

- [Alembic Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/)
