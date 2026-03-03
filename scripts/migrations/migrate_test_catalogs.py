"""Migrar catálogos de ensayos desde Access a PostgreSQL."""
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Mapping de tablas Access -> Modelos
TABLE_MAPPING = {
    'Ensayos': {
        'model': 'Ensayo',
        'fields': {
            'IdEns': 'id',
            'NomOfic': 'nombre_oficial',
            'NomEns': 'nombre_corto',
            'IdArea': 'area_id',
            'Precio': 'precio',
            'UM': 'unidad_medida',
            'Activo': 'activo',
            'EsEnsayo': 'es_ensayo'
        }
    },
    'EnsayosES': {
        'model': 'EnsayoES',
        'fields': {
            'IdEnsES': 'id',
            'NomOfic': 'nombre_oficial',
            'NomEnsES': 'nombre_corto',
            'IdArea': 'area_id',
            'IdTipoES': 'tipo_es_id',
            'Precio': 'precio',
            'UM': 'unidad_medida',
            'Activo': 'activo'
        }
    },
    'EnsayosXProductos': {
        'model': 'EnsayoXProducto',
        'fields': {
            'IdProd': 'producto_id',
            'IdEns': 'ensayo_id'
        }
    }
}


def migrate_test_catalogs(dry_run=False):
    """Migrar catálogos de ensayos."""
    logger.info(f"Migrando catálogos de ensayos... (dry_run={dry_run})")

    results = {}

    # Lógica de migración (placeholders para Access)
    # En producción usar pyodbc para conectar a Access

    # Conteo estimado de registros
    expected_counts = {
        'ensayos': 200,           # Ensayos físico-químicos
        'ensayos_es': 50,         # Ensayos de evaluación sensorial
        'ensayos_x_productos': 500,  # Relaciones many-to-many
    }

    total_expected = sum(expected_counts.values())
    logger.info(f"Total de registros de ensayos esperados: ~{total_expected}")

    if dry_run:
        logger.info("[DRY-RUN] Simulación completada - no se realizaron cambios")
        return {'status': 'dry_run', 'expected_total': total_expected}

    # TODO: Implementar lógica real de migración con pyodbc

    return {
        'status': 'pending',
        'expected_total': total_expected,
        'tables': list(TABLE_MAPPING.keys())
    }
