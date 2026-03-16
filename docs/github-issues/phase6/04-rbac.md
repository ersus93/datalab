---
title: "[Phase 6] Role-Based Access Control (RBAC)"
labels: ["phase-6", "advanced", "rbac", "security", "epic"]
---

## Overview
Implement a comprehensive Role-Based Access Control (RBAC) system with granular permissions, role matrix, decorators for route protection, and dynamic UI based on user permissions.

## Permission System Design

### Permission Granularity
Permissions follow the pattern: `{action}_{resource}`

**Actions:**
- `view` - Read access
- `create` - Create new records
- `edit` - Modify existing records
- `delete` - Remove records
- `export` - Export data
- `approve` - Approve/review actions
- `admin` - Administrative actions

**Resources:**
- `clientes` - Client management
- `fabricas` - Factory management
- `productos` - Product management
- `entradas` - Sample entries
- `pedidos` - Orders
- `ensayos` - Laboratory tests
- `informes` - Reports
- `facturacion` - Billing/invoicing
- `usuarios` - User management
- `configuracion` - System settings

### Permission Examples
```python
PERMISSIONS = [
    # Clientes
    'view_clientes',
    'create_clientes',
    'edit_clientes',
    'delete_clientes',
    
    # Entradas
    'view_entradas',
    'create_entradas',
    'edit_entradas',
    'delete_entradas',
    'export_entradas',
    
    # Ensayos
    'view_ensayos',
    'create_ensayos',
    'edit_ensayos',
    'delete_ensayos',
    'approve_ensayos',
    
    # ... etc
]
```

## Role Matrix

### Role Definitions

#### 1. Admin (Administrator)
**Description:** Full system access
**Permissions:**
- All CRUD operations on all resources
- User management
- System configuration
- Access to audit logs
- Bulk operations

```python
ADMIN_PERMISSIONS = ['*']  # All permissions
```

#### 2. Technician (Técnico de Laboratorio)
**Description:** Laboratory personnel
**Permissions:**
- **Full CRUD:** Ensayos (tests), Entradas (samples)
- **View only:** Clientes, Productos, Fábricas, Informes
- **Limited:** Pedidos (view assigned, update status)
- **Billing:** View-only access

```python
TECHNICIAN_PERMISSIONS = [
    # Full on ensayos and entradas
    'view_ensayos', 'create_ensayos', 'edit_ensayos', 'delete_ensayos',
    'view_entradas', 'create_entradas', 'edit_entradas', 'delete_entradas',
    
    # View only
    'view_clientes',
    'view_productos',
    'view_fabricas',
    'view_informes',
    
    # Limited pedidos
    'view_pedidos',
    'edit_pedidos_own',  # Only own/assigned
]
```

#### 3. Client (Cliente)
**Description:** External clients
**Permissions:**
- **View own data only:**
  - Own client profile
  - Own entradas
  - Own pedidos
  - Own informes (completed)
- **No access:** Other clients, billing details, ensayos in progress

```python
CLIENT_PERMISSIONS = [
    'view_clientes_own',
    'view_entradas_own',
    'view_pedidos_own',
    'view_informes_own_completed',
]
```

#### 4. Viewer (Visualizador)
**Description:** Read-only access for auditors/managers
**Permissions:**
- **View only:** All resources except sensitive data
- **Export:** Reports and data
- **No access:** User management, configuration, edit operations

```python
VIEWER_PERMISSIONS = [
    # Read all
    'view_clientes',
    'view_productos',
    'view_fabricas',
    'view_entradas',
    'view_pedidos',
    'view_ensayos',
    'view_informes',
    
    # Export
    'export_entradas',
    'export_informes',
    'export_pedidos',
]
```

### Role Matrix Table

