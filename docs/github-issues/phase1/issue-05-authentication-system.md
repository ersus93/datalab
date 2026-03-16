# [Phase 1] Implement Authentication System

**Labels:** `phase-1`, `authentication`, `security`, `flask-login`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days
**Depends on:** Issue #4 ([Phase 1] Database Migration Scripts)

---

## Description

Implement a complete user authentication and authorization system using Flask-Login. This is a **critical security foundation** that enables role-based access control for the laboratory management system.

The current system has **no authentication** - this issue establishes the security layer required by all subsequent features.

### User Roles

| Role | ID | Description | Permissions |
|------|-----|-------------|-------------|
| `admin` | 1 | System Administrator | Full system access, user management |
| `laboratory_manager` | 2 | Laboratory Manager (Jefe de Laboratorio) | All data access, report approval |
| `technician` | 3 | Laboratory Technician (Técnico) | Assigned work only, result entry |
| `client` | 4 | External Client (Cliente Externo) | View own samples and reports only |
| `viewer` | 5 | Read-Only Viewer | View-only access to all data |

### Authentication Features

1. **User Model**: Store user credentials with bcrypt password hashing
2. **Login/Logout**: Session-based authentication with Flask-Login
3. **Role-Based Access**: Decorators for restricting views by role
4. **Session Management**: Secure session handling with timeouts
5. **Login UI**: Professional login page template

---

## Acceptance Criteria

### User Model

- [ ] Create `User` model with fields:
  - `id` (PK, auto-increment)
  - `username` (VARCHAR 80, unique, required)
  - `email` (VARCHAR 120, unique, required)
  - `password_hash` (VARCHAR 256, bcrypt hashed)
  - `nombre_completo` (VARCHAR 150, display name)
  - `role` (Enum: admin, laboratory_manager, technician, client, viewer)
  - `activo` (Boolean, default True)
  - `cliente_id` (FK to Clientes, only for client role)
  - `ultimo_acceso` (DateTime, last login)
  - `creado_en` (DateTime)
  - `actualizado_en` (DateTime)
- [ ] Add unique indexes on `username` and `email`
- [ ] Add index on `role` for role-based queries
- [ ] Add index on `cliente_id` for client user lookups

### Password Security

- [ ] Implement `set_password(password)` method using bcrypt (12+ rounds)
- [ ] Implement `check_password(password)` method
- [ ] Generate random salt for each password
- [ ] Never store plain-text passwords
- [ ] Add password strength validation (min 8 chars, complexity)

### Flask-Login Integration

- [ ] Initialize Flask-Login in app factory
- [ ] Implement `user_loader` callback
- [ ] Add `UserMixin` inheritance to User model
- [ ] Configure `LOGIN_VIEW` to point to login route
- [ ] Configure `LOGIN_MESSAGE` (localized)
- [ ] Configure `LOGIN_MESSAGE_CATEGORY` (e.g., 'info')

### Authentication Routes

- [ ] Create `auth` blueprint with routes:
  - `GET /auth/login` - Display login form
  - `POST /auth/login` - Process login credentials
  - `GET /auth/logout` - Log out user
  - `POST /auth/logout` - Alternative logout method
- [ ] Implement login form with CSRF protection (Flask-WTF)
- [ ] Implement proper error messages (invalid credentials, inactive account)
- [ ] Redirect to original page after login (using `next` parameter)
- [ ] Redirect to dashboard after successful login

### Login Form

- [ ] Create `LoginForm` (Flask-WTF):
  - `username` field (StringField, required)
  - `password` field (PasswordField, required)
  - `remember_me` checkbox (BooleanField, optional)
  - `submit` button
- [ ] Add validation: username exists, password provided
- [ ] Add CSRF token protection

### Login Template

- [ ] Create `templates/auth/login.html`:
  - Clean, professional design matching system theme
  - Username input field
  - Password input field
  - "Remember me" checkbox
  - Submit button
  - Error message display area
  - Link to password reset (placeholder)
  - Responsive design (mobile-friendly)
  - Laboratory logo/branding
- [ ] Extend base template
- [ ] Include form validation feedback

### Role-Based Access Control

- [ ] Create `require_role(*roles)` decorator:
  ```python
  @require_role('admin', 'laboratory_manager')
  def admin_dashboard():
      pass
  ```
- [ ] Create `login_required` wrapper (Flask-Login built-in)
- [ ] Create role-checking utilities:
  - `current_user.is_admin()`
  - `current_user.is_technician()`
  - `current_user.is_client()`
  - `current_user.can_view_client_data(client_id)`
- [ ] Handle unauthorized access (403 Forbidden page)

### Session Management

- [ ] Configure session timeout (e.g., 8 hours for workday)
- [ ] Configure permanent session duration for "remember me"
- [ ] Implement `session.permanent` based on remember_me checkbox
- [ ] Add session security headers:
  - `SESSION_COOKIE_SECURE` (True in production)
  - `SESSION_COOKIE_HTTPONLY` (True)
  - `SESSION_COOKIE_SAMESITE` ('Lax' or 'Strict')
- [ ] Log login/logout events for audit trail

### Default Users

- [ ] Create seed script for initial admin user:
  - Username: `admin`
  - Password: Generate strong random password or require setup
  - Role: `admin`
  - Email: configurable via environment variable
- [ ] Document password setup procedure
- [ ] Add warning about changing default credentials

---

## Technical Notes

### User Model Implementation

