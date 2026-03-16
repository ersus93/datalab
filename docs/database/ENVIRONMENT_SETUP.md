# Configuración de Entornos

Guía de configuración de variables de entorno para diferentes ambientes de DataLab.

## Variables de Entorno

### Desarrollo (SQLite)

```bash
# .env
FLASK_ENV=development
DATABASE_URL=sqlite:///datalab.db
SECRET_KEY=dev-secret-change-in-production
DEBUG=true
```

### Testing

```bash
# .env.test
FLASK_ENV=testing
DATABASE_URL=sqlite:///:memory:
TESTING=true
WTF_CSRF_ENABLED=false
```

### Producción (PostgreSQL)

```bash
# .env.production
FLASK_ENV=production
DATABASE_URL=postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
SECRET_KEY=<YOUR_SECURE_SECRET_KEY>
DEBUG=false

# PostgreSQL Connection Pooling
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_TIMEOUT=30
```

## Estructura de DATABASE_URL

### PostgreSQL

```
postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>
```

Ejemplos:
```bash
# Local
postgresql://datalab_user:secure_pass@localhost:5432/datalab

# Docker
postgresql://datalab_user:secure_pass@postgres:5432/datalab

# AWS RDS
postgresql://datalab_user:secure_pass@datalab.abc123.us-east-1.rds.amazonaws.com:5432/datalab
```

### SQLite

```
sqlite:///<PATH_TO_FILE>
sqlite:///:memory:  # In-memory
```

Ejemplos:
```bash
# Archivo local
sqlite:///datalab.db

# Ruta absoluta
sqlite:////var/lib/datalab/data.db

# En memoria (testing)
sqlite:///:memory:
```

## Configuración por Ambiente

### Development

Archivo: `.env`

```bash
# Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key

# Database (SQLite por defecto)
DATABASE_URL=sqlite:///datalab_dev.db

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/datalab.log

# Features
DEBUG_TB_ENABLED=true
```

### Production

Archivo: `.env.production` (no commitear)

```bash
# Flask
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=<GENERATE_STRONG_KEY>

# Database (PostgreSQL requerido)
DATABASE_URL=postgresql://<USER>:<PASSWORD>@<HOST>/<DB>

# Connection Pooling
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=1800

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/datalab/app.log
```

### Docker

Archivo: `.env.docker`

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}

# Database
DATABASE_URL=postgresql://datalab_user:${DB_PASSWORD}@postgres:5432/datalab

# Redis (si se usa)
REDIS_URL=redis://redis:6379/0
```

## Generar SECRET_KEY Seguro

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

## Verificación de Configuración

```python
# Verificar variables cargadas
flask shell
>>> from app import create_app
>>> app = create_app()
>>> app.config['SQLALCHEMY_DATABASE_URI']
'postgresql://...'
>>> app.config['SECRET_KEY']
'***'  # Enmascarado
```

## Troubleshooting

### Error: "DATABASE_URL not set"
- Verificar que `.env` existe
- Verificar que `python-dotenv` está instalado
- Reiniciar shell después de cambios

### Error: "could not translate host name"
- Verificar host y puerto en DATABASE_URL
- Verificar que PostgreSQL está corriendo
- Verificar firewall/red

## Referencias

- [Flask Configuration](https://flask.palletsprojects.com/config/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [12-Factor App: Config](https://12factor.net/config)
