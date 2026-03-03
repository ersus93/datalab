# [Phase 5] Analytics Dashboard

## Description
Implement a comprehensive analytics dashboard that visualizes laboratory data from the 6 key reports derived from Access queries. The dashboard provides real-time insights into laboratory operations, pending work, and throughput metrics.

## Data Context
- **Source**: Django ORM queries (migrated from Access)
- **Update Frequency**: Real-time / On-demand
- **User Roles**: Admin, Lab Manager, Department Heads
- **Visualization Library**: Plotly.js

## Requirements

### 1. Dashboard Layout Structure
```
┌─────────────────────────────────────────────────────────────────┐
│  DATALAB ANALYTICS                    [Period Filter ▼] [🔄]   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Sensory     │  │    FQ        │  │ Microbiology │          │
│  │  Pending     │  │  Pending     │  │   Pending    │          │
│  │     45       │  │    128       │  │     67       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐ │
│  │   Completed Tests Timeline   │  │  Tests by Client Type    │ │
│  │      [Line Chart]            │  │      [Pie Chart]         │ │
│  │                              │  │                          │ │
│  └──────────────────────────────┘  └──────────────────────────┘ │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐ │
│  │    Analyzed Batches          │  │    Sampling Trends       │ │
│  │      [Bar Chart]             │  │      [Line Chart]        │ │
│  │                              │  │                          │ │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Report 1: Análisis a realizar ES (Sensory Pending)
```python
class ReporteSensoryPendiente:
    """Análisis sensorial pendientes por realizar"""

    def obtener_datos(self):
        return DetalleEnsayo.objects.filter(
            ensayo__area='ES',
            estado__in=['PENDIENTE', 'ASIGNADO'],
            entrada__estado__in=['RECIBIDO', 'EN_ANALISIS']
        ).select_related('entrada', 'ensayo').values(
            'entrada__identificacion',
            'ensayo__denominacion',
            'fecha_asignacion',
            'estado'
        )

    def obtener_resumen(self):
        return self.obtener_datos().aggregate(
            total_pendiente=Count('id', filter=Q(estado='PENDIENTE')),
            total_asignado=Count('id', filter=Q(estado='ASIGNADO')),
            total=Count('id')
        )
```

**Chart: Counter Card + Detail Table**
- Large counter showing total pending ES tests
- Breakdown by status (Pending vs Assigned)
- Drill-down table with sample details

### 3. Report 2: Análisis a realizar FQ (FQ Pending)
```python
class ReporteFQPendiente:
    """Análisis físico-químicos pendientes"""

    def obtener_datos(self):
        return DetalleEnsayo.objects.filter(
            ensayo__area='FQ',
            estado__in=['PENDIENTE', 'ASIGNADO']
        ).select_related('entrada', 'ensayo')

    def por_tipo_ensayo(self):
        return self.obtener_datos().values(
            'ensayo__denominacion'
        ).annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')
```

**Chart: Horizontal Bar Chart**
- X-axis: Number of pending tests
- Y-axis: Test type (denominacion)
- Color coding by status

### 4. Report 3: Análisis a realizar MB (Microbiology Pending)
```python
class ReporteMBPendiente:
    """Análisis microbiológicos pendientes"""

    def obtener_datos(self):
        return DetalleEnsayo.objects.filter(
            ensayo__area='MB',
            estado__in=['PENDIENTE', 'ASIGNADO']
        ).select_related('entrada', 'ensayo')

    def por_laboratorista(self):
        return self.obtener_datos().values(
            'tecnico_asignado__first_name',
            'tecnico_asignado__last_name'
        ).annotate(
            cantidad=Count('id')
        )
```

**Chart: Donut Chart + List**
- Distribution by assigned technician
- Counter for total pending microbiology tests
- SLA indicators (overdue highlighting)

### 5. Report 4: Determinaciones realizadas (Completed Tests)
```python
class ReporteDeterminacionesRealizadas:
    """Determinaciones completadas en período"""

    def por_mes(self, anio):
        return DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            fecha_completado__year=anio
        ).annotate(
            mes=TruncMonth('fecha_completado')
        ).values('mes').annotate(
            cantidad=Count('id')
        ).order_by('mes')

    def por_area(self, fecha_desde, fecha_hasta):
        return DetalleEnsayo.objects.filter(
            estado='COMPLETADO',
            fecha_completado__range=(fecha_desde, fecha_hasta)
        ).values('ensayo__area').annotate(
            cantidad=Count('id')
        )
