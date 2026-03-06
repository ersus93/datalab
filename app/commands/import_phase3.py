"""Comandos CLI para importación Phase 3.

Subcomandos:
  flask import-phase3 all      — Importar todos los datos (OT, Pedidos, Entradas)
  flask import-phase3 validate — Validar CSV sin tocar la BD (pre-import report)
  flask import-phase3 verify   — Verificar post-importación (conteos + FK + consistencia)
"""
import json
from pathlib import Path

import click
from flask.cli import with_appcontext

from app.services.phase3_import_service import Phase3ImportService


@click.group(name='import-phase3')
def import_phase3_cli():
    """Importar y verificar datos transaccionales Phase 3 desde Access."""
    pass


# ---------------------------------------------------------------------------
# Subcomando: all
# ---------------------------------------------------------------------------

@import_phase3_cli.command()
@click.option('--data-dir', required=True,
              help='Directorio con archivos CSV (ordenes_trabajo.csv, pedidos.csv, entradas.csv)')
@click.option('--dry-run', is_flag=True,
              help='Simular importación sin modificar la base de datos')
@click.option('--report-dir', default=None,
              help='Directorio donde guardar el reporte Markdown (por defecto: --data-dir)')
@click.option('--verbose', '-v', is_flag=True, help='Salida detallada (DEBUG)')
@with_appcontext
def all(data_dir, dry_run, report_dir, verbose):
    """Importar todos los datos Phase 3 (OT → Pedidos → Entradas)."""
    import logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    report_dir = report_dir or data_dir

    service = Phase3ImportService(dry_run=dry_run)

    if dry_run:
        click.echo(click.style('\n⚠️  MODO DRY-RUN — No se realizarán cambios en la BD\n', fg='yellow'))

    click.echo('Iniciando importación Phase 3...')
    with click.progressbar(length=3, label='Progreso') as bar:
        # La importación interna hace las 3 etapas secuencialmente
        result = service.import_all(data_dir)
        bar.update(3)

    r = result

    # Mostrar resumen
    click.echo('\n' + '=' * 62)
    click.echo('  RESUMEN DE IMPORTACIÓN PHASE 3')
    click.echo('=' * 62)

    if dry_run:
        click.echo(click.style('  MODO DRY-RUN: ningún cambio fue guardado\n', fg='yellow'))

    rows = [
        ('Órdenes de Trabajo', r.ordenes_trabajo, 37),
        ('Pedidos',            r.pedidos,          49),
        ('Entradas',           r.entradas,         109),
    ]
    for label, section, expected in rows:
        imp    = section['imported']
        total  = section['total']
        skip   = section['skipped']
        errors = len(section['errors'])
        color  = 'green' if imp == expected else 'yellow' if imp > 0 else 'red'
        click.echo(f'\n  {label}:')
        click.echo(f'    CSV:        {total}')
        click.echo(f'    Importados: {click.style(str(imp), fg=color)} / {expected} esperados')
        click.echo(f'    Omitidos:   {skip}')
        click.echo(f'    Errores:    {click.style(str(errors), fg="red" if errors else "green")}')

    click.echo(f'\n  Advertencias de balance: {click.style(str(len(r.balance_warnings)), fg="yellow" if r.balance_warnings else "green")}')
    click.echo(f'  Advertencias de lote:    {click.style(str(len(r.lot_warnings)),    fg="yellow" if r.lot_warnings    else "green")}')
    click.echo(f'\n  Tiempo total: {r.duration_seconds:.2f}s')
    click.echo('=' * 62)

    # Guardar reporte Markdown
    report_path = str(Path(report_dir) / 'phase3_import_report.md')
    service.generate_report(output_path=report_path)
    click.echo(f'\n✅ Reporte Markdown guardado: {report_path}')

    # Guardar también JSON para automatizaciones
    json_path = str(Path(report_dir) / 'phase3_import_report.json')
    Path(json_path).write_text(
        json.dumps(r.to_dict(), indent=2, default=str), encoding='utf-8'
    )
    click.echo(f'✅ Reporte JSON guardado:     {json_path}')

    # Mostrar primeros errores
    total_errors = r.total_errors
    if total_errors > 0:
        click.echo(click.style(f'\n⚠️  {total_errors} error(es) encontrado(s):', fg='red', bold=True))
        for section_name in ('ordenes_trabajo', 'pedidos', 'entradas'):
            section = getattr(r, section_name)
            for e in section['errors'][:3]:
                msg = e.message if hasattr(e, 'message') else str(e)
                rid = e.row_id if hasattr(e, 'row_id') else '?'
                click.echo(f'  [{section_name}] Fila {rid}: {msg}')
        if total_errors > 9:
            click.echo(f'  ... y {total_errors - 9} error(es) más (ver reporte)')


# ---------------------------------------------------------------------------
# Subcomando: validate
# ---------------------------------------------------------------------------

@import_phase3_cli.command()
@click.option('--data-dir', required=True,
              help='Directorio con archivos CSV a validar')
