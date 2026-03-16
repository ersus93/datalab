# [Phase 1] Create Base Templates for CRUD

**Labels:** `phase-1`, `frontend`, `templates`, `bootstrap`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days
**Depends on:** Issue #5 ([Phase 1] Implement Authentication System)

---

## Description

Create a comprehensive set of reusable base templates for CRUD (Create, Read, Update, Delete) operations. These templates will provide consistent UI patterns across all data management pages and significantly speed up development of Phase 2 features.

The templates must integrate with the authentication system from Issue #5 and follow Bootstrap 5 styling patterns already in use in the project.

### Template Inventory

| Template | Purpose | Reuse Across |
|----------|---------|--------------|
| `base_list.html` | Paginated list/table view | All reference tables, clients, factories |
| `base_form.html` | Create/edit form view | All entity forms |
| `base_detail.html` | Detail/read-only view | Entity detail pages |
| `macros/pagination.html` | Pagination component | All list views |
| `macros/filters.html` | Search/filter components | All list views |
| `macros/actions.html` | Action buttons (edit, delete) | All list/detail views |

---

## Acceptance Criteria

### Base List Template (`templates/crud/base_list.html`)

- [ ] Create reusable list template with blocks:
  - `title` - Page title section
  - `header_actions` - Buttons for create, export, etc.
  - `filters` - Search and filter inputs
  - `table_headers` - Customizable column headers
  - `table_body` - Data rows with loop
  - `pagination` - Page navigation
  - `empty_state` - Message when no data
- [ ] Features included:
  - [ ] Responsive table with horizontal scroll on mobile
  - [ ] Sortable column headers (click to sort)
  - [ ] Row hover effects
  - [ ] Action buttons column (edit, view, delete with confirmation)
  - [ ] Row selection checkboxes (optional)
  - [ ] Record count display
  - [ ] Items-per-page selector (10, 25, 50, 100)
- [ ] Styling:
  - [ ] Use Bootstrap 5 table classes (`table`, `table-striped`, `table-hover`)
  - [ ] Consistent header styling
  - [ ] Zebra striping for readability
  - [ ] Compact density option

### Base Form Template (`templates/crud/base_form.html`)

- [ ] Create reusable form template with blocks:
  - `title` - Form title (Create vs Edit)
  - `form_header` - Instructions or info
  - `form_fields` - Main form fields
  - `form_actions` - Submit, cancel, reset buttons
  - `form_footer` - Additional info
- [ ] Features included:
  - [ ] CSRF token automatically included
  - [ ] Field error display
  - [ ] Form-level error display
  - [ ] Required field indicators
  - [ ] Help text display
  - [ ] Two-column layout option for wide screens
  - [ ] Section/fieldset grouping support
- [ ] Styling:
  - [ ] Consistent form control styling
  - [ ] Error state styling (red borders, messages)
  - [ ] Success state styling
  - [ ] Disabled state styling

### Base Detail Template (`templates/crud/base_detail.html`)

- [ ] Create reusable detail template with blocks:
  - `title` - Entity name/title
  - `header_actions` - Edit, delete, back buttons
  - `detail_sections` - Grouped field displays
  - `related_data` - Linked entities (tabs or cards)
  - `audit_info` - Created/updated timestamps
- [ ] Features included:
  - [ ] Field label and value pairing
  - [ ] Empty value handling (show "—" or "N/A")
  - [ ] Boolean display (badges: Sí/No, Active/Inactive)
  - [ ] Date formatting
  - [ ] Related data tables/cards
  - [ ] Print-friendly styling
- [ ] Styling:
  - [ ] Card-based layout
  - [ ] Definition list styling for fields
  - [ ] Section separators

### Pagination Macro (`templates/macros/pagination.html`)

- [ ] Create reusable pagination component:
  - [ ] Previous/Next buttons
  - [ ] Page number buttons (with ellipsis for many pages)
  - [ ] First/Last page buttons
  - [ ] Current page highlight
  - [ ] Disabled state for boundaries
  - [ ] URL parameter preservation (filters, sort)
- [ ] Styling:
  - [ ] Bootstrap 5 pagination classes
  - [ ] Centered or right-aligned option
  - [ ] Size variants (sm, lg)

### Filter Macro (`templates/macros/filters.html`)

- [ ] Create reusable filter components:
  - [ ] Search input (text search across fields)
  - [ ] Dropdown filters (for foreign keys, enums)
  - [ ] Date range picker
  - [ ] Boolean toggle filters
  - [ ] Active filters display (with clear option)
  - [ ] Apply/Reset buttons
- [ ] Styling:
  - [ ] Compact inline layout
  - [ ] Collapsible on mobile
  - [ ] Clear filter indicators

### Action Buttons Macro (`templates/macros/actions.html`)

- [ ] Create reusable action button components:
  - [ ] View button (eye icon)
  - [ ] Edit button (pencil icon)
  - [ ] Delete button (trash icon with confirmation)
  - [ ] Create button (plus icon)
  - [ ] Export button (download icon)
  - [ ] Bulk action dropdown
