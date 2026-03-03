#!/usr/bin/env python3
"""Script simple para importar datos de Access."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app import create_app
from app.services.access_importer import AccessImporter


def main():
    parser = argparse.ArgumentParser(
        description='Importar datos desde Access RM2026 a PostgreSQL'
    )
    parser.add_argument(
        '--access-db',
        required=True,
        help='Ruta al archivo .accdb de Access'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular sin realizar cambios en la base de datos'
    )
    parser.add_argument(
        '--category',
        choices=['reference', 'master', 'test', 'all'],
        default='all',
        help='Categoría de datos a importar'
    )
    args = parser.parse_args()

    if not os.path.exists(args.access_db):
        logger.error(f"Archivo no encontrado: {args.access_db}")
        sys.exit(1)

    app = create_app()

    with app.app_context():
        importer = AccessImporter(args.access_db, dry_run=args.dry_run)

        try:
            if args.category in ['reference', 'all']:
                logger.info("Importando datos de referencia...")
                stats = importer.import_reference_data()
                logger.info(f"Referencia: {stats}")

            if args.category in ['master', 'all']:
                logger.info("Importando datos maestros...")
                stats = importer.import_master_data()
                logger.info(f"Maestros: {stats}")

            if args.category in ['test', 'all']:
                logger.info("Importando catálogos de ensayos...")
                stats = importer.import_test_catalogs()
                logger.info(f"Ensayos: {stats}")

            logger.info("Importación completada")

        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            importer.close()


if __name__ == '__main__':
    main()