```python
# app/database/models/user.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    """User roles for role-based access control"""
    ADMIN = 'admin'
    LABORATORY_MANAGER = 'laboratory_manager'
    TECHNICIAN = 'technician'
    CLIENT = 'client'
    VIEWER = 'viewer'

class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    
    Implements Flask-Login UserMixin for session management.
    Passwords are hashed using Werkzeug's bcrypt implementation.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='usuarios')
    
    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'
    
    def set_password(self, password):
        """Hash and set password using bcrypt"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_laboratory_manager(self):
        return self.role == UserRole.LABORATORY_MANAGER
    
    def is_technician(self):
        return self.role == UserRole.TECHNICIAN
    
    def is_client(self):
        return self.role == UserRole.CLIENT
    
    def can_view_client_data(self, client_id):
        """Check if user can view data for specific client"""
        if self.is_admin() or self.is_laboratory_manager():
            return True
        if self.is_client() and self.cliente_id == client_id:
            return True
        return False
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Required by Flask-Login"""
        return self.activo
```

### Authentication Blueprint

```python
# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.database.models import User, UserRole
from app.forms.auth import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            
            # Log the login event (for audit trail)
            # current_app.logger.info(f'User {user.username} logged in')
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
            
            flash(f'Bienvenido, {user.nombre_completo or user.username}!', 'success')
            return redirect(next_page)
        
        flash('Usuario o contraseña incorrectos.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth.login'))
```

### Role Decorator

```python
# app/decorators.py

from functools import wraps
from flask import abort
from flask_login import current_user

def require_role(*roles):
    """Decorator to restrict view to specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            if current_user.role.value not in roles:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Convenience decorators
def admin_required(f):
    return require_role('admin')(f)

def technician_required(f):
    return require_role('technician', 'admin', 'laboratory_manager')(f)

def client_access_required(client_id_param='cliente_id'):
    """Decorator to ensure user can access specific client data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            # Get client_id from kwargs or request
            client_id = kwargs.get(client_id_param) or request.args.get(client_id_param)
            
            if client_id and not current_user.can_view_client_data(int(client_id)):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### Login Form

```python
# app/forms/auth.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """Login form with CSRF protection"""
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es obligatorio'),
        Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria')
    ])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')
```

### Login Template (HTML)

```html
<!-- templates/auth/login.html -->
{% extends 'base.html' %}

{% block title %}Iniciar Sesión - DataLab{% endblock %}

{% block content %}
<div class="login-container">
    <div class="login-card">
        <div class="login-header">
            <img src="{{ url_for('static', filename='img/logo.png') }}" alt="DataLab Logo" class="login-logo">
            <h2>DataLab</h2>
            <p class="subtitle">Sistema de Gestión de Laboratorio</p>
        </div>
        
        <form method="POST" action="{{ url_for('auth.login') }}" class="login-form">
            {{ form.hidden_tag() }}
            
            <div class="form-group">
                {{ form.username.label(class="form-label") }}
                {{ form.username(class="form-control", placeholder="Usuario", autofocus=true) }}
                {% if form.username.errors %}
                    <div class="invalid-feedback">
                        {% for error in form.username.errors %}
                            {{ error }}
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            
            <div class="form-group">
                {{ form.password.label(class="form-label") }}
                {{ form.password(class="form-control", placeholder="Contraseña") }}
                {% if form.password.errors %}
                    <div class="invalid-feedback">
                        {% for error in form.password.errors %}
                            {{ error }}
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            
            <div class="form-group checkbox-group">
                {{ form.remember_me(class="form-check-input") }}
                {{ form.remember_me.label(class="form-check-label") }}
            </div>
            
            <div class="form-group">
                {{ form.submit(class="btn btn-primary btn-block") }}
            </div>
        </form>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
    </div>
</div>
{% endblock %}
```

### Application Configuration

```python
# config.py

class Config:
    # Flask-Login configuration
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Por favor inicia sesión para acceder a esta página.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    
    # Session security
    SESSION_COOKIE_SECURE = True  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
```

---

## Dependencies

**Blocked by:**
- Issue #4: [Phase 1] Database Migration Scripts (User table needs database)

**Blocks:**
- Issue #6: [Phase 1] Create Base Templates for CRUD (login template is base template)
- Issue #7: [Phase 1] CRUD API for Reference Data (needs authentication)
- All Phase 2+ work (all features need authentication)

---

## Related Documentation

- `docs/PRD.md` Section 3.2.4: User Authentication & Authorization requirements
- `docs/PRD.md` Section 4.1: User Roles and Responsibilities
- Flask-Login documentation: https://flask-login.readthedocs.io/
- Flask-WTF documentation: https://flask-wtf.readthedocs.io/

---

## Security Considerations

| Requirement | Implementation |
|-------------|----------------|
| Password hashing | bcrypt via Werkzeug (12+ rounds) |
| Session security | HttpOnly, Secure, SameSite cookies |
| CSRF protection | Flask-WTF on all forms |
| Brute force protection | Consider rate limiting (Phase 2+) |
| Password reset | Implement secure token-based reset (Phase 2+) |
| Audit logging | Log all login/logout events |

---

## Testing Requirements

- [ ] Test login with valid credentials succeeds
- [ ] Test login with invalid credentials fails with message
- [ ] Test inactive user cannot login
- [ ] Test "remember me" extends session
- [ ] Test logout clears session
- [ ] Test role decorator restricts access appropriately
- [ ] Test password hashing (cannot retrieve original)
- [ ] Test CSRF token required on login form
- [ ] Test session timeout works correctly

---

## Definition of Done

- [ ] User model created with all fields
- [ ] Password hashing implemented securely
- [ ] Flask-Login integration complete
- [ ] Login/logout routes functional
- [ ] Login template styled professionally
- [ ] Role-based access decorators working
- [ ] Session security configured
- [ ] Default admin user seed script created
- [ ] Code review completed
- [ ] All authentication tests passing
