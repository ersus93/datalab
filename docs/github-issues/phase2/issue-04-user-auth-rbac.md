# [Phase 2] User Authentication & Role Management

**Labels:** `phase-2`, `authentication`, `security`, `rbac`, `flask-login`, `high-priority`
**Milestone:** Phase 2: Core Entities & CRUD (Weeks 3-4)
**Estimated Effort:** 3 days
**Depends on:** Issue #5 (Phase 1) ([Phase 1] Authentication System)

---

## Description

Extend the Phase 1 authentication foundation with comprehensive User Management and Role-Based Access Control (RBAC). This module provides user administration capabilities, role management, and permission enforcement across the entire application.

### Current State (After Phase 1)
- Basic Flask-Login integration
- User model with password hashing
- Login/logout routes
- Basic role field

### Target State
- Complete RBAC implementation
- User management admin panel
- Role-based access decorators
- Permission matrix for all features
- User activity logging
- Password management

### User Roles & Permissions Matrix

| Feature | Admin | Lab Manager | Technician | Client | Viewer |
|---------|-------|-------------|------------|--------|--------|
| **User Management** | CRUD | View | - | - | - |
| **Clients** | CRUD | CRUD | View | View own | View |
| **Factories** | CRUD | CRUD | View | View own | View |
| **Products** | CRUD | CRUD | View | View | View |
| **Samples (Entries)** | CRUD | CRUD | CRUD own | View own | View |
| **Tests** | CRUD | CRUD | CRUD own | - | View |
| **Reports** | CRUD | CRUD | View | View own | View |
| **Billing** | CRUD | View | - | View own | - |
| **System Config** | CRUD | View | - | - | - |

**Total Users Expected:** 15-25 (Lab staff + Client accounts)

---

## Acceptance Criteria

### User Management Admin Panel

- [ ] Create `/admin/usuarios` admin route
- [ ] List all users with pagination (25 per page)
- [ ] Show columns: Username, Nombre, Email, Rol, Estado, Último Acceso
- [ ] Filter by: Rol, Estado, Último acceso
- [ ] Search by username or email
- [ ] Quick actions: Ver, Editar, Activar/Desactivar, Reset Password

### User Creation

- [ ] Create `/admin/usuarios/nuevo` route
- [ ] Form fields:
  - Username (required, unique, 3-80 chars)
  - Email (required, unique, valid format)
  - Nombre Completo (required)
  - Rol (dropdown: Admin, Lab Manager, Technician, Client, Viewer)
  - Cliente (dropdown, only for Client role)
  - Contraseña (required, min 8 chars, complexity)
  - Confirmar Contraseña (must match)
  - Activo (default true)
- [ ] Password strength indicator
- [ ] Email notification on account creation
- [ ] Success message and redirect

### User Editing

- [ ] Create `/admin/usuarios/<id>/editar` route
- [ ] Allow editing: Nombre, Email, Rol, Cliente, Estado
- [ ] Username is read-only (primary identifier)
- [ ] Separate password change form
- [ ] Cannot deactivate own account (safety)
- [ ] Audit log for role changes
- [ ] Success message and redirect

### Password Management

- [ ] Password change for own account
- [ ] Admin password reset for any user
- [ ] Password requirements enforced:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character
- [ ] Password history (prevent reuse of last 3)
- [ ] Password expiration (optional, 90 days)
- [ ] Secure reset token generation

### Role-Based Access Control (RBAC)

- [ ] Implement `@require_role()` decorator
- [ ] Implement `@admin_required()` decorator
- [ ] Implement `@lab_manager_required()` decorator
- [ ] Create permission check methods on User model:
  - `can_manage_users()`
  - `can_edit_clients()`
  - `can_view_client_data(client_id)`
  - `can_perform_tests()`
  - `can_approve_reports()`
  - `can_view_billing()`
- [ ] Apply decorators to all routes
- [ ] Custom 403 Forbidden page

### Role Management

- [ ] Display role badges with colors:
  - Admin: Red badge
  - Lab Manager: Blue badge
  - Technician: Green badge
  - Client: Orange badge
  - Viewer: Gray badge
- [ ] Role description tooltips
- [ ] Role statistics dashboard
- [ ] Role assignment audit trail

### User Activity Logging

- [ ] Log all user actions:
  - Login/Logout
  - Failed login attempts
  - Password changes
  - CRUD operations on protected resources
