# DataLab - Agent Guidelines

Flask application for laboratory data analysis and visualization.

## Commands

### Build/Run
```bash
# Start development server
python app.py
# OR
flask run

# Initialize database
flask init-db

# Database migrations
flask db migrate -m "description"
flask db upgrade
flask db downgrade
```

### Testing
```bash
# Run all tests
pytest

# Run single test file
pytest tests/unit/test_master_data_models.py

# Run single test class
pytest tests/unit/test_master_data_models.py::TestFabricaModel

# Run single test method
pytest tests/unit/test_master_data_models.py::TestFabricaModel::test_fabrica_creation

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test directory
pytest tests/unit/
pytest tests/integration/
```

### Linting (if tools available)
```bash
# Check if available
which ruff flake8 black

# Install if needed: pip install ruff black
ruff check app/
black --check app/
```

## Code Style

### General
- Python 3.9+ with type hints where beneficial
- Docstrings for all modules, classes, and functions (Google style)
- Comments in Spanish (project convention)
- Line length: ~100 characters (practical, not strict)

### Imports (grouped and separated)
```python
# 1. Standard library
from datetime import datetime
from enum import Enum

# 2. Third-party
from flask import Blueprint, render_template
from flask_login import login_required

# 3. Local application
from app import db
from app.database.models.user import User
from app.forms.auth import LoginForm
```

### Naming Conventions
- **Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`
- **Blueprints**: `{name}_bp`

### Database Models (SQLAlchemy)
```python
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
```

### Routes/Blueprints
```python
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Docstring describing the route."""
    pass
```

### Error Handling
- Use custom domain exceptions from `app.core.domain.base`
- Global handlers in `_register_error_handlers()` in app factory
- Return JSON for API routes: `jsonify({"error": str(e)}), status_code`
- Use Flask's `flash()` for user-facing messages in web routes

### Lazy Imports
Use lazy imports in routes/__init__.py and app factory to avoid circular imports:
```python
def register_routes(app):
    from app.features.clientes.infrastructure.web.routes import clientes_bp
    app.register_blueprint(clientes_bp)
```

### Project Structure
```
app/
├── __init__.py          # App factory
├── config.py            # Config classes
├── decorators.py        # Auth decorators
├── routes/              # Legacy routes (being migrated)
├── features/            # Feature modules (hexagonal architecture)
│   └── {feature}/
│       └── infrastructure/web/routes.py
├── database/models/     # SQLAlchemy models
├── core/                # Domain logic, base classes
└── utils/               # Helper functions

tests/
├── unit/                # Unit tests
└── integration/         # Integration tests
```

### Environment
- Copy `.env.example` to `.env` for local development
- `FLASK_ENV=development` for dev, `testing` for tests
- Uses SQLite in dev/testing, PostgreSQL in production

### Testing Patterns
- Use pytest with class-based test organization
- Model tests: `test_{model}_{behavior}`
- Use pytest-flask for app fixtures
- Prefer `assert` statements over unittest methods