- [ ] Features:
  - [ ] Icon + text or icon-only variants
  - [ ] Size variants (sm, md, lg)
  - [ ] Delete confirmation modal integration
  - [ ] Permission-based visibility (show/hide based on user role)

### Flash Messages Component

- [ ] Create reusable flash message display:
  - [ ] Support for categories: success, error, warning, info
  - [ ] Dismissible alerts
  - [ ] Auto-dismiss option for success messages
  - [ ] Icon per category
  - [ ] Position: top of page or inline

### Breadcrumb Component

- [ ] Create reusable breadcrumb navigation:
  - [ ] Home link always present
  - [ ] Dynamic section links
  - [ ] Current page (non-linked)
  - [ ] JSON-LD structured data for SEO (optional)

---

## Technical Notes

### Template Structure

```
templates/
├── base.html                    # Existing base template
├── auth/
│   └── login.html               # From Issue #5
├── crud/                        # <-- NEW directory
│   ├── base_list.html           # Reusable list template
│   ├── base_form.html           # Reusable form template
│   └── base_detail.html         # Reusable detail template
├── macros/                      # <-- NEW directory
│   ├── pagination.html          # Pagination component
│   ├── filters.html             # Filter components
│   ├── actions.html             # Action buttons
│   ├── forms.html               # Form field macros
│   └── utils.html               # Utility macros
└── components/                  # Shared components
    ├── flash_messages.html
    ├── breadcrumb.html
    ├── sidebar.html             # (update existing)
    └── navbar.html              # (update existing)
```

### Base List Template

```html
<!-- templates/crud/base_list.html -->
{% extends 'base.html' %}
{% import 'macros/pagination.html' as pg %}
{% import 'macros/filters.html' as flt %}
{% import 'macros/actions.html' as act %}

{% block content %}
<div class="container-fluid">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3">{% block title %}List{% endblock %}</h1>
            {% if subtitle %}<p class="text-muted">{{ subtitle }}</p>{% endif %}
        </div>
        <div class="header-actions">
            {% block header_actions %}
                {{ act.create_button(url_for('.' + create_route), 'Nuevo') }}
            {% endblock %}
        </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
        <div class="card-body">
            {% block filters %}
                <form method="GET" class="row g-3">
                    {{ flt.search_input(search_term, placeholder='Buscar...') }}
                    {% block additional_filters %}{% endblock %}
                    <div class="col-auto">
                        <button type="submit" class="btn btn-primary">Filtrar</button>
                        <a href="{{ url_for(request.endpoint) }}" class="btn btn-outline-secondary">Limpiar</a>
                    </div>
                </form>
            {% endblock %}
        </div>
    </div>

    <!-- Data Table -->
    <div class="card">
        <div class="card-body">
            {% if items %}
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                {% block table_headers %}
                                    <!-- Override with column headers -->
                                {% endblock %}
                                <th class="text-end">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in items %}
                                <tr>
                                    {% block table_row %}
                                        <!-- Override with row cells -->
                                    {% endblock %}
                                    <td class="text-end">
                                        {{ act.view_button(url_for('.' + view_route, id=item.id)) }}
                                        {{ act.edit_button(url_for('.' + edit_route, id=item.id)) }}
                                        {{ act.delete_button(url_for('.' + delete_route, id=item.id), item.name) }}
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <!-- Pagination & Info -->
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <div class="text-muted">
                        Mostrando {{ items.first }} - {{ items.last }} de {{ items.total }} registros
                    </div>
                    {{ pg.render_pagination(items, endpoint=request.endpoint) }}
                </div>
            {% else %}
                {% block empty_state %}
                    <div class="text-center py-5">
                        <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">No hay registros</h5>
                        <p class="text-muted">Comienza creando un nuevo registro.</p>
                        {{ act.create_button(url_for('.' + create_route), 'Crear Primero') }}
                    </div>
                {% endblock %}
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

### Pagination Macro

```html
<!-- templates/macros/pagination.html -->

{% macro render_pagination(pagination, endpoint) %}
{% if pagination.pages > 1 %}
<nav aria-label="Page navigation">
    <ul class="pagination mb-0">
        <!-- Previous -->
        <li class="page-item {% if not pagination.has_prev %}disabled{% endif %}">
            <a class="page-link" href="{% if pagination.has_prev %}{{ url_for(endpoint, page=pagination.prev_num, **request.args) }}{% else %}#{% endif %}">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>

        <!-- Page Numbers -->
        {% for page_num in pagination.iter_pages(left_edge=2, left_current=2, right_current=3, right_edge=2) %}
            {% if page_num %}
                <li class="page-item {% if page_num == pagination.page %}active{% endif %}">
                    <a class="page-link" href="{{ url_for(endpoint, page=page_num, **request.args) }}">{{ page_num }}</a>
                </li>
            {% else %}
                <li class="page-item disabled"><span class="page-link">...</span></li>
            {% endif %}
        {% endfor %}

        <!-- Next -->
        <li class="page-item {% if not pagination.has_next %}disabled{% endif %}">
            <a class="page-link" href="{% if pagination.has_next %}{{ url_for(endpoint, page=pagination.next_num, **request.args) }}{% else %}#{% endif %}">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    </ul>
