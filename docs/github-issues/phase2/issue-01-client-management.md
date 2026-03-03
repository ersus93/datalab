# [Phase 2] Client Management Module

**Labels:** `phase-2`, `crud`, `frontend`, `backend`, `clients`, `high-priority`
**Milestone:** Phase 2: Core Entities & CRUD (Weeks 3-4)
**Estimated Effort:** 3 days
**Depends on:** Issue #1, #2 ([Phase 1] Reference & Master Data Models)

---

## Description

Implement a complete Client Management module with full CRUD operations for the 166 client records migrated from Access. This module provides the primary interface for managing client organizations, their contact information, and associated factory locations.

### Current State
- Client models exist in database
- No UI for client management
- No search or filtering capabilities

### Target State
- Full CRUD interface for clients
- Paginated list with search and filter
- Client detail view with factory associations
- Soft delete functionality
- Audit trail for all changes

### Data Volume
| Metric | Value |
|--------|-------|
| Total Clients | 166 records |
| Avg Factories/Client | 2.4 |
| Organizations | 12 types |

---

## Acceptance Criteria

### Client List View

- [ ] Create `/clientes` route with paginated list view
- [ ] Display 25 clients per page with pagination controls
- [ ] Show columns: ID, Nombre, Organismo, Tipo, Fábricas, Estado
- [ ] Implement search by client name (fuzzy search)
- [ ] Add filter by: Organismo, Tipo Cliente, Activo/Inactivo
- [ ] Sort by: Nombre (default), ID, Organismo
- [ ] Quick actions: Ver, Editar, Desactivar buttons

### Client Detail View

- [ ] Create `/clientes/<id>` detail route
- [ ] Display complete client information:
  - Nombre completo
  - Organismo (linked)
  - Tipo de cliente
  - Estado (activo/inactivo)
  - Fecha de creación
- [ ] Show associated factories list with links
- [ ] Display statistics: total factories, total orders, total samples
- [ ] Recent activity feed (last 10 entries/orders)
- [ ] Action buttons: Editar, Nueva Fábrica, Historial

### Client Creation

- [ ] Create `/clientes/nuevo` route with form
- [ ] Form fields:
  - Nombre (required, unique, max 300 chars)
  - Organismo (dropdown from organismos table)
  - Tipo de Cliente (dropdown: 1-5 classification)
  - Activo (checkbox, default true)
- [ ] Client-side validation with JavaScript
- [ ] Server-side validation with WTForms
- [ ] Duplicate name check before save
- [ ] Success message and redirect to detail view

### Client Editing

- [ ] Create `/clientes/<id>/editar` route with form
- [ ] Pre-populate form with existing data
- [ ] Same validation as creation
- [ ] Handle concurrent edit conflicts (optimistic locking)
- [ ] Audit log entry for changes
- [ ] Success message and redirect

### Soft Delete

- [ ] Implement soft delete (set `activo = false`)
- [ ] Confirmation modal before deletion
- [ ] Check for associated factories before deactivating
- [ ] Prevent delete if active orders exist
- [ ] Show deactivated clients in separate filter view
- [ ] Option to reactivate deleted clients

### Audit Trail

- [ ] Log all CRUD operations to audit_log table:
  - Timestamp
  - User who made change
  - Action (CREATE, UPDATE, DELETE)
  - Table name and record ID
  - Before/after values (JSON)
- [ ] View audit history on client detail page
- [ ] Export audit log to CSV

---

## Technical Notes

### URL Routes

```python
# app/routes/clientes.py

@clientes_bp.route('/clientes')
def listar_clientes():
    """List clients with pagination, search, filter"""
    pass

@clientes_bp.route('/clientes/<int:id>')
def ver_cliente(id):
    """Client detail view"""
    pass

@clientes_bp.route('/clientes/nuevo', methods=['GET', 'POST'])
def crear_cliente():
    """Create new client"""
    pass

@clientes_bp.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_cliente(id):
    """Edit existing client"""
    pass

@clientes_bp.route('/clientes/<int:id>/desactivar', methods=['POST'])
def desactivar_cliente(id):
    """Soft delete client"""
    pass
```

### Client Form (WTForms)

```python
# app/forms/cliente.py

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.database.models import Cliente

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=300, message='Máximo 300 caracteres')
    ])
    organismo_id = SelectField('Organismo', coerce=int, validators=[DataRequired()])
    tipo_cliente = SelectField('Tipo de Cliente', coerce=int, choices=[
        (1, 'Tipo 1 - Industrial'),
        (2, 'Tipo 2 - Comercial'),
        (3, 'Tipo 3 - Servicios'),
        (4, 'Tipo 4 - Gobierno'),
        (5, 'Tipo 5 - Otros')
    ])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')
    
    def validate_nombre(self, field):
        """Check for duplicate client names"""
        cliente = Cliente.query.filter_by(nombre=field.data).first()
        if cliente and (not self.id or cliente.id != self.id.data):
            raise ValidationError('Ya existe un cliente con este nombre')
```

