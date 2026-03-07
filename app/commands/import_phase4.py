"""Comandos CLI para importación Phase 4.

Subcomandos:
  flask import-phase4 all      — Importar todos los datos (Detalles Ensayos, Utilizado R)
  flask import-phase4 validate — Validar CSV sin tocar la BD (pre-import report)
  flask import-phase4 verify   — Verificar post-importación (conteos + FK + consistencia)
"""
import json
from pathlib import Path

import click
from flask.cli import with_appcontext

from app.services.phase4_import_service import Phase4ImportService


@click.group(name='import-phase4')
def import_phase4_cli():
    """Importar y verificar datos de Ensayos y Utilizado Phase 4 desde Access."""
    pass


# ---------------------------------------------------------------------------
# Subcomando: all
# ---------------------------------------------------------------------------

@import_phase4_cli.command()
@click.option('--data-dir', required=True,
              help='Directorio con archivos CSV (detalles_ensayos.csv, utilizado_r.csv)')
@click.option('--dry-run', is_flag=True,
              help='Simular importación sin modificar la base de datos')
@click.option('--report-dir', default=None,
              help='Directorio donde guardar el reporte Markdown (por defecto: --data-dir)')
@click.option('--verbose', '-v', is_flag=True, help='Salida detallada (DEBUG)')
@with_appcontext
def all(data_dir, dry_run, report_dir, verbose):
    """Importar todos los datos Phase 4 (Detalles de Ensayos → Utilizado R)."""
    import logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    report_dir = report_dir or data_dir

    service = Phase4ImportService(dry_run=dry_run)

    if dry_run:
        click.echo(click.style('\n⚠️  MODO DRY-RUN — No se realizarán cambios en la BD\n', fg='yellow'))

    click.echo('Iniciando importación Phase 4...')
    with click.progressbar(length=2, label='Progreso') as bar:
        result = service.import_all(data_dir)
        bar.update(2)

    r = result

    # Mostrar resumen
    click.echo('\n' + '=' * 62)
    click.echo('  RESUMEN DE IMPORTACIÓN PHASE 4')
    click.echo('=' * 62)

    if dry_run:
        click.echo(click.style('  MODO DRY-RUN: ningún cambio fue guardado\n', fg='yellow'))

    rows = [
        ('Detalles de Ensayos', r.detalles_ensayos, 563),
        ('Utilizado R',         r.utilizados,       632),
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

    click.echo(f'\n  Advertencias de Utilizado: {click.style(str(len(r.utilizado_warnings)), fg="yellow" if r.utilizado_warnings else "green")}')
    click.echo(f'\n  Tiempo total: {r.duration_seconds:.2f}s')
    click.echo('=' * 62)

    # Guardar reporte Markdown
    report_path = str(Path(report_dir) / 'phase4_import_report.md')
    service.generate_report(output_path=report_path)
    click.echo(f'\n✅ Reporte Markdown guardado: {report_path}')

    # Guardar también JSON para automatizaciones
    json_path = str(Path(report_dir) / 'phase4_import_report.json')
    Path(json_path).write_text(
        json.dumps(r.to_dict(), indent=2, default=str), encoding='utf-8'
    )
    click.echo(f'✅ Reporte JSON guardado:     {json_path}')

    # Mostrar primeros errores
    total_errors = r.total_errors
    if total_errors > 0:
        click.echo(click.style(f'\n⚠️  {total_errors} error(es) encontrado(s):', fg='red', bold=True))
        for section_name in ('detalles_ensayos', 'utilizados'):
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

@import_phase4_cli.command()
@click.option('--data-dir', required=True,
              help='Directorio con archivos CSV a validar')
@click.option('--report-dir', default=None,
              help='Directorio donde guardar el reporte (por defecto: --data-dir)')
@click.option('--strict', is_flag=True,
              help='Salir con código de error si hay problemas bloqueantes')
@with_appcontext
def validate(data_dir, report_dir, strict):
    """
    Validar CSV de Phase 4 SIN modificar la base de datos.

    Genera un reporte de:
    - Referencias FK faltantes (entradas, ensayos)
    - Registros omitidos de utilizados
    - Errores de archivos

    Úsalo ANTES de import-phase4 all para detectar problemas.
    """
    report_dir = report_dir or data_dir

    click.echo('\nValidando datos Phase 4 (sin cambios en BD)...')
    service = Phase4ImportService(dry_run=True)
    report = service.validate_all(data_dir)

    # Mostrar resumen en consola
    click.echo('\n' + '=' * 62)
    click.echo('  REPORTE DE VALIDACIÓN PRE-IMPORTACIÓN — PHASE 4')
    click.echo('=' * 62)

    status_color = 'green' if report.is_clean else 'red'
    status_text  = '✅ LIMPIO — Listo para importar' if report.is_clean else '❌ PROBLEMAS ENCONTRADOS'
    click.echo(f'\n  Estado: {click.style(status_text, fg=status_color, bold=True)}')

    sections = [
        ('❌ Missing Entradas (FK)',    report.missing_entradas,      'red'),
        ('❌ Missing Ensayos (FK)',     report.missing_ensayos,       'red'),
        ('⚠️  Utilizados omitidos (sin entrada)', report.skipped_utilizados, 'yellow'),
        ('🔥 Errores de archivo',       [{'e': e} for e in report.file_errors], 'red'),
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
    report_path = str(Path(report_dir) / 'phase4_pre_import_validation.md')
    Path(report_path).write_text(report.to_markdown(), encoding='utf-8')
    click.echo(f'\n✅ Reporte guardado: {report_path}')
    click.echo('=' * 62)

    if strict and not report.is_clean:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Subcomando: verify
# ---------------------------------------------------------------------------

@import_phase4_cli.command()
@click.option('--report-dir', default='.',
              help='Directorio donde guardar el reporte de verificación')
@click.option('--strict', is_flag=True,
              help='Salir con código de error si algún chequeo falla')
@with_appcontext
def verify(report_dir, strict):
    """
    Verificación post-importación.

    Ejecuta después de import-phase4 all para confirmar:
    - Conteos de registros vs. esperados (563 Detalles, 632 Utilizados)
    - Integridad referencial (sin registros huérfanos)
    - Consistencia de datos
    """
    click.echo('\nVerificando datos importados en BD...')
    service = Phase4ImportService()
    verification = service.verify_post_import()

    click.echo('\n' + '=' * 62)
    click.echo('  VERIFICACIÓN POST-IMPORTACIÓN — PHASE 4')
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
    report_path = str(Path(report_dir) / 'phase4_post_import_verification.md')
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
    app.cli.add_command(import_phase4_cli)