| Resource | Action | Admin | Technician | Client | Viewer |
|----------|--------|-------|------------|--------|--------|
| Clientes | View | ✓ | ✓ | Own only | ✓ |
| | Create | ✓ | ✗ | ✗ | ✗ |
| | Edit | ✓ | ✗ | ✗ | ✗ |
| | Delete | ✓ | ✗ | ✗ | ✗ |
| Entradas | View | ✓ | ✓ | Own only | ✓ |
| | Create | ✓ | ✓ | ✗ | ✗ |
| | Edit | ✓ | ✓ | ✗ | ✗ |
| | Delete | ✓ | ✗ | ✗ | ✗ |
| Ensayos | View | ✓ | ✓ | ✗ | ✓ |
| | Create | ✓ | ✓ | ✗ | ✗ |
| | Edit | ✓ | ✓ | ✗ | ✗ |
| | Approve | ✓ | ✗ | ✗ | ✗ |
| Informes | View | ✓ | ✓ | Own/Completed | ✓ |
| | Create | ✓ | ✗ | ✗ | ✗ |
| | Finalize | ✓ | ✗ | ✗ | ✗ |
| Facturación | View | ✓ | ✓ | Own only | ✗ |
| | Create | ✓ | ✗ | ✗ | ✗ |
| Usuarios | Manage | ✓ | ✗ | ✗ | ✗ |

## Database Schema

```python
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON, default=list)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    # ... existing fields ...
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref='users')
    
    # For client-specific access
    client_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    
    # Custom permissions (override role permissions)
    custom_permissions = db.Column(db.JSON, default=list)
    restricted_permissions = db.Column(db.JSON, default=list)

# Association table for many-to-many (if needed)
user_permissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('permission', db.String(100))
)
```

## Permission Decorators

### Route Protection
```python
from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(*permissions):
    """Decorator to check if user has required permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if not current_user.has_any_permission(*permissions):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Shortcut for admin-only routes."""
    return permission_required('admin')(f)

def own_resource_only(model_class, user_field='user_id'):
    """Ensure user can only access their own resources."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get('id')
            resource = model_class.query.get_or_404(resource_id)
            
            if not current_user.can_access(resource):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### Usage Examples
```python
@app.route('/clientes')
@permission_required('view_clientes')
def list_clientes():
    pass

@app.route('/clientes', methods=['POST'])
@permission_required('create_clientes')
def create_cliente():
    pass

@app.route('/entradas/<int:id>')
@permission_required('view_entradas')
@own_resource_only(Entrada, user_field='client_id')  # For clients
def view_entrada(id):
    pass

@app.route('/admin/users')
@admin_required
def admin_users():
    pass
```

## UI Permission Integration

### Jinja2 Context Processor
```python
@app.context_processor
def inject_permissions():
    def can(permission):
        return current_user.is_authenticated and current_user.has_permission(permission)
    
    def is_admin():
        return current_user.is_authenticated and current_user.is_admin
    
    return dict(can=can, is_admin=is_admin)
```

### Template Usage
```html
<!-- Show/hide based on permission -->
{% if can('create_clientes') %}
  <a href="{{ url_for('clientes.new') }}" class="btn btn-primary">
    Nuevo Cliente
  </a>
{% endif %}

<!-- Conditional menu items -->
{% if can('view_facturacion') %}
  <li><a href="{{ url_for('billing.index') }}">Facturación</a></li>
{% endif %}

<!-- Conditional table actions -->
<td>
  <a href="{{ url_for('entradas.view', id=entrada.id) }}">Ver</a>
  {% if can('edit_entradas') %}
    <a href="{{ url_for('entradas.edit', id=entrada.id) }}">Editar</a>
  {% endif %}
  {% if can('delete_entradas') %}
    <a href="{{ url_for('entradas.delete', id=entrada.id) }}" 
       class="text-danger">Eliminar</a>
  {% endif %}
</td>
```

### JavaScript Permission Object
```javascript
// Inject permissions into page
<script>
window.userPermissions = {{ current_user.permissions|tojson }};
window.userRole = {{ current_user.role.name|tojson }};

function can(permission) {
    return window.userPermissions.includes(permission) || 
           window.userPermissions.includes('*');
}

// Usage in JS
if (can('export_entradas')) {
    showExportButton();
}
</script>
```

## API Endpoint Protection

### Flask-RESTful Integration
```python
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

