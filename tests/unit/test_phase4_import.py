"""Tests para Phase4ImportService.

Cubre los criterios de aceptación del Issue #6 (Phase 4):
- Importación de Detalles de Ensayos
- Importación de Utilizado con filtro de IDs no coincidentes
- Validación FK pre-importación
- Tracking de utilizado warnings
- Verificación post-importación
- Generación de reporte Markdown
- Soporte dry-run
"""
import csv
from pathlib import Path

import pytest

from app import db
from app.database.models import (
    Cliente, Producto, Fabrica, OrdenTrabajo, Pedido,
    UnidadMedida, Entrada, Ensayo, Area
)
from app.database.models.detalle_ensayo import DetalleEnsayo
from app.database.models.utilizado import Utilizado
from app.services.phase4_import_service import (
    Phase4ImportService,
    Phase4ImportResult,
    PreImportValidationReport,
    PostImportVerification,
)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _seed_test_data(db_session):
    """Puebla datos de referencia mínimos para tests."""
    if not Area.query.first():
        areas = [
            Area(nombre='Físico-Químico', sigla='FQ'),
            Area(nombre='Microbiología', sigla='MB'),
            Area(nombre='Evaluación Sensorial', sigla='ES'),
            Area(nombre='Otros Servicios', sigla='OS'),
        ]
        db_session.add_all(areas)
        db_session.flush()
    return Area


def _get_or_create_organismo(db_session, nombre='Organismo Test'):
    """Obtiene o crea organismo de prueba."""
    from app.database.models.reference import Organismo
    org = Organismo.query.filter_by(nombre=nombre).first()
    if not org:
        org = Organismo(nombre=nombre)
        db_session.add(org)
        db_session.flush()
    return org


def _get_or_create_provincia(db_session, nombre='La Habana Test'):
    """Obtiene o crea provincia de prueba."""
    from app.database.models.reference import Provincia
    prov = Provincia.query.filter_by(nombre=nombre).first()
    if not prov:
        prov = Provincia(nombre=nombre, sigla='LHT')
        db_session.add(prov)
        db_session.flush()
    return prov


def _get_or_create_destino(db_session):
    """Obtiene o crea destino de prueba."""
    from app.database.models.reference import Destino
    dest = Destino.query.filter_by(nombre='Destino Test').first()
    if not dest:
        dest = Destino(nombre='Destino Test', sigla='DT')
        db_session.add(dest)
        db_session.flush()
    return dest


def _get_or_create_rama(db_session):
    """Obtiene o crea rama de prueba."""
    from app.database.models.reference import Rama
    rama = Rama.query.filter_by(nombre='Rama Test').first()
    if not rama:
        rama = Rama(nombre='Rama Test')
        db_session.add(rama)
        db_session.flush()
    return rama


# ---------------------------------------------------------------------------
# Fixtures específicos para Phase 4
# ---------------------------------------------------------------------------

@pytest.fixture
def test_organismo(db_session):
    """Organismo de prueba."""
    return _get_or_create_organismo(db_session)


@pytest.fixture
def test_provincia(db_session):
    """Provincia de prueba."""
    return _get_or_create_provincia(db_session)


@pytest.fixture
def test_destino(db_session):
    """Destino de prueba."""
    return _get_or_create_destino(db_session)


@pytest.fixture
def test_rama(db_session):
    """Rama de prueba."""
    return _get_or_create_rama(db_session)


@pytest.fixture
def test_cliente(db_session, test_organismo):
    """Cliente de prueba."""
    cliente = Cliente.query.filter_by(codigo='CLI-TEST-001').first()
    if not cliente:
        cliente = Cliente(
            codigo='CLI-TEST-001',
            nombre='Cliente de Prueba S.A.',
            organismo_id=test_organismo.id,
            tipo_cliente=1,
            activo=True
        )
        db_session.add(cliente)
        db_session.flush()
    return cliente


