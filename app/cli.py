#!/usr/bin/env python3
"""Comandos CLI personalizados para DataLab."""

import subprocess
import click
from flask.cli import with_appcontext

from app import db
from app.database.models import (
    Area,
    Organismo,
    Provincia,
    Destino,
    Rama,
    Mes,
    Anno,
    TipoES,
    UnidadMedida,
)


# Area: 4 registros
AREAS_DATA = [
    {"nombre": "Físico-Químico", "sigla": "FQ"},
    {"nombre": "Microbiología", "sigla": "MB"},
    {"nombre": "Evaluación Sensorial", "sigla": "ES"},
    {"nombre": "Otros Servicios", "sigla": "OS"},
]

# Organismos: 12 registros
ORGANISMOS_DATA = [
    {"nombre": "Ministerio de la Agricultura"},
    {"nombre": "Ministerio de la Industria Alimentaria"},
    {"nombre": "Ministerio de Comercio Interior"},
    {"nombre": "Empresa de Productos Lácteos"},
    {"nombre": "Empresa de Bebidas y Refrescos"},
    {"nombre": "Empresa de Carnes"},
    {"nombre": "Empresa de Conservas Vegetales"},
    {"nombre": "Empresa de Aceites y Grasas"},
    {"nombre": "Empresa de Harinas y Cereales"},
    {"nombre": "Empresa de Confitería"},
    {"nombre": "Empresa de Pescados y Mariscos"},
    {"nombre": "Otros Organismos"},
]

# Provincias: 4 registros
PROVINCIAS_DATA = [
    {"nombre": "Pinar del Río", "sigla": "PR"},
    {"nombre": "Artemisa", "sigla": "AR"},
    {"nombre": "La Habana", "sigla": "LH"},
    {"nombre": "Mayabeque", "sigla": "MQ"},
]

# Destinos: 7 registros
DESTINOS_DATA = [
    {"nombre": "Canasta Familiar", "sigla": "CF"},
    {"nombre": "Amplio Consumo", "sigla": "AC"},
    {"nombre": "Merienda Escolar", "sigla": "ME"},
    {"nombre": "Captación Divisas", "sigla": "CD"},
    {"nombre": "Destinos Especiales", "sigla": "DE"},
    {"nombre": "Turismo", "sigla": "TU"},
    {"nombre": "Exportación", "sigla": "EX"},
]

# Ramas: 13 registros
RAMAS_DATA = [
    {"nombre": "Productos Cárnicos"},
    {"nombre": "Productos Lácteos"},
    {"nombre": "Productos Vegetales"},
    {"nombre": "Bebidas Alcohólicas"},
    {"nombre": "Bebidas No Alcohólicas"},
    {"nombre": "Aceites y Grasas Comestibles"},
    {"nombre": "Productos de Panadería y Pastelería"},
    {"nombre": "Productos de Confitería"},
    {"nombre": "Productos de Molinería"},
    {"nombre": "Conservas Vegetales"},
    {"nombre": "Conservas Cárnicas"},
    {"nombre": "Pescados y Productos del Mar"},
    {"nombre": "Otros Productos Alimenticios"},
]

# Meses: 12 registros
MESES_DATA = [
    {"id": 1, "nombre": "Enero", "sigla": "Ene"},
    {"id": 2, "nombre": "Febrero", "sigla": "Feb"},
    {"id": 3, "nombre": "Marzo", "sigla": "Mar"},
    {"id": 4, "nombre": "Abril", "sigla": "Abr"},
    {"id": 5, "nombre": "Mayo", "sigla": "May"},
    {"id": 6, "nombre": "Junio", "sigla": "Jun"},
    {"id": 7, "nombre": "Julio", "sigla": "Jul"},
    {"id": 8, "nombre": "Agosto", "sigla": "Ago"},
    {"id": 9, "nombre": "Septiembre", "sigla": "Sep"},
    {"id": 10, "nombre": "Octubre", "sigla": "Oct"},
    {"id": 11, "nombre": "Noviembre", "sigla": "Nov"},
    {"id": 12, "nombre": "Diciembre", "sigla": "Dic"},
]

