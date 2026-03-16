# [Phase 2] Dashboard for Master Data

**Labels:** `phase-2`, `dashboard`, `frontend`, `visualization`, `plotly`, `medium-priority`
**Milestone:** Phase 2: Core Entities & CRUD (Weeks 3-4)
**Estimated Effort:** 2 days
**Depends on:** Issue #1-#3 (Phase 2) ([Phase 2] Core CRUD Modules)

---

## Description

Implement a comprehensive dashboard for visualizing and managing master data. This dashboard provides at-a-glance insights into clients, factories, and products with interactive widgets, statistics cards, recent activity feeds, and data visualization using Plotly.

### Current State
- Basic dashboard with static content
- Plotly library available
- No master data visualizations

### Target State
- Interactive dashboard widgets
- Real-time statistics cards
- Recent activity feed
- Quick action buttons
- Data visualization with charts
- Geographic distribution maps
- Trend analysis

### Dashboard Overview
```
┌─────────────────────────────────────────────────────────────────┐
│  DATA LAB - Dashboard de Datos Maestros                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ CLIENTES │ │ FÁBRICAS │ │PRODUCTOS │ │ PROVIN-  │          │
│  │   166    │ │   403    │ │   160    │ │  C I A S │          │
│  │ ↑ 12%    │ │ ↑ 8%     │ │ → 0%     │ │    4     │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  Distribución por   │  │  Fábricas por       │              │
│  │  Provincia          │  │  Cliente (Top 10)   │              │
│  │  [Pie Chart]        │  │  [Bar Chart]        │              │
│  └─────────────────────┘  └─────────────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Actividad Reciente                                     │   │
│  │  • Cliente "XYZ" creado hace 5 minutos                  │   │
│  │  • Fábrica "ABC" actualizada hace 1 hora                │   │
│  │  • Producto "123" añadido hace 2 horas                  │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Acciones Rápidas: [+ Cliente] [+ Fábrica] [+ Producto]       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

### Statistics Cards

- [ ] Create 4 main KPI cards at top of dashboard:
  1. **Total Clientes**
     - Display count (166)
     - Show trend vs last month (if historical data)
     - Link to client list
     - Icon: Users
     - Color: Blue
  
  2. **Total Fábricas**
     - Display count (403)
     - Show distribution indicator
     - Link to factory list
     - Icon: Industry
     - Color: Green
  
  3. **Total Productos**
     - Display count (160)
     - Show active/inactive ratio
     - Link to product catalog
     - Icon: Box/Package
     - Color: Purple
  
  4. **Provincias Cubiertas**
     - Display count (4)
     - Show geographic spread
     - Link to factory map view
     - Icon: Map Marker
     - Color: Orange

- [ ] Card features:
  - Hover effects
  - Click navigation
  - Loading states
  - Responsive layout (2x2 on mobile, 4x1 on desktop)

### Geographic Distribution Chart

- [ ] Create province distribution pie/donut chart:
  - Data: Factories per province
  - Provinces: Pinar del Río, Artemisa, Mayabeque, La Habana
  - Interactive tooltips with counts and percentages
  - Click to filter factories by province
  - Color coding matching province badges
  
- [ ] Chart configuration:
  ```javascript
  {
    type: 'pie',
    labels: ['Pinar del Río', 'Artemisa', 'Mayabeque', 'La Habana'],
    values: [320, 45, 20, 18],  // Approximate distribution
    colors: ['#28a745', '#007bff', '#fd7e14', '#6f42c1']
  }
  ```

### Top Clients by Factory Count

- [ ] Create horizontal bar chart:
  - Top 10 clients with most factories
  - X-axis: Factory count
  - Y-axis: Client names (truncated)
  - Click to navigate to client detail
  - Show actual factory count labels

### Sector Distribution (Productos)

- [ ] Create sector distribution chart:
  - All 13 ramas (sectors)
  - Products per sector
  - Color-coded by sector
  - Optional: stacked bar by destination

### Recent Activity Feed

- [ ] Create activity feed widget:
  - Show last 10 activities
  - Activity types:
    - Client created/updated/deactivated
    - Factory created/updated
    - Product created/updated
    - Test associations changed
  - Display:
    - Icon by activity type
    - Description
    - Timestamp (relative: "hace 5 minutos")
    - User who performed action
  - "Ver todo" link to full audit log

### Quick Action Buttons

- [ ] Create action bar with buttons:
  - **+ Nuevo Cliente** → Link to client creation
  - **+ Nueva Fábrica** → Link to factory creation
  - **+ Nuevo Producto** → Link to product creation
  - **Importar Datos** → Link to import page
  - **Ver Reportes** → Link to reports
- [ ] Button styles:
  - Primary action: filled button
  - Secondary: outline button
  - Icons on all buttons

### Data Tables Summary

- [ ] Create mini tables section:
  - **Últimos Clientes**: Last 5 clients added
  - **Últimas Fábricas**: Last 5 factories added
  - **Últimos Productos**: Last 5 products added
  - Each with "Ver todos" link

### Trend Charts (Optional/Phase 2+)

- [ ] Client growth over time (if date data available)
- [ ] Factory additions by month
- [ ] Product catalog growth

### Dashboard Customization

- [ ] Allow users to:
  - Rearrange widgets (drag & drop)
  - Collapse/expand sections
  - Choose default time range
  - Save layout preferences (localStorage)

### Responsive Design

- [ ] Desktop: Full 2-column layout
- [ ] Tablet: Adjusted columns
- [ ] Mobile: Single column, stacked cards

---

## Technical Notes

### URL Route

```python
# app/routes/dashboard.py

