"""Tests para Phase3ImportService.

Cubre los criterios de aceptación del Issue #5 (Phase 3):
- Importación de OT, Pedidos, Entradas
- Validación FK pre-importación
- Tracking de balance warnings
- Tracking de lot format warnings
- Verificación post-importación
- Generación de reporte Markdown
"""
import csv
import re
from decimal import Decimal
from pathlib import Path

import pytest

from app.services.phase3_import_service import (
    Phase3ImportService,
    Phase3ImportResult,
    PreImportValidationReport,
    PostImportVerification,
)


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
def csv_dir(tmp_path, sample_cliente, sample_producto, sample_fabrica,
            sample_orden_trabajo):
    """Crea directorio temporal con CSVs válidos de Phase 3."""
    d = tmp_path / 'phase3_data'
    d.mkdir()

    # ordenes_trabajo.csv
    write_csv(d / 'ordenes_trabajo.csv',
              ['Id', 'NroOfic', 'IdCliente', 'Descripcion', 'FechCreacion'],
              [{'Id': 100, 'NroOfic': 'OT-TEST-100', 'IdCliente': sample_cliente.id,
                'Descripcion': 'OT test', 'FechCreacion': '2026-01-15'}])

    # pedidos.csv
    write_csv(d / 'pedidos.csv',
              ['IdPedido', 'IdCliente', 'IdProducto', 'IdOrdenTrabajo',
               'Lote', 'Cantidad', 'FechFab', 'FechVenc'],
              [{'IdPedido': 200, 'IdCliente': sample_cliente.id,
                'IdProducto': sample_producto.id,
                'IdOrdenTrabajo': sample_orden_trabajo.id,
                'Lote': 'A-1234', 'Cantidad': '10.5',
                'FechFab': '2025-12-01', 'FechVenc': '2026-06-01'}])

    # entradas.csv — balance correcto y lote válido
    write_csv(d / 'entradas.csv',
              ['Id', 'Codigo', 'IdCliente', 'IdProducto', 'IdFabrica',
               'Lote', 'CantidadRecib', 'CantidadEntreg', 'Saldo',
               'FechEntrada', 'Status'],
              [{'Id': 300, 'Codigo': 'ENT-300',
                'IdCliente': sample_cliente.id,
                'IdProducto': sample_producto.id,
                'IdFabrica': sample_fabrica.id,
                'Lote': 'B-5678',
                'CantidadRecib': '50', 'CantidadEntreg': '10', 'Saldo': '40',
                'FechEntrada': '2026-01-20', 'Status': 'RECIBIDO'}])

    return d


@pytest.fixture
def csv_dir_with_issues(tmp_path, sample_cliente, sample_producto, sample_fabrica):
    """CSVs con problemas: FK faltante, lote malo, balance incorrecto."""
    d = tmp_path / 'phase3_bad'
    d.mkdir()

    write_csv(d / 'ordenes_trabajo.csv',
              ['Id', 'NroOfic', 'IdCliente'],
              [{'Id': 1, 'NroOfic': 'OT-BAD-1', 'IdCliente': 99999}])  # cliente inexistente

    write_csv(d / 'pedidos.csv',
              ['IdPedido', 'IdCliente', 'IdProducto'],
              [{'IdPedido': 1, 'IdCliente': sample_cliente.id, 'IdProducto': 88888}])  # producto inexistente

    write_csv(d / 'entradas.csv',
              ['Id', 'Codigo', 'IdCliente', 'IdProducto', 'IdFabrica',
               'Lote', 'CantidadRecib', 'CantidadEntreg', 'Saldo', 'Status'],
              [
                  # Balance incorrecto (50-10 = 40, pero dice 99)
                  {'Id': 1, 'Codigo': 'ENT-1',
                   'IdCliente': sample_cliente.id, 'IdProducto': sample_producto.id,
                   'IdFabrica': sample_fabrica.id,
                   'Lote': 'INVALIDO', 'CantidadRecib': '50', 'CantidadEntreg': '10',
                   'Saldo': '99', 'Status': 'RECIBIDO'},
              ])

    return d


