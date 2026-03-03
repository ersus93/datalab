# [Phase 3] Sample Entry UI/UX

**Labels:** `phase-3`, `frontend`, `ui/ux`, `forms`, `high-priority`
**Milestone:** Phase 3: Sample Management (Weeks 5-6)
**Estimated Effort:** 4 days

---

## Description

Create a comprehensive user interface for sample entry management (Entradas) that provides an intuitive, efficient workflow for laboratory technicians. The UI includes sample entry forms with smart selectors, validation, date pickers, and a powerful list view with filters.

This interface is the **primary user touchpoint** for daily laboratory operations.

---

## Acceptance Criteria

### Sample Entry Form
- [ ] Create comprehensive entry form with sections:
  
  **Identification Section:**
  - Entry code input (auto-generated or manual)
  - Lot number input with X-XXXX format validation
  - Part number input (NroParte)
  
  **Client & Location Section:**
  - Factory selector (dropdown with search)
  - Client display (auto-populated from factory)
  - Order linking (optional Pedido selector)
  
  **Product Section:**
  - Product selector with autocomplete
  - Industry sector dropdown (Rama)
  - Product details display (on selection)
  
  **Quantity Section:**
  - Quantity received input (CantidadRecib)
  - Unit of measurement selector
  - Sample quantity input (CantidadMuest)
  - Balance preview (auto-calculated)
  
  **Dates Section:**
  - Manufacturing date picker (FechFab)
  - Expiration date picker (FechVenc)
  - Sampling date picker (FechMuestreo)
  - Entry date (auto-set to today)
  
  **Status & Notes Section:**
  - Status dropdown (Received/In Process/Completed/Delivered)
  - Work order flag (EnOS)
  - Observations textarea

### Smart Selectors
- [ ] Factory selector:
  - Dropdown with factory names
  - Search/filter capability
  - Client name displayed alongside
  - Recent selections quick access
- [ ] Product selector:
  - Autocomplete search
  - Product details on hover
  - Category filtering
  - Recently used products
- [ ] Order linking:
  - Optional "Link to Order" toggle
  - Order selector (filtered by client)
  - Create new order inline option

### Form Validation
- [ ] Real-time validation:
  - Lot format: X-XXXX pattern
  - Date validation: FechVenc > FechFab
  - Quantity: non-negative numbers
  - Required fields: Producto, Fabrica, Cliente
- [ ] Visual feedback:
  - Green check for valid fields
  - Red highlight for errors
  - Helpful error messages
- [ ] Submit validation:
  - Prevent submission with errors
  - Summary of issues to fix

### Date Pickers
- [ ] Consistent date picker component:
  - Calendar popup
  - Date format: DD/MM/YYYY
  - Quick select: Today, Tomorrow, +1 week
  - Manufacturing to Expiration auto-calculation
- [ ] Date validation:
  - Expiration must be after manufacturing
  - Sampling date validation
  - Past date warnings

### Entry List View
- [ ] Comprehensive list view:
  - Sortable columns: Code, Client, Product, Lot, Status, Date
  - Pagination (20/50/100 per page)
  - Row actions: View, Edit, Delete
  - Bulk actions: Change status, Export
- [ ] Advanced filtering:
  - Date range filter (entry date)
  - Status filter (multi-select)
  - Client filter
  - Product filter
  - Lot number search
  - Quick filters: Today, This Week, This Month
- [ ] Display columns:
  - Entry code
  - Client name
  - Product name
  - Lot number
  - Status badge (colored)
  - Balance (CantidadRecib - CantidadEntreg)
  - Entry date

### Entry Detail View
- [ ] Detail view layout:
  - Header: Entry code, status badge, action buttons
  - Info cards: Client, Product, Lot, Dates
  - Quantities section with balance display
  - Status history timeline
  - Related orders/entries
  - Observations section
- [ ] Actions available:
  - Edit entry
  - Change status
  - Record delivery
  - Print label
  - Duplicate entry

### Dashboard Widgets
- [ ] Entry statistics cards:
  - Today's entries
  - Entries in process
  - Pending delivery
  - Cancelled entries
- [ ] Quick entry button
- [ ] Recent entries list
- [ ] Entry status breakdown (mini chart)

### Responsive Design
- [ ] Desktop layout (full sidebar)
- [ ] Tablet layout (condensed)
- [ ] Mobile layout (stacked, touch-friendly)
- [ ] Print-friendly entry detail view

---

## Technical Notes

### Form Component Structure

