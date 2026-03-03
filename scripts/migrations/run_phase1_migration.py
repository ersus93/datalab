#!/usr/bin/env python3
"""Script maestro para migración Phase 1."""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Phase 1 Data Migration')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin commit')
    parser.add_argument('--category', choices=['reference', 'master', 'test', 'all'],
                       default='all', help='Categoría a migrar')
    args = parser.parse_args()

    if args.dry_run:
        logger.info("MODO DRY-RUN: No se realizarán cambios")

    # Ejecutar migraciones
    if args.category in ['reference', 'all']:
        logger.info("Migrando datos de referencia...")
        from scripts.migrations.migrate_reference_data import migrate_reference_data
        migrate_reference_data(dry_run=args.dry_run)

    if args.category in ['master', 'all']:
        logger.info("Migrando datos maestros...")
        from scripts.migrations.migrate_master_data import migrate_master_data
        migrate_master_data(dry_run=args.dry_run)

    if args.category in ['test', 'all']:
        logger.info("Migrando catálogo de ensayos...")
        from scripts.migrations.migrate_test_catalogs import migrate_test_catalogs
        migrate_test_catalogs(dry_run=args.dry_run)

    logger.info("Migración completada")


if __name__ == '__main__':
    main()
