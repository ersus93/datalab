"""Search Service - Global Search System for DataLab.

This module provides comprehensive search functionality across all entities
with fuzzy matching, filtering, and categorization capabilities.

Phase 6 Issue #56 - Global Search System
"""

from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict

from sqlalchemy import or_, and_
from sqlalchemy.orm import Query, joinedload

from app import db
from app.database.models.cliente import Cliente
from app.database.models.fabrica import Fabrica
from app.database.models.producto import Producto
from app.database.models.entrada import Entrada, EntradaStatus
from app.database.models.pedido import Pedido
from app.database.models.informe import Informe, InformeStatus
from app.database.models.reference import Area, Rama
from app.database.models.recent_search import RecentSearch


class SearchService:
    """Global search service for DataLab."""

    DEFAULT_SIMILARITY_THRESHOLD = 0.8
    MAX_RESULTS_PER_ENTITY = 50
    AUTOCOMPLETE_LIMIT = 10

    SEARCHABLE_ENTITIES = {
        'clientes': {
            'model': Cliente,
            'search_fields': ['nombre', 'codigo', 'email', 'telefono'],
            'priority': 'high',
        },
        'fabricas': {
            'model': Fabrica,
            'search_fields': ['nombre', 'id'],
            'priority': 'high',
        },
        'productos': {
            'model': Producto,
            'search_fields': ['nombre', 'id'],
            'priority': 'high',
        },
        'entradas': {
            'model': Entrada,
            'search_fields': ['codigo', 'lote', 'observaciones'],
            'priority': 'high',
        },
        'pedidos': {
            'model': Pedido,
            'search_fields': ['codigo', 'observaciones'],
            'priority': 'medium',
        },
        'informes': {
            'model': Informe,
            'search_fields': ['nro_oficial', 'titulo', 'resumen_resultados'],
            'field_mapping': {'titulo': 'nro_oficial'},
            'priority': 'medium',
        },
    }

    AREA_SIGLAS = ['FQ', 'MB', 'ES', 'OS']

    @staticmethod
    def _calculate_levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return SearchService._calculate_levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1.lower() != c2.lower())
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def _calculate_similarity(s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings."""
        if not s1 or not s2:
            return 0.0

        s1_lower = s1.lower()
        s2_lower = s2.lower()

        if s1_lower == s2_lower:
            return 1.0

        if s1_lower in s2_lower or s2_lower in s1_lower:
            return 0.9

        max_len = max(len(s1), len(s2))
        distance = SearchService._calculate_levenshtein_distance(s1_lower, s2_lower)
        similarity = 1.0 - (distance / max_len)

        return similarity

    @staticmethod
    def _apply_fuzzy_filter(items, search_fields, query, threshold):
        """Apply fuzzy matching filter to results."""
        if not query or threshold >= 1.0:
            return items
        
        filtered_items = []
        for item in items:
            for field in search_fields:
                if hasattr(item, field):
                    value = getattr(item, field)
                    if value:
                        similarity = SearchService._calculate_similarity(query, str(value))
                        if similarity >= threshold:
                            filtered_items.append(item)
                            break
        
        return filtered_items

    @staticmethod
    def _build_ilike_filter(model_class, search_fields, query, field_mapping=None):
        """Build ILIKE filter for search fields."""
        filters = []
        pattern = f'%{query}%'
        field_mapping = field_mapping or {}

        for field in search_fields:
            actual_field = field_mapping.get(field, field)
            if hasattr(model_class, actual_field):
                field_obj = getattr(model_class, actual_field)
                filters.append(field_obj.ilike(pattern))

        return or_(*filters) if filters else None

    @staticmethod
    def search(query, entities=None, filters=None, page=1, limit=20, threshold=None):
        """Perform global search across entities."""
        if not query or not query.strip():
            return SearchService._empty_results()

        query = query.strip()

        if not entities:
            entities = list(SearchService.SEARCHABLE_ENTITIES.keys())

        filters = filters or {}
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        area = filters.get('area')
        status = filters.get('status')

        results = {}
        facets = {
            'areas': defaultdict(int),
            'statuses': defaultdict(int),
            'entity_counts': {},
        }

        total_results = 0

        for entity_type in entities:
            if entity_type not in SearchService.SEARCHABLE_ENTITIES:
                continue

            entity_config = SearchService.SEARCHABLE_ENTITIES[entity_type]
            model_class = entity_config['model']
            search_fields = entity_config['search_fields']
            field_mapping = entity_config.get('field_mapping', {})

            q = db.session.query(model_class)

            if entity_type == 'fabricas':
                q = q.options(joinedload(Fabrica.cliente), joinedload(Fabrica.provincia))
            elif entity_type == 'productos':
                q = q.options(joinedload(Producto.destino), joinedload(Producto.rama))
            elif entity_type == 'entradas':
                q = q.options(joinedload(Entrada.cliente), joinedload(Entrada.producto), joinedload(Entrada.fabrica))
            elif entity_type == 'pedidos':
                q = q.options(joinedload(Pedido.cliente))
            elif entity_type == 'informes':
                q = q.options(joinedload(Informe.cliente))

            search_filter = SearchService._build_ilike_filter(
                model_class, search_fields, query, field_mapping
            )
            if search_filter is not None:
                q = q.filter(search_filter)

            q = SearchService._apply_date_filters(q, model_class, date_from, date_to)
            q = SearchService._apply_area_filter(q, model_class, area)
            q = SearchService._apply_status_filter(q, model_class, entity_type, status)

            count = q.count()

            offset = (page - 1) * limit
            items = q.limit(limit).offset(offset).all()

            # Apply fuzzy matching filter
            threshold = threshold if threshold is not None else SearchService.DEFAULT_SIMILARITY_THRESHOLD
            items = SearchService._apply_fuzzy_filter(items, search_fields, query, threshold)

            formatted_items = SearchService._format_results(
                entity_type, items, search_fields, query
            )

            results[entity_type] = formatted_items
            facets['entity_counts'][entity_type] = count
            total_results += count

        return {
            'query': query,
            'total_results': total_results,
            'results': results,
            'facets': dict(facets),
            'pagination': {
                'page': page,
                'limit': limit,
                'total_pages': (total_results + limit - 1) // limit if total_results > 0 else 0,
            },
        }

    @staticmethod
    def _apply_date_filters(q, model_class, date_from, date_to):
        """Apply date range filters to query."""
        date_field = None

        if hasattr(model_class, 'fech_entrada'):
            date_field = model_class.fech_entrada
        elif hasattr(model_class, 'fech_pedido'):
            date_field = model_class.fech_pedido
        elif hasattr(model_class, 'fecha_generacion'):
            date_field = model_class.fecha_generacion
        elif hasattr(model_class, 'created_at'):
            date_field = model_class.created_at
        elif hasattr(model_class, 'creado_en'):
            date_field = model_class.creado_en

        if date_field:
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    q = q.filter(date_field >= from_date)
                except ValueError:
                    pass

            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    q = q.filter(date_field <= to_date)
                except ValueError:
                    pass

        return q

    @staticmethod
    def _apply_area_filter(q, model_class, area):
        """Apply area filter based on product's rama."""
        if area not in SearchService.AREA_SIGLAS:
            return q

        if hasattr(model_class, 'producto'):
            q = q.join(Producto).join(Rama).filter(Rama.nombre.ilike(f'%{area}%'))
        elif hasattr(model_class, 'rama_id'):
            q = q.filter(model_class.rama_id.isnot(None))

        return q

    @staticmethod
    def _apply_status_filter(q, model_class, entity_type, status):
        """Apply status filter based on entity type."""
        status_field = None

        if entity_type == 'entradas' and hasattr(model_class, 'status'):
            status_field = model_class.status
        elif entity_type == 'pedidos' and hasattr(model_class, 'status'):
            status_field = model_class.status
        elif entity_type == 'informes' and hasattr(model_class, 'estado'):
            status_field = model_class.estado

        if status and status_field:
            q = q.filter(status_field == status)

        return q

    @staticmethod
    def _format_results(entity_type, items, search_fields, query):
        """Format search results for API response."""
        results = []

        for item in items:
            result = {
                'id': item.id,
                'type': entity_type,
                'url': SearchService._get_entity_url(entity_type, item.id),
            }

            if entity_type == 'clientes':
                result.update({
                    'title': item.nombre,
                    'description': f"Codigo: {item.codigo}",
                    'extra': {
                        'email': item.email,
                        'telefono': item.telefono,
                        'activo': item.activo,
                    }
                })
            elif entity_type == 'fabricas':
                result.update({
                    'title': item.nombre,
                    'description': f"Cliente: {item.cliente.nombre if item.cliente else 'N/A'}",
                    'extra': {
                        'provincia': item.provincia.nombre if item.provincia else None,
                    }
                })
            elif entity_type == 'productos':
                result.update({
                    'title': item.nombre,
                    'description': f"ID: {item.id}",
                    'extra': {
                        'destino': item.destino.sigla if item.destino else None,
                        'rama': item.rama.nombre if item.rama else None,
                    }
                })
            elif entity_type == 'entradas':
                result.update({
                    'title': item.codigo,
                    'description': f"Lote: {item.lote or 'N/A'} | Estado: {item.status}",
                    'extra': {
                        'cliente': item.cliente.nombre if item.cliente else None,
                        'producto': item.producto.nombre if item.producto else None,
                        'status': item.status,
                    }
                })
            elif entity_type == 'pedidos':
                result.update({
                    'title': item.codigo,
                    'description': item.observaciones[:100] if item.observaciones else 'Sin descripcion',
                    'extra': {
                        'cliente': item.cliente.nombre if item.cliente else None,
                        'status': item.status,
                    }
                })
            elif entity_type == 'informes':
                result.update({
                    'title': item.nro_oficial,
                    'description': item.resumen_resultados[:100] if item.resumen_resultados else 'Sin resumen',
                    'extra': {
                        'titulo': item.nro_oficial,
                        'estado': item.estado.value if hasattr(item.estado, 'value') else item.estado,
                        'cliente': item.cliente.nombre if item.cliente else None,
                    }
                })

            result['highlight'] = SearchService._get_highlight(item, search_fields, query)
            results.append(result)

        return results

    @staticmethod
    def _get_entity_url(entity_type, entity_id):
        """Get URL for entity detail page."""
        urls = {
            'clientes': f'/clientes/{entity_id}',
            'fabricas': f'/fabricas/{entity_id}',
            'productos': f'/productos/{entity_id}',
            'entradas': f'/entradas/{entity_id}',
            'pedidos': f'/pedidos/{entity_id}',
            'informes': f'/informes/{entity_id}',
        }
        return urls.get(entity_type, f'/{entity_type}/{entity_id}')

    @staticmethod
    def _get_highlight(item, search_fields, query):
        """Get highlighted matching text."""
        query_lower = query.lower()

        for field in search_fields:
            if hasattr(item, field):
                value = getattr(item, field)
                if value:
                    value_str = str(value)
                    if query_lower in value_str.lower():
                        idx = value_str.lower().find(query_lower)
                        start = max(0, idx - 20)
                        end = min(len(value_str), idx + len(query) + 20)
                        context = value_str[start:end]
                        if start > 0:
                            context = '...' + context
                        if end < len(value_str):
                            context = context + '...'
                        return context

        return None

    @staticmethod
    def get_autocomplete_suggestions(query, limit=10):
        """Get autocomplete suggestions based on query."""
        if not query or len(query) < 2:
            return {'suggestions': []}

        suggestions = []

        for entity_type, config in SearchService.SEARCHABLE_ENTITIES.items():
            model_class = config['model']
            search_fields = config['search_fields']

            for field in search_fields:
                if hasattr(model_class, field):
                    values = db.session.query(
                        getattr(model_class, field)
                    ).filter(
                        getattr(model_class, field).ilike(f'%{query}%')
                    ).distinct().limit(limit).all()

                    for value in values:
                        if value[0]:
                            suggestions.append(str(value[0]))

        unique_suggestions = list(dict.fromkeys(suggestions))[:limit]

        return {
            'suggestions': unique_suggestions,
            'query': query,
        }

    @staticmethod
    def get_recent_searches(user_id, limit=5):
        """Get recent searches for a user."""
        searches = db.session.query(RecentSearch).filter_by(user_id=user_id).order_by(
            RecentSearch.creado_en.desc()
        ).limit(limit).all()
        return [s.to_dict() for s in searches]

    @staticmethod
    def save_search(user_id, query):
        """Save a search query for a user."""
        if not query or not query.strip():
            return None

        query = query.strip()

        existing = db.session.query(RecentSearch).filter_by(
            user_id=user_id,
            query=query
        ).first()

        if existing:
            existing.creado_en = datetime.utcnow()
            db.session.commit()
            return existing

        search = RecentSearch(user_id=user_id, query=query)
        db.session.add(search)
        db.session.commit()
        return search

    @staticmethod
    def _empty_results():
        """Return empty results structure."""
        return {
            'query': '',
            'total_results': 0,
            'results': {},
            'facets': {
                'areas': {},
                'statuses': {},
                'entity_counts': {},
            },
            'pagination': {
                'page': 1,
                'limit': 20,
                'total_pages': 0,
            },
        }

    @staticmethod
    def get_searchable_entities():
        """Get configuration of searchable entities."""
        return SearchService.SEARCHABLE_ENTITIES

    @staticmethod
    def get_available_areas():
        """Get available laboratory areas."""
        areas = Area.query.all()
        return [{'id': a.id, 'sigla': a.sigla, 'nombre': a.nombre} for a in areas]

    @staticmethod
    def get_available_statuses():
        """Get available statuses for each entity type."""
        return {
            'entradas': [getattr(EntradaStatus, attr) for attr in dir(EntradaStatus) if not attr.startswith('_')],
            'informes': [s.value for s in InformeStatus],
        }
