"""Migrar datos maestros desde Access a PostgreSQL."""
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Mapping de tablas Access -> Modelos
TABLE_MAPPING = {
    'Clientes': {
        'model': 'Cliente',
        'fields': {
            'IdCliente': 'id',
            'Codigo': 'codigo',
            'Cliente': 'nombre',
            'Correo': 'email',
            'Telefono': 'telefono',
            'Direccion': 'direccion',
            'IdOrg': 'organismo_id',
            'TipoCliente': 'tipo_cliente',
            'Activo': 'activo'
        }
    },
    'Fabricas': {
        'model': 'Fabrica',
        'fields': {
            'IdFabrica': 'id',
            'IdCliente': 'cliente_id',
            'Fabrica': 'nombre',
            'IdProv': 'provincia_id',
            'Activo': 'activo'
        }
    },
    'Productos': {
        'model': 'Producto',
        'fields': {
            'IdProd': 'id',
            'Producto': 'nombre',
            'IdDest': 'destino_id',
            'Activo': 'activo'
        }
    }
}


def migrate_master_data(dry_run=False):
    """Migrar todas las tablas de datos maestros."""
    logger.info(f"Migrando datos maestros... (dry_run={dry_run})")

    results = {}

    # Lógica de migración (placeholders para Access)
    # En producción usar pyodbc para conectar a Access

    # Conteo estimado de registros
    expected_counts = {
        'clientes': 50,    # Aproximado
        'fabricas': 100,   # Aproximado
        'productos': 80,   # Aproximado
    }

    total_expected = sum(expected_counts.values())
    logger.info(f"Total de registros maestros esperados: ~{total_expected}")

    if dry_run:
        logger.info("[DRY-RUN] Simulación completada - no se realizaron cambios")
        return {'status': 'dry_run', 'expected_total': total_expected}

    # TODO: Implementar lógica real de migración con pyodbc

    return {
        'status': 'pending',
        'expected_total': total_expected,
        'tables': list(TABLE_MAPPING.keys())
    }
