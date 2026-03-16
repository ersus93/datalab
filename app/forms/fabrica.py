"""Formularios para gestión de fábricas."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import _

from app.database.models import Fabrica, Cliente, Provincia


class FabricaForm(FlaskForm):
    """Formulario para crear/editar fábricas."""
    
    cliente_id = SelectField(_('Cliente'), coerce=int, validators=[
        DataRequired(message=_('El cliente es obligatorio'))
    ])
    
    nombre = StringField(_('Nombre de la Fábrica'), validators=[
        DataRequired(message=_('El nombre es obligatorio')),
        Length(max=300, message=_('Máximo 300 caracteres'))
    ])
    
    provincia_id = SelectField(_('Provincia'), coerce=int)
    
    activo = BooleanField(_('Activa'), default=True)
    
    submit = SubmitField(_('Guardar'))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar dropdowns
        self.cliente_id.choices = [
            (c.id, c.nombre) for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
        ]
        self.provincia_id.choices = [(0, _('-- Seleccionar --'))] + [
            (p.id, f"{p.nombre} ({p.sigla})") for p in Provincia.query.order_by(Provincia.nombre).all()
        ]
    
    def validate_nombre(self, field):
        """Validar nombre único por cliente."""
        fabrica = Fabrica.query.filter_by(
            cliente_id=self.cliente_id.data,
            nombre=field.data
        ).first()
        if fabrica:
            if not hasattr(self, 'id') or fabrica.id != self.id.data:
                raise ValidationError(_('Este cliente ya tiene una fábrica con este nombre'))
