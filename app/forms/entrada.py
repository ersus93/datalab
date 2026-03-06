"""Formularios para entradas de muestras."""
import re
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, DateField, DecimalField, SelectField,
    StringField, TextAreaField,
)
from wtforms.validators import DataRequired, Length, ValidationError, Optional, NumberRange
from flask_babel import _

from app.database.models import Cliente, Fabrica, Producto, Rama, UnidadMedida


class EntradaForm(FlaskForm):
    """Formulario completo para crear/editar entradas."""

    # Identificación
    codigo = StringField(_('Código'), validators=[
        DataRequired(),
        Length(max=20),
    ])
    lote = StringField(_('Lote'), validators=[
        Optional(),
        Length(max=10),
    ])
    nro_parte = StringField(_('Nro. Parte'), validators=[
        Optional(),
        Length(max=50),
    ])
    fech_entrada = DateField(_('Fecha Entrada'), validators=[Optional()], format='%Y-%m-%d')

    # Relaciones
    cliente_id  = SelectField(_('Cliente'),          coerce=int, validators=[DataRequired()])
    fabrica_id  = SelectField(_('Fábrica'),          coerce=int, validators=[DataRequired()])
    producto_id = SelectField(_('Producto'),         coerce=int, validators=[DataRequired()])
    rama_id     = SelectField(_('Rama / Sector'),    coerce=int)
    pedido_id   = SelectField(_('Pedido (opcional)'), coerce=int)

    # Cantidades
    cantidad_recib = DecimalField(
        _('Cantidad Recibida'),
        validators=[DataRequired(), NumberRange(min=0.01)],
        places=2,
    )
    cantidad_muest = DecimalField(
        _('Cantidad Muestreada'),
        validators=[Optional()],
        places=2,
    )
    unidad_medida_id = SelectField(_('Unidad de Medida'), coerce=int)

    # Fechas
    fech_fab      = DateField(_('Fecha Fabricación'), validators=[Optional()], format='%Y-%m-%d')
    fech_venc     = DateField(_('Fecha Vencimiento'), validators=[Optional()], format='%Y-%m-%d')
    fech_muestreo = DateField(_('Fecha Muestreo'),    validators=[Optional()], format='%Y-%m-%d')

    # Estado y notas
    status = SelectField(_('Estado'), choices=[
        ('RECIBIDO',   _('Recibido')),
        ('EN_PROCESO', _('En Proceso')),
        ('COMPLETADO', _('Completado')),
        ('ENTREGADO',  _('Entregado')),
        ('ANULADO',    _('Anulado')),
    ], default='RECIBIDO')

    en_os = BooleanField(_('En Orden de Servicio'))

    observaciones = TextAreaField(_('Observaciones'), validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar dropdowns
        self.cliente_id.choices = [
            (c.id, c.nombre)
            for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
        ]
        self.fabrica_id.choices = [
            (f.id, f"{f.nombre} ({f.cliente.nombre})")
            for f in Fabrica.query.filter_by(activo=True).join(Cliente).order_by(Fabrica.nombre).all()
        ]
        self.producto_id.choices = [
            (p.id, p.nombre)
            for p in Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
        ]
        self.rama_id.choices = (
            [(0, _('-- Seleccionar --'))] +
            [(r.id, r.nombre) for r in Rama.query.order_by(Rama.nombre).all()]
        )
        self.pedido_id.choices = [(0, _('-- Ninguno --'))]
        self.unidad_medida_id.choices = (
            [(0, _('-- Seleccionar --'))] +
            [(u.id, f"{u.codigo} - {u.nombre}") for u in UnidadMedida.query.all()]
        )

    def validate_lote(self, field):
        """Validar formato de lote X-XXXX."""
        if field.data and not re.match(r'^[A-Z]-\d{4}$', field.data):
            raise ValidationError(_('Formato de lote debe ser X-XXXX (ej: A-1234)'))

    def validate_fech_venc(self, field):
        """Validar que vencimiento > fabricación."""
        if field.data and self.fech_fab.data:
            if field.data < self.fech_fab.data:
                raise ValidationError(
                    _('La fecha de vencimiento debe ser posterior a la de fabricación')
                )
