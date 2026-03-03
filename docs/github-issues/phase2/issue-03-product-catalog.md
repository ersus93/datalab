# [Phase 2] Product Catalog Module

**Labels:** `phase-2`, `crud`, `frontend`, `backend`, `products`, `high-priority`
**Milestone:** Phase 2: Core Entities & CRUD (Weeks 3-4)
**Estimated Effort:** 3 days
**Depends on:** Issue #1, #2 (Phase 1) ([Phase 1] Reference & Master Data Models)

---

## Description

Implement a complete Product Catalog module with full CRUD operations for the 160 product records migrated from Access. Products are classified by industry sector (rama) and have destination tracking for regulatory purposes. This module also manages product-test associations for the laboratory workflow.

### Current State
- Producto model exists in database
- No UI for product management
- No sector classification interface
- No product-test associations

### Target State
- Full CRUD interface for products
- Product catalog with 13 sector classifications (ramas)
- Destination tracking (7 destinos: CF, AC, ME, CD, DE, etc.)
- Product-Test association management
- Advanced search and filtering
- Import from Access with validation

### Data Volume
| Metric | Value |
|--------|-------|
| Total Products | 160 records |
| Sectors (Ramas) | 13 classifications |
| Destinations | 7 types |
| FQ Tests | 143 available |
| ES Tests | 29 available |

### Sector Classifications (Ramas)
1. Carne
2. Lácteos
3. Vegetales
4. Bebidas
5. Confitería
6. Pescado
7. Cereales
8. Grasas
9. Especies
10. Conservas
11. Panadería
12. Otros alimentos
13. No alimentos

### Destination Types (Destinos)
- CF: Canasta Familiar
- AC: Amplio Consumo
- ME: Merienda Escolar
- CD: Captación de Divisas
- DE: Destinos Especiales

---

## Acceptance Criteria

### Product List View

- [ ] Create `/productos` route with paginated list
- [ ] Display 25 products per page
- [ ] Show columns: ID, Producto, Rama, Destino, Tests, Estado
- [ ] Implement search by product name
- [ ] Add filter by: Rama, Destino, Estado
- [ ] Sort by: Nombre, Rama, Destino
- [ ] Show sector badge with color coding
- [ ] Show destination abbreviation
- [ ] Quick actions: Ver, Editar, Asociar Tests

### Product Detail View

- [ ] Create `/productos/<id>` detail route
- [ ] Display complete product information:
  - Nombre del producto
  - Rama (sector) with description
  - Destino with full name
  - Estado (activo/inactivo)
  - Fecha de creación
- [ ] Show associated tests section:
  - FQ tests assigned
  - ES tests assigned
  - Add/remove test buttons
- [ ] Show sample history for this product
- [ ] Statistics: total samples, tests performed
- [ ] Related products in same sector

### Product Creation

- [ ] Create `/productos/nuevo` route with form
- [ ] Form fields:
  - Nombre (required, unique, max 300 chars)
  - Rama (dropdown, 13 options, required)
  - Destino (dropdown, 7 options, required)
  - Activo (checkbox, default true)
- [ ] Validate unique product name
- [ ] Inline test assignment (optional)
- [ ] Success message and redirect

### Product Editing

- [ ] Create `/productos/<id>/editar` route
- [ ] Pre-populate all fields
- [ ] Allow changing rama and destino
- [ ] Show warning if samples exist
- [ ] Audit log for changes
- [ ] Success message and redirect

### Product-Test Associations

- [ ] Create `/productos/<id>/ensayos` route
- [ ] Show available FQ tests (143) with checkboxes
- [ ] Show available ES tests (29) with checkboxes
- [ ] Group tests by area/category
- [ ] Search tests by name
- [ ] Save associations with one click
- [ ] Show current associations highlighted
- [ ] Bulk add/remove tests

### Sector (Rama) Management

