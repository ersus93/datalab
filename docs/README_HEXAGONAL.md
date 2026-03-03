# 🏗️ Refactorización DataLab → Arquitectura Hexagonal

> Basado en [Issue #12](https://github.com/ersus93/datalab/issues/12) — Estrategia Híbrida (Opción B ⭐)

---

## 📁 Nueva Estructura

```
datalab/
├── app/
│   ├── __init__.py               ← App factory (registra features)
│   ├── config.py                 ← Configuraciones por entorno
│   │
│   ├── core/                     ← Shared Kernel (compartido entre features)
│   │   ├── domain/
│   │   │   └── base.py           ← Entity, Repository, DomainException, etc.
│   │   └── infrastructure/
│   │       └── database.py       ← SQLAlchemy db, BaseORM
│   │
│   └── features/                 ← Un directorio por dominio de negocio
│       ├── clientes/
│       │   ├── domain/
│       │   │   ├── models.py     ← Entidades puras (sin Flask/SQLAlchemy)
│       │   │   └── repositories.py ← Interfaces / Ports (ABC)
│       │   ├── application/
│       │   │   ├── commands.py   ← Casos de uso de escritura
│       │   │   ├── queries.py    ← Casos de uso de lectura
│       │   │   └── dtos.py       ← Data Transfer Objects
│       │   └── infrastructure/
│       │       ├── persistence/
│       │       │   └── sql_repository.py ← Adapter SQLAlchemy
│       │       └── web/
│       │           └── routes.py ← Adapter Flask (Blueprint)
│       │
│       ├── muestras/             ← Feature: Entradas/Muestras
│       ├── ensayos/              ← Feature: Ensayos FQ/MB/ES
│       ├── ordenes/              ← Feature: Órdenes de trabajo
│       └── reportes/             ← Feature: Informes oficiales
│
└── tests/
    ├── unit/
    │   ├── clientes/test_clientes.py   ← Tests SIN base de datos
    │   └── ensayos/test_ensayos.py
    └── integration/
```

---

## 🔄 Flujo de una petición (ejemplo: Crear Cliente)

```
HTTP POST /api/clientes
        ↓
[Flask Blueprint] routes.py       ← Adapter de entrada (Web)
        ↓  parsea JSON → Command
[CrearClienteHandler] commands.py ← Application (Caso de uso)
        ↓  llama al port
[ClienteRepository] repositories.py ← Port (interfaz ABC)
        ↑  implementado por
[SQLClienteRepository] sql_repository.py ← Adapter de salida (DB)
        ↓
SQLAlchemy → SQLite/PostgreSQL
```

---

## 🗺️ Plan de Migración (Estrategia Híbrida)

### Fase 1 — Preparación (Semana 1)
- [ ] Mover código actual a `app/legacy/`
- [ ] Instalar estructura de directorios hexagonal
- [ ] Configurar app factory en `app/__init__.py`
- [ ] Implementar `core/domain/base.py` y `core/infrastructure/database.py`

### Fase 2 — Feature Piloto: Clientes (Semana 1-2) ✅
- [x] `clientes/domain/models.py` — Entidad `Cliente`
- [x] `clientes/domain/repositories.py` — Port `ClienteRepository`
- [x] `clientes/application/dtos.py` — DTOs y Commands
- [x] `clientes/application/commands.py` — Handlers de escritura
- [x] `clientes/application/queries.py` — Queries de lectura
- [x] `clientes/infrastructure/persistence/sql_repository.py` — Adapter SQL
- [x] `clientes/infrastructure/web/routes.py` — Blueprint Flask
- [x] Tests unitarios sin BD real

### Fase 3 — Features Restantes (Semanas 2-4)
- [ ] Feature: **Muestras** (estructura creada, lógica pendiente)
- [ ] Feature: **Ensayos** FQ/MB/ES (domain listo, infrastructure pendiente)
- [ ] Feature: **Órdenes** de trabajo
- [ ] Feature: **Reportes** e informes

### Fase 4 — Migración desde Access (Semanas 4-8)
- [ ] Migrar cada una de las 22 tablas Access como features independientes
- [ ] Tests de integración por feature
- [ ] Eliminar `app/legacy/` cuando todo esté migrado

---

## 🧪 Ejecutar Tests

```bash
# Instalar dependencias
pip install pytest pytest-flask

# Correr todos los tests unitarios (sin BD)
pytest tests/unit/ -v

# Correr con cobertura
pytest tests/unit/ --cov=app/features --cov-report=html
```

---

## 💡 Principios de la Arquitectura

| Capa | Responsabilidad | Puede importar de |
|------|----------------|-------------------|
| `domain/` | Reglas de negocio puras | Solo Python stdlib |
| `application/` | Casos de uso, orquestación | `domain/` |
| `infrastructure/` | Flask, SQLAlchemy, APIs externas | `application/`, `domain/` |

### Regla de dependencias: **Todo apunta hacia el dominio**

```
infrastructure → application → domain
                                ↑
                          (núcleo puro)
```

---

## ✅ Ventajas obtenidas

1. **Tests rápidos** — Los tests de domain y application no necesitan BD
2. **Cambio de framework** — Cambiar Flask → FastAPI sin tocar `domain/`
3. **Migración Access progresiva** — Feature por feature, sin big bang
4. **Trabajo paralelo** — Dev A en Clientes, Dev B en Ensayos (sin conflictos)
5. **Reglas de negocio centralizadas** — Validaciones en `domain/models.py`
