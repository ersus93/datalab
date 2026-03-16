"""Formularios para datos de referencia."""
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from flask_babel import _


def create_reference_form(model_class, field_names):
    """
    Factory para crear formularios dinámicos basados en modelo.
    
    Args:
        model_class: Clase del modelo SQLAlchemy
        field_names: Lista de nombres de campos a incluir
    
    Returns:
        Clase de formulario Flask-WTF
    """
    attrs = {}
    
    for field_name in field_names:
        # Determinar tipo de campo según nombre
        if field_name == 'activo':
            attrs[field_name] = BooleanField(_('Activo'), default=True)
        elif field_name == 'anno':
            attrs[field_name] = StringField(_('Año'), validators=[
                DataRequired(),
                Length(min=4, max=4)
            ])
        elif field_name == 'sigla':
            attrs[field_name] = StringField(_('Sigla'), validators=[
                DataRequired(),
                Length(max=10)
            ])
        elif field_name == 'codigo':
            attrs[field_name] = StringField(_('Código'), validators=[
                DataRequired(),
                Length(max=10)
            ])
        else:
            # Campo genérico StringField
            label = field_name.replace('_', ' ').title()
            attrs[field_name] = StringField(_(label), validators=[
                DataRequired(),
                Length(max=200)
            ])
    
    attrs['submit'] = SubmitField(_('Guardar'))
    
    return type(f'{model_class.__name__}Form', (FlaskForm,), attrs)
