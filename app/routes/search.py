"""Search routes - Global Search API endpoints.

Phase 6 Issue #56 - Global Search System
"""

import logging

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.database.models import Cliente, OrdenTrabajo, Pedido
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)

bp = Blueprint('search', __name__)

MAX_QUERY_LENGTH = 200


@bp.route('/api/search')
@login_required
def search():
    """
    Global search endpoint with filtering and categorization.
    
    Query parameters:
        q: Search query string (required)
        entities: Comma-separated list of entity types to search
        date_from: Start date filter (ISO format)
        date_to: End date filter (ISO format)
        area: Laboratory area filter (FQ, MB, ES, OS)
        status: Status filter
        page: Page number (default: 1)
        limit: Results per page (default: 20, max: 100)
    
    Returns:
        JSON with search results categorized by entity type
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({
            'results': [],
            'message': 'No search query provided'
        })
    
    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({
            'results': [],
            'message': f'Query exceeds maximum length of {MAX_QUERY_LENGTH} characters'
        }), 400
    
    entities_param = request.args.get('entities')
    entities = None
    if entities_param:
        entities = [e.strip() for e in entities_param.split(',') if e.strip()]
    
    filters = {}
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to
    
    area = request.args.get('area')
    if area:
        filters['area'] = area
    
    status = request.args.get('status')
    if status:
        filters['status'] = status
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        page = 1
        limit = 20
    
    page = max(1, page)
    limit = min(max(1, limit), 100)
    
    try:
        results = SearchService.search(
            query=query,
            entities=entities,
            filters=filters if filters else None,
            page=page,
            limit=limit
        )
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search error: {type(e).__name__}")
        return jsonify({
            'error': 'An error occurred while processing your search',
            'results': {},
            'message': 'Search error occurred'
        }), 500


@bp.route('/api/search/autocomplete')
@login_required
def autocomplete():
    """
    Autocomplete suggestions endpoint.
    
    Query parameters:
        q: Partial query string (min 2 characters)
        limit: Max suggestions (default: 10)
    
    Returns:
        JSON with autocomplete suggestions
    """
    query = request.args.get('q', '')
    
    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({
            'suggestions': [],
            'query': query[:MAX_QUERY_LENGTH],
            'message': f'Query exceeds maximum length of {MAX_QUERY_LENGTH} characters'
        }), 400
    
    if len(query) < 2:
        return jsonify({
            'suggestions': [],
            'query': query
        })
    
    try:
        limit = int(request.args.get('limit', 10))
        limit = min(max(1, limit), 20)
    except ValueError:
        limit = 10
    
    try:
        suggestions = SearchService.get_autocomplete_suggestions(query, limit)
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Autocomplete error: {type(e).__name__}")
        return jsonify({
            'suggestions': [],
            'query': query,
            'message': 'An error occurred while fetching suggestions'
        }), 500


@bp.route('/api/search/entities')
@login_required
def search_entities():
    """
    Get available searchable entities configuration.
    
    Returns:
        JSON with entity configuration
    """
    try:
        entities = SearchService.get_searchable_entities()
        
        config = {}
        for entity_type, entity_config in entities.items():
            config[entity_type] = {
                'search_fields': entity_config['search_fields'],
                'priority': entity_config['priority']
            }
        
        return jsonify({
            'entities': config
        })
    except Exception as e:
        logger.error(f"Search entities error: {type(e).__name__}")
        return jsonify({
            'entities': {},
            'message': 'An error occurred while fetching entity configuration'
        }), 500


@bp.route('/api/search/filters')
@login_required
def search_filters():
    """
    Get available filter options.
    
    Returns:
        JSON with available areas and statuses
    """
    try:
        areas = SearchService.get_available_areas()
        statuses = SearchService.get_available_statuses()
        
        return jsonify({
            'areas': areas,
            'statuses': statuses
        })
    except Exception as e:
        logger.error(f"Search filters error: {type(e).__name__}")
        return jsonify({
            'areas': [],
            'statuses': [],
            'message': 'An error occurred while fetching filter options'
        }), 500


@bp.route('/api/search/legacy')
@login_required
def search_legacy():
    """Legacy search endpoint - redirects to new format."""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'results': []})
    
    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({
            'results': [],
            'message': f'Query exceeds maximum length of {MAX_QUERY_LENGTH} characters'
        }), 400
    
    results = []
    
    try:
        pedidos = Pedido.query.filter(
            or_(
                Pedido.numero_pedido.ilike(f'%{query}%'),
                Pedido.descripcion.ilike(f'%{query}%')
            )
        ).limit(5).all()

        clientes = Cliente.query.filter(
            or_(
                Cliente.nombre.ilike(f'%{query}%'),
                Cliente.codigo.ilike(f'%{query}%')
            )
        ).limit(5).all()

        ordenes = OrdenTrabajo.query.filter(
            or_(
                OrdenTrabajo.numero.ilike(f'%{query}%'),
                OrdenTrabajo.descripcion.ilike(f'%{query}%')
            )
        ).limit(5).all()

        for pedido in pedidos:
            results.append({
                'title': f'Pedido #{pedido.numero_pedido}',
                'description': pedido.descripcion[:100] + '...' if pedido.descripcion and len(pedido.descripcion) > 100 else pedido.descripcion or '',
                'url': f'/pedidos/{pedido.id}',
                'type': 'pedido'
            })

        for cliente in clientes:
            results.append({
                'title': cliente.nombre,
                'description': f'Codigo: {cliente.codigo}',
                'url': f'/clientes/{cliente.id}',
                'type': 'cliente'
            })

        for orden in ordenes:
            results.append({
                'title': f'Orden #{orden.numero}',
                'description': orden.descripcion[:100] + '...' if orden.descripcion and len(orden.descripcion) > 100 else orden.descripcion or '',
                'url': f'/ordenes/{orden.id}',
                'type': 'orden'
            })

    except Exception as e:
        logger.error(f"Legacy search error: {type(e).__name__}")
        return jsonify({
            'results': [],
            'message': 'An error occurred while performing the search'
        }), 500

    return jsonify({
        'results': results[:10]
    })


@bp.route('/api/search/recent', methods=['GET'])
@login_required
def get_recent_searches():
    """
    Get recent searches for the current user.
    
    Query parameters:
        limit: Max number of searches (default: 10, max: 10)
    
    Returns:
        JSON with list of recent searches
    """
    try:
        limit = int(request.args.get('limit', 10))
        limit = min(max(1, limit), 10)
    except ValueError:
        limit = 10
    
    try:
        searches = SearchService.get_recent_searches(current_user.id, limit)
        return jsonify({
            'searches': searches
        })
    except Exception as e:
        logger.error(f"Get recent searches error: {type(e).__name__}")
        return jsonify({
            'searches': [],
            'message': 'An error occurred while fetching recent searches'
        }), 500


@bp.route('/api/search/recent', methods=['POST'])
@login_required
def save_recent_search():
    """
    Save a search query for the current user.
    
    Request body:
        query: Search query string (required)
    
    Returns:
        JSON confirming the operation
    """
    data = request.get_json()
    query = data.get('query') if data else None
    
    if not query or not query.strip():
        return jsonify({
            'success': False,
            'message': 'Query is required'
        }), 400
    
    try:
        search = SearchService.save_search(current_user.id, query)
        if search:
            return jsonify({
                'success': True,
                'message': 'Search saved successfully',
                'search': search.to_dict() if hasattr(search, 'to_dict') else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save search'
            }), 500
    except Exception as e:
        logger.error(f"Save search error: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while saving the search'
        }), 500
