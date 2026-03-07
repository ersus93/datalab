"""Tests unitarios para el servicio de Analytics."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestAnalyticsService:
    """Tests para AnalyticsService."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock de la sesión de base de datos."""
        with patch('app.services.analytics_service.db') as mock_db:
            yield mock_db

    @pytest.fixture
    def mock_cache(self):
        """Mock del gestor de caché."""
        with patch('app.services.analytics_service.cache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            yield mock_cache

    def test_get_cache_key(self):
        """Test generación de claves de caché."""
        from app.services.analytics_service import AnalyticsService

        key = AnalyticsService._get_cache_key("test_method", param1="value1", param2="value2")
        assert "analytics:test_method:param1=value1:param2=value2" == key

    def test_get_cache_key_with_empty_params(self):
        """Test generación de clave sin parámetros."""
        from app.services.analytics_service import AnalyticsService

        key = AnalyticsService._get_cache_key("test_method")
        assert "analytics:test_method:" == key

    @patch('app.services.analytics_service.cache')
    @patch('app.services.analytics_service.db')
    def test_get_es_pending_returns_cached_data(self, mock_db, mock_cache):
        """Test que retorna datos en caché si existen."""
        from app.services.analytics_service import AnalyticsService

        cached_data = [{"area": "Test Area", "sigla": "TA", "count": 5}]
        mock_cache.get.return_value = cached_data

        result = AnalyticsService.get_es_pending()

        assert result == cached_data
        mock_cache.get.assert_called_once()
        mock_db.session.query.assert_not_called()

    @patch('app.services.analytics_service.cache')
    @patch('app.services.analytics_service.db')
    def test_get_es_pending_queries_database(self, mock_db, mock_cache):
        """Test que consulta la base de datos cuando no hay caché."""
        from app.services.analytics_service import AnalyticsService

        mock_cache.get.return_value = None

        # Mock de la query
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.session.query.return_value = mock_query

        result = AnalyticsService.get_es_pending()

        assert isinstance(result, list)
        mock_db.session.query.assert_called()

    @patch('app.services.analytics_service.cache')
    @patch('app.services.analytics_service.db')
    def test_get_kpis_returns_correct_structure(self, mock_db, mock_cache):
        """Test que get_analytics_kpis retorna la estructura correcta."""
        from app.services.analytics_service import AnalyticsService

        mock_cache.get.return_value = None

        # Mock DetalleEnsayo query
        mock_detalle_query = MagicMock()
        mock_detalle_query.filter.return_value = mock_detalle_query
        mock_detalle_query.count.return_value = 10

        # Mock Entrada query
        mock_entrada_query = MagicMock()
        mock_entrada_query.filter.return_value = mock_entrada_query
        mock_entrada_query.count.return_value = 5

        mock_db.session.query.side_effect = [mock_detalle_query, mock_entrada_query]

        with patch('app.database.models.detalle_ensayo.DetalleEnsayo') as mock_detalle_cls, \
             patch('app.database.models.entrada.Entrada') as mock_entrada_cls, \
             patch('app.database.models.detalle_ensayo.DetalleEnsayoStatus') as mock_status, \
             patch('app.database.models.entrada.EntradaStatus') as mock_entrada_status, \
             patch('app.services.analytics_service.datetime') as mock_datetime:

            mock_datetime.utcnow.return_value = datetime(2024, 1, 15, 12, 0, 0)

            result = AnalyticsService.get_analytics_kpis()

            assert 'ensayos_pendientes' in result
            assert 'ensayos_completados' in result
            assert 'completados_mes' in result
            assert 'entradas_pendientes' in result
            assert 'timestamp' in result

    @patch('app.services.analytics_service.cache')
    @patch('app.services.analytics_service.db')
    def test_get_full_analytics_returns_all_sections(self, mock_db, mock_cache):
        """Test que get_full_analytics retorna todas las secciones."""
        from app.services.analytics_service import AnalyticsService

        mock_cache.get.return_value = None

        # Mock queries
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.session.query.return_value = mock_query

        with patch('app.database.models.detalle_ensayo.DetalleEnsayo') as mock_detalle_cls, \
             patch('app.database.models.detalle_ensayo.DetalleEnsayoStatus') as mock_status, \
             patch('app.services.analytics_service.datetime') as mock_datetime:

            mock_datetime.utcnow.return_value = datetime(2024, 1, 15)

            result = AnalyticsService.get_full_analytics()

            assert 'es_pending' in result
            assert 'fq_pending' in result
            assert 'mb_pending_by_tech' in result
            assert 'completed_timeline' in result
            assert 'lotes_by_type_client' in result
            assert 'muestreos_by_client_type' in result
            assert 'kpis' in result
            assert 'timestamp' in result

    @patch('app.services.analytics_service.cache')
    def test_invalidate_cache(self, mock_cache):
        """Test invalidación de caché."""
        from app.services.analytics_service import AnalyticsService

        mock_cache.clear_pattern.return_value = 5

        result = AnalyticsService.invalidate_cache()

        assert result == 5
        mock_cache.clear_pattern.assert_called_once_with("analytics:*")

    @patch('app.services.analytics_service.cache')
    @patch('app.services.analytics_service.db')
    def test_get_completed_timeline_with_custom_months(self, mock_db, mock_cache):
        """Test timeline con meses personalizados."""
        from app.services.analytics_service import AnalyticsService

        mock_cache.get.return_value = None
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.session.query.return_value = mock_query

        with patch('app.database.models.detalle_ensayo.DetalleEnsayo') as mock_detalle_cls, \
             patch('app.database.models.detalle_ensayo.DetalleEnsayoStatus') as mock_status, \
             patch('app.services.analytics_service.datetime') as mock_datetime:

            result = AnalyticsService.get_completed_timeline(months=6)

            assert isinstance(result, list)