- [ ] Color-coded sector badges:
  - Carne: Red (#dc3545)
  - Lácteos: Blue (#007bff)
  - Vegetales: Green (#28a745)
  - Bebidas: Purple (#6f42c1)
  - Confitería: Pink (#e83e8c)
  - Pescado: Cyan (#17a2b8)
  - Cereales: Yellow (#ffc107)
  - Others: Gray (#6c757d)
- [ ] Filter by single or multiple sectors
- [ ] Sector statistics on dashboard
- [ ] Sector distribution chart

### Destination Tracking

- [ ] Show destination with icon/badge:
  - CF: Shopping basket icon
  - AC: Users icon
  - ME: School icon
  - CD: Dollar icon
  - DE: Star icon
- [ ] Filter by destination
- [ ] Destination compliance report
- [ ] Export by destination

---

## Technical Notes

### URL Routes

```python
# app/routes/productos.py

@productos_bp.route('/productos')
def listar_productos():
    """List products with filters"""
    pass

@productos_bp.route('/productos/<int:id>')
def ver_producto(id):
    """Product detail view"""
    pass

@productos_bp.route('/productos/nuevo', methods=['GET', 'POST'])
def crear_producto():
    """Create new product"""
    pass

@productos_bp.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
def editar_producto(id):
    """Edit product"""
    pass

@productos_bp.route('/productos/<int:id>/ensayos', methods=['GET', 'POST'])
def gestionar_ensayos(id):
    """Manage product-test associations"""
    pass

@productos_bp.route('/api/productos/<int:id>/ensayos', methods=['PUT'])
def api_actualizar_ensayos(id):
    """API endpoint for updating test associations"""
    pass
```

### Product Form

```python
# app/forms/producto.py

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.database.models import Producto

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=300, message='Máximo 300 caracteres')
    ])
    rama_id = SelectField('Rama / Sector', coerce=int, validators=[DataRequired()])
    destino_id = SelectField('Destino', coerce=int, validators=[DataRequired()])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate dropdowns
        from app.database.models import Rama, Destino
        self.rama_id.choices = [
            (r.id, r.nombre) for r in Rama.query.order_by(Rama.nombre).all()
        ]
        self.destino_id.choices = [
            (d.id, f"{d.sigla} - {d.nombre}") for d in Destino.query.all()
        ]
    
    def validate_nombre(self, field):
        """Check for duplicate product names"""
        producto = Producto.query.filter_by(nombre=field.data).first()
        if producto and (not self.id or producto.id != self.id.data):
            raise ValidationError('Ya existe un producto con este nombre')
```

### Sector Color Helper

```python
# app/utils/ramas.py

RAMA_COLORS = {
    1: {'name': 'Carne', 'color': '#dc3545', 'badge': 'danger'},
    2: {'name': 'Lácteos', 'color': '#007bff', 'badge': 'primary'},
    3: {'name': 'Vegetales', 'color': '#28a745', 'badge': 'success'},
    4: {'name': 'Bebidas', 'color': '#6f42c1', 'badge': 'purple'},
    5: {'name': 'Confitería', 'color': '#e83e8c', 'badge': 'pink'},
    6: {'name': 'Pescado', 'color': '#17a2b8', 'badge': 'info'},
    7: {'name': 'Cereales', 'color': '#ffc107', 'badge': 'warning'},
    8: {'name': 'Grasas', 'color': '#fd7e14', 'badge': 'orange'},
    9: {'name': 'Especies', 'color': '#20c997', 'badge': 'teal'},
    10: {'name': 'Conservas', 'color': '#6610f2', 'badge': 'indigo'},
    11: {'name': 'Panadería', 'color': '#795548', 'badge': 'brown'},
    12: {'name': 'Otros alimentos', 'color': '#6c757d', 'badge': 'secondary'},
    13: {'name': 'No alimentos', 'color': '#343a40', 'badge': 'dark'},
}

def get_rama_color(rama_id):
    """Get color info for a sector"""
    return RAMA_COLORS.get(rama_id, {'color': '#6c757d', 'badge': 'secondary'})
```

### Product List with Sector Badges

```html
<!-- templates/productos/listar.html -->

{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>Catálogo de Productos</h1>
    <a href="{{ url_for('productos.crear_producto') }}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Nuevo Producto
    </a>
</div>

<!-- Sector Filter -->
<div class="sector-filters mb-3">
    <span class="mr-2">Filtrar por sector:</span>
    <a href="{{ url_for('productos.listar_productos') }}" 
       class="badge {% if not request.args.get('rama') %}badge-dark{% else %}badge-light{% endif %}">
        Todos
    </a>
    {% for rama in ramas %}
    <a href="{{ url_for('productos.listar_productos', rama=rama.id) }}"
       class="badge badge-{{ rama_colors[rama.id].badge }}">
        {{ rama.nombre }}
    </a>
    {% endfor %}
</div>

<!-- Filters -->
<div class="card filters-card mb-3">
    <form method="GET" class="row">
        <div class="col-md-4">
            <input type="text" name="q" class="form-control" placeholder="Buscar producto..."
                   value="{{ request.args.get('q', '') }}">
        </div>
        <div class="col-md-3">
            <select name="destino" class="form-control">
                <option value="">Todos los destinos</option>
                {% for dest in destinos %}
                <option value="{{ dest.id }}" {% if request.args.get('destino')|int == dest.id %}selected{% endif %}>
                    {{ dest.sigla }} - {{ dest.nombre }}
                </option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-3">
            <select name="con_ensayos" class="form-control">
                <option value="">Todos</option>
                <option value="1" {% if request.args.get('con_ensayos') == '1' %}selected{% endif %}>
                    Con ensayos asignados
                </option>
                <option value="0" {% if request.args.get('con_ensayos') == '0' %}selected{% endif %}>
                    Sin ensayos
                </option>
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-secondary btn-block">Filtrar</button>
        </div>
    </form>
</div>

<!-- Products Table -->
<div class="card">
    <table class="table table-hover">
        <thead>
            <tr>
                <th>ID</th>
                <th>Producto</th>
                <th>Rama</th>
                <th>Destino</th>
                <th>Ensayos</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for producto in productos.items %}
            <tr>
                <td>{{ producto.id }}</td>
                <td>
                    <a href="{{ url_for('productos.ver_producto', id=producto.id) }}">
                        {{ producto.nombre }}
                    </a>
                </td>
                <td>
                    <span class="badge badge-{{ rama_colors[producto.rama_id].badge }}">
                        {{ producto.rama.nombre }}
                    </span>
                </td>
                <td>
                    <span class="badge badge-light" title="{{ producto.destino.nombre }}">
                        <i class="fas fa-{{ destino_icons[producto.destino.sigla] }}"></i>
                        {{ producto.destino.sigla }}
                    </span>
                </td>
                <td>
                    {% set total_tests = producto.ensayos|length + producto.ensayos_es|length %}
                    {% if total_tests > 0 %}
                    <span class="badge badge-info">{{ total_tests }} ensayos</span>
                    {% else %}
                    <span class="badge badge-warning">Sin ensayos</span>
                    {% endif %}
                </td>
                <td>
                    <a href="{{ url_for('productos.ver_producto', id=producto.id) }}" class="btn btn-sm btn-info">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="{{ url_for('productos.editar_producto', id=producto.id) }}" class="btn btn-sm btn-warning">
                        <i class="fas fa-edit"></i>
                    </a>
                    <a href="{{ url_for('productos.gestionar_ensayos', id=producto.id) }}" class="btn btn-sm btn-primary">
                        <i class="fas fa-flask"></i>
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    {{ render_pagination(productos, 'productos.listar_productos') }}
</div>
{% endblock %}
```

### Test Association Manager

```html
<!-- templates/productos/ensayos.html -->

{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>Asociar Ensayos - {{ producto.nombre }}</h1>
    <a href="{{ url_for('productos.ver_producto', id=producto.id) }}" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> Volver
    </a>
</div>

<div class="row">
    <!-- FQ Tests -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Ensayos Físico-Químicos (FQ)</h5>
                <input type="text" class="form-control form-control-sm" 
                       placeholder="Buscar ensayo..." id="search-fq">
            </div>
            <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                <form id="ensayos-form" method="POST">
                    {{ form.hidden_tag() }}
                    
                    <div class="test-list">
                        {% for ensayo in ensayos_fq %}
                        <div class="form-check test-item" data-name="{{ ensayo.nombre_corto|lower }}">
                            <input class="form-check-input" type="checkbox" 
                                   name="ensayos_fq" value="{{ ensayo.id }}"
                                   id="fq_{{ ensayo.id }}"
                                   {% if ensayo.id in ensayos_asignados_fq %}checked{% endif %}>
                            <label class="form-check-label" for="fq_{{ ensayo.id }}">
                                <strong>{{ ensayo.nombre_corto }}</strong>
                                <small class="text-muted">{{ ensayo.nombre_oficial[:60] }}...</small>
                                <span class="badge badge-light">${{ ensayo.precio }}</span>
                            </label>
                        </div>
                        {% endfor %}
                    </div>
            </div>
        </div>
    </div>
    
    <!-- ES Tests -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Ensayos Sensoriales (ES)</h5>
                <input type="text" class="form-control form-control-sm" 
                       placeholder="Buscar ensayo..." id="search-es">
            </div>
            <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                <div class="test-list">
                    {% for ensayo in ensayos_es %}
                    <div class="form-check test-item" data-name="{{ ensayo.nombre_corto|lower }}">
                        <input class="form-check-input" type="checkbox" 
                               name="ensayos_es" value="{{ ensayo.id }}"
                               id="es_{{ ensayo.id }}"
                               {% if ensayo.id in ensayos_asignados_es %}checked{% endif %}>
                        <label class="form-check-label" for="es_{{ ensayo.id }}">
                            <strong>{{ ensayo.nombre_corto }}</strong>
                            <small class="text-muted">{{ ensayo.tipo_es.nombre if ensayo.tipo_es }}</small>
                            <span class="badge badge-light">${{ ensayo.precio }}</span>
                        </label>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-3">
    <div class="col-12">
        <button type="submit" class="btn btn-success btn-lg btn-block">
            <i class="fas fa-save"></i> Guardar Asociaciones
        </button>
    </div>
</div>
</form>

{% block scripts %}
<script>
// Search functionality for test lists
document.getElementById('search-fq').addEventListener('input', function(e) {
    const term = e.target.value.toLowerCase();
    document.querySelectorAll('#fq-tests .test-item').forEach(item => {
        const name = item.dataset.name;
        item.style.display = name.includes(term) ? 'block' : 'none';
    });
});

document.getElementById('search-es').addEventListener('input', function(e) {
    const term = e.target.value.toLowerCase();
    document.querySelectorAll('#es-tests .test-item').forEach(item => {
        const name = item.dataset.name;
        item.style.display = name.includes(term) ? 'block' : 'none';
    });
});
</script>
{% endblock %}

{% endblock %}
```

---

## Dependencies

**Blocked by:**
- Issue #1, #2 (Phase 1): Reference & Master Data Models
- Issue #3 (Phase 1): Test Catalog Models (Ensayos, EnsayosES)

**Blocks:**
- Issue #5 (Phase 2): Master Data Import
- Phase 3: Sample Management (uses Producto references)

---

## Related Documentation

- `docs/PRD.md` Section 2.3.2: Product Catalog
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Lines 172-179: Productos schema
- `plans/MIGRATION_PLAN.md` Phase 2.1: Product Catalog

---

## Testing Requirements

- [ ] Test product creation with all sectors
- [ ] Test duplicate name validation
- [ ] Test sector filter displays correctly
- [ ] Test test association save/load
- [ ] Test search filters correctly
- [ ] Test responsive design

---

## Definition of Done

- [ ] All CRUD operations functional
- [ ] Sector badges color-coded
- [ ] Test association manager working
- [ ] Destination tracking complete
- [ ] Import validation complete
- [ ] Code review completed