```html
<!-- templates/entradas/form.html -->

{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
  <h1>{% if entrada %}Editar{% else %}Nueva{% endif %} Entrada</h1>
  
  <form id="entrada-form" method="POST" action="{{ url_for('entradas.save') }}">
    {{ form.hidden_tag() }}
    
    <!-- Identification Section -->
    <div class="card mb-3">
      <div class="card-header">Identificación</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            {{ form.codigo.label }}
            {{ form.codigo(class="form-control", placeholder="AUTO") }}
          </div>
          <div class="col-md-3">
            {{ form.lote.label }}
            {{ form.lote(class="form-control", placeholder="A-1234", 
                        pattern="[A-Z]-\d{4}", title="Formato: X-XXXX") }}
            <small class="text-muted">Formato: X-XXXX</small>
          </div>
          <div class="col-md-3">
            {{ form.nro_parte.label }}
            {{ form.nro_parte(class="form-control") }}
          </div>
          <div class="col-md-3">
            {{ form.fech_entrada.label }}
            {{ form.fech_entrada(class="form-control", type="date") }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Client & Location Section -->
    <div class="card mb-3">
      <div class="card-header">Cliente y Ubicación</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            {{ form.fabrica_id.label }}
            <select id="fabrica-select" class="form-select" name="fabrica_id" required>
              <option value="">Seleccionar Fábrica...</option>
            </select>
          </div>
          <div class="col-md-6">
            <label>Cliente</label>
            <input type="text" id="cliente-display" class="form-control" readonly>
            <input type="hidden" id="cliente_id" name="cliente_id">
          </div>
        </div>
        
        <div class="row mt-3">
          <div class="col-md-12">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="link-pedido">
              <label class="form-check-label" for="link-pedido">
                Vincular a Pedido
              </label>
            </div>
          </div>
        </div>
        
        <div class="row mt-2" id="pedido-selector-row" style="display:none;">
          <div class="col-md-6">
            {{ form.pedido_id.label }}
            <select id="pedido-select" class="form-select" name="pedido_id">
              <option value="">Seleccionar Pedido...</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Product Section -->
    <div class="card mb-3">
      <div class="card-header">Producto</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            {{ form.producto_id.label }}
            <select id="producto-select" class="form-select" name="producto_id" required>
              <option value="">Buscar Producto...</option>
            </select>
          </div>
          <div class="col-md-6">
            {{ form.rama_id.label }}
            {{ form.rama_id(class="form-select") }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quantities Section -->
    <div class="card mb-3">
      <div class="card-header">Cantidades</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            {{ form.cantidad_recib.label }}
            {{ form.cantidad_recib(class="form-control", type="number", 
                                   step="0.01", min="0", required=True) }}
          </div>
          <div class="col-md-3">
            {{ form.cantidad_entreg.label }}
            {{ form.cantidad_entreg(class="form-control", type="number", 
                                    step="0.01", min="0", value="0") }}
          </div>
          <div class="col-md-3">
            <label>Saldo</label>
            <input type="text" id="saldo-display" class="form-control" readonly 
                   value="{{ entrada.saldo if entrada else 0 }}">
          </div>
          <div class="col-md-3">
            {{ form.unidad_medida_id.label }}
            {{ form.unidad_medida_id(class="form-select") }}
          </div>
        </div>
        <div class="row mt-3">
          <div class="col-md-4">
            {{ form.cantidad_muest.label }}
            {{ form.cantidad_muest(class="form-control", type="number", step="0.01", min="0") }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Dates Section -->
    <div class="card mb-3">
      <div class="card-header">Fechas</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            {{ form.fech_fab.label }}
            {{ form.fech_fab(class="form-control", type="date") }}
          </div>
          <div class="col-md-4">
            {{ form.fech_venc.label }}
            {{ form.fech_venc(class="form-control", type="date") }}
            <small class="text-danger" id="fecha-error" style="display:none;">
              La fecha de vencimiento debe ser posterior a la de fabricación
            </small>
          </div>
          <div class="col-md-4">
            {{ form.fech_muestreo.label }}
            {{ form.fech_muestreo(class="form-control", type="date") }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Status & Notes Section -->
    <div class="card mb-3">
      <div class="card-header">Estado y Observaciones</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            {{ form.status.label }}
            {{ form.status(class="form-select") }}
          </div>
          <div class="col-md-6">
            <div class="form-check mt-4">
              {{ form.en_os(class="form-check-input") }}
              {{ form.en_os.label(class="form-check-label") }}
            </div>
          </div>
        </div>
        <div class="row mt-3">
          <div class="col-md-12">
            {{ form.observaciones.label }}
            {{ form.observaciones(class="form-control", rows="3") }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
      <a href="{{ url_for('entradas.index') }}" class="btn btn-secondary">Cancelar</a>
      <button type="submit" class="btn btn-primary">Guardar</button>
    </div>
  </form>
</div>
{% endblock %}

{% block scripts %}
<script>
// Factory selector with client auto-population
$('#fabrica-select').select2({
  ajax: {
    url: '/api/fabricas/search',
    dataType: 'json',
    delay: 250,
    processResults: function(data) {
      return {
        results: data.map(f => ({
          id: f.id,
          text: f.nombre,
          cliente: f.cliente
        }))
      };
    }
  }
}).on('select2:select', function(e) {
  var data = e.params.data;
  $('#cliente-display').val(data.cliente.nombre);
  $('#cliente_id').val(data.cliente.id);
  
  // Load orders for this client
  loadPedidos(data.cliente.id);
});

// Product selector
$('#producto-select').select2({
  ajax: {
    url: '/api/productos/search',
    dataType: 'json',
    delay: 250
  }
});

// Balance auto-calculation
function updateSaldo() {
  var recib = parseFloat($('#cantidad_recib').val()) || 0;
  var entreg = parseFloat($('#cantidad_entreg').val()) || 0;
  var saldo = recib - entreg;
  $('#saldo-display').val(saldo.toFixed(2));
}

$('#cantidad_recib, #cantidad_entreg').on('input', updateSaldo);

// Date validation
$('#fech_venc').on('change', function() {
  var fab = $('#fech_fab').val();
  var venc = $(this).val();
  if (fab && venc && venc < fab) {
    $('#fecha-error').show();
    $(this).addClass('is-invalid');
  } else {
    $('#fecha-error').hide();
    $(this).removeClass('is-invalid');
  }
});

// Toggle pedido selector
$('#link-pedido').on('change', function() {
  $('#pedido-selector-row').toggle(this.checked);
});
</script>
{% endblock %}
```

