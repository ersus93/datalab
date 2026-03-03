#!/usr/bin/env python3
"""Script maestro para migración Phase 1 con importación real desde Access."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Phase 1 Data Migration from Access')
    parser.add_argument('--access-db', required=True, help='Path to Access .accdb file')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without committing')
    parser.add_argument('--category', choices=['reference', 'master', 'test', 'all'],
                       default='all')
    args = parser.parse_args()

    if not os.path.exists(args.access_db):
        logger.error(f"Archivo Access no encontrado: {args.access_db}")
        sys.exit(1)

    from app import create_app
    from app.services.access_importer import AccessImporter

    app = create_app()

    with app.app_context():
        importer = AccessImporter(args.access_db, dry_run=args.dry_run)

        try:
            start_time = datetime.now()

            if args.category in ['reference', 'all']:
                logger.info("=== Importando datos de referencia ===")
                result = importer.import_reference_data()
                logger.info(f"Estadísticas referencia: {result['total']}")

            if args.category in ['master', 'all']:
                logger.info("=== Importando datos maestros ===")
                result = importer.import_master_data()
                logger.info(f"Estadísticas maestros: {result['total']}")

            if args.category in ['test', 'all']:
                logger.info("=== Importando catálogos de ensayos ===")
                result = importer.import_test_catalogs()
                logger.info(f"Estadísticas ensayos: {result['total']}")

            if not args.dry_run and args.category == 'all':
                logger.info("=== Validando integridad referencial ===")
                if importer.validate_references():
                    logger.info("✓ Validación exitosa")
                else:
                    logger.warning("⚠ Se encontraron inconsistencias referenciales")

            elapsed = (datetime.now() - start_time).total_seconds()
            stats = importer.get_stats()

            logger.info("=" * 50)
            logger.info("RESUMEN DE MIGRACIÓN")
            logger.info("=" * 50)
            logger.info(f"Tiempo transcurrido: {elapsed:.2f}s")
            logger.info(f"Insertados: {stats['inserted']}")
            logger.info(f"Actualizados: {stats['updated']}")
            logger.info(f"Omitidos: {stats['skipped']}")
            logger.info(f"Errores: {stats['errors']}")
            logger.info("=" * 50)

            if args.dry_run:
                logger.info("[DRY-RUN] No se realizaron cambios en la base de datos")
            else:
                logger.info("Migración completada exitosamente")

        except Exception as e:
            logger.error(f"Error en migración: {e}")
            if not args.dry_run:
                logger.error("Ejecutando rollback...")
            raise
        finally:
            importer.close()


if __name__ == '__main__':
    main()
