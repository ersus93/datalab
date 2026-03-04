# [CRITICAL] Fix missing clientes feature module - ImportError blocking app startup

**Labels:** `critical`, `blocking`, `architecture`, `phase-1`  
**GitHub Issue:** #36  
**Priority:** CRITICAL - Blocks all development work

---

## Problem

The application fails to start due to a missing module:

```
ModuleNotFoundError: No module named 'app.features.clientes.infrastructure.web.routes'
```

The file `app/routes/__init__.py` attempts to import from a non-existent directory structure.

## Root Cause

The hexagonal architecture refactoring created the import in `routes/__init__.py`:
```python
from app.features.clientes.infrastructure.web.routes import clientes_bp
```

But the actual directory `app/features/clientes/` does not exist. Only these feature directories exist:
- `app/features/ensayos/`
- `app/features/muestras/`
- `app/features/ordenes/`
- `app/features/reportes/`

## Temporary Workaround

Modify `app/routes/__init__.py` to use legacy routes temporarily:
```python
from app.routes.clientes import clientes_bp
```

## Proper Solution

Create the complete hexagonal structure for clientes:
```
app/features/clientes/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── models.py
├── application/
│   ├── __init__.py
│   └── services.py
└── infrastructure/
    ├── __init__.py
    └── web/
        ├── __init__.py
        └── routes.py
```

## Acceptance Criteria
- [ ] Application starts without ImportError
- [ ] Routes are accessible at /clientes/*
- [ ] Existing functionality preserved
- [ ] Tests pass

## Related Issues
- Blocks: Issue #38 (Create missing database migrations)
- Blocks: Issue #40 (Execute reference data seeding)

## Created
2026-03-04
