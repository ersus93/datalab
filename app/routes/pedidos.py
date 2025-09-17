"""Routes for handling orders (pedidos)."""
from flask import Blueprint, render_template, request, jsonify
from app.database.models.pedido import Pedido
from app.database.models.cliente import Cliente
from app import db

bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

@bp.route('/', methods=['GET'])
def index():
    """Show orders list and creation form."""
    return render_template('pages/pedidos/index.html')

@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_pedido():
    """Create a new order."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validar datos
            if not data.get('numero_pedido'):
                return jsonify({'success': False, 'error': 'Número de pedido es requerido'}), 400
                
            if not data.get('cliente_id'):
                return jsonify({'success': False, 'error': 'Debe seleccionar un cliente'}), 400
                
            # Crear nuevo pedido
            pedido = Pedido(
                numero_pedido=data['numero_pedido'],
                descripcion=data.get('descripcion', ''),
                cliente_id=data['cliente_id'],
                estado='pendiente'
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Pedido creado exitosamente',
                'pedido_id': pedido.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
            
    return jsonify({'success': False, 'error': 'Método no permitido'}), 405

@bp.route('/clientes', methods=['GET'])
def obtener_clientes():
    """Get clients list for dropdown."""
    try:
        clientes = Cliente.query.all()
        return jsonify({
            'success': True,
            'clientes': [{
                'id': c.id,
                'nombre': f"{c.nombre} {c.apellido}",
                'identificacion': c.identificacion or ''
            } for c in clientes]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
