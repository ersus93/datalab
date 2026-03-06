# 🔍 Auditoría de Implementación — DataLab Fases 1, 2 y 3

**Fecha:** 2026-03-05  
**Alcance:** Implementación vs. Especificaciones en `docs/github-issues/phase1-3`  
**Resultado General:** ⚠️ Fases 1-3 mayormente implementadas con **10 brechas críticas** que bloquean estabilidad y corrección

---

## Resumen Ejecutivo

| Fase | Estado Declarado | Estado Real | Brechas |
|------|-----------------|-------------|---------|
| Fase 1 – Foundation & Schema | ✅ Completada | ⚠️ 90% — issues menores | 4 |
| Fase 2 – Core Entities & CRUD | ✅ Completada | ⚠️ 85% — gaps funcionales | 3 |
| Fase 3 – Sample Management | ✅ Completada | ⚠️ 80% — deuda técnica | 3 |

---

## Hallazgos por Fase

---

### 🔴 FASE 1 — Foundation & Schema

#### Issue #1-3: Modelos de datos de referencia, maestros y ensayos
**Estado:** ✅ Implementado correctamente  
- `Area`, `Organismo`, `Provincia`, `Destino`, `Rama`, `Mes`, `Anno`, `TipoES`, `UnidadMedida` → todos presentes en `app/database/models/reference.py`
- `Cliente`, `Fabrica`, `Producto` → presentes y con relaciones FK correctas
- `Ensayo`, `EnsayoES` → presentes

#### Issue #4: Migration Scripts
**Estado:** ✅ Implementado (Alembic configurado en `migrations/`)

#### Issue #5: Authentication System
**Estado:** ⚠️ Mayormente implementado — 2 brechas  

🔴 **Brecha 1 — Timeout de sesión no configurado:**  
El issue especifica `PERMANENT_SESSION_LIFETIME = timedelta(hours=8)` y las cookies de seguridad. La config actual en `app/config.py` no incluye estos valores explícitamente.

🔴 **Brecha 2 — `_get_locale()` ignora el parámetro `?lang=`:**  
El README indica que el usuario puede cambiar idioma con `?lang=en`, pero `_get_locale()` en `app/__init__.py` solo usa `request.accept_languages` y nunca lee `request.args.get('lang')`.

#### Issue #6: Base Templates
**Estado:** ⚠️ Implementado con deuda estructural  

🟡 **Brecha 3 — Carpetas de templates duplicadas:**  
Existen `app/templates/componentes/` y `app/templates/components/` simultáneamente, y también `app/templates/pages/` con subdirectorios que repiten lo que ya está en `app/templates/clientes/`, `app/templates/pedidos/`, etc. Esto genera ambigüedad en cuál plantilla es la canónica.

#### Issue #7: CRUD API Reference Data
**Estado:** ✅ Implementado en `app/routes/reference.py`

#### Issue #8: Import Access Data
**Estado:** ✅ Implementado en `app/services/access_importer.py` y `app/commands/import_cli.py`

---

### 🔴 FASE 2 — Core Entities & CRUD

#### Issue #1: Client Management
**Estado:** ⚠️ Implementado con 2 brechas  

🔴 **Brecha 4 — Campo `codigo` en `ClienteForm` ausente:**  
El modelo `Cliente` tiene campo `codigo` (VARCHAR 20, unique, not null), pero el formulario `app/forms/cliente.py` **no lo incluye**. Esto hace imposible crear un cliente desde la UI, ya que `codigo` es `nullable=False` en la base de datos.

🔴 **Brecha 5 — Audit logging no conectado en rutas:**  
El issue especifica que todas las operaciones CRUD deben loguear en `audit_log`. El modelo `AuditLog` existe en `app/database/models/audit.py`, pero **ninguna ruta** (clientes, fabricas, productos, etc.) llama a `AuditLog.log_change()`. El audit trail está completamente desconectado.

#### Issue #2-3: Factory & Product Management
**Estado:** ✅ Rutas implementadas en `app/routes/fabricas.py` y `app/routes/productos.py`