@pytest.fixture
def test_producto(db_session, test_destino, test_rama):
    """Producto de prueba."""
    prod = Producto.query.filter_by(nombre='Producto Test').first()
    if not prod:
        prod = Producto(
            nombre='Producto Test',
            destino_id=test_destino.id,
            rama_id=test_rama.id,
            activo=True
        )
        db_session.add(prod)
        db_session.flush()
    return prod


@pytest.fixture
def test_unidad_medida(db_session):
    """Unidad de medida de prueba."""
    um = UnidadMedida.query.filter_by(codigo='KG').first()
    if not um:
        um = UnidadMedida(codigo='KG', nombre='Kilogramo')
        db_session.add(um)
        db_session.flush()
    return um


@pytest.fixture
def test_fabrica(db_session, test_cliente, test_provincia):
    """Fábrica de prueba."""
    fab = Fabrica.query.filter_by(nombre='Fábrica Test').first()
    if not fab:
        fab = Fabrica(
            nombre='Fábrica Test',
            cliente_id=test_cliente.id,
            provincia_id=test_provincia.id,
            activo=True
        )
        db_session.add(fab)
        db_session.flush()
    return fab


@pytest.fixture
def test_orden_trabajo(db_session, test_cliente):
    """Orden de trabajo de prueba."""
    ot = OrdenTrabajo.query.filter_by(nro_ofic='OT-TEST-2026-001').first()
    if not ot:
        ot = OrdenTrabajo(
            nro_ofic='OT-TEST-2026-001',
            codigo='OT-T-001',
            cliente_id=test_cliente.id,
            descripcion='OT de prueba'
        )
        db_session.add(ot)
        db_session.flush()
    return ot


@pytest.fixture
def test_pedido(db_session, test_cliente, test_producto, test_orden_trabajo, test_unidad_medida):
    """Pedido de prueba."""
    pedido = Pedido.query.filter_by(codigo='PED-TEST-001').first()
    if not pedido:
        pedido = Pedido(
            codigo='PED-TEST-001',
            cliente_id=test_cliente.id,
            producto_id=test_producto.id,
            orden_trabajo_id=test_orden_trabajo.id,
            unidad_medida_id=test_unidad_medida.id
        )
        db_session.add(pedido)
        db_session.flush()
    return pedido


@pytest.fixture
def test_entrada(db_session, test_pedido, test_producto, test_fabrica,
                 test_cliente, test_unidad_medida):
    """Entrada de muestra de prueba."""
    entrada = Entrada.query.filter_by(codigo='ENT-TEST-001').first()
    if not entrada:
        entrada = Entrada(
            codigo='ENT-TEST-001',
            lote='A-1234',
            pedido_id=test_pedido.id,
            producto_id=test_producto.id,
            fabrica_id=test_fabrica.id,
            cliente_id=test_cliente.id,
            unidad_medida_id=test_unidad_medida.id,
            cantidad_recib=100,
            cantidad_entreg=0
        )
        db_session.add(entrada)
        db_session.flush()
    return entrada


@pytest.fixture
def test_ensayo_fq(db_session):
    """Ensayo de área FQ de prueba."""
    area_fq = Area.query.filter_by(sigla='FQ').first()
    if not area_fq:
        area_fq = Area(nombre='Físico-Químico', sigla='FQ')
        db_session.add(area_fq)
        db_session.flush()

    ensayo = Ensayo(
        nombre_oficial='Ensayo FQ Test',
        nombre_corto='FQ-Test',
        area_id=area_fq.id,
        precio=10.00,
        activo=True,
        es_ensayo=True
    )
    db_session.add(ensayo)
    db_session.flush()
    return ensayo


# ---------------------------------------------------------------------------
# Helpers para crear CSVs de prueba en tmp
# ---------------------------------------------------------------------------

