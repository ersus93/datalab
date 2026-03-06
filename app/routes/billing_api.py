"""
Billing API - Rutas para tracking de uso y facturación
"""
# Web route
@billing_bp.route("/web", methods=["GET"])
@login_required
def billing_index():
    from app.services.billing_service import BillingService
    from app.database.models.utilizado import Utilizado, Factura, UtilizadoStatus
    
    pendientes = BillingService.get_utilizados_pendientes_facturacion()
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).limit(50).all()
    resumen = BillingService.get_resumen_por_tipo_ensayo()
    
    return render_template("billing/index.html",
        pendientes=pendientes,
        pendientes_count=len(pendientes),
        total_pendiente=sum(float(u.importe) for u in pendientes),
        facturas=facturas,
        resumen=resumen.get("items", []))


from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.services.billing_service import BillingService
from app.database.models.utilizado import Utilizado, Factura, UtilizadoStatus
from app.database.models.cliente import Cliente
from app import db

billing_bp = Blueprint('billing', __name__, url_prefix='/api/billing')


@billing_bp.route('/utilizados', methods=['GET'])
@login_required
def list_utilizados():
    """Lista registros de uso con filtros."""
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado')
    mes = request.args.get('mes')
    
    if cliente_id:
        utilizados = BillingService.get_utilizados_por_cliente(cliente_id, estado, mes)
    else:
        query = Utilizado.query
        if estado:
            query = query.filter(Utilizado.estado == estado)
        if mes:
            query = query.filter(Utilizado.mes_facturacion == mes)
        utilizados = query.all()
    
    return jsonify({
        'utilizados': [u.to_dict() for u in utilizados],
        'total': len(utilizados)
    })


@billing_bp.route('/utilizados', methods=['POST'])
@login_required
def crear_utilizado():
    """Crea un nuevo registro de uso."""
    data = request.get_json()
    
    try:
        utilizado = BillingService.crear_utilizado(
            entrada_id=data['entrada_id'],
            ensayo_id=data['ensayo_id'],
            cantidad=data.get('cantidad', 1),
            precio_unitario=data.get('precio_unitario', 0),
            detalle_ensayo_id=data.get('detalle_ensayo_id')
        )
        return jsonify({'success': True, 'utilizado': utilizado.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@billing_bp.route('/utilizados/<int:id>', methods=['PUT'])
@login_required
def actualizar_utilizado(id):
    """Actualiza un registro de uso."""
    utilizado = Utilizado.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'cantidad' in data:
            utilizado.cantidad = data['cantidad']
        if 'precio_unitario' in data:
            utilizado.precio_unitario = data['precio_unitario']
        if 'estado' in data:
            utilizado.estado = data['estado']
        
        utilizado.calcular_importe()
        db.session.commit()
        
        return jsonify({'success': True, 'utilizado': utilizado.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@billing_bp.route('/pendientes', methods=['GET'])
@login_required
def list_pendientes():
    """Lista registros pendientes de facturación."""
    cliente_id = request.args.get('cliente_id', type=int)
    mes = request.args.get('mes')
    
    utilizados = BillingService.get_utilizados_pendientes_facturacion(cliente_id, mes)
    
    return jsonify({
        'utilizados': [u.to_dict() for u in utilizados],
        'total': len(utilizados),
        'importe_total': sum(float(u.importe) for u in utilizados)
    })


@billing_bp.route('/facturas', methods=['GET'])
@login_required
def list_facturas():
    """Lista facturas con filtros."""
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado')
    
    query = Factura.query
    if cliente_id:
        query = query.filter(Factura.cliente_id == cliente_id)
    if estado:
        query = query.filter(Factura.estado == estado)
    
    facturas = query.order_by(Factura.fecha_emision.desc()).all()
    
    return jsonify({
        'facturas': [f.to_dict() for f in facturas],
        'total': len(facturas)
    })


@billing_bp.route('/facturas', methods=['POST'])
@login_required
def crear_factura():
    """Genera una factura desde registros de uso."""
    data = request.get_json()
    
    try:
        factura = BillingService.generar_factura(
            cliente_id=data['cliente_id'],
            utilizado_ids=data['utilizado_ids'],
            numero_factura=data['numero_factura']
        )
        return jsonify({'success': True, 'factura': factura.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@billing_bp.route('/facturas/<int:id>', methods=['GET'])
@login_required
def get_factura(id):
    """Obtiene detalle de una factura."""
    factura = Factura.query.get_or_404(id)
    return jsonify(factura.to_dict())


@billing_bp.route('/resumen/por-ensayo', methods=['GET'])
@login_required
def resumen_por_ensayo():
    """Resumen de usage por tipo de ensayo."""
    cliente_id = request.args.get('cliente_id', type=int)
    mes = request.args.get('mes')
    
    resumen = BillingService.get_resumen_por_tipo_ensayo(cliente_id, mes)
    return jsonify(resumen)


@billing_bp.route('/reporte', methods=['GET'])
@login_required
def reporte():
    """Reporte de facturación."""
    cliente_id = request.args.get('cliente_id', type=int)
    
    reporte = BillingService.get_reporte_facturacion(cliente_id)
    return jsonify(reporte)