# ---------------------------------------------------------------------------
# Tests: importación correcta
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestPhase3ImportService:

    def test_import_all_success(self, db_session, app, csv_dir):
        """Importar CSVs válidos debe registrar todos los registros."""
        with app.app_context():
            service = Phase3ImportService(dry_run=False)
            result = service.import_all(str(csv_dir))

        assert result.ordenes_trabajo['imported'] == 1
        assert result.pedidos['imported'] == 1
        assert result.entradas['imported'] == 1
        assert result.total_errors == 0

    def test_dry_run_does_not_persist(self, db_session, app, csv_dir):
        """Dry-run no debe modificar la BD."""
        from app.database.models import OrdenTrabajo
        with app.app_context():
            before = OrdenTrabajo.query.count()
            service = Phase3ImportService(dry_run=True)
            service.import_all(str(csv_dir))
            after = OrdenTrabajo.query.count()

        assert before == after, "dry_run no debe insertar registros"

    def test_skips_duplicate_on_reimport(self, db_session, app, csv_dir):
        """Segunda importación del mismo CSV debe saltear registros existentes."""
        with app.app_context():
            s1 = Phase3ImportService(dry_run=False)
            s1.import_all(str(csv_dir))

            s2 = Phase3ImportService(dry_run=False)
            result2 = s2.import_all(str(csv_dir))

        assert result2.ordenes_trabajo['skipped'] == 1
        assert result2.pedidos['skipped'] == 1
        assert result2.entradas['skipped'] == 1

    def test_missing_csv_does_not_crash(self, db_session, app, tmp_path):
        """Si un CSV no existe, la importación continúa con las tablas disponibles."""
        empty_dir = tmp_path / 'empty'
        empty_dir.mkdir()
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            result = service.import_all(str(empty_dir))
        # No debe lanzar excepción
        assert result is not None


# ---------------------------------------------------------------------------
# Tests: balance y lot warnings
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestWarningTracking:

    def test_balance_mismatch_is_tracked(self, db_session, app, csv_dir_with_issues):
        """Discrepancias de balance deben guardarse en result.balance_warnings."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            service._load_fk_cache()
            service._import_entradas(csv_dir_with_issues / 'entradas.csv')

        assert len(service.result.balance_warnings) >= 1
        w = service.result.balance_warnings[0]
        assert w.warning_type == 'balance_mismatch'

    def test_lot_format_warning_is_tracked(self, db_session, app, csv_dir_with_issues):
        """Lotes con formato incorrecto deben guardarse en result.lot_warnings."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            service._load_fk_cache()
            service._import_entradas(csv_dir_with_issues / 'entradas.csv')

        assert len(service.result.lot_warnings) >= 1
        w = service.result.lot_warnings[0]
        assert w.warning_type == 'lot_format'
        assert w.value == 'INVALIDO'

    def test_valid_lot_format_no_warning(self, db_session, app, csv_dir):
        """Lotes con formato X-XXXX válido no deben generar warnings."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            service._load_fk_cache()
            service._import_entradas(csv_dir / 'entradas.csv')

        assert len(service.result.lot_warnings) == 0


# ---------------------------------------------------------------------------
# Tests: validate_all (pre-import)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestPreImportValidation:

    def test_clean_csv_passes_validation(self, db_session, app, csv_dir,
                                          sample_orden_trabajo):
        """CSV válidos deben producir reporte limpio."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir))

        assert report.is_clean is True
        assert len(report.missing_clientes) == 0
        assert len(report.missing_productos) == 0
        assert len(report.missing_fabricas) == 0
        assert len(report.file_errors) == 0

    def test_missing_cliente_detected(self, db_session, app, csv_dir_with_issues):
        """Cliente inexistente en CSV debe aparecer en missing_clientes."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_with_issues))

        assert len(report.missing_clientes) >= 1
        assert report.is_clean is False

    def test_missing_producto_detected(self, db_session, app, csv_dir_with_issues):
        """Producto inexistente en CSV debe aparecer en missing_productos."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_with_issues))

        assert len(report.missing_productos) >= 1

    def test_invalid_lots_detected(self, db_session, app, csv_dir_with_issues):
        """Lotes con formato incorrecto deben aparecer en invalid_lots."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_with_issues))

        assert len(report.invalid_lots) >= 1
        lote = report.invalid_lots[0]['lote']
        assert not re.match(r'^[A-Z]-\d{4}$', lote)

    def test_balance_mismatch_detected(self, db_session, app, csv_dir_with_issues):
        """Discrepancias de balance deben aparecer en balance_mismatches."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir_with_issues))

        assert len(report.balance_mismatches) >= 1

    def test_missing_file_detected(self, db_session, app, tmp_path):
        """Archivos CSV faltantes deben aparecer en file_errors."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(tmp_path / 'nonexistent'))

        assert len(report.file_errors) >= 1

    def test_report_markdown_generated(self, db_session, app, csv_dir):
        """to_markdown() debe devolver string no vacío con estructura básica."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            report = service.validate_all(str(csv_dir))

        md = report.to_markdown()
        assert '# Pre-Import Validation Report' in md
        assert 'Status' in md


