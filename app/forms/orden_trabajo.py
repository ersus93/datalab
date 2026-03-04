"""Formularios para órdenes de trabajo."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.database.models import Cliente, OrdenTrabajo


class OrdenTrabajoForm(FlaskForm):
    """Formulario para órdenes de trabajo."""
    
    nro_ofic = StringField(_('Nro. Oficial'), validators=[
        DataRequired(),
        Length(max=30)
    ])
    
    codigo = StringField(_('Código Interno'), validators=[
        Optional(),
        Length(max=20)
    ])
    
    cliente_id = SelectField(_('Cliente'), coerce=int, validators=[DataRequired()])
    
    descripcion = TextAreaField(_('Descripción'), validators=[Optional()])
    observaciones = TextAreaField(_('Observaciones'), validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente_id.choices = [(c.id, c.nombre) for c in
                                   Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()]
    
    def validate_nro_ofic(self, field):
        """Validar unicidad de NroOfic."""
        if field.data:
            existente = OrdenTrabajo.query.filter_by(nro_ofic=field.data).first()
            if existente and (not hasattr(self, 'obj') or existente.id != self.obj.id):
                raise ValidationError(_('Este número oficial ya existe'))