# Años: 10 registros (2020-2029)
ANNOS_DATA = [
    {"anno": "2020", "activo": False},
    {"anno": "2021", "activo": False},
    {"anno": "2022", "activo": False},
    {"anno": "2023", "activo": False},
    {"anno": "2024", "activo": True},
    {"anno": "2025", "activo": True},
    {"anno": "2026", "activo": True},
    {"anno": "2027", "activo": True},
    {"anno": "2028", "activo": True},
    {"anno": "2029", "activo": True},
]

# Tipo ES: 4 registros
TIPO_ES_DATA = [
    {"nombre": "Análisis Visual"},
    {"nombre": "Análisis Olfativo"},
    {"nombre": "Análisis Gustativo"},
    {"nombre": "Análisis Táctil"},
]

# Unidades de Medida: 3 registros
UNIDADES_MEDIDA_DATA = [
    {"codigo": "g", "nombre": "Gramos"},
    {"codigo": "mg/L", "nombre": "Miligramos por Litro"},
    {"codigo": "mL", "nombre": "Mililitros"},
]


def seed_areas():
    """Seed areas table."""
    with db.session.no_autoflush:
        existing = {a.sigla for a in Area.query.all()}
        for data in AREAS_DATA:
            if data["sigla"] not in existing:
                area = Area(**data)
                db.session.add(area)
        db.session.commit()
        return Area.query.count()


def seed_organismos():
    """Seed organismos table."""
    with db.session.no_autoflush:
        existing = {o.nombre for o in Organismo.query.all()}
        for data in ORGANISMOS_DATA:
            if data["nombre"] not in existing:
                org = Organismo(**data)
                db.session.add(org)
        db.session.commit()
        return Organismo.query.count()


def seed_provincias():
    """Seed provincias table."""
    with db.session.no_autoflush:
        existing = {p.sigla for p in Provincia.query.all()}
        for data in PROVINCIAS_DATA:
            if data["sigla"] not in existing:
                prov = Provincia(**data)
                db.session.add(prov)
        db.session.commit()
        return Provincia.query.count()


def seed_destinos():
    """Seed destinos table."""
    with db.session.no_autoflush:
        existing = {d.sigla for d in Destino.query.all()}
        for data in DESTINOS_DATA:
            if data["sigla"] not in existing:
                dest = Destino(**data)
                db.session.add(dest)
        db.session.commit()
        return Destino.query.count()


def seed_ramas():
    """Seed ramas table."""
    with db.session.no_autoflush:
        existing = {r.nombre for r in Rama.query.all()}
        for data in RAMAS_DATA:
            if data["nombre"] not in existing:
                rama = Rama(**data)
                db.session.add(rama)
        db.session.commit()
        return Rama.query.count()


def seed_meses():
    """Seed meses table."""
    with db.session.no_autoflush:
        existing = {m.id for m in Mes.query.all()}
        for data in MESES_DATA:
            if data["id"] not in existing:
                mes = Mes(**data)
                db.session.add(mes)
        db.session.commit()
        return Mes.query.count()


def seed_annos():
    """Seed annos table."""
    with db.session.no_autoflush:
        existing = {a.anno for a in Anno.query.all()}
        for data in ANNOS_DATA:
            if data["anno"] not in existing:
                anno = Anno(**data)
                db.session.add(anno)
        db.session.commit()
        return Anno.query.count()


def seed_tipo_es():
    """Seed tipo_es table."""
    with db.session.no_autoflush:
        existing = {t.nombre for t in TipoES.query.all()}
        for data in TIPO_ES_DATA:
            if data["nombre"] not in existing:
                tipo = TipoES(**data)
                db.session.add(tipo)
        db.session.commit()
        return TipoES.query.count()


def seed_unidades_medida():
    """Seed unidades_medida table."""
    with db.session.no_autoflush:
        existing = {u.codigo for u in UnidadMedida.query.all()}
        for data in UNIDADES_MEDIDA_DATA:
            if data["codigo"] not in existing:
                um = UnidadMedida(**data)
                db.session.add(um)
        db.session.commit()
        return UnidadMedida.query.count()


