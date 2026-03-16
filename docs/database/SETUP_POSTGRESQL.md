# Setup PostgreSQL para DataLab

Guía de instalación y configuración de PostgreSQL para el entorno de producción de DataLab.

## Requisitos

- PostgreSQL 14+
- Acceso de administrador al servidor

## Instalación

### Opción 1: Instalación Local

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (con Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**
Descargar instalador desde https://www.postgresql.org/download/windows/

### Opción 2: Docker

```bash
docker run -d \
  --name datalab-postgres \
  -e POSTGRES_DB=datalab \
  -e POSTGRES_USER=datalab_user \
  -e POSTGRES_PASSWORD=<YOUR_SECURE_PASSWORD> \
  -p 5432:5432 \
  postgres:14
```

## Configuración

### 1. Crear Base de Datos y Usuario

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos
CREATE DATABASE datalab;

# Crear usuario
CREATE USER datalab_user WITH PASSWORD '<YOUR_SECURE_PASSWORD>';

# Conceder permisos
GRANT ALL PRIVILEGES ON DATABASE datalab TO datalab_user;

# Salir
\q
```

### 2. Configurar Acceso

Editar `pg_hba.conf` (ubicación varía según OS):

```bash
# Ubuntu/Debian
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Añadir o modificar:
# IPv4 local connections:
host    datalab    datalab_user    127.0.0.1/32    scram-sha-256
```

Reiniciar PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Verificación de Conexión

### 1. Probar conexión con psql

```bash
psql -h localhost -U datalab_user -d datalab
```

### 2. Configurar DataLab

Editar archivo `.env`:

```bash
# Desarrollo (SQLite)
DATABASE_URL=sqlite:///datalab.db

# Producción (PostgreSQL)
DATABASE_URL=postgresql://datalab_user:<YOUR_SECURE_PASSWORD>@localhost:5432/datalab
```

### 3. Verificar desde Flask

```bash
flask shell
>>> from app import create_app
>>> from app.core.infrastructure.database import db
>>> app = create_app('production')
>>> with app.app_context():
...     db.engine.execute('SELECT 1')
```

## Migraciones

Una vez configurado PostgreSQL:

```bash
# Aplicar migraciones existentes
flask db upgrade

# O crear base de datos desde cero
flask db init      # Solo si no existe migrations/
flask db migrate -m "initial migration"
flask db upgrade
```

## Backup y Restore

### Backup

```bash
pg_dump -h localhost -U datalab_user datalab > datalab_backup.sql
```

### Restore

```bash
psql -h localhost -U datalab_user datalab < datalab_backup.sql
```

## Troubleshooting

### Error: "password authentication failed"
- Verificar contraseña en `.env`
- Revisar `pg_hba.conf` tiene método correcto

### Error: "database does not exist"
- Crear base de datos: `CREATE DATABASE datalab;`

### Error: "permission denied"
- Verificar grants: `GRANT ALL PRIVILEGES ON DATABASE datalab TO datalab_user;`

## Referencias

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Alembic](https://alembic.sqlalchemy.org/)