- [ ] Activity log viewer for admins
- [ ] Filter by user, date range, action type
- [ ] Export activity log to CSV
- [ ] Auto-cleanup after 1 year

### Client User Association

- [ ] For Client role, must select associated Client
- [ ] Client users can only see their own:
  - Factories
  - Samples (Entries)
  - Orders
  - Reports
- [ ] Validation: Client role requires cliente_id
- [ ] Show client name in user list

### Session Management Enhancements

- [ ] View active sessions (admin only)
  - User, IP address, Login time, Last activity
- [ ] Force logout user (admin only)
- [ ] Session timeout warnings (5 min before)
- [ ] Concurrent session limit (optional)
- [ ] Login from new device notification

---

## Technical Notes

### Enhanced User Model

```python
# app/database/models/user.py

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import secrets

db = SQLAlchemy()

class UserRole(enum.Enum):
    """User roles for RBAC"""
    ADMIN = 'admin'
    LABORATORY_MANAGER = 'laboratory_manager'
    TECHNICIAN = 'technician'
    CLIENT = 'client'
    VIEWER = 'viewer'

class User(UserMixin, db.Model):
    """
    Enhanced User model with RBAC support
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # For client role
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    
    # Tracking
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Password management
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_reset_token = db.Column(db.String(100), nullable=True, index=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='usuarios')
    activity_logs = db.relationship('UserActivityLog', back_populates='user', 
                                     lazy='dynamic', cascade='all, delete-orphan')
    
    # Role checking methods
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_laboratory_manager(self):
        return self.role == UserRole.LABORATORY_MANAGER
    
    def is_technician(self):
        return self.role == UserRole.TECHNICIAN
    
    def is_client(self):
        return self.role == UserRole.CLIENT
    
    def is_viewer(self):
        return self.role == UserRole.VIEWER
    
    # Permission methods
    def can_manage_users(self):
        return self.is_admin()
    
    def can_edit_clients(self):
        return self.is_admin() or self.is_laboratory_manager()
    
    def can_view_client_data(self, client_id):
        if self.is_admin() or self.is_laboratory_manager() or self.is_viewer():
            return True
        if self.is_client() and self.cliente_id == client_id:
            return True
        return False
    
    def can_perform_tests(self):
        return self.is_admin() or self.is_laboratory_manager() or self.is_technician()
    
    def can_approve_reports(self):
        return self.is_admin() or self.is_laboratory_manager()
    
    def can_view_billing(self):
        return self.is_admin() or self.is_laboratory_manager() or self.is_client()
    
    # Password methods
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=16
        )
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def generate_password_reset_token(self):
        """Generate secure reset token"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        return self.password_reset_token
    
    def verify_password_reset_token(self, token):
        """Verify reset token is valid and not expired"""
        if self.password_reset_token != token:
            return False
        if datetime.utcnow() > self.password_reset_expires:
            return False
        return True
    
    def clear_password_reset_token(self):
        """Clear reset token after use"""
        self.password_reset_token = None
        self.password_reset_expires = None
    
    def is_password_expired(self):
        """Check if password has expired (90 days)"""
        expiration = timedelta(days=90)
        return datetime.utcnow() - self.password_changed_at > expiration
    
    def log_activity(self, action, details=None, ip_address=None):
        """Log user activity"""
        log = UserActivityLog(
            user_id=self.id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        return log


class UserActivityLog(db.Model):
    """User activity audit log"""
    __tablename__ = 'user_activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # LOGIN, LOGOUT, CREATE, UPDATE, DELETE, etc.
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', back_populates='activity_logs')
```

### Role Decorators

```python
# app/decorators.py

from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user, login_required

def require_role(*roles):
    """Decorator to restrict access to specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    abort(401)
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role.value not in roles:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Convenience decorators
def admin_required(f):
    return require_role('admin')(f)

def lab_manager_required(f):
    return require_role('admin', 'laboratory_manager')(f)

def technician_required(f):
    return require_role('admin', 'laboratory_manager', 'technician')(f)

def client_access_required(f):
    """Allow admin, lab_manager, or the specific client"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.is_admin() or current_user.is_laboratory_manager():
            return f(*args, **kwargs)
        
        # For client role, check if accessing own data
        client_id = kwargs.get('cliente_id') or request.view_args.get('cliente_id')
        if current_user.is_client() and current_user.cliente_id == client_id:
            return f(*args, **kwargs)
        
        abort(403)
    return decorated_function
```

### User Admin Routes

