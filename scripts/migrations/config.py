"""Configuración para migraciones de datos."""
import os

# Access database path (no incluir ruta real, usar placeholder)
ACCESS_DB_PATH = os.getenv('ACCESS_DB_PATH', '**REDACTED**')

# PostgreSQL connection (placeholder)
DATABASE_URL = os.getenv('DATABASE_URL', '**REDACTED**')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Batch size for inserts
BATCH_SIZE = 100

# Tables to migrate
REFERENCE_TABLES = [
    'areas', 'organismos', 'provincias', 'destinos',
    'ramas', 'meses', 'annos', 'tipos_es', 'unidades_medida'
]

MASTER_TABLES = ['clientes', 'fabricas', 'productos']
TEST_TABLES = ['ensayos', 'ensayos_es', 'ensayos_x_productos']
