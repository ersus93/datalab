# Análisis de Implementación — Phase 4 / Issue 5: Test Data Import

**Fecha del análisis:** 2026-03-06  
**Issue:** `docs/github-issues/phase4/issue-5-test-data-import.md`  
**Estimado original:** 8 SP / 3-4 días  

---

## 🔍 Resumen Ejecutivo

El issue requiere importar **563 registros** de `Detalles de Ensayos` y **632 registros** de `Utilizado R` desde la base Access legacy. La infraestructura de **modelos y servicios de dominio** está en gran parte lista, pero el **pipeline de importación Phase 4 aún no existe**. Se ha completado aproximadamente el **35–40%** del trabajo total.

---

## ✅ Lo que YA está implementado

### 1. Modelo `DetalleEnsayo` — `app/database/models/detalle_ensayo.py`
- Todos los campos requeridos por el issue: `entrada_id`, `ensayo_id`, `cantidad`, `estado`, `fecha_asignacion`, `fecha_inicio`, `fecha_completado`, `tecnico_asignado_id`, `observaciones`
- Campos adicionales para resultados: `valor_numerico`, `valor_texto`, `valor_booleano`, `resultado_cumple`
- `UniqueConstraint("entrada_id", "ensayo_id")` implementado
- `Index("ix_detalle_entrada_estado", "entrada_id", "estado")` creado
- State machine completa con `VALID_TRANSITIONS` y métodos `can_transition` / `get_valid_transitions`
- Flujo: `PENDIENTE → ASIGNADO → EN_PROCESO → COMPLETADO → REPORTADO` (+ `PAUSADO`)

### 2. Migración Alembic para `DetalleEnsayo` — `migrations/versions/abeec908fc2d_*.py`
- Tabla `detalles_ensayo` creada formalmente con Alembic
- FKs a `entradas.id`, `ensayos.id`, `users.id`
- Enum `detalle_ensayo_status` definido

### 3. Modelo `Utilizado` — `app/database/models/utilizado.py`
- Campos financieros completos: `cantidad`, `precio_unitario`, `importe`, `fecha_uso`, `mes_facturacion`
- `calcular_importe()` implementado
- `UtilizadoStatus` con estados `PENDIENTE / FACTURADO / ANULADO`
- Modelo `Factura` incluido en el mismo archivo
- Índices compuestos para optimización: `idx_utilizado_entrada_fecha`, `idx_utilizado_estado_facturacion`

### 4. `DetalleEnsayoService` — `app/services/detalle_ensayo_service.py`
- Todas las transiciones de estado implementadas:
  - `asignar_ensayos()` — bulk assignment con dedup
  - `asignar_tecnico()` → ASIGNADO
  - `iniciar_ensayo()` → EN_PROCESO
  - `completar_ensayo()` → COMPLETADO (con auto-transición de `Entrada`)
  - `pausar_ensayo()` → PAUSADO
  - `reanudar_ensayo()` → EN_PROCESO
  - `reportar_ensayo()` → REPORTADO
  - `eliminar_detalle()` (solo desde PENDIENTE)
- Audit trail en `AuditLog` para todas las operaciones
- Queries: `get_detalles_por_entrada`, `get_detalles_agrupados_por_area`

### 5. Tests unitarios existentes
- `tests/unit/test_detalle_ensayo_model.py`
- `tests/unit/test_detalle_ensayo_service.py`

### 6. Infraestructura Phase 3 como referencia
- `app/commands/import_phase3.py` con subcomandos `all`, `validate`, `verify`
- `app/services/phase3_import_service.py` con `import_all`, `validate_all`, `verify_post_import`
- **Patrón comprobado** que se puede replicar para Phase 4

---

## ❌ Lo que FALTA implementar

### CRÍTICO — Bloqueantes para el issue

#### 1. ⚠️ No existe migración Alembic para `utilizados` y `facturas`
El modelo `Utilizado` y `Factura` están codificados pero **ninguna migración los crea en la BD**.  
Ejecutar `flask db upgrade` actualmente NO crea estas tablas.  
La `Utilizado` también referencia `detalle_ensayos` (FK) pero la tabla en Alembic se llama `detalles_ensayo` — **posible discrepancia de nombre** a verificar.

```bash
# Verificar con:
flask db current
flask db check
```

#### 2. ❌ No existe `phase4_import_service.py`
No hay equivalente a `phase3_import_service.py` para la Phase 4.  
Necesita implementar:
- `import_detalles_ensayos(data_dir)` — 563 registros con FK a `entradas` + `ensayos`
- `import_utilizado_r(data_dir)` — 632 registros con `precio`, `importe`, cálculo financiero
- `validate_all(data_dir)` — validación FK pre-import
- `verify_post_import()` — verificación post-import (conteos + FK + cálculo importe)