```python
# app/routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.database.models import User, UserRole, Cliente
from app.forms.user import UserForm, UserEditForm, PasswordChangeForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """List all users with filters"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')
    estado = request.args.get('estado')
    q = request.args.get('q', '')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=UserRole(role))
    if estado:
        query = query.filter_by(activo=(estado == 'activo'))
    if q:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                User.nombre_completo.ilike(f'%{q}%')
            )
        )
    
    usuarios = query.order_by(User.creado_en.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    """Create new user"""
    form = UserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            nombre_completo=form.nombre_completo.data,
            role=UserRole(form.role.data),
            cliente_id=form.cliente_id.data if form.role.data == 'client' else None,
            activo=form.activo.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        user.log_activity('USER_CREATED', {'by': current_user.username})
        
        flash(f'Usuario {user.username} creado exitosamente.', 'success')
        return redirect(url_for('admin.listar_usuarios'))
    
    return render_template('admin/crear_usuario.html', form=form)

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    """Edit user"""
    user = User.query.get_or_404(id)
    
    # Prevent self-deactivation
    if user.id == current_user.id and request.method == 'POST':
        if not form.activo.data:
            flash('No puedes desactivar tu propia cuenta.', 'error')
            return redirect(url_for('admin.editar_usuario', id=id))
    
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        old_role = user.role
        
        user.nombre_completo = form.nombre_completo.data
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        user.cliente_id = form.cliente_id.data if form.role.data == 'client' else None
        user.activo = form.activo.data
        
        db.session.commit()
        
        # Log role change
        if old_role != user.role:
            user.log_activity('ROLE_CHANGED', {
                'from': old_role.value,
                'to': user.role.value,
                'by': current_user.username
            })
        
        flash(f'Usuario {user.username} actualizado.', 'success')
        return redirect(url_for('admin.listar_usuarios'))
    
    return render_template('admin/editar_usuario.html', form=form, user=user)

@admin_bp.route('/usuarios/<int:id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(id):
    """Admin reset user password"""
    user = User.query.get_or_404(id)
    
    # Generate temporary password
    temp_password = secrets.token_urlsafe(12)
    user.set_password(temp_password)
    db.session.commit()
    
    user.log_activity('PASSWORD_RESET_BY_ADMIN', {'by': current_user.username})
    
    flash(f'Contraseña restablecida. Temporal: {temp_password}', 'warning')
    return redirect(url_for('admin.listar_usuarios'))
```

### User Form Classes

```python
# app/forms/user.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.database.models import User, UserRole, Cliente

class UserForm(FlaskForm):
    """Form for creating new users"""
    username = StringField('Usuario', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    nombre_completo = StringField('Nombre Completo', validators=[
        DataRequired(),
        Length(max=150)
    ])
    role = SelectField('Rol', choices=[
        ('admin', 'Administrador'),
        ('laboratory_manager', 'Jefe de Laboratorio'),
        ('technician', 'Técnico'),
        ('client', 'Cliente'),
        ('viewer', 'Solo Lectura')
    ], validators=[DataRequired()])
    cliente_id = SelectField('Cliente Asociado', coerce=int)
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='Mínimo 8 caracteres')
    ])
    confirmar_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Crear Usuario')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente_id.choices = [(0, '-- Seleccionar --')] + [
            (c.id, c.nombre) for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
        ]
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nombre de usuario ya existe')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este email ya está registrado')
    
    def validate_cliente_id(self, field):
        if self.role.data == 'client' and field.data == 0:
            raise ValidationError('Debe seleccionar un cliente para el rol Cliente')


class PasswordChangeForm(FlaskForm):
    """Form for password change"""
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
               message='Debe contener mayúscula, minúscula, número y especial')
    ])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(),
        EqualTo('new_password')
    ])
    submit = SubmitField('Cambiar Contraseña')
```

### Admin User List Template