### List View Component

```html
<!-- templates/entradas/list.html -->

<div class="d-flex justify-content-between align-items-center mb-3">
  <h1>Entradas</h1>
  <a href="{{ url_for('entradas.create') }}" class="btn btn-primary">
    <i class="bi bi-plus"></i> Nueva Entrada
  </a>
</div>

<!-- Filters -->
<div class="card mb-3">
  <div class="card-body">
    <form id="filter-form" class="row g-3">
      <div class="col-md-3">
        <input type="text" name="search" class="form-control" 
               placeholder="Buscar código, lote...">
      </div>
      <div class="col-md-2">
        <select name="status" class="form-select">
          <option value="">Todos los estados</option>
          <option value="RECIBIDO">Recibido</option>
          <option value="EN_PROCESO">En Proceso</option>
          <option value="COMPLETADO">Completado</option>
          <option value="ENTREGADO">Entregado</option>
        </select>
      </div>
      <div class="col-md-3">
        <select id="cliente-filter" name="cliente_id" class="form-select">
          <option value="">Todos los clientes</option>
        </select>
      </div>
      <div class="col-md-2">
        <input type="date" name="desde" class="form-control" placeholder="Desde">
      </div>
      <div class="col-md-2">
        <button type="submit" class="btn btn-outline-primary">Filtrar</button>
        <button type="reset" class="btn btn-outline-secondary">Limpiar</button>
      </div>
    </form>
  </div>
</div>

<!-- Quick Filters -->
<div class="btn-group mb-3" role="group">
  <button type="button" class="btn btn-outline-secondary" data-filter="today">Hoy</button>
  <button type="button" class="btn btn-outline-secondary" data-filter="week">Esta Semana</button>
  <button type="button" class="btn btn-outline-secondary" data-filter="month">Este Mes</button>
</div>

<!-- Table -->
<table class="table table-striped table-hover">
  <thead>
    <tr>
      <th>Código</th>
      <th>Cliente</th>
      <th>Producto</th>
      <th>Lote</th>
      <th>Estado</th>
      <th>Saldo</th>
      <th>Fecha Entrada</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
    {% for entrada in entradas %}
    <tr>
      <td>{{ entrada.codigo }}</td>
      <td>{{ entrada.cliente.nombre }}</td>
      <td>{{ entrada.producto.nombre }}</td>
      <td><code>{{ entrada.lote }}</code></td>
      <td>
        <span class="badge bg-{{ entrada.status_color }}">
          {{ entrada.status_display }}
        </span>
      </td>
      <td>{{ entrada.saldo }} {{ entrada.unidad_medida.codigo if entrada.unidad_medida }}</td>
      <td>{{ entrada.fech_entrada.strftime('%d/%m/%Y') }}</td>
      <td>
        <div class="btn-group btn-group-sm">
          <a href="{{ url_for('entradas.show', id=entrada.id) }}" 
             class="btn btn-outline-primary">Ver</a>
          <a href="{{ url_for('entradas.edit', id=entrada.id) }}" 
             class="btn btn-outline-secondary">Editar</a>
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<!-- Pagination -->
{{ render_pagination(pagination, 'entradas.index') }}
```

### Status Badge Component