@click.command("seed-reference")
@with_appcontext
def seed_reference_command():
    """Seed reference tables with initial data from Access RM2026."""
    click.echo("\n=== Seeding Reference Data ===")
    click.echo("Migrating 73 records from Access RM2026...\n")

    areas = seed_areas()
    click.echo(f"✓ Areas: {areas} registros")

    organismos = seed_organismos()
    click.echo(f"✓ Organismos: {organismos} registros")

    provincias = seed_provincias()
    click.echo(f"✓ Provincias: {provincias} registros")

    destinos = seed_destinos()
    click.echo(f"✓ Destinos: {destinos} registros")

    ramas = seed_ramas()
    click.echo(f"✓ Ramas: {ramas} registros")

    meses = seed_meses()
    click.echo(f"✓ Meses: {meses} registros")

    annos = seed_annos()
    click.echo(f"✓ Años: {annos} registros")

    tipos_es = seed_tipo_es()
    click.echo(f"✓ Tipo ES: {tipos_es} registros")

    unidades = seed_unidades_medida()
    click.echo(f"✓ Unidades de Medida: {unidades} registros")

    total = areas + organismos + provincias + destinos + ramas + meses + annos + tipos_es + unidades

    click.echo("\n=== Reference Data Seeding Complete ===")
    click.echo(f"Total records: {total}/69")

    if total == 69:
        click.echo("✅ All reference data seeded successfully!")
    else:
        click.echo(f"⚠️  Expected 69 records, got {total}")


# ============================================================
# TAILWIND CSS CLI COMMANDS
# ============================================================

@click.command('tailwind:watch')
@with_appcontext
def tailwind_watch():
    """
    Watch and rebuild Tailwind CSS during development.
    
    Runs TailwindCSS CLI in watch mode, automatically rebuilding
    output.css when input files change.
    
    Usage:
        flask tailwind:watch
    
    Opens a separate terminal for this long-running process.
    """
    click.echo('🎨 Starting TailwindCSS watch mode...')
    click.echo('📁 Input: app/static/css/input.css')
    click.echo('📁 Output: app/static/css/output.css')
    click.echo('⚡ Press CTRL+C to stop watching\n')
    
    try:
        subprocess.run(
            [
                '.\\tailwindcss.exe',
                '-i', 'app/static/css/input.css',
                '-o', 'app/static/css/output.css',
                '--watch'
            ],
            shell=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f'❌ Error: {e}', fg='red'))
        raise click.Abort()
    except KeyboardInterrupt:
        click.echo('\n✨ Stopped watching. CSS changes will no longer auto-rebuild.')


@click.command('tailwind:build')
@with_appcontext
def tailwind_build():
    """
    Build Tailwind CSS for production (minified).
    
    Compiles input.css to output.css with full purging and minification.
    Run this before deploying to production.
    
    Usage:
        flask tailwind:build
    """
    click.echo('🏗️  Building TailwindCSS for production...')
    click.echo('📁 Input: app/static/css/input.css')
    click.echo('📁 Output: app/static/css/output.css')
    click.echo('⚡ Minification enabled\n')
    
    try:
        result = subprocess.run(
            [
                '.\\tailwindcss.exe',
                '-i', 'app/static/css/input.css',
                '-o', 'app/static/css/output.css',
                '--minify'
            ],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Show build stats
        import os
        output_path = 'app/static/css/output.css'
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            click.echo(click.style(f'✅ Build complete!', fg='green'))
            click.echo(f'📦 Output size: {size:,} bytes ({size/1024:.1f} KB)')
        
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f'❌ Build failed: {e.stderr}', fg='red'))
        raise click.Abort()


def register_cli_commands(app):
    """Register custom CLI commands."""
    # Tailwind CSS commands
    app.cli.add_command(tailwind_watch)
    app.cli.add_command(tailwind_build)
    
    # Reference data seeding
    app.cli.add_command(seed_reference_command)

    # Phase 1/2 import commands
    from app.commands.import_cli import import_cli
    app.cli.add_command(import_cli)

    # Phase 3 transactional import commands
    from app.commands.import_phase3 import import_phase3_cli
    app.cli.add_command(import_phase3_cli)

    # Phase 4 import commands (Detalles de Ensayos y Utilizado)
    from app.commands.import_phase4 import import_phase4_cli
    app.cli.add_command(import_phase4_cli)
