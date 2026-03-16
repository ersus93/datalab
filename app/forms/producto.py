"""Formularios para catálogo de productos."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import _

from app.database.models import Producto, Rama, Destino


class ProductoForm(FlaskForm):
    """Formulario para crear/editar productos."""
    
    nombre = StringField(_('Nombre del Producto'), validators=[
        DataRequired(message=_('El nombre es obligatorio')),
        Length(max=300, message=_('Máximo 300 caracteres'))
    ])
    
    rama_id = SelectField(_('Rama / Sector'), coerce=int)
    destino_id = SelectField(_('Destino'), coerce=int)
    
    activo = BooleanField(_('Activo'), default=True)
    
    submit = SubmitField(_('Guardar'))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar dropdowns
        self.rama_id.choices = [(0, _('-- Seleccionar --'))] + [
            (r.id, r.nombre) for r in Rama.query.order_by(Rama.nombre).all()
        ]
        self.destino_id.choices = [(0, _('-- Seleccionar --'))] + [
            (d.id, f"{d.sigla} - {d.nombre}") for d in Destino.query.order_by(Destino.sigla).all()
        ]
    
    def validate_nombre(self, field):
        """Validar nombre único."""
        producto = Producto.query.filter_by(nombre=field.data).first()
        if producto:
            if not hasattr(self, 'id') or self.id.data != producto.id:
                raise ValidationError(_('Ya existe un producto con este nombre'))