#### 3. ❌ No existe `import_phase4.py` CLI
No hay grupo CLI `flask import-phase4`.  
Necesita subcomandos `all`, `validate`, `verify` (patrón idéntico a Phase 3).

#### 4. ❌ No hay datos extraídos del Access
No existen archivos CSV/JSON con los datos del legacy:
- `detalles_ensayos.csv` (563 registros de `Detalles de ensayos`)
- `utilizado_r.csv` (632 registros de `Utilizado R`)

El archivo Access `utiles/RM2026_be.accdb` existe pero los datos no han sido exportados.  
El `access_importer.py` en servicios puede servir de base.

---

### SECUNDARIO — Completar para cerrar todos los Acceptance Criteria

#### 5. 📋 Validación cruzada Utilizado ↔ DetalleEnsayo
El issue requiere verificar que `cantidad` en Utilizado ≤ `cantidad` en DetalleEnsayo  
y que `importe == cantidad × precio`. No hay lógica de este tipo en ningún servicio.

#### 6. 📋 Reporte de importación en formato definido
El issue define un formato específico de reporte (con bloques `═══`).  
El patrón de Phase 3 genera Markdown + JSON, adaptable.

#### 7. 📋 Rollback capability
Phase 3 usa transacciones implícitas de SQLAlchemy. Para Phase 4 debería  
documentarse explícitamente el procedimiento de rollback + backup previo.

---

## 📊 Estado de Acceptance Criteria

| Criterio | Estado | Notas |
|----------|--------|-------|
| Import script para Detalles de Ensayos creado | ❌ FALTA | Ni CLI ni service |
| Import script para Utilizado R creado | ❌ FALTA | Ni CLI ni service |
| 563 detalle records importados | ❌ FALTA | Sin datos extraídos del Access |
| 632 utilizado records importados | ❌ FALTA | Sin datos extraídos del Access |
| FK a entradas validadas | ❌ FALTA | No hay servicio de validación |
| FK a ensayos validadas | ❌ FALTA | No hay servicio de validación |
| Test assignments verificados contra samples | ❌ FALTA | No hay servicio |
| Test results importados si disponibles | ⚠️ N/A | Access tiene 0 filas en `Resultados de ensayos` |
| Data integrity checks pasados | ❌ FALTA | No existe lógica de verificación |
| Import report generado con estadísticas | ❌ FALTA | No existe el módulo de reporte |
| Rollback capability testeado | ❌ FALTA | No documentado/testeado |

**Completado: 0/11 criterios de aceptación** (la infraestructura de modelos es prerequisito, no criterio)

---

## 🏗️ Plan de Implementación Recomendado

Dado el patrón establecido en Phase 3, estimar **2–3 días reales** para completar:

### Día 1: Migración + Extracción de datos
```bash
# 1. Corregir/crear migración para utilizados y facturas
flask db migrate -m "add utilizados and facturas tables"
flask db upgrade

# 2. Exportar datos del Access usando access_importer.py
python utiles/analyze_access.py --export-table "Detalles de ensayos" --output data/migrations/detalles_ensayos.csv
python utiles/analyze_access.py --export-table "Utilizado R" --output data/migrations/utilizado_r.csv
```

### Día 2: Phase4ImportService
Crear `app/services/phase4_import_service.py` con:
- `import_detalles_ensayos(file_path, dry_run)`
- `import_utilizado_r(file_path, dry_run)`
- `validate_all(data_dir)` — FK checks pre-import
- `verify_post_import()` — conteos + integridad financiera

### Día 3: CLI + Tests + Report
Crear `app/commands/import_phase4.py` con subcomandos `all`, `validate`, `verify`  
Escribir tests en `tests/unit/test_phase4_import.py`  
Registrar en `app/__init__.py`

---

## ⚠️ Riesgos Identificados

| Riesgo | Descripción | Mitigación |
|--------|-------------|------------|
| Discrepancia de nombre de tabla | `utilizados` (modelo) vs potencial FK en migración | Verificar con `flask db check` antes de migrar |
| FKs huérfanas | Los 563 detalles referencian 109 entradas — posibles IDs no mapeados | Validar con dry-run primero |
| `Utilizado R` tiene 0 precios | El Access tiene `Precio` e `Importe` pero podrían estar en 0 | Revisar datos crudos antes de asumir integridad financiera |
| `detalle_ensayo_id` en Utilizado | Requiere que `detalles_ensayo` esté importado PRIMERO | Respetar orden: DetalleEnsayo → Utilizado |

---

## 📁 Archivos a Crear

```
app/
├── commands/
│   └── import_phase4.py          ← NUEVO
└── services/
    └── phase4_import_service.py  ← NUEVO

migrations/versions/
└── xxxx_add_utilizados_facturas_tables.py  ← NUEVO

tests/unit/
└── test_phase4_import.py         ← NUEVO

data/migrations/                  ← NUEVO directorio
├── detalles_ensayos.csv
└── utilizado_r.csv
```
