"""Formularios para pedidos."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from flask_babel import _

from app.database.models import Cliente, Producto, OrdenTrabajo, UnidadMedida


class PedidoForm(FlaskForm):
    """Formulario para pedidos."""
    
    codigo = StringField(_('Código'), validators=[DataRequired(), Length(max=20)])
    cliente_id = SelectField(_('Cliente'), coerce=int, validators=[DataRequired()])
    producto_id = SelectField(_('Producto'), coerce=int, validators=[DataRequired()])
    orden_trabajo_id = SelectField(_('Orden de Trabajo (opcional)'), coerce=int)
    
    lote = StringField(_('Lote'), validators=[Optional(), Length(max=20)])
    cantidad = DecimalField(_('Cantidad'), validators=[Optional()], places=2)
    unidad_medida_id = SelectField(_('Unidad de Medida'), coerce=int)
    
    fech_fab = DateField(_('Fecha Fabricación'), validators=[Optional()], format='%Y-%m-%d')
    fech_venc = DateField(_('Fecha Vencimiento'), validators=[Optional()], format='%Y-%m-%d')
    
    observaciones = TextAreaField(_('Observaciones'), validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente_id.choices = [(c.id, c.nombre) for c in
                                   Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()]
        self.producto_id.choices = [(p.id, p.nombre) for p in
                                    Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()]
        self.orden_trabajo_id.choices = [(0, _('-- Ninguna --'))] + [(ot.id, f"{ot.numero} - {ot.cliente.nombre}") for ot in
                                                                     OrdenTrabajo.query.filter_by(estado='pendiente').all()]
        self.unidad_medida_id.choices = [(0, _('-- Seleccionar --'))] + [(u.id, f"{u.codigo} - {u.nombre}") for u in
                                                                          UnidadMedida.query.all()]
    
    def validate_fech_venc(self, field):
        """Validar que vencimiento > fabricación."""
        if field.data and self.fech_fab.data:
            if field.data < self.fech_fab.data:
                raise ValidationError(_('La fecha de vencimiento debe ser posterior a la de fabricación'))
