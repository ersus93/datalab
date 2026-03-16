"""Rutas CRUD para catálogo de productos."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _

from app import db
from app.database.models import Producto, Rama, Destino, Ensayo, EnsayoES, EnsayoXProducto, EnsayoESXProducto
from app.forms.producto import ProductoForm
from app.decorators import admin_required, laboratory_manager_required

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')


@productos_bp.route('/')
@login_required
def listar():
    """Listar productos con paginación y filtros."""
    page = request.args.get('page', 1, type=int)
    rama_id = request.args.get('rama', type=int)
    destino_id = request.args.get('destino', type=int)
    con_ensayos = request.args.get('con_ensayos')
    q = request.args.get('q', '')
    
    query = Producto.query
    
    if rama_id:
        query = query.filter_by(rama_id=rama_id)
    if destino_id:
        query = query.filter_by(destino_id=destino_id)
    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))
    if con_ensayos == '1':
        query = query.filter(Producto.ensayos.any())
    elif con_ensayos == '0':
        query = query.filter(~Producto.ensayos.any())
    
    productos = query.order_by(Producto.nombre).paginate(
        page=page, per_page=25, error_out=False
    )
    
    # Datos para filtros
    ramas = Rama.query.all()
    destinos = Destino.query.all()
    
    return render_template('productos/listar.html',
                         productos=productos,
                         ramas=ramas,
                         destinos=destinos,
                         q=q)


@productos_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de producto."""
    producto = Producto.query.get_or_404(id)
    
    # Ensayos asignados
    ensayos_fq = producto.ensayos.all()
    
    # Ensayos ES asignados
    ensayos_es_ids = db.session.query(EnsayoESXProducto.ensayo_es_id).filter_by(producto_id=id).all()
    ensayos_es_ids = [e[0] for e in ensayos_es_ids]
    ensayos_es = EnsayoES.query.filter(EnsayoES.id.in_(ensayos_es_ids)).all() if ensayos_es_ids else []
    
    return render_template('productos/ver.html',
                         producto=producto,
                         ensayos_fq=ensayos_fq,
                         ensayos_es=ensayos_es)


@productos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def nuevo():
    """Crear nuevo producto."""
    form = ProductoForm()
    
    if form.validate_on_submit():
        producto = Producto(
            nombre=form.nombre.data,
            rama_id=form.rama_id.data or None,
            destino_id=form.destino_id.data or None,
            activo=form.activo.data
        )
        
        db.session.add(producto)
        db.session.commit()
        
        flash(_('Producto creado exitosamente.'), 'success')
        return redirect(url_for('productos.ver', id=producto.id))
    
    return render_template('productos/form.html',
                         form=form,
                         titulo=_('Nuevo Producto'))


@productos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def editar(id):
    """Editar producto existente."""
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.rama_id = form.rama_id.data or None
        producto.destino_id = form.destino_id.data or None
        producto.activo = form.activo.data
        
        db.session.commit()
        
        flash(_('Producto actualizado exitosamente.'), 'success')
        return redirect(url_for('productos.ver', id=producto.id))
    
    return render_template('productos/form.html',
                         form=form,
                         producto=producto,
                         titulo=_('Editar Producto'))


@productos_bp.route('/<int:id>/ensayos', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def gestionar_ensayos(id):
    """Gestionar asociación de ensayos al producto."""
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obtener ensayos seleccionados
        ensayos_fq_ids = request.form.getlist('ensayos_fq', type=int)
        ensayos_es_ids = request.form.getlist('ensayos_es', type=int)
        
        # Limpiar asociaciones actuales FQ
        EnsayoXProducto.query.filter_by(producto_id=id).delete()
        
        # Limpiar asociaciones actuales ES
        EnsayoESXProducto.query.filter_by(producto_id=id).delete()
        
        # Crear nuevas asociaciones FQ
        for ensayo_id in ensayos_fq_ids:
            asoc = EnsayoXProducto(producto_id=id, ensayo_id=ensayo_id)
            db.session.add(asoc)
        
        # Crear nuevas asociaciones ES
        for ensayo_es_id in ensayos_es_ids:
            asoc = EnsayoESXProducto(producto_id=id, ensayo_es_id=ensayo_es_id)
            db.session.add(asoc)
        
        db.session.commit()
        flash(_('Ensayos actualizados exitosamente.'), 'success')
        return redirect(url_for('productos.ver', id=id))
    
    # Obtener todos los ensayos disponibles
    ensayos_fq = Ensayo.query.filter_by(activo=True).order_by(Ensayo.nombre_corto).all()
    ensayos_es = EnsayoES.query.filter_by(activo=True).order_by(EnsayoES.nombre_corto).all()
    
    # Ensayos ya asignados FQ
    asignados_fq = {e.id for e in producto.ensayos}
    
    # Ensayos ya asignados ES
    asignados_es_ids = db.session.query(EnsayoESXProducto.ensayo_es_id).filter_by(producto_id=id).all()
    asignados_es = {e[0] for e in asignados_es_ids}
    
    return render_template('productos/ensayos.html',
                         producto=producto,
                         ensayos_fq=ensayos_fq,
                         ensayos_es=ensayos_es,
                         asignados_fq=asignados_fq,
                         asignados_es=asignados_es)
