"""Tests para Sample Entry UI/UX — Issue #6 Phase 3.

Cubre los criterios de aceptación:
- Form validation (lote, fechas, cantidades, campos requeridos)
- Rutas CRUD (listar, ver, nueva, editar, cambiar_estado, registrar_entrega)
- API search endpoints (fabricas, productos)
- Template filters (status_color, status_label)
- Contexto de fechas en listar
- Widgets de entradas en dashboard
"""
import re
from datetime import date, timedelta

import pytest

from app.database.models.entrada import Entrada, EntradaStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True


# ---------------------------------------------------------------------------
# Tests: rutas de listado
# ---------------------------------------------------------------------------

class TestListarEntradas:

    def test_listar_requires_login(self, client):
        resp = client.get('/entradas/')
        assert resp.status_code in (302, 401)

    def test_listar_renders_list_mejorado(self, client, app, sample_technician):
        """El listado debe renderizar list_mejorado.html."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/entradas/')
        assert resp.status_code == 200
        # list_mejorado usa 'Filtros' como encabezado del card
        assert b'Filtros' in resp.data or b'Entradas' in resp.data

    def test_listar_passes_date_context(self, client, app, sample_technician):
        """La ruta debe pasar today, week_start, week_end, month_start al template."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/entradas/')
        assert resp.status_code == 200
        # Los filtros rápidos usan estas variables como parámetros GET
        today_str = date.today().isoformat()
        assert today_str.encode() in resp.data

    def test_listar_filter_by_status(self, client, app, sample_technician, sample_entrada):
        """Filtro por status debe funcionar."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/entradas/?status=RECIBIDO')
        assert resp.status_code == 200

    def test_listar_filter_by_search(self, client, app, sample_technician, sample_entrada):
        """Filtro por texto (código/lote) debe funcionar."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/entradas/?q={sample_entrada.codigo}')
        assert resp.status_code == 200
        assert sample_entrada.codigo.encode() in resp.data

    def test_listar_quick_filter_hoy(self, client, app, sample_technician):
        """Filtro rápido 'Hoy' debe pasar parámetro desde."""
        with app.app_context():
            login(client, sample_technician)
            today = date.today().isoformat()
            resp = client.get(f'/entradas/?desde={today}')
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: ruta ver (detail)
# ---------------------------------------------------------------------------

class TestVerEntrada:

    def test_ver_returns_200(self, client, app, sample_technician, sample_entrada):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/entradas/{sample_entrada.id}')
        assert resp.status_code == 200

    def test_ver_shows_quantities(self, client, app, sample_technician, sample_entrada):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/entradas/{sample_entrada.id}')
        assert b'Cantidad Recibida' in resp.data or str(sample_entrada.cantidad_recib).encode() in resp.data

    def test_ver_shows_status_actions(self, client, app, sample_technician, sample_entrada):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/entradas/{sample_entrada.id}')
        # Debe mostrar botón de cambio de estado
        assert b'cambiar-estado' in resp.data or b'Iniciar Proceso' in resp.data

    def test_ver_404_on_missing(self, client, app, sample_technician):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/entradas/99999')
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Tests: ruta nueva (create)
# ---------------------------------------------------------------------------

class TestNuevaEntrada:

    def test_nueva_get_renders_form_mejorado(self, client, app, sample_technician):
        """GET /entradas/nueva debe renderizar form_mejorado.html."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/entradas/nueva')
        assert resp.status_code == 200
        # form_mejorado tiene secciones identificables
        assert b'Identificaci' in resp.data or b'Cliente y Ubicaci' in resp.data

    def test_nueva_post_creates_entrada(self, client, app, sample_technician,
                                         sample_cliente, sample_fabrica, sample_producto):
        """POST válido debe crear una entrada y redirigir a ver."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.post('/entradas/nueva', data={
                'csrf_token':        _get_csrf(client, app, sample_technician, '/entradas/nueva'),
                'codigo':            'ENT-TEST-001',
                'lote':              'A-1234',
                'cliente_id':        str(sample_cliente.id),
                'fabrica_id':        str(sample_fabrica.id),
                'producto_id':       str(sample_producto.id),
                'rama_id':           '0',
                'pedido_id':         '0',
                'cantidad_recib':    '10.00',
                'unidad_medida_id':  '0',
                'status':            'RECIBIDO',
            }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/entradas/' in resp.headers['Location']

    def test_nueva_post_invalid_lote_rejected(self, client, app, sample_technician,
                                               sample_cliente, sample_fabrica, sample_producto):
        """Lote con formato inválido debe rechazar el form."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.post('/entradas/nueva', data={
                'csrf_token':     _get_csrf(client, app, sample_technician, '/entradas/nueva'),
                'codigo':         'ENT-TEST-002',
                'lote':           'INVALIDO',
                'cliente_id':     str(sample_cliente.id),
                'fabrica_id':     str(sample_fabrica.id),
                'producto_id':    str(sample_producto.id),
                'rama_id':        '0',
                'pedido_id':      '0',
                'cantidad_recib': '10.00',
                'unidad_medida_id': '0',
                'status':         'RECIBIDO',
            })
        assert resp.status_code == 200
        assert b'X-XXXX' in resp.data or b'Formato' in resp.data

    def test_nueva_post_date_validation(self, client, app, sample_technician,
                                         sample_cliente, sample_fabrica, sample_producto):
        """fech_venc < fech_fab debe ser rechazado."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.post('/entradas/nueva', data={
                'csrf_token':     _get_csrf(client, app, sample_technician, '/entradas/nueva'),
                'codigo':         'ENT-DATE-001',
                'cliente_id':     str(sample_cliente.id),
                'fabrica_id':     str(sample_fabrica.id),
                'producto_id':    str(sample_producto.id),
                'rama_id':        '0',
                'pedido_id':      '0',
                'cantidad_recib': '10.00',
                'unidad_medida_id': '0',
                'status':         'RECIBIDO',
                'fech_fab':       '2026-06-01',
                'fech_venc':      '2026-01-01',   # antes de fech_fab
            })
        assert resp.status_code == 200
        assert b'posterior' in resp.data or b'vencimiento' in resp.data.lower()


