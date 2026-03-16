"""Schemas para la entidad Entrada usando Marshmallow."""
from marshmallow import Schema, fields, validates, validates_schema, ValidationError, post_dump
from datetime import date


class EntradaStatus:
    """Estados posibles de una entrada."""
    RECIBIDO = 'RECIBIDO'
    EN_PROCESO = 'EN_PROCESO'
    COMPLETADO = 'COMPLETADO'
    ENTREGADO = 'ENTREGADO'
    ANULADO = 'ANULADO'


class ProductoSchema(Schema):
    """Schema ligero para Producto."""
    id = fields.Integer()
    nombre = fields.String()


class ClienteSchema(Schema):
    """Schema ligero para Cliente."""
    id = fields.Integer()
    nombre = fields.String()
    codigo = fields.String()


class FabricaSchema(Schema):
    """Schema ligero para Fabrica."""
    id = fields.Integer()
    nombre = fields.String()


class RamaSchema(Schema):
    """Schema ligero para Rama."""
    id = fields.Integer()
    nombre = fields.String()


class UnidadMedidaSchema(Schema):
    """Schema ligero para UnidadMedida."""
    id = fields.Integer()
    codigo = fields.String()
    nombre = fields.String()


class EntradaSchema(Schema):
    """Schema completo para serialización de Entrada."""
    id = fields.Integer(dump_only=True)
    codigo = fields.String(required=True)
    lote = fields.String()
    nro_parte = fields.String()
    cantidad_recib = fields.Decimal(as_string=True, places=2)
    cantidad_entreg = fields.Decimal(as_string=True, places=2)
    saldo = fields.Decimal(as_string=True, places=2)
    cantidad_muest = fields.Decimal(as_string=True, places=2)
    fech_fab = fields.Date()
    fech_venc = fields.Date()
    fech_muestreo = fields.Date()
    fech_entrada = fields.DateTime()
    status = fields.String()
    en_os = fields.Boolean()
    anulado = fields.Boolean()
    ent_entregada = fields.Boolean()
    observaciones = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Foreign keys
    pedido_id = fields.Integer()
    producto_id = fields.Integer()
    fabrica_id = fields.Integer()
    cliente_id = fields.Integer()
    rama_id = fields.Integer()
    unidad_medida_id = fields.Integer()
    
    # Relaciones anidadas
    producto = fields.Nested(ProductoSchema, dump_only=True)
    cliente = fields.Nested(ClienteSchema, dump_only=True)
    fabrica = fields.Nested(FabricaSchema, dump_only=True)
    rama = fields.Nested(RamaSchema, dump_only=True)
    unidad_medida = fields.Nested(UnidadMedidaSchema, dump_only=True)
    
    @post_dump
    def process_saldo(self, data, **kwargs):
        """Asegurar que el saldo se calcule si no está presente."""
        if 'cantidad_recib' in data and 'cantidad_entreg' in data:
            if 'saldo' not in data or data['saldo'] is None:
                try:
                    from decimal import Decimal
                    recib = Decimal(data['cantidad_recib']) if data['cantidad_recib'] else Decimal('0')
                    entreg = Decimal(data['cantidad_entreg']) if data['cantidad_entreg'] else Decimal('0')
                    data['saldo'] = str(recib - entreg)
                except (ValueError, TypeError):
                    pass
        return data


class EntradaCreateSchema(Schema):
    """Schema para creación de entradas."""
    codigo = fields.String(required=True, error_messages={
        'required': 'El código es obligatorio'
    })
    producto_id = fields.Integer(required=True, error_messages={
        'required': 'El producto es obligatorio'
    })
    fabrica_id = fields.Integer(required=True, error_messages={
        'required': 'La fábrica es obligatoria'
    })
    cliente_id = fields.Integer(required=True, error_messages={
        'required': 'El cliente es obligatorio'
    })
    cantidad_recib = fields.Decimal(required=True, places=2, as_string=True, error_messages={
        'required': 'La cantidad recibida es obligatoria'
    })
    
    # Campos opcionales
    lote = fields.String()
    nro_parte = fields.String()
    cantidad_entreg = fields.Decimal(load_default=0, places=2, as_string=True)
    cantidad_muest = fields.Decimal(places=2, as_string=True)
    fech_fab = fields.Date()
    fech_venc = fields.Date()
    fech_muestreo = fields.Date()
    observaciones = fields.String()
    pedido_id = fields.Integer()
    rama_id = fields.Integer()
    unidad_medida_id = fields.Integer()
    
    @validates('lote')
    def validate_lote(self, value, **kwargs):
        """Validar formato de lote X-XXXX."""
        if value:
            import re
            if not re.match(r'^[A-Z]-\d{4}$', value):
                raise ValidationError('El formato de lote debe ser X-XXXX (ej: A-1234)')

    @validates('fech_venc')
    def validate_fech_venc(self, value, **kwargs):
        """Validar que vencimiento sea posterior a fabricación."""
        if value and self.context.get('fech_fab'):
            fech_fab = self.context.get('fech_fab')
            if isinstance(fech_fab, str):
                from datetime import datetime
                fech_fab = datetime.strptime(fech_fab, '%Y-%m-%d').date()
            if isinstance(fech_fab, date) and value < fech_fab:
                raise ValidationError('La fecha de vencimiento debe ser posterior a la fecha de fabricación')

    @validates('cantidad_recib')
    def validate_cantidad_recib(self, value, **kwargs):
        """Validar que cantidad recibida sea >= 0."""
        if value is not None and value < 0:
            raise ValidationError('La cantidad recibida no puede ser negativa')


