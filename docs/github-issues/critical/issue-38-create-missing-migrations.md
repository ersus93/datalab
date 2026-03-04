# [CRITICAL] Create missing database migrations - 14 tables not in database

**Labels:** `critical`, `blocking`, `database`, `migration`, `sqlalchemy`, `phase-1`  
**GitHub Issue:** #38  
**Priority:** CRITICAL - Blocks database operations and feature development

---

## Problem

Only 1 out of 15 database models have migrations. The database only has the `clientes` table, but 14 other tables are missing.

## Current State

**Migration files:** 1
- `5772e0718a9e_initial_migration_with_existing_models.py` - Creates only `clientes` table

**Models defined:** 15 (22 total tables including join tables)

| # | Table | Model File | Has Migration |
|---|-------|------------|---------------|
| 1 | ✅ `clientes` | cliente.py | ✅ Yes |
| 2 | ❌ `areas` | reference.py | ❌ No |
| 3 | ❌ `organismos` | reference.py | ❌ No |
| 4 | ❌ `provincias` | reference.py | ❌ No |
| 5 | ❌ `destinos` | reference.py | ❌ No |
| 6 | ❌ `ramas` | reference.py | ❌ No |
| 7 | ❌ `meses` | reference.py | ❌ No |
| 8 | ❌ `annos` | reference.py | ❌ No |
| 9 | ❌ `tipos_es` | reference.py | ❌ No |
| 10 | ❌ `unidades_medida` | reference.py | ❌ No |
| 11 | ❌ `fabricas` | fabrica.py | ❌ No |
| 12 | ❌ `productos` | producto.py | ❌ No |
| 13 | ❌ `ensayos` | ensayo.py | ❌ No |
| 14 | ❌ `ensayos_es` | ensayo_es.py | ❌ No |
| 15 | ❌ `ensayos_x_productos` | ensayo_x_producto.py | ❌ No |
| 16 | ❌ `pedidos` | pedido.py | ❌ No |
| 17 | ❌ `ordenes_trabajo` | orden_trabajo.py | ❌ No |
| 18 | ❌ `entradas` | entrada.py | ❌ No |
| 19 | ❌ `status_history` | status_history.py | ❌ No |
| 20 | ❌ `audit_log` | audit.py | ❌ No |
| 21 | ❌ `notifications` | notification.py | ❌ No |
| 22 | ❌ `users` | user.py | ❌ No |

## Impact

Foreign key relationships will fail:
- `Cliente.organismo_id` → `organismos.id` (target doesn't exist)
- `Fabrica.provincia_id` → `provincias.id` (target doesn't exist)
- `Producto.destino_id` → `destinos.id` (target doesn't exist)

## Solution

Generate a comprehensive migration:
```bash
flask db migrate -m "add_all_remaining_models"
```

This should create tables for all models in `app/database/models/`:

### Reference Data (9 tables)
- areas, organismos, provincias, destinos, ramas
- meses, annos, tipos_es, unidades_medida

### Master Data (2 tables)
- fabricas, productos

### Test Catalog (3 tables)
- ensayos, ensayos_es, ensayos_x_productos

### Transaction Core (3 tables)
- pedidos, ordenes_trabajo, entradas

### Audit & Security (4 tables)
- status_history, audit_log, notifications, users

## Acceptance Criteria
- [ ] Migration file created with all tables
- [ ] `flask db upgrade` executes successfully
- [ ] All 22 tables exist in database
- [ ] Foreign key constraints are valid
- [ ] No data loss on existing `clientes` table

## Prerequisites
- Issue #36 must be resolved (app must start to run migrations)

## Related Issues
- Depends on: Issue #36 (Fix missing clientes module)
- Blocks: Issue #40 (Execute reference data seeding)

## Created
2026-03-04