#### Issue #4: User Auth & RBAC
**Estado:** ✅ Completo — `User`, `UserRole`, decoradores en `app/decorators.py`

#### Issue #5-6: Master Data Import & Dashboard
**Estado:** ✅ Implementados

---

### 🔴 FASE 3 — Sample Management

#### Issue #1: Sample Entry System
**Estado:** ⚠️ Implementado con brecha arquitectónica  

🟡 **Brecha 6 — `features/clientes/infrastructure/persistence/sql_repository.py` eliminado:**  
El directorio `__pycache__` contiene `sql_repository.cpython-313.pyc` pero el archivo fuente `.py` no existe. Esto indica que el archivo fue borrado accidentalmente, dejando la arquitectura hexagonal incompleta en ese feature. Las rutas actuales de clientes **bypasean** la capa `features/` y acceden directamente a `app/database/models/`, violando la arquitectura hexagonal definida.

#### Issue #2-3: Order & Work Order Management
**Estado:** ✅ Implementado en `app/routes/pedidos.py` y `app/routes/ordenes_trabajo.py`

#### Issue #4: Status Workflow
**Estado:** ✅ Bien implementado en `app/services/status_workflow.py` con máquina de estados correcta

#### Issue #5: Transactional Data Import
**Estado:** ✅ `app/services/phase3_import_service.py` y `app/commands/import_phase3.py`

#### Issue #6: Sample Entry UI
**Estado:** ⚠️ Brecha  

🟡 **Brecha 7 — Templates duplicados en entradas:**  
Existen `templates/entradas/form.html` Y `templates/entradas/form_mejorado.html`, y también `templates/entradas/listar.html` Y `templates/entradas/list_mejorado.html`. No está claro cuál es el activo, generando deuda de mantenimiento.

---

## Hallazgos Transversales (Todas las Fases)

🔴 **Brecha 8 — `tests/conftest.py` ausente:**  
Los tests en `tests/unit/` y `tests/integration/` no tienen `conftest.py` en la raíz de `tests/`. Sin este archivo, pytest no puede configurar la app de test, la base de datos en memoria, ni los fixtures compartidos. **Los tests no corren correctamente.**

🔴 **Brecha 9 — Directorio malformado `tests/unit/{clientes,muestras,ensayos}/`:**  
Existe un directorio con nombre literal `{clientes,muestras,ensayos}` (sintaxis bash glob usada accidentalmente como nombre de carpeta). Este directorio es inútil y confunde la estructura.

🟡 **Brecha 10 — Error handlers retornan JSON en contextos HTML:**  
En `app/__init__.py`, los handlers para `NotFoundError`, `ValidationError` y `DomainException` retornan `jsonify(...)`. Pero estas excepciones pueden ser lanzadas desde rutas que esperan renderizar páginas HTML, resultando en respuestas JSON inesperadas para el usuario final. Deberían detectar si la solicitud espera JSON o HTML.

---

## Plan de Correcciones Aplicadas

Las siguientes correcciones se aplican directamente al código:

| # | Brecha | Acción |
|---|--------|--------|
| 1 | Session timeout no configurado | Agregar `PERMANENT_SESSION_LIFETIME` y cookies seguras a configs |
| 2 | `_get_locale` ignora `?lang=` | Agregar lectura de `request.args.get('lang')` |
| 3 | Templates duplicados | Documentar canónicos (no se eliminan por seguridad) |
| 4 | `codigo` ausente en `ClienteForm` | Agregar campo `codigo` al formulario |
| 5 | Audit logging desconectado | Conectar `AuditLog.log_change()` en rutas de clientes |
| 6 | `sql_repository.py` eliminado | Recrear archivo de repositorio para clientes |
| 7 | Templates duplicados entradas | Documentar en comentarios el canónico |
| 8 | `tests/conftest.py` ausente | **Crear `conftest.py` completo** |
| 9 | Directorio malformado | Eliminar directorio `{clientes,muestras,ensayos}` |
| 10 | Error handlers solo JSON | Agregar detección content-type y render HTML |

---

*Auditoría generada automáticamente — DataLab Migration Project*
