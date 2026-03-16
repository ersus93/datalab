# DataLab - Context Guide

## Project Overview

**DataLab** is a modern Laboratory Information Management System (LIMS) for Cuba's National State Inspection Office (ONIE). It replaces a 15+ year old Microsoft Access system (RM2026) with a web-based solution built on Flask and SQLAlchemy.

### Key Facts
- **Purpose**: Manage laboratory samples, tests, and workflows across 4 areas (Physical-Chemical, Microbiology, Sensory Evaluation, Other Services)
- **Architecture**: Hexagonal (Ports & Adapters) with feature modules as bounded contexts
- **Migration**: Handles ~2,632 records across 25 tables from legacy Access database
- **Stack**: Python 3.11+, Flask 3.0.0, SQLAlchemy 2.0.35, PostgreSQL/SQLite, Bootstrap 5, Plotly.js
- **i18n**: Spanish (primary) and English support via GNU gettext

---

## Project Structure

```
datalab/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── cli.py                   # Custom CLI commands (seed, import)
│   ├── config.py                # Configuration classes
│   ├── decorators.py            # Auth decorators (admin_required, etc.)
│   ├── core/                    # Shared Kernel
│   │   ├── domain/
│   │   │   ├── base.py          # Entity, AuditMixin, DomainException, Repository ABC
│   │   │   └── __init__.py
│   │   └── infrastructure/
│   │       └── database.py      # SQLAlchemy configuration
│   ├── features/                # Bounded Contexts (Hexagonal Architecture)
│   │   ├── clientes/            # Client management
│   │   ├── ensayos/             # Test catalog management
│   │   ├── muestras/            # Sample management
│   │   ├── ordenes/             # Work order management
│   │   └── reportes/            # Reports and dashboard
│   │       └── {feature}/
│   │           ├── domain/      # Pure Python entities
│   │           ├── application/ # Use cases/services
│   │           └── infrastructure/
│   │               ├── persistence/  # Repository implementations
│   │               └── web/          # Flask routes (adapters)
│   ├── database/                # Legacy SQLAlchemy models (being migrated)
│   │   └── models/              # 24 model files (User, Cliente, Pedido, etc.)
│   ├── routes/                  # Legacy routes (being migrated to features)
│   ├── forms/                   # WTForms form classes
│   ├── schemas/                 # Marshmallow schemas for serialization
│   ├── services/                # Business logic services
│   ├── utils/                   # Helper utilities (cache, flash_messages)
│   ├── templates/               # Jinja2 templates
│   └── static/                  # CSS, JS, images
├── config/                      # Flask configuration modules
├── locales/                     # i18n translations (es/, en/)
├── migrations/                  # Alembic migrations
├── tests/
│   ├── conftest.py              # Pytest fixtures (app, db, auth, entities)
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── app.py                       # Main entry point
└── AGENTS.md                    # Agent guidelines (code style, commands)
```

---

## Building and Running

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings
```

### Database Setup

```bash
# Initialize database tables
flask init_db

# Or run migrations
flask db upgrade

# Seed reference data (73 records from Access RM2026)
flask seed-reference

# Create admin user
flask create_admin
```

### Run Development Server

```bash
# Option 1: Direct
python app.py

# Option 2: Flask CLI
flask run
```

Access at: `http://localhost:5000`

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_master_data_models.py

# Run specific test class
pytest tests/unit/test_master_data_models.py::TestFabricaModel

# Run specific test method
pytest tests/unit/test_master_data_models.py::TestFabricaModel::test_fabrica_creation

# Run by directory
pytest tests/unit/
pytest tests/integration/
```

### Test Fixtures Available

| Fixture | Scope | Description |
|---------|-------|-------------|
| `app` | session | Flask app in testing mode |
| `db` | session | In-memory SQLite database |
| `db_session` | function | Database session with rollback |
| `client` | function | HTTP test client |
| `admin_user` | function | Admin user instance |
| `logged_in_admin` | function | Logged-in admin client |
| `sample_cliente` | function | Sample client entity |
| `sample_fabrica` | function | Sample factory entity |
| `sample_entrada` | function | Sample entry/muestra entity |

---

## Key Commands

### Database Management

```bash
flask init_db                    # Initialize database
flask db migrate -m "message"    # Create migration
flask db upgrade                 # Apply migrations
flask db downgrade               # Revert migration
```

### Data Import (from Access RM2026)

```bash
flask import-access --file "path/to/RM2026.accdb"
flask import-phase3              # Import transactional data
flask import-phase4              # Import test details
```

### Internationalization

```bash
flask extract_messages           # Extract translatable strings
flask update_translations        # Update .po files
flask compile_translations       # Compile .mo files
```

### Other

```bash
flask seed-reference             # Seed reference tables
flask create_admin               # Create admin user
flask export_data                # Export data to CSV/Excel
```

---

## Development Conventions

### Code Style

- **Python**: 3.9+ with type hints where beneficial
- **Docstrings**: Google style for all modules, classes, functions
- **Comments**: In Spanish (project convention)
- **Line length**: ~100 characters (practical)
- **Imports**: Grouped (stdlib, third-party, local) with blank lines

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | `snake_case.py` | `clientes.py` |
| Classes | `PascalCase` | `Cliente` |
| Functions | `snake_case()` | `listar_clientes()` |
| Variables | `snake_case` | `cliente_id` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_PER_PAGE` |
| Blueprints | `{name}_bp` | `clientes_bp` |

### Database Models (SQLAlchemy)

```python
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps (project convention)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
```

### Domain Entities (Hexagonal Core)

