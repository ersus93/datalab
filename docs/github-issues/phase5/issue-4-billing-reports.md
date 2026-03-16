# [Phase 5] Billing Reports

## Description
Implement a comprehensive billing and invoicing system that tracks laboratory service usage, generates usage reports, and creates billing documentation for clients. The system must accurately calculate costs based on test prices and generate exportable reports for accounting integration.

## Data Context
- **Source Tables**: Detalles de Ensayos, Entradas, Ensayos (prices), Clientes
- **Currency**: ARS (Argentine Peso) - support for USD in future
- **Billing Cycle**: Monthly with custom period options
- **Integration**: Export to Excel for external accounting systems

## Requirements

### 1. Usage Reports by Client
```python
class ReporteUsoPorCliente:
    """Generate usage reports grouped by client"""

    def generar(self, cliente_id=None, fecha_desde=None, fecha_hasta=None):
        queryset = DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            resultado__isnull=False
        )

        if cliente_id:
            queryset = queryset.filter(entrada__cliente_id=cliente_id)
        if fecha_desde and fecha_hasta:
            queryset = queryset.filter(
                fecha_completado__range=(fecha_desde, fecha_hasta)
            )

        return queryset.values(
            'entrada__cliente__id',
            'entrada__cliente__nombre',
            'entrada__cliente__cuit',
            'ensayo__denominacion'
        ).annotate(
            cantidad_ensayos=Count('id'),
            precio_unitario=Avg('ensayo__precio_referencia'),
            total=Sum('ensayo__precio_referencia'),
            ultima_fecha=Max('fecha_completado')
        ).order_by('entrada__cliente__nombre')

    def resumen_por_cliente(self, cliente_id, fecha_desde, fecha_hasta):
        """Summary billing for a specific client"""
        detalles = self.generar(cliente_id, fecha_desde, fecha_hasta)

        return {
            'cliente': Cliente.objects.get(id=cliente_id),
            'periodo': f"{fecha_desde} - {fecha_hasta}",
            'total_ensayos': detalles.aggregate(Sum('cantidad_ensayos'))['cantidad_ensayos__sum'],
            'monto_total': detalles.aggregate(Sum('total'))['total__sum'],
            'detalle_por_tipo': list(detalles),
            'entradas_incluidas': Entrada.objects.filter(
                cliente_id=cliente_id,
                detalleensayo__fecha_completado__range=(fecha_desde, fecha_hasta)
            ).distinct().count()
        }
```

**Report Format:**
```
CLIENTE: Laboratorios XYZ S.A.
CUIT: 30-12345678-9
PERÍODO: 01/01/2024 - 31/01/2024

DETALLE DE SERVICIOS:
┌──────────────────────┬──────────┬─────────────┬──────────┐
│ Ensayo               │ Cantidad │ Precio Unit │  Total   │
├──────────────────────┼──────────┼─────────────┼──────────┤
│ pH Determinación     │    15    │   $1,200    │ $18,000  │
│ Densidad Aparente    │    12    │   $1,500    │ $18,000  │
│ Recuento de Mohos    │     8    │   $2,100    │ $16,800  │
│ ...                  │   ...    │     ...     │   ...    │
├──────────────────────┼──────────┼─────────────┼──────────┤
│ TOTAL                │    35    │             │ $52,800  │
└──────────────────────┴──────────┴─────────────┴──────────┘

RESUMEN:
- Total de Muestras Procesadas: 12
- Total de Ensayos Realizados: 35
- Monto Total del Período: $52,800.00
```

### 2. Usage Reports by Period
```python
class ReporteUsoPorPeriodo:
    """Monthly/yearly usage reports"""

    def mensual(self, anio, mes):
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        return DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            fecha_completado__range=(fecha_inicio, fecha_fin)
        ).aggregate(
            total_ensayos=Count('id'),
            total_facturado=Sum('ensayo__precio_referencia'),
            promedio_por_entrada=Avg('entrada__detalleensayo__count'),
            clientes_unicos=Count('entrada__cliente', distinct=True)
        )

    def comparativo_mensual(self, anio):
        """Compare all months of a year"""
        data = []
        for mes in range(1, 13):
            data.append({
                'mes': mes,
                'nombre_mes': calendar.month_name[mes],
                'datos': self.mensual(anio, mes)
            })
        return data
```

### 3. Usage Reports by Test Type
```python
class ReporteUsoPorTipoEnsayo:
    """Usage analysis by test type"""

    def ranking_ensayos(self, fecha_desde, fecha_hasta, top_n=20):
        return DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            fecha_completado__range=(fecha_desde, fecha_hasta)
        ).values(
            'ensayo__codigo',
            'ensayo__denominacion',
            'ensayo__area',
            'ensayo__precio_referencia'
        ).annotate(
            cantidad_realizada=Count('id'),
            ingreso_total=Sum('ensayo__precio_referencia'),
            clientes_distintos=Count('entrada__cliente', distinct=True)
        ).order_by('-cantidad_realizada')[:top_n]

    def por_area(self, fecha_desde, fecha_hasta):
        return DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            fecha_completado__range=(fecha_desde, fecha_hasta)
        ).values('ensayo__area').annotate(
            cantidad=Count('id'),
            ingreso=Sum('ensayo__precio_referencia')
        )
```