</nav>
{% endif %}
{% endmacro %}
```

### Form Field Macro

```html
<!-- templates/macros/forms.html -->

{% macro render_field(field, placeholder='', extra_class='') %}
<div class="mb-3">
    {{ field.label(class="form-label") }}
    {% if field.flags.required %}<span class="text-danger">*</span>{% endif %}
    
    {% set class_name = "form-control " + extra_class %}
    {% if field.errors %}{% set class_name = class_name + " is-invalid" %}{% endif %}
    
    {{ field(class=class_name, placeholder=placeholder) }}
    
    {% if field.description %}
        <div class="form-text">{{ field.description }}</div>
    {% endif %}
    
    {% if field.errors %}
        <div class="invalid-feedback">
            {% for error in field.errors %}
                {{ error }}
            {% endfor %}
        </div>
    {% endif %}
</div>
{% endmacro %}

{% macro render_checkbox(field) %}
<div class="mb-3 form-check">
    {{ field(class="form-check-input") }}
    {{ field.label(class="form-check-label") }}
</div>
{% endmacro %}
```

### Action Buttons Macro

```html
<!-- templates/macros/actions.html -->

{% macro view_button(url, text='Ver', size='sm') %}
<a href="{{ url }}" class="btn btn-outline-primary btn-{{ size }}" title="{{ text }}">
    <i class="fas fa-eye"></i> {% if size != 'sm' %}{{ text }}{% endif %}
</a>
{% endmacro %}

{% macro edit_button(url, text='Editar', size='sm') %}
<a href="{{ url }}" class="btn btn-outline-warning btn-{{ size }}" title="{{ text }}">
    <i class="fas fa-edit"></i> {% if size != 'sm' %}{{ text }}{% endif %}
</a>
{% endmacro %}

{% macro delete_button(url, item_name, text='Eliminar', size='sm') %}
<form action="{{ url }}" method="POST" class="d-inline" 
      onsubmit="return confirm('¿Está seguro de eliminar {{ item_name }}?');">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button type="submit" class="btn btn-outline-danger btn-{{ size }}" title="{{ text }}">
        <i class="fas fa-trash"></i> {% if size != 'sm' %}{{ text }}{% endif %}
    </button>
</form>
{% endmacro %}

{% macro create_button(url, text='Nuevo') %}
<a href="{{ url }}" class="btn btn-primary">
    <i class="fas fa-plus"></i> {{ text }}
</a>
{% endmacro %}
```

### Usage Example

```html
<!-- templates/areas/list.html - Using base_list.html -->
{% extends 'crud/base_list.html' %}

{% block title %}Áreas de Laboratorio{% endblock %}
{% block subtitle %}Gestión de áreas FQ, MB, ES y OS{% endblock %}

{% block table_headers %}
    <th>ID</th>
    <th>Nombre</th>
    <th>Sigla</th>
{% endblock %}

{% block table_row %}
    <td>{{ item.id }}</td>
    <td>{{ item.nombre }}</td>
    <td><span class="badge bg-secondary">{{ item.sigla }}</span></td>
{% endblock %}
```

---

## Dependencies

**Blocked by:**
- Issue #5: [Phase 1] Implement Authentication System (templates extend base)

**Blocks:**
- Issue #7: [Phase 1] CRUD API for Reference Data (uses these templates)
- All Phase 2 CRUD features (clients, factories, products, etc.)

---

## Related Documentation

- `docs/PRD.md` Section 3.2.5: Mobile Responsive Design
- `docs/PROJECT_ANALYSIS.md`: Current template structure
- Bootstrap 5 documentation: https://getbootstrap.com/docs/5.3/

---

## Integration with Authentication

- [ ] Only show "Create" button if user has write permission
- [ ] Only show "Edit" button if user has edit permission
- [ ] Only show "Delete" button if user has delete permission
- [ ] Pass `current_user` to templates for permission checks
- [ ] Add `can_view`, `can_edit`, `can_delete` variables to template context

Example:
```html
{% if current_user.is_admin() or current_user.is_laboratory_manager() %}
    {{ act.create_button(...) }}
{% endif %}
```

---

## Testing Requirements

- [ ] Test pagination displays correctly with few/many pages
- [ ] Test filters preserve state across page navigation
- [ ] Test table is responsive on mobile devices
- [ ] Test delete confirmation prevents accidental deletion
- [ ] Test form validation displays errors correctly
- [ ] Test flash messages appear and can be dismissed
- [ ] Test empty state displays when no data

---

## Definition of Done

- [ ] All base templates created
- [ ] All macros created and documented
- [ ] Example usage templates created (at least 2)
- [ ] Responsive design verified
- [ ] Flash messages component working
- [ ] Breadcrumb component working
- [ ] Templates integrate with authentication
- [ ] Code review completed
- [ ] Ready for use in Issue #7 and beyond