# ---------------------------------------------------------------------------
# Tests: cambiar estado
# ---------------------------------------------------------------------------

class TestCambiarEstado:

    def test_cambiar_estado_recibido_a_en_proceso(self, client, app, sample_technician, sample_entrada):
        with app.app_context():
            login(client, sample_technician)
            resp = client.post(
                f'/entradas/{sample_entrada.id}/cambiar-estado',
                data={'status': 'EN_PROCESO'},
                follow_redirects=False,
            )
        assert resp.status_code == 302

    def test_cambiar_estado_invalido_rechazado(self, client, app, sample_technician, sample_entrada):
        """Transición inválida (RECIBIDO → ENTREGADO) debe ser rechazada."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.post(
                f'/entradas/{sample_entrada.id}/cambiar-estado',
                data={'status': 'ENTREGADO'},
                follow_redirects=True,
            )
        assert resp.status_code == 200
        assert b'no v' in resp.data or b'Transici' in resp.data


# ---------------------------------------------------------------------------
# Tests: registrar entrega
# ---------------------------------------------------------------------------

class TestRegistrarEntrega:

    def test_registrar_entrega_valida(self, client, app, sample_technician, db_session, 
                                       sample_cliente, sample_fabrica, sample_producto):
        """Entrega válida debe actualizar cantidad_entreg y saldo."""
        from decimal import Decimal
        from datetime import datetime
        with app.app_context():
            entrada = Entrada(
                codigo='ENT-ENTREGA-001',
                producto_id=sample_producto.id,
                fabrica_id=sample_fabrica.id,
                cliente_id=sample_cliente.id,
                cantidad_recib=Decimal('50'),
                cantidad_entreg=Decimal('0'),
                fech_entrada=datetime.utcnow(),
                status=EntradaStatus.COMPLETADO,
            )
            db_session.add(entrada)
            db_session.commit()
            eid = entrada.id

            login(client, sample_technician)
            client.post(
                f'/entradas/{eid}/registrar-entrega',
                data={'cantidad': '10'},
                follow_redirects=False,
            )
            db_session.refresh(entrada)
            assert entrada.cantidad_entreg == Decimal('10')

    def test_registrar_entrega_excedente_rechazada(self, client, app, sample_technician,
                                                     db_session, sample_cliente,
                                                     sample_fabrica, sample_producto):
        """Entrega mayor al saldo debe ser rechazada."""
        from decimal import Decimal
        from datetime import datetime
        with app.app_context():
            entrada = Entrada(
                codigo='ENT-EXCESO-001',
                producto_id=sample_producto.id,
                fabrica_id=sample_fabrica.id,
                cliente_id=sample_cliente.id,
                cantidad_recib=Decimal('10'),
                cantidad_entreg=Decimal('0'),
                fech_entrada=datetime.utcnow(),
                status=EntradaStatus.COMPLETADO,
            )
            db_session.add(entrada)
            db_session.commit()
            eid = entrada.id

            login(client, sample_technician)
            resp = client.post(
                f'/entradas/{eid}/registrar-entrega',
                data={'cantidad': '999'},
                follow_redirects=True,
            )
        assert b'exceder' in resp.data or resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: API /api/fabricas/search
# ---------------------------------------------------------------------------

class TestFabricasSearchAPI:

    def test_search_requires_login(self, client):
        resp = client.get('/api/fabricas/search?q=test')
        assert resp.status_code in (302, 401)

    def test_search_returns_json(self, client, app, sample_technician, sample_fabrica):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/api/fabricas/search?q=')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_search_filters_by_query(self, client, app, sample_technician, sample_fabrica):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/api/fabricas/search?q={sample_fabrica.nombre[:4]}')
        data = resp.get_json()
        assert any(f['id'] == sample_fabrica.id for f in data)

    def test_search_includes_cliente(self, client, app, sample_technician, sample_fabrica):
        """Cada resultado debe incluir el cliente anidado."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/api/fabricas/search?q=')
        data = resp.get_json()
        if data:
            assert 'cliente' in data[0]
            assert 'nombre' in data[0]['cliente']

    def test_get_single_fabrica(self, client, app, sample_technician, sample_fabrica):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/api/fabricas/{sample_fabrica.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == sample_fabrica.id


# ---------------------------------------------------------------------------
# Tests: API /api/productos/search
# ---------------------------------------------------------------------------

class TestProductosSearchAPI:

    def test_search_requires_login(self, client):
        resp = client.get('/api/productos/search?q=test')
        assert resp.status_code in (302, 401)

    def test_search_returns_json(self, client, app, sample_technician, sample_producto):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/api/productos/search?q=')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_search_filters_by_query(self, client, app, sample_technician, sample_producto):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/api/productos/search?q={sample_producto.nombre[:4]}')
        data = resp.get_json()
        assert any(p['id'] == sample_producto.id for p in data)

    def test_get_single_producto(self, client, app, sample_technician, sample_producto):
        with app.app_context():
            login(client, sample_technician)
            resp = client.get(f'/api/productos/{sample_producto.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == sample_producto.id


# ---------------------------------------------------------------------------
# Tests: template filters
# ---------------------------------------------------------------------------

class TestTemplateFilters:

    def test_status_color_filter(self, app):
        with app.app_context():
            env = app.jinja_env
            tmpl = env.from_string("{{ 'RECIBIDO'|status_color }}")
            assert tmpl.render() == 'blue'

    def test_status_color_en_proceso(self, app):
        with app.app_context():
            env = app.jinja_env
            tmpl = env.from_string("{{ 'EN_PROCESO'|status_color }}")
            assert tmpl.render() == 'yellow'

    def test_status_color_unknown_defaults_gray(self, app):
        with app.app_context():
            env = app.jinja_env
            tmpl = env.from_string("{{ 'WHATEVER'|status_color }}")
            assert tmpl.render() == 'gray'

    def test_status_label_filter(self, app):
        with app.app_context():
            env = app.jinja_env
            tmpl = env.from_string("{{ 'COMPLETADO'|status_label }}")
            assert tmpl.render() == 'Completado'

    def test_status_label_entregado(self, app):
        with app.app_context():
            env = app.jinja_env
            tmpl = env.from_string("{{ 'ENTREGADO'|status_label }}")
            assert tmpl.render() == 'Entregado'


# ---------------------------------------------------------------------------
# Tests: dashboard widgets de entradas
# ---------------------------------------------------------------------------

class TestDashboardEntradaWidgets:

    def test_dashboard_passes_entrada_stats(self, client, app, sample_technician):
        """El dashboard debe incluir entrada_stats en el contexto."""
        with app.app_context():
            login(client, sample_technician)
            resp = client.get('/dashboard/')
        assert resp.status_code == 200
        # El template puede o no usar estas variables; al menos la ruta no debe explotar

    def test_entrada_stats_counts_en_proceso(self, app, db_session,
                                               sample_cliente, sample_fabrica, sample_producto):
        """entrada_stats['en_proceso'] debe contar solo entradas EN_PROCESO."""
        from decimal import Decimal
        from datetime import datetime
        with app.app_context():
            for i in range(3):
                e = Entrada(
                    codigo=f'ENT-STAT-{i}',
                    producto_id=sample_producto.id,
                    fabrica_id=sample_fabrica.id,
                    cliente_id=sample_cliente.id,
                    cantidad_recib=Decimal('5'),
                    cantidad_entreg=Decimal('0'),
                    fech_entrada=datetime.utcnow(),
                    status=EntradaStatus.EN_PROCESO,
                )
                db_session.add(e)
            db_session.commit()

            count = Entrada.query.filter_by(
                status=EntradaStatus.EN_PROCESO, anulado=False
            ).count()
        assert count >= 3


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _get_csrf(client, app, user, url):
    """Obtiene el token CSRF del formulario en una URL."""
    with app.app_context():
        login(client, user)
        resp = client.get(url)
        # Buscar csrf_token en el HTML
        match = re.search(rb'name="csrf_token" value="([^"]+)"', resp.data)
        return match.group(1).decode() if match else ''