```html
<!-- templates/admin/usuarios.html -->

{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>Gestión de Usuarios</h1>
    <a href="{{ url_for('admin.crear_usuario') }}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Nuevo Usuario
    </a>
</div>

<!-- Filters -->
<div class="card filters-card mb-3">
    <form method="GET" class="row">
        <div class="col-md-3">
            <input type="text" name="q" class="form-control" placeholder="Buscar..."
                   value="{{ request.args.get('q', '') }}">
        </div>
        <div class="col-md-2">
            <select name="role" class="form-control">
                <option value="">Todos los roles</option>
                <option value="admin" {% if request.args.get('role') == 'admin' %}selected{% endif %}>Admin</option>
                <option value="laboratory_manager" {% if request.args.get('role') == 'laboratory_manager' %}selected{% endif %}>Jefe Lab</option>
                <option value="technician" {% if request.args.get('role') == 'technician' %}selected{% endif %}>Técnico</option>
                <option value="client" {% if request.args.get('role') == 'client' %}selected{% endif %}>Cliente</option>
                <option value="viewer" {% if request.args.get('role') == 'viewer' %}selected{% endif %}>Lectura</option>
            </select>
        </div>
        <div class="col-md-2">
            <select name="estado" class="form-control">
                <option value="">Todos</option>
                <option value="activo" {% if request.args.get('estado') == 'activo' %}selected{% endif %}>Activo</option>
                <option value="inactivo" {% if request.args.get('estado') == 'inactivo' %}selected{% endif %}>Inactivo</option>
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-secondary btn-block">Filtrar</button>
        </div>
    </form>
</div>

<!-- Users Table -->
<div class="card">
    <table class="table table-hover">
        <thead>
            <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Cliente</th>
                <th>Estado</th>
                <th>Último Acceso</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for user in usuarios.items %}
            <tr>
                <td><strong>{{ user.username }}</strong></td>
                <td>{{ user.nombre_completo }}</td>
                <td>{{ user.email }}</td>
                <td>
                    <span class="badge badge-role badge-{{ user.role.value }}">
                        {{ role_labels[user.role.value] }}
                    </span>
                </td>
                <td>
                    {% if user.cliente %}
                    <a href="{{ url_for('clientes.ver_cliente', id=user.cliente_id) }}">
                        {{ user.cliente.nombre[:30] }}...
                    </a>
                    {% else %}-
                    {% endif %}
                </td>
                <td>
                    {% if user.activo %}
                    <span class="badge badge-success">Activo</span>
                    {% else %}
                    <span class="badge badge-secondary">Inactivo</span>
                    {% endif %}
                </td>
                <td>
                    {% if user.ultimo_acceso %}
                    {{ user.ultimo_acceso.strftime('%d/%m/%Y %H:%M') }}
                    {% else %}-
                    {% endif %}
                </td>
                <td>
                    <a href="{{ url_for('admin.editar_usuario', id=user.id) }}" class="btn btn-sm btn-warning">
                        <i class="fas fa-edit"></i>
                    </a>
                    {% if user.id != current_user.id %}
                    <form method="POST" action="{{ url_for('admin.reset_password', id=user.id) }}" 
                          style="display: inline;" onsubmit="return confirm('¿Restablecer contraseña?')">
                        <button type="submit" class="btn btn-sm btn-info" title="Reset Password">
                            <i class="fas fa-key"></i>
                        </button>
                    </form>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    {{ render_pagination(usuarios, 'admin.listar_usuarios') }}
</div>
{% endblock %}
```

### Role Badge Styles

```css
/* static/css/roles.css */

.badge-role {
    padding: 0.4em 0.8em;
    font-size: 0.85em;
    font-weight: 600;
}

.badge-admin { background-color: #dc3545; color: white; }
.badge-laboratory_manager { background-color: #007bff; color: white; }
.badge-technician { background-color: #28a745; color: white; }
.badge-client { background-color: #fd7e14; color: white; }
.badge-viewer { background-color: #6c757d; color: white; }
```

---

## Dependencies

**Blocked by:**
- Issue #5 (Phase 1): [Phase 1] Authentication System (base User model)
- Issue #1 (Phase 2): [Phase 2] Client Management (for client association)

**Blocks:**
- All Phase 3+ work (RBAC required for all features)

---

## Related Documentation

- `docs/PRD.md` Section 3.2.4: User Authentication & Authorization
- `docs/PRD.md` Section 4.1: User Roles and Responsibilities
- `plans/MIGRATION_PLAN.md` Phase 2.3: User Authentication System

---

## Testing Requirements

- [ ] Test role-based access control on all routes
- [ ] Test user creation with all roles
- [ ] Test client user data isolation
- [ ] Test password strength validation
- [ ] Test admin cannot deactivate self
- [ ] Test activity logging captures events
- [ ] Test password reset flow

---

## Definition of Done

- [ ] RBAC fully implemented
- [ ] User admin panel complete
- [ ] Role decorators applied to routes
- [ ] Permission matrix enforced
- [ ] Activity logging working
- [ ] Password management complete
- [ ] Code review completed