### 4. Invoice Generation Interface
```python
class Factura(models.Model):
    # Identification
    numero = CharField(max_length=50, unique=True)
    tipo = CharField(choices=[
        ('A', 'Factura A'),
        ('B', 'Factura B'),
        ('C', 'Factura C'),
    ])

    # Client
    cliente = ForeignKey(Cliente, on_delete=models.PROTECT)
    cuit_cliente = CharField(max_length=13)
    direccion_cliente = TextField()

    # Dates
    fecha_emision = DateField()
    fecha_vencimiento = DateField()
    fecha_desde = DateField()  # Billing period start
    fecha_hasta = DateField()  # Billing period end

    # Amounts
    subtotal = DecimalField(max_digits=12, decimal_places=2)
    descuento = DecimalField(max_digits=12, decimal_places=2, default=0)
    iva = DecimalField(max_digits=12, decimal_places=2)
    total = DecimalField(max_digits=12, decimal_places=2)

    # Status
    estado = CharField(choices=[
        ('BORRADOR', 'Borrador'),
        ('EMITIDA', 'Emitida'),
        ('ENVIADA', 'Enviada'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ], default='BORRADOR')

    # Relationships
    detalles = ManyToManyField(DetalleEnsayo, through='FacturaDetalle')

class FacturaDetalle(models.Model):
    factura = ForeignKey(Factura, on_delete=models.CASCADE)
    detalle_ensayo = ForeignKey(DetalleEnsayo, on_delete=models.PROTECT)
    descripcion = CharField(max_length=255)
    cantidad = IntegerField()
    precio_unitario = DecimalField(max_digits=10, decimal_places=2)
    total = DecimalField(max_digits=10, decimal_places=2)
```

**Invoice Generation Workflow:**
```python
class GeneradorFactura:
    def generar_desde_periodo(self, cliente_id, fecha_desde, fecha_hasta):
        # 1. Get completed tests in period
        ensayos = DetalleEnsayo.objects.filter(
            entrada__cliente_id=cliente_id,
            estado='COMPLETADO',
            fecha_completado__range=(fecha_desde, fecha_hasta),
            factura__isnull=True  # Not yet billed
        )

        # 2. Group by test type for invoice lines
        lineas = ensayos.values('ensayo').annotate(
            cantidad=Count('id'),
            precio=Avg('ensayo__precio_referencia')
        )

        # 3. Create invoice
        factura = Factura.objects.create(
            numero=self.generar_numero(),
            cliente_id=cliente_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            # ... calculate amounts
        )

        # 4. Link tests to invoice
        for ensayo in ensayos:
            FacturaDetalle.objects.create(
                factura=factura,
                detalle_ensayo=ensayo,
                # ...
            )

        return factura
```

### 5. Billing Calculation Verification
```python
class VerificacionFacturacion:
    """Verify billing accuracy"""

    def verificar_precios(self, factura_id):
        """Verify prices match current catalog"""
        factura = Factura.objects.get(id=factura_id)
        discrepancias = []

        for detalle in factura.detalles.all():
            precio_actual = detalle.ensayo.precio_referencia
            if detalle.precio_unitario != precio_actual:
                discrepancias.append({
                    'ensayo': detalle.ensayo.denominacion,
                    'precio_facturado': detalle.precio_unitario,
                    'precio_actual': precio_actual
                })

        return discrepancias

    def verificar_completitud(self, cliente_id, fecha_desde, fecha_hasta):
        """Check for unbilled completed tests"""
        return DetalleEnsayo.objects.filter(
            entrada__cliente_id=cliente_id,
            estado='COMPLETADO',
            fecha_completado__range=(fecha_desde, fecha_hasta),
            factura__isnull=True
        )

    def conciliacion(self, factura_id):
        """Reconcile invoice totals"""
        factura = Factura.objects.get(id=factura_id)

        suma_detalles = factura.facturadetalle_set.aggregate(
            Sum('total')
        )['total__sum']

        return {
            'factura_total': factura.total,
            'suma_detalles': suma_detalles,
            'diferencia': factura.total - suma_detalles,
            'ok': abs(factura.total - suma_detalles) < 0.01
        }
```

### 6. Export Billing Data to Excel
```python
class ExportarFacturacionExcel:
    def generar_resumen_mensual(self, anio, mes):
        """Generate monthly billing summary"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)

        # Summary sheet
        ws_summary = workbook.add_worksheet('Resumen')
        self._escribir_encabezado(ws_summary, ['Cliente', 'CUIT', 'Total Ensayos', 'Monto'])

        # Detail sheet
        ws_detail = workbook.add_worksheet('Detalle')
        self._escribir_encabezado(ws_detail, [
            'Factura #', 'Cliente', 'Fecha', 'Ensayo', 'Cantidad', 'Precio', 'Total'
        ])

        # Fill data...

        workbook.close()
        output.seek(0)
        return output

    def generar_pendientes_facturacion(self):
        """Export unbilled completed tests"""
        pendientes = DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            factura__isnull=True
        ).select_related('entrada__cliente', 'ensayo')

        # Export to Excel...
```

## Acceptance Criteria
- [ ] Usage reports by client with detailed breakdown
- [ ] Usage reports by period (monthly/yearly)
- [ ] Usage reports by test type with rankings
- [ ] Invoice generation interface with line items
- [ ] Billing calculation verification tools
- [ ] Export billing data to Excel format
- [ ] Support for multiple invoice types (A, B, C)
- [ ] Track billing status (draft, issued, paid)
- [ ] Prevent double billing of same tests
- [ ] Billing period validation
- [ ] Client billing history view

## Technical Notes
- Use `DecimalField` for all monetary values (avoid float)
- Implement soft delete for invoices (legal requirement)
- Invoice numbers must be sequential and gap-free
- Consider AFIP (Argentine tax authority) integration in future
- All amounts in ARS with 2 decimal places
- Implement proper rounding rules (banker's rounding)
- Cache price lookups to avoid N+1 queries
- Index on (cliente_id, fecha_completado, estado) for performance

## Labels
`phase-5`, `billing`, `invoicing`, `reporting`, `excel`, `finance`, `backend`, `frontend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 4-5 days
