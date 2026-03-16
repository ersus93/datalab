# Guía de Alembic (Flask-Migrate)

Guía completa para el manejo de migraciones de base de datos con Alembic en DataLab.

## Conceptos Básicos

**Alembic** es la herramienta de migraciones de SQLAlchemy. **Flask-Migrate** es el wrapper que integra Alembic con Flask.

### ¿Qué es una migración?

Una migración es un archivo Python que describe cambios en el esquema de la base de datos (crear tablas, añadir columnas, índices, etc.).

## Comandos Principales

### 1. Inicializar Migraciones (Primera vez)

```bash
flask db init
```

Crea la carpeta `migrations/` con la configuración inicial.

### 2. Crear una Nueva Migración

```bash
flask db migrate -m "descripción del cambio"
```

Ejemplos:
```bash
flask db migrate -m "add reference data models"
flask db migrate -m "add user authentication"
flask db migrate -m "add billing tables"
```

### 3. Aplicar Migraciones

```bash
flask db upgrade
```

Aplica todas las migraciones pendientes.

Para aplicar hasta una versión específica:
```bash
flask db upgrade <revision>
```

### 4. Rollback (Deshacer)

Deshacer última migración:
```bash
flask db downgrade
```

Deshacer N migraciones:
```bash
flask db downgrade -N
```

Deshacer hasta versión específica:
```bash
flask db downgrade <revision>
```

### 5. Ver Historial

```bash
flask db history
```

Muestra todas las migraciones con sus revisiones.

### 6. Versión Actual

```bash
flask db current
```

## Workflow de Desarrollo

### Caso 1: Nuevo Feature con Nuevos Modelos

```bash
# 1. Modificar/agregar modelos SQLAlchemy

# 2. Crear migración
flask db migrate -m "add X feature"

# 3. Revisar archivo generado en migrations/versions/

# 4. Aplicar migración
flask db upgrade

# 5. Verificar en base de datos
```

### Caso 2: Colaboración en Equipo

```bash
# 1. Hacer pull de cambios
git pull origin dev

# 2. Aplicar nuevas migraciones
flask db upgrade

# 3. Continuar desarrollo...
```

### Caso 3: Resolución de Conflictos

Si dos desarrolladores crean migraciones simultáneamente:

```bash
# 1. Mergear código

# 2. Revisar migraciones en migrations/versions/

# 3. Si hay conflictos, mantener ambas migraciones
# Alembic las aplicará en orden cronológico

# 4. Aplicar
flask db upgrade
```

## Estructura de una Migración

```python
"""add reference data models

Revision ID: 001
Revises: 
Create Date: 2026-03-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Comandos para aplicar cambios
    op.create_table(
        'areas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Comandos para revertir cambios
    op.drop_table('areas')
```

## Mejores Prácticas

### 1. Nomenclatura

Usar nombres descriptivos:
- ✅ `"add user authentication"`
- ✅ `"create reference tables"`
- ❌ `"fix"`
- ❌ `"update"`

### 2. Revisar Migraciones Generadas

Antes de aplicar, revisar el archivo generado:
```bash
# Ver archivo antes de upgrade
cat migrations/versions/001_*.py
```

### 3. Migraciones Reversibles

Asegurar que `downgrade()` revierta correctamente:
- Si `upgrade()` crea una tabla, `downgrade()` debe eliminarla
- Si `upgrade()` añade una columna, `downgrade()` debe eliminarla

### 4. Backup Antes de Migraciones en Producción

```bash
# PostgreSQL
pg_dump -h localhost -U <USER> <DB> > backup_pre_migration.sql

# SQLite
cp datalab.db datalab_backup.db
```

### 5. No Modificar Migraciones Aplicadas

Una vez aplicada una migración compartida, no modificarla. Crear una nueva migración para correcciones.

## Troubleshooting

### Error: "Can't locate revision identified by 'abc123'"

La base de datos está en una versión que no existe en el código.

**Solución:**
```bash
# Resetear a base limpia (DESARROLLO)
flask db downgrade base
flask db upgrade

# O manualmente en PostgreSQL:
DROP TABLE alembic_version;
flask db upgrade
```

### Error: "Target database is not up to date"

Hay migraciones pendientes por aplicar.

**Solución:**
```bash
flask db upgrade
```

### Migración Fallida en Producción

1. Hacer backup antes de cualquier migración
2. Probar en staging primero
3. Si falla, usar `flask db downgrade` para revertir
4. Corregir problema y crear nueva migración

## Referencias

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/)
