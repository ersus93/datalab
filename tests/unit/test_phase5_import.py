"""Tests unitarios para Phase5ImportService."""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock WeasyPrint before importing app to avoid OSError
sys.modules['weasyprint'] = MagicMock()
sys.modules['weasyprint.html'] = MagicMock()
sys.modules['weasyprint.text'] = MagicMock()

from app import create_app, db
from app.services.phase5_import_service import (
    Phase5ImportService,
    Phase5ImportResult,
    PreImportValidationReport,
    PostImportVerification,
    ImportError,
    ImportWarning,
    EXPECTED_COUNTS,
)


@pytest.fixture
def app():
    """Crear aplicación de prueba."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba."""
    return app.test_client()


class TestPhase5ImportResult:
    """Tests para Phase5ImportResult."""

    def test_initial_state(self):
        """Verificar estado inicial del resultado."""
        result = Phase5ImportResult()

        assert result.plantillas['total'] == 0
        assert result.plantillas['imported'] == 0
        assert result.plantillas['skipped'] == 0
        assert result.plantillas['errors'] == []

        assert result.informes['total'] == 0
        assert result.informes['created'] == 0
        assert result.informes['skipped'] == 0
        assert result.informes['errors'] == []

        assert result.start_time is None
        assert result.end_time is None
        assert result.duration_seconds == 0.0

    def test_duration_calculation(self):
        """Verificar cálculo de duración."""
        result = Phase5ImportResult()
        result.start_time = datetime(2026, 1, 1, 10, 0, 0)
        result.end_time = datetime(2026, 1, 1, 10, 0, 10)

        assert result.duration_seconds == 10.0

    def test_total_created(self):
        """Verificar total creado."""
        result = Phase5ImportResult()
        result.plantillas['imported'] = 15
        result.informes['created'] = 18

        assert result.total_created == 33

    def test_total_errors(self):
        """Verificar total de errores."""
        result = Phase5ImportResult()
        result.plantillas['errors'] = [Mock(), Mock()]
        result.informes['errors'] = [Mock()]

        assert result.total_errors == 3

    def test_to_dict(self):
        """Verificar serialización a dict."""
        result = Phase5ImportResult()
        result.start_time = datetime(2026, 1, 1, 10, 0, 0)
        result.end_time = datetime(2026, 1, 1, 10, 0, 10)

        d = result.to_dict()

        assert 'duration_seconds' in d
        assert 'total_created' in d
        assert 'total_errors' in d
        assert 'plantillas' in d
        assert 'informes' in d


class TestPreImportValidationReport:
    """Tests para PreImportValidationReport."""

    def test_initial_state(self):
        """Verificar estado inicial."""
        report = PreImportValidationReport()

        assert report.missing_entradas == []
        assert report.missing_clientes == []
        assert report.file_errors == []
        assert report.is_clean is True

    def test_is_clean_with_errors(self):
        """Verificar is_clean con errores."""
        report = PreImportValidationReport()
        report.file_errors.append("Error de archivo")

        assert report.is_clean is False

    def test_to_markdown(self):
        """Verificar generación de markdown."""
        report = PreImportValidationReport()
        report.file_errors.append("Error de prueba")

        md = report.to_markdown()

        assert '# Pre-Import Validation Report' in md
        assert 'Phase 5' in md
        assert '❌ ISSUES FOUND' in md


class TestPostImportVerification:
    """Tests para PostImportVerification."""

    def test_initial_state(self):
        """Verificar estado inicial."""
        v = PostImportVerification()

        assert v.count_checks == {}
        assert v.fk_checks == {}
        assert v.consistency_checks == {}
        assert v.all_passed is True

    def test_all_passed_with_failed_checks(self):
        """Verificar all_passed con checks fallidos."""
        v = PostImportVerification()
        v.count_checks['test'] = {'passed': False}

        assert v.all_passed is False

    def test_to_markdown(self):
        """Verificar generación de markdown."""
        v = PostImportVerification()
        v.count_checks['test'] = {'expected': 10, 'actual': 10, 'passed': True}

        md = v.to_markdown()

        assert '# Post-Import Verification Report' in md
        assert 'Phase 5' in md
        assert '✅ ALL CHECKS PASSED' in md


class TestImportError:
    """Tests para ImportError."""

    def test_creation(self):
        """Verificar creación de error."""
        err = ImportError("test_table", 1, "test_field", "Test error", "bad_value")

        assert err.table == "test_table"
        assert err.row_id == 1
        assert err.field == "test_field"
        assert err.message == "Test error"
        assert err.original_value == "bad_value"
        assert err.timestamp is not None

    def test_to_dict(self):
        """Verificar serialización."""
        err = ImportError("test_table", 1, "test_field", "Test error", "bad_value")

        d = err.to_dict()

        assert d['table'] == "test_table"
        assert d['row_id'] == 1
        assert d['field'] == "test_field"
        assert d['message'] == "Test error"
        assert d['original_value'] == "bad_value"


class TestImportWarning:
    """Tests para ImportWarning."""

    def test_creation(self):
        """Verificar creación de advertencia."""
        warn = ImportWarning("test_table", 1, "type", "Warning message", "value")

        assert warn.table == "test_table"
        assert warn.row_id == 1
        assert warn.warning_type == "type"
        assert warn.message == "Warning message"
        assert warn.value == "value"

    def test_to_dict(self):
        """Verificar serialización."""
        warn = ImportWarning("test_table", 1, "type", "Warning message", "value")

        d = warn.to_dict()

        assert d['table'] == "test_table"
        assert d['row_id'] == 1
        assert d['type'] == "type"
        assert d['message'] == "Warning message"
        assert d['value'] == "value"


class TestPhase5ImportService:
    """Tests para Phase5ImportService - sin app context para evitar problemas con SQLite."""

    def test_service_can_be_imported(self):
        """Verificar que el servicio puede ser importado."""
        from app.services.phase5_import_service import Phase5ImportService
        assert Phase5ImportService is not None

    def test_initial_state_mocked(self):
        """Verificar estado inicial del servicio sin DB."""
        with patch('app.services.phase5_import_service.db'):
            service = Phase5ImportService(dry_run=True)
            assert service.dry_run is True
            assert service.result is not None
            assert service._valid_entradas is None
            assert service._valid_clientes is None

    def test_batch_size_constant(self):
        """Verificar constante BATCH_SIZE."""
        assert Phase5ImportService.BATCH_SIZE == 50

    def test_expected_counts(self):
        """Verificar constantes de conteos esperados."""
        assert EXPECTED_COUNTS['plantillas'] == 20
        assert EXPECTED_COUNTS['informes'] == 20
