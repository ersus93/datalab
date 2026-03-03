"""Migrar datos de referencia desde Access a PostgreSQL."""
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Mapping de tablas Access -> Modelos
TABLE_MAPPING = {
    'Areas': {
        'model': 'Area',
        'fields': {'IdArea': 'id', 'Area': 'nombre', 'Sigla': 'sigla'}
    },
    'Organismos': {
        'model': 'Organismo',
        'fields': {'IdOrg': 'id', 'Organismo': 'nombre'}
    },
    'Provincias': {
        'model': 'Provincia',
        'fields': {'IdProv': 'id', 'Provincia': 'nombre', 'Sigla': 'sigla'}
    },
    'Destinos': {
        'model': 'Destino',
        'fields': {'IdDest': 'id', 'Destino': 'nombre', 'Sigla': 'sigla'}
    },
    'Ramas': {
        'model': 'Rama',
        'fields': {'IdRama': 'id', 'Rama': 'nombre'}
    },
    'Meses': {
        'model': 'Mes',
        'fields': {'IdMes': 'id', 'Mes': 'nombre', 'Sigla': 'sigla'}
    },
    'Annos': {
        'model': 'Anno',
        'fields': {'Anno': 'anno', 'Activo': 'activo'}
    },
    'TipoES': {
        'model': 'TipoES',
        'fields': {'IdTipoES': 'id', 'TipoES': 'nombre'}
    },
    'UnidadesMedida': {
        'model': 'UnidadMedida',
        'fields': {'IdUM': 'id', 'Codigo': 'codigo', 'UnidadMedida': 'nombre'}
    }
}


def migrate_reference_data(dry_run=False):
    """Migrar todas las tablas de referencia."""
    results = {}

    # Lógica de migración (placeholders para Access)
    # En producción usar pyodbc para conectar a Access
    # Ejemplo:
    # import pyodbc
    # conn = pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={ACCESS_DB_PATH}')

    logger.info(f"Migrando datos de referencia... (dry_run={dry_run})")

    # Conteo de registros esperados por tabla
    expected_counts = {
        'areas': 4,        # FQ, MB, ES, OS
        'organismos': 5,   # MIPIME, Minal, etc.
        'provincias': 16,  # Provincias de Cuba
        'destinos': 5,     # CF, AC, ME, CD, DE
        'ramas': 8,        # Carne, Lácteos, etc.
        'meses': 12,       # Enero-Diciembre
        'annos': 5,        # Años activos
        'tipos_es': 4,     # Tipos de evaluación sensorial
        'unidades_medida': 14,  # kg, g, mg, ml, l, etc.
    }

    total_expected = sum(expected_counts.values())
    logger.info(f"Total de registros esperados: {total_expected}")

    if dry_run:
        logger.info("[DRY-RUN] Simulación completada - no se realizaron cambios")
        return {'status': 'dry_run', 'expected_total': total_expected}

    # TODO: Implementar lógica real de migración con pyodbc
    # Por ahora retornamos estructura para futura implementación

    return {
        'status': 'pending',
        'expected_total': total_expected,
        'tables': list(TABLE_MAPPING.keys())
    }