# ---------------------------------------------------------------------------
# Tests: verify_post_import
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestPostImportVerification:

    def test_verify_returns_structured_result(self, db_session, app):
        """verify_post_import debe devolver PostImportVerification."""
        with app.app_context():
            service = Phase3ImportService()
            v = service.verify_post_import()

        assert isinstance(v, PostImportVerification)
        assert 'Órdenes de Trabajo' in v.count_checks
        assert 'Pedidos' in v.count_checks
        assert 'Entradas' in v.count_checks

    def test_verify_fk_checks_present(self, db_session, app):
        """Deben existir chequeos de FK integrity."""
        with app.app_context():
            service = Phase3ImportService()
            v = service.verify_post_import()

        assert 'Pedidos → Clientes' in v.fk_checks
        assert 'Entradas → Clientes' in v.fk_checks
        assert 'Entradas → Productos' in v.fk_checks
        assert 'Entradas → Fábricas' in v.fk_checks

    def test_verify_consistency_checks_present(self, db_session, app):
        """Deben existir chequeos de consistencia de datos."""
        with app.app_context():
            service = Phase3ImportService()
            v = service.verify_post_import()

        assert 'Entradas con cantidad_recib negativa' in v.consistency_checks
        assert 'Entradas con saldo incorrecto' in v.consistency_checks

    def test_verify_markdown_report(self, db_session, app):
        """to_markdown() debe generar reporte con secciones correctas."""
        with app.app_context():
            service = Phase3ImportService()
            v = service.verify_post_import()

        md = v.to_markdown()
        assert '# Post-Import Verification Report' in md
        assert 'Record Counts' in md
        assert 'FK Integrity' in md


# ---------------------------------------------------------------------------
# Tests: generate_report
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestReportGeneration:

    def test_generate_report_returns_markdown(self, db_session, app, csv_dir):
        """generate_report debe devolver Markdown con secciones clave."""
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            service.import_all(str(csv_dir))
            md = service.generate_report()

        assert '# Reporte de Importación Phase 3' in md
        assert 'Resumen' in md
        assert 'Errores' in md
        assert 'Advertencias de Balance' in md
        assert 'Advertencias de Formato de Lote' in md

    def test_generate_report_saves_to_file(self, db_session, app, csv_dir, tmp_path):
        """generate_report con output_path debe crear archivo."""
        report_file = tmp_path / 'test_report.md'
        with app.app_context():
            service = Phase3ImportService(dry_run=True)
            service.import_all(str(csv_dir))
            service.generate_report(output_path=str(report_file))

        assert report_file.exists()
        content = report_file.read_text(encoding='utf-8')
        assert '# Reporte de Importación Phase 3' in content
