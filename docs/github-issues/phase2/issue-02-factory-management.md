# [Phase 2] Factory Management Module

**Labels:** `phase-2`, `crud`, `frontend`, `backend`, `factories`, `high-priority`
**Milestone:** Phase 2: Core Entities & CRUD (Weeks 3-4)
**Estimated Effort:** 3 days
**Depends on:** Issue #1 (Phase 2) ([Phase 2] Client Management Module)

---

## Description

Implement a complete Factory Management module with full CRUD operations for the 403 factory records migrated from Access. Factories represent physical production locations belonging to clients, distributed across 4 provinces. This module supports multiple factories per client and provides geographic filtering capabilities.

### Current State
- Fabrica model exists in database
- No UI for factory management
- No province-based filtering

### Target State
- Full CRUD interface for factories
- Factory list linked to clients
- Province filter (4 provinces: Pinar del Río, Artemisa, Mayabeque, La Habana)
- Factory detail with sample history
- Multiple factories per client support
- Import validation from Access

### Data Volume
| Metric | Value |
|--------|-------|
| Total Factories | 403 records |
| Avg Factories/Client | 2.4 |
| Provinces | 4 (Pinar del Río has majority) |
| Max Factories/Client | ~20+ (large clients) |

---

## Acceptance Criteria

### Factory List View

- [ ] Create `/fabricas` route with paginated list view
- [ ] Display 25 factories per page
- [ ] Show columns: ID, Nombre, Cliente, Provincia, Muestras, Estado
- [ ] Implement search by factory name
- [ ] Add filter by: Cliente, Provincia, Estado
- [ ] Sort by: Nombre, Cliente, Provincia
- [ ] Show client name as clickable link
- [ ] Quick actions: Ver, Editar, Desactivar

### Factory Detail View

- [ ] Create `/fabricas/<id>` detail route
- [ ] Display complete factory information:
  - Nombre
  - Cliente (linked to client detail)
  - Provincia
  - Estado
  - Fecha de creación
- [ ] Show client summary card:
  - Client logo/initials
  - Total factories for this client
  - Link to client detail
- [ ] Display sample history:
  - Last 10 samples from this factory
  - Status indicators
  - Links to entry details
- [ ] Statistics: total samples, samples this year, pending tests
- [ ] Geographic info: province badge, map placeholder

### Factory Creation

- [ ] Create `/fabricas/nueva` route with form
- [ ] Form fields:
  - Cliente (dropdown/search, required)
  - Nombre (required, max 300 chars)
  - Provincia (dropdown, required)
  - Activo (checkbox, default true)
- [ ] Validate duplicate factory names within same client
- [ ] Quick-create from client detail page (pre-fill client)
- [ ] Success message and redirect to detail view

### Factory Editing

- [ ] Create `/fabricas/<id>/editar` route with form
- [ ] Pre-populate all fields
- [ ] Allow changing client (with warning about associations)
- [ ] Same validation as creation
- [ ] Audit log for changes
- [ ] Success message and redirect

### Client-Factory Relationship

- [ ] Show factories list on client detail page
- [ ] Create factory button on client detail page (auto-assign client)
- [ ] Show factory count badge on client list
- [ ] Filter factories by client view
- [ ] Bulk operations for client factories

### Province Management

- [ ] Display province with color-coded badges:
  - Pinar del Río: Green
  - Artemisa: Blue
  - Mayabeque: Orange
  - La Habana: Purple
- [ ] Filter by single or multiple provinces
- [ ] Province statistics on dashboard
- [ ] Geographic distribution chart

### Import Validation

- [ ] Validate FK integrity during Access import:
  - All factories must have valid cliente_id
  - All factories must have valid provincia_id
- [ ] Report orphaned factories (if any)
- [ ] Validate factory name uniqueness per client
- [ ] Log import errors with row numbers

---

## Technical Notes

### URL Routes

```python
# app/routes/fabricas.py

@fabricas_bp.route('/fabricas')
def listar_fabricas():
    """List factories with filters"""
    pass

@fabricas_bp.route('/fabricas/<int:id>')
def ver_fabrica(id):
    """Factory detail with sample history"""
    pass

@fabricas_bp.route('/fabricas/nueva', methods=['GET', 'POST'])
def crear_fabrica():
    """Create new factory"""
    pass

@fabricas_bp.route('/fabricas/nueva/<int:cliente_id>', methods=['GET', 'POST'])
def crear_fabrica_para_cliente(cliente_id):
    """Create factory for specific client"""
    pass

@fabricas_bp.route('/fabricas/<int:id>/editar', methods=['GET', 'POST'])
def editar_fabrica(id):
    """Edit factory"""
    pass

@fabricas_bp.route('/clientes/<int:cliente_id>/fabricas')
def fabricas_por_cliente(cliente_id):
    """List all factories for a client"""
    pass
```