@click.option('--report-dir', default=None,
              help='Directorio donde guardar el reporte (por defecto: --data-dir)')
@click.option('--strict', is_flag=True,
              help='Salir con código de error si hay problemas bloqueantes')
@with_appcontext
def validate(data_dir, report_dir, strict):
    """
    Validar CSV de Phase 3 SIN modificar la base de datos.

    Genera un reporte de:
    - Referencias FK faltantes (clientes, productos, fábricas)
    - Discrepancias de balance
    - Lotes con formato incorrecto
    - Errores de fechas

    Úsalo ANTES de import-phase3 all para detectar problemas.
    """
    report_dir = report_dir or data_dir

    click.echo('\nValidando datos Phase 3 (sin cambios en BD)...')
    service = Phase3ImportService(dry_run=True)
    report = service.validate_all(data_dir)

    # Mostrar resumen en consola
    click.echo('\n' + '=' * 62)
    click.echo('  REPORTE DE VALIDACIÓN PRE-IMPORTACIÓN — PHASE 3')
    click.echo('=' * 62)

    status_color = 'green' if report.is_clean else 'red'
    status_text  = '✅ LIMPIO — Listo para importar' if report.is_clean else '❌ PROBLEMAS ENCONTRADOS'
    click.echo(f'\n  Estado: {click.style(status_text, fg=status_color, bold=True)}')

    sections = [
        ('❌ Missing Clientes (bloqueante)',    report.missing_clientes,      'red'),
        ('❌ Missing Productos (bloqueante)',    report.missing_productos,     'red'),
        ('❌ Missing Fábricas (bloqueante)',     report.missing_fabricas,      'red'),
        ('⚠️  Missing OT (FK ignorada)',         report.missing_ordenes_trabajo, 'yellow'),
        ('⚠️  Lotes con formato incorrecto',     report.invalid_lots,          'yellow'),
        ('⚠️  Discrepancias de balance',         report.balance_mismatches,    'yellow'),
        ('⚠️  Errores de fecha',                 report.date_errors,           'yellow'),
        ('🔥 Errores de archivo',               [{'e': e} for e in report.file_errors], 'red'),
    ]

    for label, items, color in sections:
        count = len(items)
        if count > 0:
            click.echo(f'\n  {label}: {click.style(str(count), fg=color, bold=True)}')
            for item in items[:5]:
                click.echo(f'    → {item}')
            if count > 5:
                click.echo(f'    ... y {count - 5} más (ver reporte)')

    # Guardar reporte Markdown
    report_path = str(Path(report_dir) / 'phase3_pre_import_validation.md')
    Path(report_path).write_text(report.to_markdown(), encoding='utf-8')
    click.echo(f'\n✅ Reporte guardado: {report_path}')
    click.echo('=' * 62)

    if strict and not report.is_clean:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Subcomando: verify
# ---------------------------------------------------------------------------

@import_phase3_cli.command()
@click.option('--report-dir', default='.',
              help='Directorio donde guardar el reporte de verificación')
@click.option('--strict', is_flag=True,
              help='Salir con código de error si algún chequeo falla')
@with_appcontext
def verify(report_dir, strict):
    """
    Verificación post-importación.

    Ejecuta después de import-phase3 all para confirmar:
    - Conteos de registros vs. esperados (37 OT, 49 Pedidos, 109 Entradas)
    - Integridad referencial (sin registros huérfanos)
    - Consistencia de datos (saldos, flags, cantidades)
    """
    click.echo('\nVerificando datos importados en BD...')
    service = Phase3ImportService()
    verification = service.verify_post_import()

    click.echo('\n' + '=' * 62)
    click.echo('  VERIFICACIÓN POST-IMPORTACIÓN — PHASE 3')
    click.echo('=' * 62)

    status_color = 'green' if verification.all_passed else 'red'
    status_text  = '✅ TODOS LOS CHEQUEOS PASARON' if verification.all_passed else '❌ ALGUNOS CHEQUEOS FALLARON'
    click.echo(f'\n  Estado: {click.style(status_text, fg=status_color, bold=True)}')

    all_checks = [
        ('Conteos de registros', verification.count_checks),
        ('FK Integrity',         verification.fk_checks),
        ('Consistencia',         verification.consistency_checks),
    ]

    for section_title, checks in all_checks:
        click.echo(f'\n  {section_title}:')
        for name, c in checks.items():
            icon  = '✅' if c.get('passed') else '❌'
            color = 'green' if c.get('passed') else 'red'
            line  = f'    {icon} {name}: {c.get("actual")} (esperado: {c.get("expected")})'
            click.echo(click.style(line, fg=color))

    # Guardar reporte
    report_path = str(Path(report_dir) / 'phase3_post_import_verification.md')
    Path(report_path).write_text(verification.to_markdown(), encoding='utf-8')
    click.echo(f'\n✅ Reporte guardado: {report_path}')
    click.echo('=' * 62)

    if strict and not verification.all_passed:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def init_app(app):
    """Registrar comandos en la app Flask."""
    app.cli.add_command(import_phase3_cli)
