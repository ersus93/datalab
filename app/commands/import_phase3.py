"""Comandos CLI para importación Phase 3."""
import click
import json
from flask.cli import with_appcontext
from pathlib import Path

from app.services.phase3_import_service import Phase3ImportService


@click.group(name='import-phase3')
def import_phase3_cli():
    """Importar datos transaccionales Phase 3 desde Access."""
    pass


@import_phase3_cli.command()
@click.option('--data-dir', required=True, help='Directorio con archivos CSV')
@click.option('--dry-run', is_flag=True, help='Simular sin importar')
@click.option('--verbose', '-v', is_flag=True, help='Salida detallada')
@with_appcontext
def all(data_dir, dry_run, verbose):
    """Importar todos los datos Phase 3 (OT, Pedidos, Entradas)."""
    import logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    service = Phase3ImportService(dry_run=dry_run)
    result = service.import_all(data_dir)

    # Mostrar resumen
    click.echo("\n" + "="*60)
    click.echo("RESUMEN DE IMPORTACIÓN PHASE 3")
    click.echo("="*60)

    if dry_run:
        click.echo(click.style("MODO DRY-RUN: No se realizaron cambios", fg='yellow'))

    click.echo(f"\nÓrdenes de Trabajo:")
    click.echo(f"  Total: {result.ordenes_trabajo['total']}")
    click.echo(f"  Importadas: {click.style(str(result.ordenes_trabajo['imported']), fg='green')}")
    click.echo(f"  Omitidas: {result.ordenes_trabajo['skipped']}")
    click.echo(f"  Errores: {click.style(str(len(result.ordenes_trabajo['errors'])), fg='red' if result.ordenes_trabajo['errors'] else 'green')}")

    click.echo(f"\nPedidos:")
    click.echo(f"  Total: {result.pedidos['total']}")
    click.echo(f"  Importados: {click.style(str(result.pedidos['imported']), fg='green')}")
    click.echo(f"  Omitidos: {result.pedidos['skipped']}")
    click.echo(f"  Errores: {click.style(str(len(result.pedidos['errors'])), fg='red' if result.pedidos['errors'] else 'green')}")

    click.echo(f"\nEntradas:")
    click.echo(f"  Total: {result.entradas['total']}")
    click.echo(f"  Importadas: {click.style(str(result.entradas['imported']), fg='green')}")
    click.echo(f"  Omitidas: {result.entradas['skipped']}")
    click.echo(f"  Errores: {click.style(str(len(result.entradas['errors'])), fg='red' if result.entradas['errors'] else 'green')}")

    click.echo(f"\nTiempo total: {result.duration_seconds:.2f} segundos")

    # Guardar reporte
    report_path = Path(data_dir) / 'import_report.json'
    with open(report_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    click.echo(f"\nReporte guardado: {report_path}")

    # Mostrar errores si hay
    total_errors = (
        len(result.ordenes_trabajo['errors']) +
        len(result.pedidos['errors']) +
        len(result.entradas['errors'])
    )

    if total_errors > 0:
        click.echo("\n" + click.style("ERRORES ENCONTRADOS:", fg='red', bold=True))
        for error in result.ordenes_trabajo['errors'][:5]:
            click.echo(f"  OT - Fila {error.row_id}: {error.message}")
        for error in result.pedidos['errors'][:5]:
            click.echo(f"  Pedido - Fila {error.row_id}: {error.message}")
        for error in result.entradas['errors'][:5]:
            click.echo(f"  Entrada - Fila {error.row_id}: {error.message}")

        if total_errors > 15:
            click.echo(f"  ... y {total_errors - 15} errores más")


def init_app(app):
    """Registrar comandos en la app Flask."""
    app.cli.add_command(import_phase3_cli)