def write_csv(path: Path, fieldnames: list, rows: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def csv_dir(tmp_path, test_entrada, test_ensayo_fq, db_session):
    """Crea directorio temporal con CSVs válidos de Phase 4."""
    d = tmp_path / 'phase4_data'
    d.mkdir()

    from app.database.models import Area, Ensayo
    area_mb = Area.query.filter_by(sigla='MB').first()
    if not area_mb:
        area_mb = Area(nombre='Microbiología', sigla='MB')
        db_session.add(area_mb)
        db_session.flush()

    ensayo_mb = Ensayo(
        nombre_oficial='Ensayo MB Test',
        nombre_corto='MB-Test',
        area_id=area_mb.id,
        precio=15.00,
        activo=True,
        es_ensayo=True
    )
    db_session.add(ensayo_mb)
    db_session.flush()

    write_csv(d / 'detalles_ensayos.csv',
              ['IdEnt', 'IdEns', 'Cantidad', 'FechReal'],
              [
                  {'IdEnt': test_entrada.id, 'IdEns': test_ensayo_fq.id, 'Cantidad': '1', 'FechReal': ''},
                  {'IdEnt': test_entrada.id, 'IdEns': ensayo_mb.id, 'Cantidad': '2', 'FechReal': ''},
              ])

    write_csv(d / 'utilizado_r.csv',
              ['IdEnt', 'Mes', 'IdUM', 'CantEnt', 'CantCont', 'CantFQ', 'CantMB', 'CantES', 'ValeNo'],
              [
                  {'IdEnt': str(test_entrada.id), 'Mes': '1', 'IdUM': '1', 'CantEnt': '5.0', 'CantCont': '0.0', 'CantFQ': '2.0', 'CantMB': '3.0', 'CantES': '0.0', 'ValeNo': '001'},
                  {'IdEnt': str(test_entrada.id), 'Mes': '2', 'IdUM': '2', 'CantEnt': '3.0', 'CantCont': '1.0', 'CantFQ': '0.0', 'CantMB': '1.0', 'CantES': '1.0', 'ValeNo': '002'},
              ])

    return d


@pytest.fixture
def csv_dir_with_issues(tmp_path, test_entrada, test_ensayo_fq, db_session, app):
    """CSVs con problemas: FK faltante en detalles_ensayos y utilizado_r."""
    d = tmp_path / 'phase4_bad'
    d.mkdir()

    entrada_inexistente = 99999

    write_csv(d / 'detalles_ensayos.csv',
              ['IdEnt', 'IdEns', 'Cantidad', 'FechReal'],
              [
                  {'IdEnt': entrada_inexistente, 'IdEns': test_ensayo_fq.id, 'Cantidad': '1', 'FechReal': ''},
                  {'IdEnt': test_entrada.id, 'IdEns': test_ensayo_fq.id, 'Cantidad': '2', 'FechReal': ''},
              ])

    write_csv(d / 'utilizado_r.csv',
              ['IdEnt', 'Mes', 'IdUM', 'CantEnt', 'CantCont', 'CantFQ', 'CantMB', 'CantES', 'ValeNo'],
              [
                  {'IdEnt': str(entrada_inexistente), 'Mes': '1', 'IdUM': '1', 'CantEnt': '5.0', 'CantCont': '0.0', 'CantFQ': '2.0', 'CantMB': '3.0', 'CantES': '0.0', 'ValeNo': '001'},
                  {'IdEnt': str(test_entrada.id), 'Mes': '2', 'IdUM': '2', 'CantEnt': '3.0', 'CantCont': '1.0', 'CantFQ': '0.0', 'CantMB': '1.0', 'CantES': '1.0', 'ValeNo': '002'},
              ])

    return d


@pytest.fixture
def csv_dir_missing_ensayo(tmp_path, test_entrada, db_session, app):
    """CSV con ensayo inexistente."""
    d = tmp_path / 'phase4_bad_ensayo'
    d.mkdir()

    ensayo_inexistente = 88888

    write_csv(d / 'detalles_ensayos.csv',
              ['IdEnt', 'IdEns', 'Cantidad', 'FechReal'],
              [
                  {'IdEnt': test_entrada.id, 'IdEns': ensayo_inexistente, 'Cantidad': '1', 'FechReal': ''},
              ])

    write_csv(d / 'utilizado_r.csv',
              ['IdEnt', 'Mes', 'IdUM', 'CantEnt', 'CantCont', 'CantFQ', 'CantMB', 'CantES', 'ValeNo'],
              [
                  {'IdEnt': str(test_entrada.id), 'Mes': '1', 'IdUM': '1', 'CantEnt': '5.0', 'CantCont': '0.0', 'CantFQ': '2.0', 'CantMB': '3.0', 'CantES': '0.0', 'ValeNo': '001'},
              ])

    return d


# ---------------------------------------------------------------------------
# Tests: importación correcta
# ---------------------------------------------------------------------------

class TestPhase4ImportService:

    def test_import_detalles_ensayos_basic(self, db_session, app, csv_dir):
        """Importar detalles de ensayos desde CSV válido debe registrar todos los registros."""
        with app.app_context():
            service = Phase4ImportService(dry_run=False)
            result = service.import_all(str(csv_dir))

        assert result.detalles_ensayos['total'] == 2
        assert result.detalles_ensayos['imported'] == 2
        assert result.detalles_ensayos['errors'] == []
        assert result.total_errors == 0

    def test_import_utilizado_r_filters_non_matching(self, db_session, app, csv_dir):
        """Utilizado con IDs de entrada no existentes debe ser filtrado y generar advertencias."""
        d = csv_dir.parent / 'phase4_with_filter'
        d.mkdir()

        from app.database.models import Entrada, Ensayo, Area
        entrada_existente = Entrada.query.first()
        area_fq = Area.query.filter_by(sigla='FQ').first()

        write_csv(d / 'detalles_ensayos.csv',
                  ['IdEnt', 'IdEns', 'Cantidad', 'FechReal'],
                  [{'IdEnt': entrada_existente.id, 'IdEns': '1', 'Cantidad': '1', 'FechReal': ''}])

        write_csv(d / 'utilizado_r.csv',
                  ['IdEnt', 'Mes', 'IdUM', 'CantEnt', 'CantCont', 'CantFQ', 'CantMB', 'CantES', 'ValeNo'],
                  [
                      {'IdEnt': str(entrada_existente.id), 'Mes': '1', 'IdUM': '1', 'CantEnt': '5.0', 'CantCont': '0.0', 'CantFQ': '2.0', 'CantMB': '3.0', 'CantES': '0.0', 'ValeNo': '001'},
                      {'IdEnt': '999', 'Mes': '1', 'IdUM': '1', 'CantEnt': '5.0', 'CantCont': '0.0', 'CantFQ': '2.0', 'CantMB': '3.0', 'CantES': '0.0', 'ValeNo': ''},
                  ])

        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            result = service.import_all(str(d))

        assert result.utilizados['skipped'] >= 1
        assert len(result.utilizado_warnings) >= 1
        warning = result.utilizado_warnings[0]
        assert warning.warning_type == 'no_entry_match'

    def test_validate_all_detects_missing_fks(self, db_session, app, csv_dir_with_issues):
        """Validación debe detectar FKs faltantes en detalles de ensayos."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_with_issues))

        assert len(report.missing_entradas) >= 1

    def test_verify_post_import_counts(self, db_session, app, csv_dir):
        """Verificación post-import debe devolver conteos estructurados."""
        with app.app_context():
            service = Phase4ImportService()
            v = service.verify_post_import()

        assert isinstance(v, PostImportVerification)
        assert 'Detalles de Ensayos' in v.count_checks
        assert 'Utilizados' in v.count_checks
        assert 'Detalles → Entradas' in v.fk_checks
        assert 'Detalles → Ensayos' in v.fk_checks
        assert 'Utilizados → Entradas' in v.fk_checks
        assert 'Utilizados → Ensayos' in v.fk_checks

    def test_generate_report_markdown(self, db_session, app, csv_dir):
        """generate_report debe devolver Markdown con secciones clave."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            service.import_all(str(csv_dir))
            md = service.generate_report()

        assert '# Reporte de Importación Phase 4' in md
        assert 'Resumen' in md
        assert 'Errores' in md
        assert 'Verificación de Conteos' in md

    def test_dry_run_no_changes(self, db_session, app, csv_dir):
        """Dry-run no debe modificar la base de datos."""
        from app.database.models import DetalleEnsayo, Utilizado
        with app.app_context():
            before_detalles = DetalleEnsayo.query.count()
            before_utilizados = Utilizado.query.count()

            service = Phase4ImportService(dry_run=True)
            service.import_all(str(csv_dir))

            after_detalles = DetalleEnsayo.query.count()
            after_utilizados = Utilizado.query.count()

        assert before_detalles == after_detalles, "dry_run no debe insertar DetalleEnsayo"
        assert before_utilizados == after_utilizados, "dry_run no debe insertar Utilizado"


# ---------------------------------------------------------------------------
# Tests: validate_all (pre-import)
# ---------------------------------------------------------------------------

class TestPreImportValidationPhase4:

    def test_clean_csv_passes_validation(self, db_session, app, csv_dir):
        """CSV válidos deben producir reporte limpio."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir))

        assert report.is_clean is True
        assert len(report.missing_entradas) == 0
        assert len(report.missing_ensayos) == 0
        assert len(report.file_errors) == 0

    def test_missing_ensayo_detected(self, db_session, app, csv_dir_missing_ensayo):
        """Ensayo inexistente en CSV debe aparecer en missing_ensayos."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_missing_ensayo))

        assert len(report.missing_ensayos) >= 1

    def test_skipped_utilizados_detected(self, db_session, app, csv_dir_with_issues):
        """Utilizados con ID de entrada inexistente deben aparecer en skipped_utilizados."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_with_issues))

        assert len(report.skipped_utilizados) >= 1

    def test_report_markdown_generated(self, db_session, app, csv_dir):
        """to_markdown() debe devolver string no vacío con estructura básica."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir))

        md = report.to_markdown()
        assert '# Pre-Import Validation Report' in md
        assert 'Status' in md


# ---------------------------------------------------------------------------
# Tests: verify_post_import
# ---------------------------------------------------------------------------

class TestPostImportVerificationPhase4:

    def test_verify_returns_structured_result(self, db_session, app):
        """verify_post_import debe devolver PostImportVerification."""
        with app.app_context():
            service = Phase4ImportService()
            v = service.verify_post_import()

        assert isinstance(v, PostImportVerification)
        assert 'Detalles de Ensayos' in v.count_checks
        assert 'Utilizados' in v.count_checks

    def test_verify_fk_checks_present(self, db_session, app):
        """Deben existir chequeos de FK integrity."""
        with app.app_context():
            service = Phase4ImportService()
            v = service.verify_post_import()

        assert 'Detalles → Entradas' in v.fk_checks
        assert 'Detalles → Ensayos' in v.fk_checks
        assert 'Utilizados → Entradas' in v.fk_checks
        assert 'Utilizados → Ensayos' in v.fk_checks

    def test_verify_markdown_report(self, db_session, app):
        """to_markdown() debe generar reporte con secciones correctas."""
        with app.app_context():
            service = Phase4ImportService()
            v = service.verify_post_import()

        md = v.to_markdown()
        assert '# Post-Import Verification Report' in md
        assert 'Record Counts' in md
        assert 'FK Integrity' in md


# ---------------------------------------------------------------------------
# Tests: generate_report
# ---------------------------------------------------------------------------

class TestReportGenerationPhase4:

    def test_generate_report_returns_markdown(self, db_session, app, csv_dir):
        """generate_report debe devolver Markdown con secciones clave."""
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            service.import_all(str(csv_dir))
            md = service.generate_report()

        assert '# Reporte de Importación Phase 4' in md
        assert 'Resumen' in md
        assert 'Errores' in md
        assert 'Verificación de Conteos' in md

    def test_generate_report_saves_to_file(self, db_session, app, csv_dir, tmp_path):
        """generate_report con output_path debe crear archivo."""
        report_file = tmp_path / 'test_report.md'
        with app.app_context():
            service = Phase4ImportService(dry_run=True)
            service.import_all(str(csv_dir))
            service.generate_report(output_path=str(report_file))

        assert report_file.exists()
        content = report_file.read_text(encoding='utf-8')
        assert '# Reporte de Importación Phase 4' in content
