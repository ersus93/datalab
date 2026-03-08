"""Search routes - Global Search API endpoints.

Phase 6 Issue #56 - Global Search System
"""

import json
from flask import Blueprint, jsonify, request
from app.services.search_service import SearchService
from app.database.models import Pedido, Cliente, OrdenTrabajo
from sqlalchemy import or_

bp = Blueprint('search', __name__)


@bp.route('/api/search')
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
    
    # Parse entities parameter
    entities_param = request.args.get('entities')
    entities = None
    if entities_param:
        entities = [e.strip() for e in entities_param.split(',') if e.strip()]
    
    # Parse filters
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
    
    # Pagination
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        page = 1
        limit = 20
    
    # Validate limits
    page = max(1, page)
    limit = min(max(1, limit), 100)
    
    # Perform search using SearchService
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
        return jsonify({
            'error': str(e),
            'results': {},
            'message': 'Search error occurred'
        }), 500


@bp.route('/api/search/autocomplete')
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
    
    suggestions = SearchService.get_autocomplete_suggestions(query, limit)
    return jsonify(suggestions)


@bp.route('/api/search/entities')
def search_entities():
    """
    Get available searchable entities configuration.
    
    Returns:
        JSON with entity configuration
    """
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


@bp.route('/api/search/filters')
def search_filters():
    """
    Get available filter options.
    
    Returns:
        JSON with available areas and statuses
    """
    areas = SearchService.get_available_areas()
    statuses = SearchService.get_available_statuses()
    
    return jsonify({
        'areas': areas,
        'statuses': statuses
    })


# Legacy endpoint for backward compatibility
@bp.route('/api/search/legacy')
def search_legacy():
    """Legacy search endpoint - redirects to new format."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})

    results = []

    try:
        # Buscar en pedidos
        pedidos = Pedido.query.filter(
            or_(
                Pedido.numero_pedido.ilike(f'%{query}%'),
                Pedido.descripcion.ilike(f'%{query}%')
            )
        ).limit(5).all()

        # Buscar en clientes
        clientes = Cliente.query.filter(
            or_(
                Cliente.nombre.ilike(f'%{query}%'),
                Cliente.codigo.ilike(f'%{query}%')
            )
        ).limit(5).all()

        # Buscar en ordenes de trabajo
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

    except Exception:
        results = []

    return jsonify({
        'results': results[:10]
    })
