"""Comandos CLI para importación de datos."""
import os
import click
from flask.cli import with_appcontext

from app.services.import_service import MasterDataImportService


@click.group(name='import')
def import_cli():
    """Comandos de importación desde Access."""
    pass


@import_cli.command()
@click.option('--file', required=True, help='Ruta al CSV de clientes')
@click.option('--dry-run', is_flag=True, help='Simular sin insertar')
@click.option('--skip-existing', is_flag=True, default=True, help='Omitir existentes')
@with_appcontext
def clientes(file, dry_run, skip_existing):
    """Importar clientes desde CSV."""
    service = MasterDataImportService(dry_run=dry_run)
    result = service.import_clientes(file, skip_existing=skip_existing)

    click.echo(f"Clientes importados: {result.imported}")
    click.echo(f"Omitidos: {result.skipped}")
    click.echo(f"Errores: {len(result.errors)}")
    click.echo(f"Duración: {result.duration_ms}ms")

    if result.errors:
        click.echo("\nErrores (primeros 10):")
        for error in result.errors[:10]:
            click.echo(f"  Fila {error.row_number}: {error.message}")


@import_cli.command()
@click.option('--file', required=True, help='Ruta al CSV de fábricas')
@click.option('--dry-run', is_flag=True)
@click.option('--skip-existing', is_flag=True, default=True)
@with_appcontext
def fabricas(file, dry_run, skip_existing):
    """Importar fábricas desde CSV."""
    service = MasterDataImportService(dry_run=dry_run)
    result = service.import_fabricas(file, skip_existing=skip_existing)

    click.echo(f"Fábricas importadas: {result.imported}")
    click.echo(f"Omitidas: {result.skipped}")
    click.echo(f"Errores: {len(result.errors)}")


@import_cli.command()
@click.option('--file', required=True, help='Ruta al CSV de productos')
@click.option('--dry-run', is_flag=True)
@click.option('--skip-existing', is_flag=True, default=True)
@with_appcontext
def productos(file, dry_run, skip_existing):
    """Importar productos desde CSV."""
    service = MasterDataImportService(dry_run=dry_run)
    result = service.import_productos(file, skip_existing=skip_existing)

    click.echo(f"Productos importados: {result.imported}")
    click.echo(f"Omitidos: {result.skipped}")
    click.echo(f"Errores: {len(result.errors)}")


@import_cli.command()
@click.option('--data-dir', default='data/migrations', help='Directorio con CSVs')
@click.option('--dry-run', is_flag=True, help='Validar sin insertar')
@click.option('--force', is_flag=True, help='Saltar confirmación')
@with_appcontext
def all(data_dir, dry_run, force):
    """Importar todos los datos maestros."""
    if not force and not dry_run:
        click.confirm('¿Importar todos los datos maestros?', abort=True)

    service = MasterDataImportService(dry_run=dry_run)

    # Importar en orden correcto (clientes primero para FKs)
    click.echo("=== Importando clientes ===")
    result_c = service.import_clientes(os.path.join(data_dir, 'clientes.csv'))
    click.echo(f"✓ {result_c.imported} clientes")

    click.echo("\n=== Importando fábricas ===")
    result_f = service.import_fabricas(os.path.join(data_dir, 'fabricas.csv'))
    click.echo(f"✓ {result_f.imported} fábricas")

    click.echo("\n=== Importando productos ===")
    result_p = service.import_productos(os.path.join(data_dir, 'productos.csv'))
    click.echo(f"✓ {result_p.imported} productos")

    # Validar
    click.echo("\n=== Validando ===")
    validations = service.validate_all()

    # Reporte
    click.echo("\n" + "="*50)
    click.echo("RESUMEN DE IMPORTACIÓN")
    click.echo("="*50)
    total = result_c.imported + result_f.imported + result_p.imported
    click.echo(f"Total importados: {total}/729")

    for table, check in validations.items():
        if table != 'fk_integrity':
            status = "✓" if check['passed'] else "✗"
            click.echo(f"  {status} {table}: {check['actual']}/{check['expected']}")

    # Guardar reporte
    report_path = 'import_report.json'
    with open(report_path, 'w') as f:
        f.write(service.generate_report())
    click.echo(f"\nReporte guardado: {report_path}")


def init_app(app):
    """Registrar comandos en la app Flask."""
    app.cli.add_command(import_cli)
