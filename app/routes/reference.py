"""Rutas CRUD para datos de referencia."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _

from app import db
from app.database.models.reference import (
    Area, Organismo, Provincia, Destino, Rama,
    Mes, Anno, TipoES, UnidadMedida
)
from app.decorators import admin_required

reference_bp = Blueprint('reference', __name__, url_prefix='/reference')

# Configuración de modelos CRUD
REFERENCE_MODELS = {
    'areas': {
        'model': Area,
        'title': _('Áreas de Laboratorio'),
        'fields': ['nombre', 'sigla'],
        'icon': 'flask'
    },
    'organismos': {
        'model': Organismo,
        'title': _('Organismos'),
        'fields': ['nombre'],
        'icon': 'building'
    },
    'provincias': {
        'model': Provincia,
        'title': _('Provincias'),
        'fields': ['nombre', 'sigla'],
        'icon': 'map'
    },
    'destinos': {
        'model': Destino,
        'title': _('Destinos'),
        'fields': ['nombre', 'sigla'],
        'icon': 'flag'
    },
    'ramas': {
        'model': Rama,
        'title': _('Ramas'),
        'fields': ['nombre'],
        'icon': 'industry'
    },
    'meses': {
        'model': Mes,
        'title': _('Meses'),
        'fields': ['nombre', 'sigla'],
        'icon': 'calendar'
    },
    'annos': {
        'model': Anno,
        'title': _('Años'),
        'fields': ['anno', 'activo'],
        'icon': 'clock'
    },
    'tipos-es': {
        'model': TipoES,
        'title': _('Tipos ES'),
        'fields': ['nombre'],
        'icon': 'eye'
    },
    'unidades-medida': {
        'model': UnidadMedida,
        'title': _('Unidades de Medida'),
        'fields': ['codigo', 'nombre'],
        'icon': 'ruler'
    }
}


@reference_bp.route('/')
@login_required
def index():
    """Dashboard de datos de referencia."""
    return render_template('reference/index.html', models=REFERENCE_MODELS)


@reference_bp.route('/<model_name>')
@login_required
def list_items(model_name):
    """Listar ítems de una tabla de referencia."""
    if model_name not in REFERENCE_MODELS:
        flash(_('Modelo no encontrado'), 'error')
        return redirect(url_for('reference.index'))
    
    config = REFERENCE_MODELS[model_name]
    model = config['model']
    items = model.query.all()
    
    return render_template('reference/list.html',
                         model_name=model_name,
                         title=config['title'],
                         fields=config['fields'],
                         items=items,
                         icon=config['icon'])


@reference_bp.route('/<model_name>/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_item(model_name):
    """Crear nuevo ítem."""
    if model_name not in REFERENCE_MODELS:
        flash(_('Modelo no encontrado'), 'error')
        return redirect(url_for('reference.index'))
    
    config = REFERENCE_MODELS[model_name]
    model = config['model']
    
    from app.forms.reference import create_reference_form
    form_class = create_reference_form(model, config['fields'])
    form = form_class()
    
    if form.validate_on_submit():
        try:
            # Crear nueva instancia del modelo
            kwargs = {}
            for field_name in config['fields']:
                kwargs[field_name] = getattr(form, field_name).data
            
            # Anno usa 'anno' como PK, no 'id'
            if model_name == 'annos':
                kwargs['anno'] = form.anno.data
            
            item = model(**kwargs)
            db.session.add(item)
            db.session.commit()
            
            flash(_('%(title)s creado exitosamente', title=config['title']), 'success')
            return redirect(url_for('reference.list_items', model_name=model_name))
        except Exception as e:
            db.session.rollback()
            flash(_('Error al crear: %(error)s', error=str(e)), 'error')
    
    return render_template('reference/form.html',
                         model_name=model_name,
                         title=_('Nuevo %(title)s', title=config['title']),
                         fields=config['fields'],
                         form=form,
                         icon=config['icon'])


@reference_bp.route('/<model_name>/<id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(model_name, id):
    """Editar ítem existente."""
    if model_name not in REFERENCE_MODELS:
        flash(_('Modelo no encontrado'), 'error')
        return redirect(url_for('reference.index'))
    
    config = REFERENCE_MODELS[model_name]
    model = config['model']
    
    # Anno usa 'anno' como PK
    if model_name == 'annos':
        item = model.query.get_or_404(id)
    else:
        item = model.query.get_or_404(int(id))
    
    from app.forms.reference import create_reference_form
    form_class = create_reference_form(model, config['fields'])
    form = form_class(obj=item)
    
    if form.validate_on_submit():
        try:
            for field_name in config['fields']:
                setattr(item, field_name, getattr(form, field_name).data)
            
            db.session.commit()
            flash(_('%(title)s actualizado exitosamente', title=config['title']), 'success')
            return redirect(url_for('reference.list_items', model_name=model_name))
        except Exception as e:
            db.session.rollback()
            flash(_('Error al actualizar: %(error)s', error=str(e)), 'error')
    
    return render_template('reference/form.html',
                         model_name=model_name,
                         title=_('Editar %(title)s', title=config['title']),
                         fields=config['fields'],
                         form=form,
                         item=item,
                         icon=config['icon'])


@reference_bp.route('/<model_name>/<id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_item(model_name, id):
    """Eliminar ítem."""
    if model_name not in REFERENCE_MODELS:
        flash(_('Modelo no encontrado'), 'error')
        return redirect(url_for('reference.index'))
    
    config = REFERENCE_MODELS[model_name]
    model = config['model']
    
    # Anno usa 'anno' como PK
    if model_name == 'annos':
        item = model.query.get_or_404(id)
    else:
        item = model.query.get_or_404(int(id))
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash(_('%(title)s eliminado exitosamente', title=config['title']), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error al eliminar: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('reference.list_items', model_name=model_name))
