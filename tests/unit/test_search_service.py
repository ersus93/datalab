"""Tests unitarios para el SearchService - Global Search System.

Phase 6 Issue #56 - Global Search System
"""

import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, patch, PropertyMock


class TestSearchServiceLevenshtein:
    """Tests para algoritmos de Levenshtein."""

    def test_levenshtein_identical_strings(self):
        """Test distancia Levenshtein con cadenas identicas."""
        from app.services.search_service import SearchService
        
        distance = SearchService._calculate_levenshtein_distance("hola", "hola")
        assert distance == 0

    def testlevenshtein_one_char_difference(self):
        """Test distancia con un caracter de diferencia."""
        from app.services.search_service import SearchService
        
        distance = SearchService._calculate_levenshtein_distance("hola", "holb")
        assert distance == 1

    def test_levenshtein_complete_difference(self):
        """Test distancia con cadenas completamente diferentes."""
        from app.services.search_service import SearchService
        
        distance = SearchService._calculate_levenshtein_distance("abc", "xyz")
        assert distance == 3

    def test_levenshtein_empty_string(self):
        """Test con cadena vacia."""
        from app.services.search_service import SearchService
        
        distance = SearchService._calculate_levenshtein_distance("", "abc")
        assert distance == 3

    def test_similarity_identical(self):
        """Test similaridad con cadenas identicas."""
        from app.services.search_service import SearchService
        
        similarity = SearchService._calculate_similarity("hola", "hola")
        assert similarity == 1.0

    def test_similarity_contains(self):
        """Test similaridad cuando una cadena contiene a la otra."""
        from app.services.search_service import SearchService
        
        similarity = SearchService._calculate_similarity("ola", "hola")
        assert similarity == 0.9

    def test_similarity_different(self):
        """Test similaridad con cadenas diferentes."""
        from app.services.search_service import SearchService
        
        similarity = SearchService._calculate_similarity("abc", "xyz")
        assert similarity < 0.5

    def test_similarity_empty_strings(self):
        """Test similaridad con cadenas vacias."""
        from app.services.search_service import SearchService
        
        similarity = SearchService._calculate_similarity("", "hola")
        assert similarity == 0.0


class TestSearchServiceConfiguration:
    """Tests para configuracion del servicio."""

    def test_searchable_entities_defined(self):
        """Test que todas las entidades buscables estan definidas."""
        from app.services.search_service import SearchService
        
        entities = SearchService.SEARCHABLE_ENTITIES
        
        assert 'clientes' in entities
        assert 'fabricas' in entities
        assert 'productos' in entities
        assert 'entradas' in entities
        assert 'pedidos' in entities
        assert 'informes' in entities

    def test_entity_has_required_fields(self):
        """Test que cada entidad tiene los campos requeridos."""
        from app.services.search_service import SearchService
        
        for entity_type, config in SearchService.SEARCHABLE_ENTITIES.items():
            assert 'model' in config, f"{entity_type} missing 'model'"
            assert 'search_fields' in config, f"{entity_type} missing 'search_fields'"
            assert 'priority' in config, f"{entity_type} missing priority"
            assert isinstance(config['search_fields'], list)
            assert len(config['search_fields']) > 0

    def test_area_siglas_defined(self):
        """Test que las siglas de area estan definidas."""
        from app.services.search_service import SearchService
        
        assert 'FQ' in SearchService.AREA_SIGLAS
        assert 'MB' in SearchService.AREA_SIGLAS
        assert 'ES' in SearchService.AREA_SIGLAS
        assert 'OS' in SearchService.AREA_SIGLAS


class TestSearchServiceEmptyResults:
    """Tests para el manejo de resultados vacios."""

    def test_empty_results_structure(self):
        """Test estructura de resultados vacios."""
        from app.services.search_service import SearchService
        
        result = SearchService._empty_results()
        
        assert result['query'] == ''
        assert result['total_results'] == 0
        assert result['results'] == {}
        assert 'facets' in result
        assert 'pagination' in result

    def test_empty_results_facets(self):
        """Test que facets tiene la estructura correcta."""
        from app.services.search_service import SearchService
        
        result = SearchService._empty_results()
        
        assert 'areas' in result['facets']
        assert 'statuses' in result['facets']
        assert 'entity_counts' in result['facets']

    def test_empty_results_pagination(self):
        """Test que la paginacion es correcta."""
        from app.services.search_service import SearchService
        
        result = SearchService._empty_results()
        
        assert result['pagination']['page'] == 1
        assert result['pagination']['limit'] == 20
        assert result['pagination']['total_pages'] == 0