```python
@dataclass
class Cliente(Entity, AuditMixin):
    """Entidad de dominio: Cliente del laboratorio."""
    codigo: str = ""
    nombre: str = ""
    email: Optional[str] = None
    activo: bool = True

    def __post_init__(self):
        self._validar()

    def _validar(self):
        if not self.codigo:
            raise ValidationError("El código del cliente es obligatorio.")

    def desactivar(self):
        """Desactivar cliente (soft delete)."""
        self.activo = False
```

### Routes/Blueprints

```python
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
@login_required
def listar():
    """Listar clientes con paginación, búsqueda y filtros."""
    page = request.args.get('page', 1, type=int)
    query = Cliente.query
    clientes = query.order_by(Cliente.nombre).paginate(page=page, per_page=25)
    return render_template('clientes/listar.html', clientes=clientes)
```

### Error Handling

- Use custom domain exceptions from `app.core.domain.base`:
  - `DomainException` (base)
  - `NotFoundError` (404 for entities)
  - `ValidationError` (400 for business rules)
- Global handlers in `_register_error_handlers()` (app factory)
- JSON responses for API routes: `jsonify({"error": str(e)}), status_code`
- Use `flash()` for user-facing messages in web routes

### Lazy Imports

Use lazy imports in `routes/__init__.py` and app factory to avoid circular imports:

```python
def register_routes(app):
    from app.features.clientes.infrastructure.web.routes import clientes_bp
    app.register_blueprint(clientes_bp)
```

---

## Architecture Notes

### Hexagonal Structure per Feature

```
features/clientes/
├── domain/
│   ├── models.py        # Pure Python entities (no Flask/SQLAlchemy)
│   └── repositories.py  # Repository interfaces (ABC)
├── application/
│   └── services.py      # Use cases / application services
└── infrastructure/
    ├── persistence/     # SQLAlchemy repository implementations
    └── web/
        └── routes.py    # Flask route adapters
```

### Migration Status

The project is in transition from legacy structure to hexagonal architecture:

| Layer | Status | Location |
|-------|--------|----------|
| **Features (new)** | In progress | `app/features/` |
| **Legacy models** | Active | `app/database/models/` |
| **Legacy routes** | Active | `app/routes/` |

**Important**: When adding new functionality, prefer the feature module structure over legacy patterns.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/testing/production) | `development` |
| `SECRET_KEY` | Session secret key | `dev-secret-change-in-prod` |
| `DATABASE_URL` | Database connection string | `sqlite:///datalab_dev.db` |
| `REDIS_URL` | Redis cache URL | `None` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `BABEL_DEFAULT_LOCALE` | Default language | `es` |

See `.env.example` for full list.

---

## Key Domain Concepts

### Laboratory Areas

| Code | Name | Description |
|------|------|-------------|
| FQ | Físico-Químico | Physical-chemical analysis |
| MB | Microbiología | Microbiology tests |
| ES | Evaluación Sensorial | Sensory evaluation |
| OS | Otros Servicios | Other services |

### Core Entities

- **Cliente**: Client organization requesting analysis
- **Fábrica**: Manufacturing facility belonging to a client
- **Producto**: Product to be analyzed
- **Pedido**: Order/request for analysis
- **Entrada**: Sample entry with batch tracking
- **OrdenTrabajo**: Work order grouping samples
- **Ensayo**: Test/assay definition
- **DetalleEnsayo**: Individual test result

### User Roles (RBAC)

| Role | Permissions |
|------|-------------|
| `ADMIN` | Full system access |
| `LABORATORY_MANAGER` | User management, reports, configuration |
| `TECHNICIAN` | Daily operations, tests, samples |
| `CLIENT` | View own data and reports |
| `VIEWER` | Read-only access |

---

## AI Agents

DataLab has specialized agents configured in `.opencode/agents/`. Invoke with `@agent-name`:

| Agent | Purpose |
|-------|---------|
| `@code-reviewer` | Review code against DataLab conventions |
| `@test-generator` | Generate unit/integration tests |
| `@debug` | Analyze errors and bugs |
| `@security` | Security audit |
| `@database` | SQLAlchemy, migrations, query optimization |
| `@performance` | Performance optimization |

See `AGENTS.md` for detailed usage.

---

## Common Tasks

### Add New Feature Module

1. Create feature directory: `app/features/{feature_name}/`
2. Add domain entities: `domain/models.py`
3. Define repository interfaces: `domain/repositories.py`
4. Implement repositories: `infrastructure/persistence/`
5. Create routes: `infrastructure/web/routes.py`
6. Register blueprint in `app/routes/__init__.py`

### Add Database Migration

```bash
flask db migrate -m "Add new column to table"
flask db upgrade
```

### Add Translation

1. Wrap strings with `_()`: `from flask_babel import _; label = _("Translate me")`
2. Extract: `flask extract_messages`
3. Translate in `locales/{lang}/LC_MESSAGES/messages.po`
4. Compile: `flask compile_translations`

### Add Test

1. Create test file: `tests/unit/test_{feature}.py`
2. Use class-based organization: `class Test{Entity}Model:`
3. Use fixtures from `conftest.py`
4. Run: `pytest tests/unit/test_{feature}.py -v`

---

## Troubleshooting

### Circular Imports

Use lazy imports inside functions:
```python
def my_function():
    from app.features.clientes.domain.models import Cliente
    return Cliente.query.all()
```

### Database Not Initialized

```bash
flask init_db
# or
flask db upgrade
```

### Tests Failing with Import Errors

Ensure you're running from project root with venv activated:
```bash
cd C:\Users\ernes\datalab
venv\Scripts\activate
pytest
```

---

## External Resources

- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Hexagonal Architecture**: https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)
- **Project PRD**: `docs/PRD.md`
- **Legacy Analysis**: `docs/analysis.md`
