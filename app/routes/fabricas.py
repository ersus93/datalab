"""Rutas CRUD para gestión de fábricas."""
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from sqlalchemy.orm import joinedload

from app import db
from app.database.models import Fabrica, Cliente, Provincia
from app.database.models.entrada import Entrada
from app.forms.fabrica import FabricaForm
from app.decorators import admin_required, laboratory_manager_required

fabricas_bp = Blueprint('fabricas', __name__, url_prefix='/fabricas')


@fabricas_bp.route('/')
@login_required
def listar():
    """Listar fábricas con paginación y filtros."""
    page = request.args.get('page', 1, type=int)
    cliente_id = request.args.get('cliente', type=int)
    provincia_id = request.args.get('provincia', type=int)
    q = request.args.get('q', '')
    
    query = Fabrica.query
    
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    if provincia_id:
        query = query.filter_by(provincia_id=provincia_id)
    if q:
        query = query.filter(Fabrica.nombre.ilike(f'%{q}%'))
    
    fabricas = query.order_by(Fabrica.nombre).paginate(
        page=page, per_page=25, error_out=False
    )
    
    # Datos para filtros
    clientes = Cliente.query.filter_by(activo=True).all()
    provincias = Provincia.query.all()
    
    # Estadísticas por provincia
    stats_provincia = {}
    for p in provincias:
        stats_provincia[p.id] = Fabrica.query.filter_by(provincia_id=p.id).count()
    
    return render_template('fabricas/listar.html',
                         fabricas=fabricas,
                         clientes=clientes,
                         provincias=provincias,
                         stats_provincia=stats_provincia)


@fabricas_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de fábrica."""
    fabrica = Fabrica.query.get_or_404(id)
    
    # Obtener últimas 10 entradas de esta fábrica con eager loading
    ultimas_entradas = (
        Entrada.query
        .options(joinedload(Entrada.producto))
        .filter_by(fabrica_id=id)
        .filter_by(anulado=False)
        .order_by(Entrada.fech_entrada.desc())
        .limit(10)
        .all()
    )
    
    # Estadísticas
    current_year = datetime.now().year
    stats = {
        'total_muestras': Entrada.query.filter_by(fabrica_id=id, anulado=False).count(),
        'muestras_anio': Entrada.query.filter(
            Entrada.fabrica_id == id,
            Entrada.anulado == False,
            db.func.extract('year', Entrada.fech_entrada) == current_year
        ).count(),
        'ensayos_pendientes': 0,  # Phase 3+
        'ultimas_entradas': ultimas_entradas
    }
    
    return render_template('fabricas/ver.html',
                         fabrica=fabrica,
                         stats=stats)


@fabricas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def nueva():
    """Crear nueva fábrica."""
    form = FabricaForm()
    
    # Pre-llenar cliente si viene de cliente específico
    cliente_id = request.args.get('cliente_id', type=int)
    if cliente_id:
        form.cliente_id.data = cliente_id
    
    if form.validate_on_submit():
        fabrica = Fabrica(
            cliente_id=form.cliente_id.data,
            nombre=form.nombre.data,
            provincia_id=form.provincia_id.data or None,
            activo=form.activo.data
        )
        
        db.session.add(fabrica)
        db.session.commit()
        
        flash(_('Fábrica creada exitosamente.'), 'success')
        return redirect(url_for('fabricas.ver', id=fabrica.id))
    
    return render_template('fabricas/form.html', 
                         form=form, 
                         titulo=_('Nueva Fábrica'))


@fabricas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def editar(id):
    """Editar fábrica existente."""
    fabrica = Fabrica.query.get_or_404(id)
    form = FabricaForm(obj=fabrica)
    
    if form.validate_on_submit():
        fabrica.cliente_id = form.cliente_id.data
        fabrica.nombre = form.nombre.data
        fabrica.provincia_id = form.provincia_id.data or None
        fabrica.activo = form.activo.data
        
        db.session.commit()
        
        flash(_('Fábrica actualizada exitosamente.'), 'success')
        return redirect(url_for('fabricas.ver', id=fabrica.id))
    
    return render_template('fabricas/form.html',
                         form=form,
                         fabrica=fabrica,
                         titulo=_('Editar Fábrica'))


@fabricas_bp.route('/cliente/<int:cliente_id>')
@login_required
def por_cliente(cliente_id):
    """Listar fábricas de un cliente específico."""
    cliente = Cliente.query.get_or_404(cliente_id)
    page = request.args.get('page', 1, type=int)
    
    fabricas = Fabrica.query.filter_by(cliente_id=cliente_id).order_by(
        Fabrica.nombre
    ).paginate(page=page, per_page=25, error_out=False)
    
    return render_template('fabricas/por_cliente.html',
                         cliente=cliente,
                         fabricas=fabricas)