@dashboard_bp.route('/dashboard/master-data')
@login_required
def master_data_dashboard():
    """Master data dashboard with visualizations"""
    
    # Statistics
    stats = {
        'total_clientes': Cliente.query.filter_by(activo=True).count(),
        'total_fabricas': Fabrica.query.filter_by(activo=True).count(),
        'total_productos': Producto.query.filter_by(activo=True).count(),
        'total_provincias': Provincia.query.count(),
    }
    
    # Province distribution for chart
    provincia_data = db.session.query(
        Provincia.nombre,
        Provincia.sigla,
        db.func.count(Fabrica.id).label('count')
    ).outerjoin(Fabrica).group_by(Provincia.id).all()
    
    # Top clients by factory count
    top_clientes = db.session.query(
        Cliente.id,
        Cliente.nombre,
        db.func.count(Fabrica.id).label('factory_count')
    ).join(Fabrica).group_by(Cliente.id).order_by(
        db.desc('factory_count')
    ).limit(10).all()
    
    # Sector distribution
    sector_data = db.session.query(
        Rama.nombre,
        db.func.count(Producto.id).label('count')
    ).outerjoin(Producto).group_by(Rama.id).all()
    
    # Recent activity
    recent_activity = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).limit(10).all()
    
    # Recent additions
    latest_clientes = Cliente.query.order_by(
        Cliente.creado_en.desc()
    ).limit(5).all()
    
    latest_fabricas = Fabrica.query.order_by(
        Fabrica.creado_en.desc()
    ).limit(5).all()
    
    latest_productos = Producto.query.order_by(
        Producto.creado_en.desc()
    ).limit(5).all()
    
    return render_template('dashboard/master_data.html',
                         stats=stats,
                         provincia_data=provincia_data,
                         top_clientes=top_clientes,
                         sector_data=sector_data,
                         recent_activity=recent_activity,
                         latest_clientes=latest_clientes,
                         latest_fabricas=latest_fabricas,
                         latest_productos=latest_productos)
```

### Dashboard Template

```html
<!-- templates/dashboard/master_data.html -->

{% extends 'base.html' %}

{% block title %}Dashboard - Datos Maestros{% endblock %}

{% block content %}
<div class="dashboard-header">
    <h1>Dashboard de Datos Maestros</h1>
    <p class="text-muted">Resumen de clientes, fábricas y productos</p>
</div>

<!-- Statistics Cards -->
<div class="row stats-row">
    <div class="col-md-3 col-sm-6">
        <div class="stat-card card-clientes" onclick="location.href='{{ url_for('clientes.listar') }}'">
            <div class="stat-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-content">
                <h3>{{ stats.total_clientes }}</h3>
                <p>Clientes</p>
                <small class="stat-trend">
                    <i class="fas fa-arrow-up"></i> Activos
                </small>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 col-sm-6">
        <div class="stat-card card-fabricas" onclick="location.href='{{ url_for('fabricas.listar') }}'">
            <div class="stat-icon">
                <i class="fas fa-industry"></i>
            </div>
            <div class="stat-content">
                <h3>{{ stats.total_fabricas }}</h3>
                <p>Fábricas</p>
                <small class="stat-distribution">
                    ~{{ (stats.total_fabricas / stats.total_clientes)|round(1) }} por cliente
                </small>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 col-sm-6">
        <div class="stat-card card-productos" onclick="location.href='{{ url_for('productos.listar') }}'">
            <div class="stat-icon">
                <i class="fas fa-box"></i>
            </div>
            <div class="stat-content">
                <h3>{{ stats.total_productos }}</h3>
                <p>Productos</p>
                <small>En catálogo</small>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 col-sm-6">
        <div class="stat-card card-provincias">
            <div class="stat-icon">
                <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="stat-content">
                <h3>{{ stats.total_provincias }}</h3>
                <p>Provincias</p>
                <small>Cobertura total</small>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions -->