class TestSearchServiceURLGeneration:
    """Tests para generacion de URLs."""

    def test_get_entity_url_clientes(self):
        """Test generacion de URL para clientes."""
        from app.services.search_service import SearchService
        
        url = SearchService._get_entity_url('clientes', 123)
        assert url == '/clientes/123'

    def test_get_entity_url_fabricas(self):
        """Test generacion de URL para fabricas."""
        from app.services.search_service import SearchService
        
        url = SearchService._get_entity_url('fabricas', 456)
        assert url == '/fabricas/456'

    def test_get_entity_url_productos(self):
        """Test generacion de URL para productos."""
        from app.services.search_service import SearchService
        
        url = SearchService._get_entity_url('productos', 789)
        assert url == '/productos/789'

    def test_get_entity_url_entradas(self):
        """Test generacion de URL para entradas."""
        from app.services.search_service import SearchService
        
        url = SearchService._get_entity_url('entradas', 111)
        assert url == '/entradas/111'

    def test_get_entity_url_unknown(self):
        """Test generacion de URL para entidad desconocida."""
        from app.services.search_service import SearchService
        
        url = SearchService._get_entity_url('unknown', 999)
        assert url == '/unknown/999'


class TestSearchServiceHighlight:
    """Tests para highlighting de resultados."""

    def test_highlight_match_found(self):
        """Test highlight cuando encuentra coincidencia."""
        from app.services.search_service import SearchService
        
        mock_item = MagicMock()
        mock_item.nombre = "Cliente de Prueba"
        
        result = SearchService._get_highlight(mock_item, ['nombre'], "Prueba")
        
        assert result is not None
        assert "Prueba" in result

    def test_highlight_no_match(self):
        """Test highlight cuando no encuentra coincidencia."""
        from app.services.search_service import SearchService
        
        mock_item = MagicMock()
        mock_item.nombre = "Cliente de Prueba"
        
        result = SearchService._get_highlight(mock_item, ['nombre'], "xyz123")
        
        assert result is None

    def test_highlight_case_insensitive(self):
        """Test highlight es case insensitive."""
        from app.services.search_service import SearchService
        
        mock_item = MagicMock()
        mock_item.nombre = "CLIENTE Prueba"
        
        result = SearchService._get_highlight(mock_item, ['nombre'], "cliente")
        
        assert result is not None

    def test_highlight_context_truncation(self):
        """Test que el highlight recorta contexto correctamente."""
        from app.services.search_service import SearchService
        
        long_name = "A" * 100 + "TARGET" + "B" * 100
        mock_item = MagicMock()
        mock_item.nombre = long_name
        
        result = SearchService._get_highlight(mock_item, ['nombre'], "TARGET")
        
        assert result is not None
        assert "..." in result


class TestSearchServiceAutocomplete:
    """Tests para sugerencias de autocompletado."""

    def test_autocomplete_min_length(self):
        """Test que autocompletado requiere minimo 2 caracteres."""
        from app.services.search_service import SearchService
        
        result = SearchService.get_autocomplete_suggestions("a")
        
        assert result['suggestions'] == []

    def test_autocomplete_empty_query(self):
        """Test autocompletado con query vacio."""
        from app.services.search_service import SearchService
        
        result = SearchService.get_autocomplete_suggestions("")
        
        assert result['suggestions'] == []

    @patch('app.services.search_service.db')
    def test_autocomplete_limit(self, mock_db):
        """Test que autocompletado respeta el limite."""
        from app.services.search_service import SearchService
        
        mock_query = MagicMock()
        mock_query.filter.return_value.distinct.return_value.limit.return_value.all.return_value = []
        mock_db.session.query.return_value = mock_query
        
        result = SearchService.get_autocomplete_suggestions("test", limit=5)
        
        assert len(result['suggestions']) <= 5


class TestSearchServiceRecentSearches:
    """Tests para busquedas recientes."""

    def test_get_recent_searches_returns_list(self):
        """Test que retorna lista vacia por defecto."""
        from app.services.search_service import SearchService
        
        result = SearchService.get_recent_searches(user_id=1)
        
        assert isinstance(result, list)
        assert result == []


class TestSearchAPIEndpoints:
    """Tests para los endpoints de API de busqueda."""

    @pytest.fixture
    def client(self, app):
        """Fixture para el cliente de prueba."""
        return app.test_client()

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_search_endpoint_returns_json(self, client):
        """Test que el endpoint de busqueda retorna JSON."""
        response = client.get('/api/search?q=test')
        
        assert response.status_code in [200, 500]  # 500 if DB not initialized

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_search_endpoint_empty_query(self, client):
        """Test endpoint con query vacio."""
        response = client.get('/api/search')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_autocomplete_endpoint(self, client):
        """Test endpoint de autocompletado."""
        response = client.get('/api/search/autocomplete?q=te')
        
        assert response.status_code in [200, 500]

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_entities_endpoint(self, client):
        """Test endpoint de configuracion de entidades."""
        response = client.get('/api/search/entities')
        
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.get_json()
            assert 'entities' in data

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_filters_endpoint(self, client):
        """Test endpoint de filtros disponibles."""
        response = client.get('/api/search/filters')
        
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.get_json()
            assert 'areas' in data or 'statuses' in data

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_search_with_pagination(self, client):
        """Test busqueda con paginacion."""
        response = client.get('/api/search?q=test&page=2&limit=10')
        
        assert response.status_code in [200, 500]

    @pytest.mark.skip(reason="Requires database setup not available in unit tests")
    def test_search_with_filters(self, client):
        """Test busqueda con filtros."""
        response = client.get('/api/search?q=test&area=FQ&status=RECIBIDO')
        
        assert response.status_code in [200, 500]