class EntradasAPI(Resource):
    method_decorators = [jwt_required()]
    
    def get(self):
        current_user = User.query.get(get_jwt_identity())
        if not current_user.has_permission('view_entradas'):
            return {'error': 'Permission denied'}, 403
        
        # ... handle request
    
    def post(self):
        current_user = User.query.get(get_jwt_identity())
        if not current_user.has_permission('create_entradas'):
            return {'error': 'Permission denied'}, 403
        
        # ... handle request
```

### Permission Middleware
```python
class PermissionMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Check permissions before request
        return self.app(environ, start_response)
```

## Permission Caching

```python
from functools import lru_cache

class User(db.Model):
    # ... existing code ...
    
    @property
    @lru_cache(maxsize=128)
    def permissions(self):
        """Cache permissions to avoid repeated DB queries."""
        perms = set(self.role.permissions if self.role else [])
        perms.update(self.custom_permissions or [])
        perms.difference_update(self.restricted_permissions or [])
        return list(perms)
    
    def has_permission(self, permission):
        if '*' in self.permissions:
            return True
        return permission in self.permissions
    
    def has_any_permission(self, *permissions):
        return any(self.has_permission(p) for p in permissions)
```

## Audit Logging

```python
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50))  # view, create, edit, delete
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def log_access(action, resource_type, resource_id, details=None):
    if current_user.is_authenticated:
        log = AuditLog(
            user_id=current_user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
```

## Role Management UI

### Admin Interface
```
┌─────────────────────────────────────────────────────────────┐
│ Role Management                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Roles:  [Admin] [Technician] [Client] [Viewer] [+ New]      │
│                                                              │
│ Selected: Technician                                        │
│ Description: Laboratory personnel with test/sample access   │
│                                                              │
│ Permissions:                                                 │
│ ☑ view_entradas    ☑ create_entradas    ☑ edit_entradas   │
│ ☑ view_ensayos     ☑ create_ensayos     ☑ edit_ensayos    │
│ ☑ view_clientes    ☐ create_clientes    ☐ edit_clientes   │
│ ...                                                          │
│                                                              │
│ [Save Changes]  [Duplicate]  [Delete]                       │
└─────────────────────────────────────────────────────────────┘
```

## Migration Script

```python
# migrations/add_roles.py
from app import db
from app.models import Role

def upgrade():
    roles = [
        Role(name='admin', description='Full system access', 
             permissions=['*']),
        Role(name='technician', description='Laboratory technician',
             permissions=[
                 'view_entradas', 'create_entradas', 'edit_entradas', 'delete_entradas',
                 'view_ensayos', 'create_ensayos', 'edit_ensayos', 'delete_ensayos',
                 'view_clientes', 'view_productos', 'view_fabricas', 'view_informes',
                 'view_pedidos', 'edit_pedidos_own'
             ]),
        Role(name='client', description='External client',
             permissions=[
                 'view_clientes_own', 'view_entradas_own',
                 'view_pedidos_own', 'view_informes_own_completed'
             ]),
        Role(name='viewer', description='Read-only viewer',
             permissions=[
                 'view_clientes', 'view_productos', 'view_fabricas',
                 'view_entradas', 'view_pedidos', 'view_ensayos', 'view_informes',
                 'export_entradas', 'export_informes', 'export_pedidos'
             ])
    ]
    
    for role in roles:
        db.session.add(role)
    
    db.session.commit()
```

## Acceptance Criteria

- [ ] Role model with permission storage
- [ ] 4 default roles created (Admin, Technician, Client, Viewer)
- [ ] Permission decorators for route protection
- [ ] UI elements show/hide based on permissions
- [ ] API endpoints protected
- [ ] Client users can only see own data
- [ ] Admin role has full access
- [ ] Role management UI for administrators
- [ ] Permission caching implemented
- [ ] Audit logging for sensitive actions
- [ ] Migration script for existing users
- [ ] Unit tests for permission checks
- [ ] Integration tests for protected routes

## Related Issues
- #XX - User authentication system
- #XX - Audit logging system
- #XX - API authentication

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 2-3 weeks

## Dependencies
- User authentication system complete
- Database migration system
- Admin UI framework