<div class="quick-actions mb-4">
    <a href="{{ url_for('clientes.crear') }}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Nuevo Cliente
    </a>
    <a href="{{ url_for('fabricas.crear') }}" class="btn btn-success">
        <i class="fas fa-plus"></i> Nueva Fábrica
    </a>
    <a href="{{ url_for('productos.crear') }}" class="btn btn-purple">
        <i class="fas fa-plus"></i> Nuevo Producto
    </a>
    <a href="{{ url_for('import.all') }}" class="btn btn-outline-secondary">
        <i class="fas fa-upload"></i> Importar Datos
    </a>
</div>

<!-- Charts Row -->
<div class="row charts-row">
    <div class="col-md-6">
        <div class="card chart-card">
            <div class="card-header">
                <h5>Distribución por Provincia</h5>
            </div>
            <div class="card-body">
                <div id="provincia-chart"></div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card chart-card">
            <div class="card-header">
                <h5>Top 10 Clientes por Fábricas</h5>
            </div>
            <div class="card-body">
                <div id="clientes-chart"></div>
            </div>
        </div>
    </div>
</div>

<!-- Second Charts Row -->
<div class="row charts-row mt-4">
    <div class="col-md-6">
        <div class="card chart-card">
            <div class="card-header">
                <h5>Distribución por Sector (Rama)</h5>
            </div>
            <div class="card-body">
                <div id="sector-chart"></div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Actividad Reciente</h5>
                <a href="{{ url_for('audit.log') }}" class="btn btn-sm btn-link">Ver todo</a>
            </div>
            <div class="card-body p-0">
                <ul class="activity-feed">
                    {% for activity in recent_activity %}
                    <li class="activity-item">
                        <div class="activity-icon activity-{{ activity.action|lower }}">
                            <i class="fas fa-{{ activity_icon(activity.action) }}"></i>
                        </div>
                        <div class="activity-content">
                            <p>{{ activity.description }}</p>
                            <small>
                                {{ activity.user.nombre_completo }} • 
                                {{ timeago(activity.created_at) }}
                            </small>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</div>

<!-- Latest Additions -->
<div class="row mt-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6>Últimos Clientes</h6>
            </div>
            <ul class="list-group list-group-flush">
                {% for cliente in latest_clientes %}
                <li class="list-group-item">
                    <a href="{{ url_for('clientes.ver', id=cliente.id) }}">
                        {{ cliente.nombre[:40] }}...
                    </a>
                    <small class="text-muted">
                        {{ timeago(cliente.creado_en) }}
                    </small>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6>Últimas Fábricas</h6>
            </div>
            <ul class="list-group list-group-flush">
                {% for fabrica in latest_fabricas %}
                <li class="list-group-item">
                    <a href="{{ url_for('fabricas.ver', id=fabrica.id) }}">
                        {{ fabrica.nombre[:40] }}...
                    </a>
                    <small class="text-muted">
                        {{ fabrica.cliente.nombre[:20] }}...
                    </small>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6>Últimos Productos</h6>
            </div>
            <ul class="list-group list-group-flush">
                {% for producto in latest_productos %}
                <li class="list-group-item">
                    <a href="{{ url_for('productos.ver', id=producto.id) }}">
                        {{ producto.nombre[:40] }}...
                    </a>
                    <span class="badge badge-{{ rama_colors[producto.rama_id].badge }}">
                        {{ producto.rama.nombre[:10] }}
                    </span>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
// Province Distribution Pie Chart
var provinciaData = [{
    values: {{ provincia_data | map(attribute='count') | list | tojson }},
    labels: {{ provincia_data | map(attribute='nombre') | list | tojson }},
    type: 'pie',
    hole: 0.4,
    marker: {
        colors: ['#28a745', '#007bff', '#fd7e14', '#6f42c1']
    },
    textinfo: 'label+percent',
    textposition: 'outside'
}];

var provinciaLayout = {
    showlegend: true,
    legend: { orientation: 'h' },
    margin: { t: 10, b: 10, l: 10, r: 10 }
};

Plotly.newPlot('provincia-chart', provinciaData, provinciaLayout, {responsive: true});

