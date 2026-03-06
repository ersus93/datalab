"""Formularios para gestión de clientes."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import _

from app.database.models import Cliente, Organismo


class ClienteForm(FlaskForm):
    """Formulario para crear/editar clientes."""
    
    codigo = StringField(_('Código'), validators=[
        DataRequired(message=_('El código es obligatorio')),
        Length(max=20, message=_('Máximo 20 caracteres'))
    ])
    
    nombre = StringField(_('Nombre'), validators=[
        DataRequired(message=_('El nombre es obligatorio')),
        Length(max=300, message=_('Máximo 300 caracteres'))
    ])
    
    organismo_id = SelectField(_('Organismo'), coerce=int, validators=[
        DataRequired(message=_('El organismo es obligatorio'))
    ])
    
    tipo_cliente = SelectField(_('Tipo de Cliente'), coerce=int, choices=[
        (1, _('Tipo 1 - Industrial')),
        (2, _('Tipo 2 - Comercial')),
        (3, _('Tipo 3 - Servicios')),
        (4, _('Tipo 4 - Gobierno')),
        (5, _('Tipo 5 - Otros'))
    ], default=1)
    
    activo = BooleanField(_('Activo'), default=True)
    
    submit = SubmitField(_('Guardar'))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar dropdown de organismos
        self.organismo_id.choices = [
            (o.id, o.nombre) for o in Organismo.query.order_by(Organismo.nombre).all()
        ]
    
    def validate_codigo(self, field):
        """Validar que no exista un cliente con el mismo código."""
        cliente = Cliente.query.filter_by(codigo=field.data).first()
        if cliente:
            if hasattr(self, 'id') and self.id.data == cliente.id:
                return
            raise ValidationError(_('Ya existe un cliente con este código'))

    def validate_nombre(self, field):
        """Validar que no exista un cliente con el mismo nombre."""
        cliente = Cliente.query.filter_by(nombre=field.data).first()
        if cliente:
            # Si estamos editando, permitir el mismo nombre
            if hasattr(self, 'id') and self.id.data == cliente.id:
                return
            raise ValidationError(_('Ya existe un cliente con este nombre'))
