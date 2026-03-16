# Development Commands Reference

Quick reference guide for common development commands in the DataLab project.

---

## 1. Setup Commands

### 1.1 Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd datalab

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
# Edit .env with your configuration

# Initialize database
flask init-db

# Run the application
flask run
```

### 1.2 Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Database
DATABASE_URL=sqlite:///datalab.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/datalab

# Logging
LOG_LEVEL=INFO
```

### 1.3 Verify Setup

```bash
# Check Python version (requires 3.11+)
python --version

# Verify Flask installation
flask --version

# Check if app runs
flask run --help
```

---

## 2. Database Commands

### 2.1 Database Initialization

```bash
# Initialize database with tables
flask init-db

# This command is defined in app.py and:
# - Creates all tables
# - Sets up initial system configuration
# - Ready for use
```

### 2.2 Flask-Migrate Commands

```bash
# Initialize migration repository (first time only)
flask db init

# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations to database
flask db upgrade

# Rollback last migration
flask db downgrade

# View current migration version
flask db current

# View migration history
flask db history
```

### 2.3 Database Utilities

```bash
# Open Flask shell with app context
flask shell

# Inside shell, you can interact with models:
>>> from app.database.models import Cliente, Pedido, OrdenTrabajo
>>> from app import db
>>> 
>>> # Query all clients
>>> clients = Cliente.query.all()
>>> 
>>> # Create new client
>>> new_client = Cliente(codigo='CLI001', nombre='Test Client')
>>> db.session.add(new_client)
>>> db.session.commit()
>>> 
>>> # Exit shell
>>> exit()
```

### 2.4 Database Backup/Restore (SQLite)

```bash
# Backup database
copy datalab.db datalab_backup_$(date +%Y%m%d).db

# Restore database
copy datalab_backup_YYYYMMDD.db datalab.db

# For PostgreSQL, use pg_dump and pg_restore
```

---

## 3. Run Commands

### 3.1 Development Server

```bash
# Standard run
flask run

# Run with specific host and port
flask run --host=0.0.0.0 --port=8080

# Run with debugger and reloader
flask run --debug

# Run with custom environment
FLASK_ENV=development flask run
```

### 3.2 Production Server

```bash
# Using Gunicorn (install first: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"

# Using Waitress (Windows-friendly, install: pip install waitress)
waitress-serve --port=8000 --call "app:create_app"
```

### 3.3 Debug Mode

```bash
# Enable debug mode
set FLASK_DEBUG=1  # Windows
export FLASK_DEBUG=1  # macOS/Linux

# Or in .env file
DEBUG=True
```

---

## 4. Testing Commands

### 4.1 Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_clientes.py

# Run specific test class
python -m pytest tests/test_clientes.py::TestClientes

# Run specific test method
python -m pytest tests/test_clientes.py::TestClientes::test_create_client
```

### 4.2 Test Coverage

```bash
# Run tests with coverage
python -m pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=app --cov-report=html
# Report will be in htmlcov/index.html

# Generate XML coverage report (for CI)
python -m pytest --cov=app --cov-report=xml
```

### 4.3 Test Database

```bash
# Tests use in-memory SQLite automatically
# Configure in config.py TestingConfig
```

---

## 5. Code Quality Commands

### 5.1 Linting

```bash
# Run flake8 (install: pip install flake8)
flake8 app/

# Run with specific options
flake8 app/ --max-line-length=100 --exclude=venv,migrations
```

### 5.2 Formatting

```bash
# Auto-format with black (install: pip install black)
black app/

# Check formatting without changes
black --check app/

# Format specific file
black app/routes/clientes.py
```

### 5.3 Import Sorting

```bash
# Sort imports with isort (install: pip install isort)
isort app/

# Check import order
isort --check-only app/
```

### 5.4 Type Checking

```bash
# Run mypy (install: pip install mypy)
mypy app/

# With specific config
mypy app/ --ignore-missing-imports
```

---

## 6. Git Commands

### 6.1 Daily Workflow

```bash
# Check status
git status

# Pull latest changes
git pull origin develop

# Create feature branch
git checkout -b feature/DL-123-description

# Stage changes
git add .
# or specific files:
git add app/routes/clientes.py

# Commit with conventional format
git commit -m "feat(clientes): add search functionality"

# Push branch
git push -u origin feature/DL-123-description

# After PR approval, cleanup
git checkout develop
git pull origin develop
git branch -d feature/DL-123-description
```

### 6.2 Useful Git Commands

```bash
# View commit history
git log --oneline --graph

# View changes
git diff

# Undo uncommitted changes
git checkout -- <file>

# Amend last commit
git commit --amend

# Stash changes
git stash
git stash pop

# View remote branches
git branch -a
```

---

## 7. Utility Commands

### 7.1 Dependency Management

```bash
# Export installed packages
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Update a specific package
pip install --upgrade flask

# Show package info
pip show flask
```

### 7.2 Environment Management

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Deactivate
deactivate

# Remove virtual environment
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux
```

### 7.3 Project Structure Commands

```bash
# View project tree (Windows)
tree /f

# View project tree (macOS/Linux)
find . -type f -name "*.py" | head -20
tree -L 3 -I '__pycache__|venv|*.pyc'
```

---

## 8. Troubleshooting Commands

### 8.1 Database Issues

```bash
# Reset database (DEVELOPMENT ONLY!)
# Delete datalab.db file and reinitialize
rm datalab.db  # macOS/Linux
del datalab.db  # Windows
flask init-db

# Check database connection
flask shell
>>> from app import db
>>> db.engine.execute("SELECT 1")
```

### 8.2 Cache Issues

```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Or manually delete __pycache__ folders
```

### 8.3 Port Already in Use

```bash
# Windows - find process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

---

## 9. Quick Reference Card

```bash
# Setup (run once)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask init-db

# Daily development
venv\Scripts\activate
flask run

# Before committing
flake8 app/
black app/
python -m pytest

# Database changes
flask db migrate -m "description"
flask db upgrade

# Git workflow
git checkout develop
git pull origin develop
git checkout -b feature/DL-XXX-description
# ... make changes ...
git add .
git commit -m "feat(scope): description"
git push -u origin feature/DL-XXX-description
# ... create PR ...
```

---

*Last Updated:* March 2026
