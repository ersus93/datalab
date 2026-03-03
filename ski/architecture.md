# DataLab Architecture Overview

This document describes the architecture of the DataLab application, including project structure, technology stack, data flow, and design patterns.

---

## 1. Project Structure

```
datalab/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   └── models.py            # System configuration models
│   ├── database/                # Database layer
│   │   ├── __init__.py
│   │   ├── database.py          # Database configuration
│   │   ├── init_db.py           # Database initialization
│   │   └── models/              # Domain models
│   │       ├── __init__.py
│   │       ├── cliente.py       # Client model
│   │       ├── pedido.py        # Order model
│   │       └── orden_trabajo.py # Work order model
│   ├── routes/                  # HTTP route handlers (blueprints)
│   │   ├── __init__.py          # Blueprint registration
│   │   ├── clientes.py          # Client routes
│   │   ├── dashboard.py         # Dashboard routes
│   │   ├── pedidos.py           # Order routes
│   │   └── search.py            # Search routes
│   ├── services/                # Business services (future)
│   │   └── __init__.py
│   ├── static/                  # Static assets
│   │   ├── css/                 # Stylesheets
│   │   ├── js/                  # JavaScript files
│   │   └── images/              # Image assets
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   ├── componentes/         # Reusable components
│   │   │   ├── layouts/         # Layout components
│   │   │   ├── modals/          # Modal dialogs
│   │   │   └── parties/         # UI partials
│   │   └── pages/               # Page templates
│   │       ├── clientes/        # Client pages
│   │       ├── dashboard/       # Dashboard pages
│   │       └── ...
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── flash_messages.py    # Flash message helpers
├── config/                      # Configuration
│   ├── __init__.py
│   └── config.py                # Config classes
├── docs/                        # Documentation
│   ├── PRD.md                   # Product Requirements
│   └── ...
├── plans/                       # Development plans
│   └── phase-1-foundation.md
├── ski/                         # Standards & Knowledge
│   ├── architecture.md          # This file
│   ├── commands.md              # Command reference
│   └── workflow.md              # Development workflow
├── migrations/                  # Alembic migrations
│   └── ...
├── tests/                       # Test suite
│   └── ...
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview
```

---

## 2. Tech Stack Details

### 2.1 Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.11+ | Core programming language |
| Framework | Flask | 3.0.0 | Web application framework |
| ORM | SQLAlchemy | 2.0.35 | Database abstraction |
| Migration | Flask-Migrate | 4.0.5 | Database schema versioning |
| WSGI | Werkzeug | 3.0.1 | WSGI utilities and dev server |

**Flask Extensions:**
- `Flask-SQLAlchemy` - SQLAlchemy integration
- `Flask-Migrate` - Alembic migration commands

### 2.2 Frontend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Templating | Jinja2 | Server-side HTML rendering |
| Styling | Custom CSS | Application styles |
| Interactivity | Vanilla JavaScript | DOM manipulation |
| Visualization | Plotly | Charts and graphs |
| Icons | (TBD) | Icon system |

### 2.3 Database Stack

| Environment | Technology | Notes |
|-------------|------------|-------|
| Development | SQLite | File-based, zero config |
| Production | PostgreSQL | Recommended for production |
| ORM | SQLAlchemy | Database abstraction layer |

**Database Schema:**
- `clientes` - Client information
- `pedidos` - Orders from clients
- `ordenes_trabajo` - Work orders for lab analysis
- `system_config` - System configuration settings

### 2.4 Development Tools

| Tool | Purpose |
|------|---------|
| python-dotenv | Environment variable management |
| Click | CLI framework (via Flask) |
| Git | Version control |

### 2.5 Optional/Future Tools

| Tool | Purpose | Status |
|------|---------|--------|
| pytest | Testing framework | Recommended |
| flake8 | Linting | Recommended |
| black | Code formatting | Recommended |
| mypy | Type checking | Optional |
| gunicorn | Production WSGI | Production |

---

## 3. Data Flow

### 3.1 Request-Response Cycle

```
┌─────────────┐     HTTP Request      ┌─────────────┐
│   Client    │ ────────────────────> │    Nginx    │
│  (Browser)  │                       │   (Proxy)   │
└─────────────┘                       └──────┬──────┘
       ^                                     │
       │                                     │
       │ HTTP Response                       │ WSGI
       │                                     v
┌─────────────┐                       ┌─────────────┐
│  Template   │ <── Render HTML ─────│    Flask    │
│   (Jinja2)  │                       │  Application│
└─────────────┘                       └──────┬──────┘
                                             │
                                             │ SQL
                                             v
                                       ┌─────────────┐
                                       │  SQLAlchemy │
                                       │    ORM      │
                                       └──────┬──────┘
                                              │
                                              │ SQL
                                              v
                                       ┌─────────────┐
                                       │  SQLite/    │
                                       │ PostgreSQL  │
                                       └─────────────┘
```

### 3.2 Data Flow by Feature

#### Client Management Flow
```
User Request
    ↓
clientes_bp (Blueprint)
    ↓
Route Handler (clientes.py)
    ↓
Cliente Model (SQLAlchemy)
    ↓
Database
    ↓
Template Rendering (Jinja2)
    ↓
HTML Response
```

