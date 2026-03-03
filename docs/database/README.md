# Documentación de Base de Datos - DataLab

Esta carpeta contiene toda la documentación relacionada con la base de datos de DataLab.

## Archivos Disponibles

| Archivo | Descripción |
|---------|-------------|
| [SETUP_POSTGRESQL.md](./SETUP_POSTGRESQL.md) | Guía de instalación y configuración de PostgreSQL |
| [ALEMBIC_GUIDE.md](./ALEMBIC_GUIDE.md) | Guía completa de migraciones con Alembic |
| [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) | Configuración de variables de entorno |
| [MIGRATION_STRATEGY.md](./MIGRATION_STRATEGY.md) | Estrategia de versionado y condensación |

## Stack Tecnológico

- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic (Flask-Migrate)
- **Desarrollo**: SQLite
- **Producción**: PostgreSQL 14+

## Quick Start

### Desarrollo (SQLite)

```bash
# Clonar repo
git clone <repo>
cd datalab

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env

# Aplicar migraciones
flask db upgrade

# Ejecutar
flask run
```

### Producción (PostgreSQL)

```bash
# 1. Instalar PostgreSQL
# Ver: SETUP_POSTGRESQL.md

# 2. Crear base de datos y usuario
createdb datalab
createuser datalab_user

# 3. Configurar .env
DATABASE_URL=postgresql://datalab_user:<PASSWORD>@localhost/datalab

# 4. Aplicar migraciones
flask db upgrade

# 5. Ejecutar
flask run
```

## Estructura de Migraciones

```
migrations/
├── versions/              # Migraciones activas
│   ├── 001_initial.py
│   └── ...
├── versions_legacy/       # Migraciones condensadas (historial)
├── alembic.ini           # Configuración Alembic
└── env.py                # Entorno Alembic
```

## Comandos Útiles

```bash
# Crear migración
flask db migrate -m "descripción"

# Aplicar migraciones
flask db upgrade

# Rollback
flask db downgrade

# Ver historial
flask db history

# Ver versión actual
flask db current
```

## Soporte

Para dudas o problemas:
1. Revisar la documentación específica
2. Consultar el issue #13 (Setup PostgreSQL + Alembic)
3. Contactar al equipo de desarrollo