```html
<!-- templates/components/status-badge.html -->

{% macro status_badge(status) %}
  {% set colors = {
    'RECIBIDO': 'secondary',
    'EN_PROCESO': 'primary',
    'COMPLETADO': 'success',
    'ENTREGADO': 'info',
    'ANULADO': 'danger'
  } %}
  {% set labels = {
    'RECIBIDO': 'Recibido',
    'EN_PROCESO': 'En Proceso',
    'COMPLETADO': 'Completado',
    'ENTREGADO': 'Entregado',
    'ANULADO': 'Anulado'
  } %}
  <span class="badge bg-{{ colors.get(status, 'secondary') }}">
    {{ labels.get(status, status) }}
  </span>
{% endmacro %}
```

### JavaScript Form Validation

```javascript
// static/js/entrada-form.js

class EntradaForm {
  constructor() {
    this.form = document.getElementById('entrada-form');
    this.setupValidation();
    this.setupCalculations();
  }
  
  setupValidation() {
    // Lot format validation
    const loteInput = document.getElementById('lote');
    loteInput.addEventListener('blur', (e) => {
      const value = e.target.value;
      if (value && !/^[A-Z]-\d{4}$/.test(value)) {
        this.showError(e.target, 'Formato debe ser X-XXXX (ej: A-1234)');
      } else {
        this.clearError(e.target);
      }
    });
    
    // Date validation
    const fechFab = document.getElementById('fech_fab');
    const fechVenc = document.getElementById('fech_venc');
    
    const validateDates = () => {
      if (fechFab.value && fechVenc.value) {
        if (new Date(fechVenc.value) <= new Date(fechFab.value)) {
          this.showError(fechVenc, 'Vencimiento debe ser posterior a fabricación');
        } else {
          this.clearError(fechVenc);
        }
      }
    };
    
    fechFab.addEventListener('change', validateDates);
    fechVenc.addEventListener('change', validateDates);
    
    // Form submission
    this.form.addEventListener('submit', (e) => {
      if (!this.form.checkValidity()) {
        e.preventDefault();
        this.showFormErrors();
      }
    });
  }
  
  setupCalculations() {
    const cantRecib = document.getElementById('cantidad_recib');
    const cantEntreg = document.getElementById('cantidad_entreg');
    const saldoDisplay = document.getElementById('saldo-display');
    
    const calcSaldo = () => {
      const recib = parseFloat(cantRecib.value) || 0;
      const entreg = parseFloat(cantEntreg.value) || 0;
      saldoDisplay.value = (recib - entreg).toFixed(2);
    };
    
    cantRecib.addEventListener('input', calcSaldo);
    cantEntreg.addEventListener('input', calcSaldo);
  }
  
  showError(input, message) {
    input.classList.add('is-invalid');
    const feedback = input.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.textContent = message;
    }
  }
  
  clearError(input) {
    input.classList.remove('is-invalid');
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new EntradaForm();
});
```

### File Locations

```
app/templates/
├── entradas/
│   ├── list.html               # Entry list with filters
│   ├── form.html                 # Create/edit form
│   ├── detail.html               # Entry detail view
│   ├── _form_identificacion.html # Sub-components
│   ├── _form_cliente.html
│   ├── _form_producto.html
│   ├── _form_cantidades.html
│   ├── _form_fechas.html
│   └── _form_estado.html
├── components/
│   ├── status-badge.html         # Status display
│   ├── date-picker.html          # Date picker
│   ├── entity-selector.html      # Generic selector
│   └── pagination.html

static/
├── js/
│   ├── entrada-form.js           # Form validation & logic
│   ├── entrada-list.js           # List interactions
│   └── components/
│       ├── date-picker.js
│       └── entity-selector.js
├── css/
│   └── entradas.css              # Entry-specific styles
```

---

## Dependencies

**Blocked by:**
- Issue #[Phase 1] Base Templates and CRUD Layouts
- Issue #[Phase 1] Authentication System (user context)
- Issue #[Phase 3] Sample Entry System (Entrada model, API)
- Issue #[Phase 3] Order Management (Pedido API for linking)

**Blocks:**
- None (end of frontend chain)

---

## Related Documentation

- `docs/PRD.md` Section 3.2: UI Requirements
- `docs/PRD.md` Section 3.3.2: Sample Entry Workflow

---

## Testing Requirements

- [ ] Test form validation (all fields)
- [ ] Test factory → client auto-population
- [ ] Test product autocomplete
- [ ] Test balance auto-calculation
- [ ] Test date validation
- [ ] Test lot format validation
- [ ] Test list filtering
- [ ] Test responsive layouts
- [ ] Cross-browser testing

---

## Definition of Done

- [ ] Entry form complete with all fields
- [ ] Smart selectors working
- [ ] Validation in place
- [ ] Date pickers functional
- [ ] List view with filters
- [ ] Detail view complete
- [ ] Responsive design verified
- [ ] Tests passing
- [ ] Code review completed