### Factory Form

```python
# app/forms/fabrica.py

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError
from app.database.models import Fabrica, Cliente

class FabricaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    nombre = StringField('Nombre de la Fábrica', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=300, message='Máximo 300 caracteres')
    ])
    provincia_id = SelectField('Provincia', coerce=int, validators=[DataRequired()])
    activo = BooleanField('Activa', default=True)
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate dropdowns
        self.cliente_id.choices = [
            (c.id, c.nombre) for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
        ]
        from app.database.models import Provincia
        self.provincia_id.choices = [
            (p.id, p.nombre) for p in Provincia.query.all()
        ]
    
    def validate_nombre(self, field):
        """Check for duplicate factory names within same client"""
        fabrica = Fabrica.query.filter_by(
            cliente_id=self.cliente_id.data,
            nombre=field.data
        ).first()
        if fabrica and (not self.id or fabrica.id != self.id.data):
            raise ValidationError('Este cliente ya tiene una fábrica con este nombre')
```

### Province Badge Styles

```css
/* static/css/provincias.css */

.badge-provincia {
    padding: 0.35em 0.65em;
    border-radius: 0.25rem;
    font-size: 0.875em;
    font-weight: 600;
}

.badge-pinar { background-color: #28a745; color: white; }
.badge-artemisa { background-color: #007bff; color: white; }
.badge-mayabeque { background-color: #fd7e14; color: white; }
.badge-habana { background-color: #6f42c1; color: white; }
```

### Factory List with Province Filter

```html
<!-- templates/fabricas/listar.html -->

{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>Fábricas</h1>
    <a href="{{ url_for('fabricas.crear_fabrica') }}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Nueva Fábrica
    </a>
</div>

<!-- Province Filter Buttons -->
<div class="province-filters mb-3">
    <a href="{{ url_for('fabricas.listar_fabricas') }}" 
       class="btn btn-sm {% if not request.args.get('provincia') %}btn-dark{% else %}btn-outline-secondary{% endif %}">
        Todas
    </a>
    {% for prov in provincias %}
    <a href="{{ url_for('fabricas.listar_fabricas', provincia=prov.id) }}"
       class="btn btn-sm {% if request.args.get('provincia')|int == prov.id %}btn-dark{% else %}btn-outline-secondary{% endif %}">
        {{ prov.sigla }}
    </a>
    {% endfor %}
</div>

<!-- Filters Card -->
<div class="card filters-card mb-3">
    <form method="GET" class="row">
        <div class="col-md-4">
            <input type="text" name="q" class="form-control" placeholder="Buscar fábrica..."
                   value="{{ request.args.get('q', '') }}">
        </div>
        <div class="col-md-4">
            <select name="cliente" class="form-control">
                <option value="">Todos los clientes</option>
                {% for cli in clientes %}
                <option value="{{ cli.id }}" {% if request.args.get('cliente')|int == cli.id %}selected{% endif %}>
                    {{ cli.nombre[:50] }}...
                </option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-secondary btn-block">Filtrar</button>
        </div>
    </form>
</div>

<!-- Statistics Cards -->
<div class="row mb-3">
    <div class="col-md-3">
        <div class="card stat-card">
            <div class="card-body">
                <h5>{{ total_fabricas }}</h5>
                <small>Total Fábricas</small>
            </div>
        </div>
    </div>
    {% for stat in provincia_stats %}
    <div class="col-md-2">
        <div class="card stat-card">
            <div class="card-body">
                <h5>{{ stat.count }}</h5>
                <small class="badge badge-{{ stat.color }}">{{ stat.sigla }}</small>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Factories Table -->
<div class="card">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Fábrica</th>
                <th>Cliente</th>
                <th>Provincia</th>
                <th>Muestras</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for fabrica in fabricas.items %}
            <tr>
                <td>{{ fabrica.id }}</td>
                <td>
                    <a href="{{ url_for('fabricas.ver_fabrica', id=fabrica.id) }}">
                        {{ fabrica.nombre }}
                    </a>
                </td>
                <td>
                    <a href="{{ url_for('clientes.ver_cliente', id=fabrica.cliente_id) }}">
                        {{ fabrica.cliente.nombre[:40] }}...
                    </a>
                </td>
                <td>
                    <span class="badge-provincia badge-{{ fabrica.provincia.sigla|lower }}">
                        {{ fabrica.provincia.sigla }}
                    </span>
                </td>
                <td>
                    <span class="badge badge-info">{{ fabrica.entradas|length }}</span>
                </td>
                <td>
                    <a href="{{ url_for('fabricas.ver_fabrica', id=fabrica.id) }}" class="btn btn-sm btn-info">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="{{ url_for('fabricas.editar_fabrica', id=fabrica.id) }}" class="btn btn-sm btn-warning">
                        <i class="fas fa-edit"></i>
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    {{ render_pagination(fabricas, 'fabricas.listar_fabricas') }}
</div>
{% endblock %}
```