```

**Chart: Multi-line Timeline**
- Line for each area (FQ, MB, ES, OS)
- X-axis: Months
- Y-axis: Number of completed tests
- Hover tooltips with exact values

### 6. Report 5: Lotes Analizados (Analyzed Batches)
```python
class ReporteLotesAnalizados:
    """Lotes analizados por período y tipo"""

    def por_tipo_muestra(self, fecha_desde, fecha_hasta):
        return Entrada.objects.filter(
            estado='COMPLETADO',
            fecha_completado__range=(fecha_desde, fecha_hasta)
        ).values('tipo_muestra__nombre').annotate(
            cantidad=Count('id'),
            promedio_ensayos=Avg('detalleensayo__count')
        )

    def por_cliente_top(self, fecha_desde, fecha_hasta, limite=10):
        return Entrada.objects.filter(
            fecha_entrada__range=(fecha_desde, fecha_hasta)
        ).values('cliente__nombre').annotate(
            lotes=Count('id')
        ).order_by('-lotes')[:limite]
```

**Chart: Stacked Bar Chart**
- X-axis: Time periods (weeks/months)
- Y-axis: Number of batches
- Stacks by sample type

### 7. Report 6: Muestreos por tipo de cliente (Sampling by Client Type)
```python
class ReporteMuestreosPorCliente:
    """Análisis de muestreos por tipo de cliente"""

    def por_tipo_cliente(self, fecha_desde, fecha_hasta):
        return Entrada.objects.filter(
            fecha_entrada__range=(fecha_desde, fecha_hasta)
        ).values('cliente__tipo__nombre').annotate(
            muestreos=Count('id'),
            ensayos_promedio=Avg('detalleensayo__count'),
            ingreso_promedio=Avg('costo_total')
        )

    def tendencia_mensual(self, anio):
        return Entrada.objects.filter(
            fecha_entrada__year=anio
        ).annotate(
            mes=TruncMonth('fecha_entrada')
        ).values('mes', 'cliente__tipo__nombre').annotate(
            cantidad=Count('id')
        ).order_by('mes')
```

**Chart: Area Chart + Pie Chart**
- Area chart: Trend over time by client type
- Pie chart: Distribution percentage

### 8. Plotly Integration
```python
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

class DashboardChartService:
    def crear_linea_temporal(self, datos):
        fig = go.Figure()
        for area in ['FQ', 'MB', 'ES', 'OS']:
            fig.add_trace(go.Scatter(
                x=datos['meses'],
                y=datos[area],
                name=area,
                mode='lines+markers'
            ))
        fig.update_layout(
            title='Determinaciones Realizadas',
            xaxis_title='Mes',
            yaxis_title='Cantidad'
        )
        return fig.to_json()

    def crear_pastel(self, datos, titulo):
        fig = go.Figure(data=[go.Pie(
            labels=datos['labels'],
            values=datos['values'],
            hole=0.4
        )])
        fig.update_layout(title=titulo)
        return fig.to_json()
```

### 9. Export Functionality
```python
class ExportarReporte:
    def a_excel(self, reporte_id, fecha_desde, fecha_hasta):
        """Export report data to Excel"""
        pass

    def a_pdf(self, reporte_id, fecha_desde, fecha_hasta):
        """Export report to PDF with charts"""
        pass

    def a_csv(self, reporte_id, fecha_desde, fecha_hasta):
        """Export raw data to CSV"""
        pass
```

## Acceptance Criteria
- [ ] Dashboard with 6 key reports implemented
- [ ] Plotly integration for interactive charts
- [ ] Line charts for temporal data
- [ ] Pie/Donut charts for distributions
- [ ] Bar charts for comparisons
- [ ] Counter cards for KPIs
- [ ] Period filter (date range selector)
- [ ] Export to Excel functionality
- [ ] Export to PDF with embedded charts
- [ ] Real-time data refresh capability
- [ ] Responsive layout for different screen sizes

## Technical Notes
- Install Plotly: `pip install plotly`
- Use Django's `TruncMonth` for date aggregations
- Cache expensive queries with Redis (TTL: 5 minutes)
- Implement database indexes on filtered columns
- Use `select_related` and `prefetch_related` for query optimization
- Consider materialized views for complex aggregations
- Implement user-specific dashboard preferences

## Labels
`phase-5`, `analytics`, `dashboard`, `plotly`, `charts`, `reporting`, `frontend`, `backend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 4-5 days