#### Dashboard Data Flow
```
Dashboard Request
    ↓
dashboard_bp
    ↓
Query Multiple Models
    ├── Cliente.query.count()
    ├── Pedido.query.filter_by(status)
    └── OrdenTrabajo.query.all()
    ↓
Aggregate Data
    ↓
Render Template with Metrics
    ↓
Response with Plotly Charts
```

### 3.3 Model Relationships

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Cliente    │◄─────►│   Pedido    │◄─────►│OrdenTrabajo │
│  (Client)   │  1:N  │   (Order)   │  1:N  │ (Work Order)│
└─────────────┘       └─────────────┘       └─────────────┘
       │
       │ Attributes:
       │ - id (PK)
       │ - codigo
       │ - nombre
       │ - email
       │ - telefono
       │ - direccion
       │ - activo
       │ - timestamps
```

**Relationship Details:**
- **Cliente → Pedido:** One-to-Many (A client can have multiple orders)
- **Pedido → OrdenTrabajo:** One-to-Many (An order can have multiple work orders)

---

## 4. Key Patterns Used

### 4.1 Application Factory Pattern

The application uses Flask's application factory pattern for better testability and configuration management.

```python
# app/__init__.py
def create_app(config_name=None):
    app = Flask(__name__)
    # Configuration based on environment
    app.config.from_object(Config)
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # Register blueprints
    register_routes(app)
    return app
```

**Benefits:**
- Multiple app instances with different configs
- Easier testing
- No circular import issues

### 4.2 Blueprint Pattern

Routes are organized using Flask blueprints for modularity.

```python
# app/routes/clientes.py
clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes')
def index():
    return render_template('pages/clientes/index.html')

# app/routes/__init__.py
def register_routes(app):
    from app.routes.clientes import clientes_bp
    app.register_blueprint(clientes_bp)
```

**Benefits:**
- Modular route organization
- URL prefix and template folder support
- Reusable across applications

### 4.3 Model-View Architecture

The application follows an MVC-like pattern:

- **Models:** Database models in `app/database/models/`
- **Views:** Templates in `app/templates/`
- **Controllers:** Route handlers in `app/routes/`

### 4.4 Repository Pattern (Implicit)

SQLAlchemy models act as repositories:

```python
# Query all
clientes = Cliente.query.all()

# Query with filter
clientes_activos = Cliente.query.filter_by(activo=True).all()

# Create
nuevo_cliente = Cliente(nombre="Test", codigo="CLI001")
db.session.add(nuevo_cliente)
db.session.commit()
```

### 4.5 Configuration Management

Environment-based configuration using classes:

```python
# config/config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

### 4.6 Template Inheritance

Base template with blocks for child templates:

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>{% block head %}{% endblock %}</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

<!-- templates/pages/clientes/index.html -->
{% extends "base.html" %}
{% block content %}
    <h1>Clientes</h1>
{% endblock %}
```

---

## 5. Security Considerations

### 5.1 Implemented
- SQL Injection Prevention (SQLAlchemy ORM)
- CSRF Protection (session-based)
- Secure Session Configuration
- Environment-based SECRET_KEY

### 5.2 Future Implementation
- User authentication and authorization
- Password hashing (bcrypt)
- HTTPS enforcement
- Rate limiting
- Input validation (WTForms)
- XSS protection headers

---

## 6. Performance Considerations

### 6.1 Database
- Indexes on frequently queried columns (codigo, numero_pedido, numero)
- Lazy loading for relationships
- Query optimization with SQLAlchemy

### 6.2 Caching Opportunities
- Template caching in production
- Query result caching for dashboard metrics
- Static file caching (Nginx/CDN)

### 6.3 Frontend
- Minified CSS/JS in production
- Image optimization
- Lazy loading for data tables

---

## 7. Scalability Roadmap

### Current (Phase 1)
- Single Flask instance
- SQLite/PostgreSQL database
- Synchronous request handling

### Phase 2 (Future)
- Application factory for multiple workers
- Redis for session storage
- Background task queue (Celery)

### Phase 3 (Future)
- Microservices architecture
- API Gateway
- Containerization (Docker/Kubernetes)

---

## 8. Architecture Decision Records (ADRs)

### ADR 1: Flask over Django
**Decision:** Use Flask instead of Django  
**Rationale:** Lighter weight, more flexible for custom requirements, easier to learn for small team  
**Status:** Accepted

### ADR 2: SQLAlchemy ORM
**Decision:** Use SQLAlchemy as ORM  
**Rationale:** Industry standard for Flask, supports multiple databases, powerful query capabilities  
**Status:** Accepted

### ADR 3: Server-Side Rendering
**Decision:** Use Jinja2 templates over SPA framework  
**Rationale:** Simpler architecture, better for SEO, faster initial page load, less JavaScript complexity  
**Status:** Accepted

### ADR 4: SQLite for Development
**Decision:** Use SQLite in development, PostgreSQL in production  
**Rationale:** Zero configuration for developers, easy setup, production parity with config change  
**Status:** Accepted

---

*Last Updated:* March 2026