### Factory Detail with Sample History

```html
<!-- templates/fabricas/ver.html -->

{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>{{ fabrica.nombre }}</h1>
    <div>
        <a href="{{ url_for('fabricas.editar_fabrica', id=fabrica.id) }}" class="btn btn-warning">
            <i class="fas fa-edit"></i> Editar
        </a>
    </div>
</div>

<div class="row">
    <!-- Factory Info -->
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5>Información</h5>
            </div>
            <div class="card-body">
                <table class="table table-borderless">
                    <tr>
                        <td><strong>Cliente:</strong></td>
                        <td>
                            <a href="{{ url_for('clientes.ver_cliente', id=fabrica.cliente_id) }}">
                                {{ fabrica.cliente.nombre }}
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Provincia:</strong></td>
                        <td>
                            <span class="badge-provincia badge-{{ fabrica.provincia.sigla|lower }}">
                                {{ fabrica.provincia.nombre }}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Estado:</strong></td>
                        <td>
                            {% if fabrica.activo %}
                            <span class="badge badge-success">Activa</span>
                            {% else %}
                            <span class="badge badge-secondary">Inactiva</span>
                            {% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Creada:</strong></td>
                        <td>{{ fabrica.creado_en.strftime('%d/%m/%Y') }}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <!-- Statistics -->
        <div class="card mt-3">
            <div class="card-header">
                <h5>Estadísticas</h5>
            </div>
            <div class="card-body">
                <div class="stat-item">
                    <span class="stat-value">{{ stats.total_muestras }}</span>
                    <span class="stat-label">Total Muestras</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{{ stats.muestras_anio }}</span>
                    <span class="stat-label">Muestras este año</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{{ stats.ensayos_pendientes }}</span>
                    <span class="stat-label">Ensayos pendientes</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Sample History -->
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5>Historial de Muestras</h5>
                <a href="#" class="btn btn-sm btn-primary">Ver todas</a>
            </div>
            <div class="card-body p-0">
                <table class="table table-sm mb-0">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Fecha</th>
                            <th>Producto</th>
                            <th>Lote</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for entrada in ultimas_muestras %}
                        <tr>
                            <td>{{ entrada.id }}</td>
                            <td>{{ entrada.fecha_entrada.strftime('%d/%m/%Y') }}</td>
                            <td>{{ entrada.producto.nombre[:30] }}...</td>
                            <td>{{ entrada.lote }}</td>
                            <td>
                                {% if entrada.anulado %}
                                <span class="badge badge-danger">Anulada</span>
                                {% elif entrada.entrada_entregada %}
                                <span class="badge badge-success">Entregada</span>
                                {% else %}
                                <span class="badge badge-warning">Pendiente</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Dependencies

**Blocked by:**
- Issue #1 (Phase 2): [Phase 2] Client Management Module
- Issue #2 (Phase 1): [Phase 1] Master Data Models (Fabrica model)

**Blocks:**
- Issue #3 (Phase 2): [Phase 2] Product Catalog Module
- Issue #5 (Phase 2): [Phase 2] Master Data Import from Access

---

## Related Documentation

- `docs/PRD.md` Section 2.3.2: Master Data tables
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Lines 162-170: Fabricas schema
- `plans/MIGRATION_PLAN.md` Phase 2.1: Factory Management

---

## Testing Requirements

- [ ] Test factory creation with all provinces
- [ ] Test duplicate name validation within client
- [ ] Test province filter shows correct results
- [ ] Test sample history displays correctly
- [ ] Test FK validation during import
- [ ] Test responsive design

---

## Definition of Done

- [ ] All CRUD operations functional
- [ ] Province filter working
- [ ] Client association working
- [ ] Sample history displayed
- [ ] Import validation complete
- [ ] Code review completed