### List View Template Structure

```html
<!-- templates/clientes/listar.html -->
{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>Clientes</h1>
    <a href="{{ url_for('clientes.crear_cliente') }}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Nuevo Cliente
    </a>
</div>

<!-- Filters -->
<div class="card filters-card">
    <form method="GET" action="{{ url_for('clientes.listar_clientes') }}">
        <div class="row">
            <div class="col-md-4">
                <input type="text" name="q" value="{{ request.args.get('q', '') }}" 
                       placeholder="Buscar por nombre..." class="form-control">
            </div>
            <div class="col-md-3">
                <select name="organismo" class="form-control">
                    <option value="">Todos los organismos</option>
                    {% for org in organismos %}
                    <option value="{{ org.id }}" {% if request.args.get('organismo')|int == org.id %}selected{% endif %}>
                        {{ org.nombre }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <select name="estado" class="form-control">
                    <option value="">Todos los estados</option>
                    <option value="activo" {% if request.args.get('estado') == 'activo' %}selected{% endif %}>Activo</option>
                    <option value="inactivo" {% if request.args.get('estado') == 'inactivo' %}selected{% endif %}>Inactivo</option>
                </select>
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-secondary">Filtrar</button>
            </div>
        </div>
    </form>
</div>

<!-- Clients Table -->
<div class="card">
    <table class="table table-striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Organismo</th>
                <th>Tipo</th>
                <th>Fábricas</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for cliente in clientes.items %}
            <tr>
                <td>{{ cliente.id }}</td>
                <td>
                    <a href="{{ url_for('clientes.ver_cliente', id=cliente.id) }}">
                        {{ cliente.nombre }}
                    </a>
                </td>
                <td>{{ cliente.organismo.nombre if cliente.organismo else '-' }}</td>
                <td>{{ cliente.tipo_cliente }}</td>
                <td>
                    <span class="badge badge-info">{{ cliente.fabricas|length }}</span>
                </td>
                <td>
                    {% if cliente.activo %}
                    <span class="badge badge-success">Activo</span>
                    {% else %}
                    <span class="badge badge-secondary">Inactivo</span>
                    {% endif %}
                </td>
                <td>
                    <a href="{{ url_for('clientes.ver_cliente', id=cliente.id) }}" class="btn btn-sm btn-info">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="{{ url_for('clientes.editar_cliente', id=cliente.id) }}" class="btn btn-sm btn-warning">
                        <i class="fas fa-edit"></i>
                    </a>
                    {% if cliente.activo %}
                    <button class="btn btn-sm btn-danger" data-toggle="modal" data-target="#deleteModal{{ cliente.id }}">
                        <i class="fas fa-trash"></i>
                    </button>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- Pagination -->
    {{ render_pagination(clientes, 'clientes.listar_clientes') }}
</div>
{% endblock %}
```

### Audit Log Model Extension

```python
# app/database/models/audit.py

from datetime import datetime
from app.database import db

class AuditLog(db.Model):
    """Audit trail for all data changes"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')
    
    @classmethod
    def log_change(cls, user_id, action, table_name, record_id, 
                   old_values=None, new_values=None):
        """Create audit log entry"""
        log = cls(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:500] if request.user_agent else None
        )
        db.session.add(log)
        return log
```

---

## Dependencies

**Blocked by:**
- Issue #1: [Phase 1] Reference Data Models (Organismos FK)
- Issue #2: [Phase 1] Master Data Models (Cliente, Fabrica models)
- Issue #5: [Phase 1] Authentication System (login required)

**Blocks:**
- Issue #2 (Phase 2): Factory Management (needs client selection)
- Issue #5 (Phase 2): Master Data Import (needs client CRUD ready)

---

## Related Documentation

- `docs/PRD.md` Section 2.3.2: Master Data - Core Entities
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Lines 146-161: Clientes schema
- `plans/MIGRATION_PLAN.md` Phase 2.1: Client Management Module

---

## Testing Requirements

- [ ] Test create client with valid data succeeds
- [ ] Test create client with duplicate name fails
- [ ] Test pagination shows correct number of items
- [ ] Test search filters results correctly
- [ ] Test soft delete preserves data
- [ ] Test audit log captures all changes
- [ ] Test client with factories cannot be hard deleted
- [ ] Test responsive design on mobile devices

---

## Definition of Done

- [ ] All CRUD operations functional
- [ ] Search and filter working
- [ ] Pagination implemented
- [ ] Soft delete with reactivation option
- [ ] Audit trail logging all changes
- [ ] All templates responsive
- [ ] Code review completed
- [ ] Unit tests passing