class EntradaUpdateSchema(Schema):
    """Schema para actualización de entradas."""
    codigo = fields.String()
    lote = fields.String()
    nro_parte = fields.String()
    cantidad_recib = fields.Decimal(places=2, as_string=True)
    cantidad_entreg = fields.Decimal(places=2, as_string=True)
    cantidad_muest = fields.Decimal(places=2, as_string=True)
    fech_fab = fields.Date()
    fech_venc = fields.Date()
    fech_muestreo = fields.Date()
    observaciones = fields.String()
    producto_id = fields.Integer()
    fabrica_id = fields.Integer()
    cliente_id = fields.Integer()
    pedido_id = fields.Integer()
    rama_id = fields.Integer()
    unidad_medida_id = fields.Integer()
    status = fields.String()
    en_os = fields.Boolean()
    anulado = fields.Boolean()
    ent_entregada = fields.Boolean()

    @validates('lote')
    def validate_lote(self, value, **kwargs):
        """Validar formato de lote X-XXXX."""
        if value:
            import re
            if not re.match(r'^[A-Z]-\d{4}$', value):
                raise ValidationError('El formato de lote debe ser X-XXXX (ej: A-1234)')

    @validates('fech_venc')
    def validate_fech_venc(self, value, **kwargs):
        """Validar que vencimiento sea posterior a fabricación."""
        if value and self.context.get('fech_fab'):
            fech_fab = self.context.get('fech_fab')
            if isinstance(fech_fab, str):
                from datetime import datetime
                fech_fab = datetime.strptime(fech_fab, '%Y-%m-%d').date()
            if isinstance(fech_fab, date) and value < fech_fab:
                raise ValidationError('La fecha de vencimiento debe ser posterior a la fecha de fabricación')

    @validates('cantidad_recib')
    def validate_cantidad_recib(self, value, **kwargs):
        """Validar que cantidad recibida sea >= 0."""
        if value is not None and value < 0:
            raise ValidationError('La cantidad recibida no puede ser negativa')
    
    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        """Validar que al menos un campo esté presente."""
        if not data:
            raise ValidationError('Debe proporcionar al menos un campo para actualizar')


class EntregaSchema(Schema):
    """Schema para registrar entregas."""
    cantidad = fields.Decimal(required=True, places=2, as_string=True, error_messages={
        'required': 'La cantidad es obligatoria'
    })
    observaciones = fields.String()
    
    @validates('cantidad')
    def validate_cantidad(self, value, **kwargs):
        """Validar que cantidad sea > 0."""
        if value is not None and value <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero')


class CambioEstadoSchema(Schema):
    """Schema para cambios de estado."""
    nuevo_estado = fields.String(required=True, error_messages={
        'required': 'El nuevo estado es obligatorio'
    })
    razon = fields.String()
    
    @validates('nuevo_estado')
    def validate_nuevo_estado(self, value, **kwargs):
        """Validar que el estado sea válido."""
        estados_validos = [
            EntradaStatus.RECIBIDO,
            EntradaStatus.EN_PROCESO,
            EntradaStatus.COMPLETADO,
            EntradaStatus.ENTREGADO,
            EntradaStatus.ANULADO
        ]
        if value not in estados_validos:
            raise ValidationError(f'Estado no válido. Opciones: {", ".join(estados_validos)}')


class EntradaListSchema(Schema):
    """Schema ligero para listados de entradas."""
    id = fields.Integer()
    codigo = fields.String()
    lote = fields.String()
    producto_nombre = fields.String()
    cliente_nombre = fields.String()
    status = fields.String()
    cantidad_recib = fields.Decimal(as_string=True, places=2)
    saldo = fields.Decimal(as_string=True, places=2)
    fech_entrada = fields.DateTime()


class EntradaFilterSchema(Schema):
    """Schema para filtros de búsqueda de entradas."""
    cliente_id = fields.Integer()
    producto_id = fields.Integer()
    status = fields.String()
    fecha_desde = fields.Date()
    fecha_hasta = fields.Date()
    
    @validates('fecha_hasta')
    def validate_fecha_hasta(self, value, **kwargs):
        """Validar que fecha_hasta sea >= fecha_desde."""
        if value and self.context.get('fecha_desde'):
            fecha_desde = self.context.get('fecha_desde')
            if isinstance(fecha_desde, str):
                from datetime import datetime
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            if isinstance(fecha_desde, date) and value < fecha_desde:
                raise ValidationError('La fecha hasta debe ser mayor o igual a la fecha desde')