// Top Clients Bar Chart
var clientesData = [{
    y: {{ top_clientes | map(attribute='nombre') | list | tojson }},
    x: {{ top_clientes | map(attribute='factory_count') | list | tojson }},
    type: 'bar',
    orientation: 'h',
    marker: { color: '#007bff' },
    text: {{ top_clientes | map(attribute='factory_count') | list | tojson }},
    textposition: 'auto'
}];

var clientesLayout = {
    xaxis: { title: 'Número de Fábricas' },
    yaxis: { automargin: true },
    margin: { t: 10, b: 40, l: 150, r: 10 }
};

Plotly.newPlot('clientes-chart', clientesData, clientesLayout, {responsive: true});

// Sector Distribution
var sectorData = [{
    x: {{ sector_data | map(attribute='nombre') | list | tojson }},
    y: {{ sector_data | map(attribute='count') | list | tojson }},
    type: 'bar',
    marker: { color: '#6f42c1' }
}];

var sectorLayout = {
    xaxis: { tickangle: -45 },
    yaxis: { title: 'Productos' },
    margin: { t: 10, b: 100, l: 50, r: 10 }
};

Plotly.newPlot('sector-chart', sectorData, sectorLayout, {responsive: true});
</script>
{% endblock %}
```

### CSS Styles

```css
/* static/css/dashboard.css */

/* Stats Cards */
.stats-row {
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 1rem;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-right: 1rem;
}

.card-clientes .stat-icon { background: rgba(0,123,255,0.1); color: #007bff; }
.card-fabricas .stat-icon { background: rgba(40,167,69,0.1); color: #28a745; }
.card-productos .stat-icon { background: rgba(111,66,193,0.1); color: #6f42c1; }
.card-provincias .stat-icon { background: rgba(253,126,20,0.1); color: #fd7e14; }

.stat-content h3 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
}

.stat-content p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
}

/* Quick Actions */
.quick-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.quick-actions .btn {
    padding: 0.5rem 1rem;
}

/* Chart Cards */
.chart-card {
    height: 100%;
}

.chart-card .card-body {
    min-height: 300px;
}

/* Activity Feed */
.activity-feed {
    list-style: none;
    padding: 0;
    margin: 0;
}

.activity-item {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    border-bottom: 1px solid #e9ecef;
}

.activity-item:last-child {
    border-bottom: none;
}

.activity-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    flex-shrink: 0;
}

.activity-create { background: rgba(40,167,69,0.1); color: #28a745; }
.activity-update { background: rgba(0,123,255,0.1); color: #007bff; }
.activity-delete { background: rgba(220,53,69,0.1); color: #dc3545; }

.activity-content p {
    margin: 0;
    font-size: 0.9rem;
}

.activity-content small {
    color: #6c757d;
}
```

### Timeago Filter

```python
# app/utils/filters.py

from datetime import datetime
from flask import Blueprint

filters_bp = Blueprint('filters', __name__)

@filters_bp.app_template_filter('timeago')
def timeago_filter(date):
    """Convert datetime to relative time string"""
    if not date:
        return ''
    
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'hace un momento'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'hace {minutes} minuto{"s" if minutes > 1 else ""}'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'hace {hours} hora{"s" if hours > 1 else ""}'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'hace {days} día{"s" if days > 1 else ""}'
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'hace {weeks} semana{"s" if weeks > 1 else ""}'
    else:
        return date.strftime('%d/%m/%Y')
```

---

## Dependencies

**Blocked by:**
- Issue #1-#3 (Phase 2): Core CRUD modules (for data)
- Issue #4 (Phase 2): User Authentication (for audit log)

**Blocks:**
- Phase 5: Advanced Dashboards (builds on this)

---

## Related Documentation

- `docs/PRD.md` Section 3.2.1: Visual Dashboard requirements
- `docs/PROJECT_ANALYSIS.md`: Current dashboard status
- Plotly.js documentation: https://plotly.com/javascript/

---

## Testing Requirements

- [ ] Test all charts render correctly
- [ ] Test responsive layout on mobile
- [ ] Test statistics match database counts
- [ ] Test quick action links work
- [ ] Test activity feed displays correctly
- [ ] Test tooltips and interactivity

---

## Definition of Done

- [ ] All 4 statistic cards displaying
- [ ] All 3 charts rendering with Plotly
- [ ] Activity feed showing recent actions
- [ ] Quick action buttons functional
- [ ] Responsive layout working
- [ ] Data matches database (729 records total)
- [ ] Code review completed
