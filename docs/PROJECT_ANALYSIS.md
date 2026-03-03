# Project Analysis - DataLab

## Project Overview

**DataLab** is a web-based management system designed for the **Food Chemistry Laboratory of ONIE** (Oficina Nacional de Inspección Estatal). It's a Flask application that facilitates the management of food chemical analysis and technical report generation.

---

## Technical Architecture

| Component | Technology |
|-----------|------------|
| **Framework** | Flask 3.0.0 |
| **ORM** | SQLAlchemy 2.0.35 |
| **Database** | SQLite (development) / PostgreSQL (production) |
| **Frontend** | Jinja2 Templates + Vanilla CSS + JavaScript |
| **Migrations** | Flask-Migrate |
| **Visualization** | Plotly 5.17.0 |
| **Architecture** | Hexagonal Architecture (Ports & Adapters) |

### Architecture Overview

The project follows **Hexagonal Architecture** (also known as Ports and Adapters) combined with **Clean Architecture** principles:

- **Domain Layer**: Pure Python entities with no framework dependencies
- **Application Layer**: Use cases, DTOs, commands/queries with business logic
- **Infrastructure Layer**: Flask routes, SQLAlchemy repositories, external adapters

**Dependency Direction**: Infrastructure → Application → Domain (inward dependencies only)

See [Hexagonal Architecture Implementation](#hexagonal-architecture-implementation) for detailed documentation.

---

## Project Structure

```
datalab/
├── app/                     # Main application
│   ├── core/                # Shared Kernel
│   │   ├── domain/          # Entity, Repository ABC, AuditMixin
│   │   └── infrastructure/  # Database adapters (SQLAlchemy)
│   ├── features/            # Business domains
│   │   ├── clientes/        # Feature: Clientes
│   │   │   ├── domain/      # models.py (pure Python)
│   │   │   ├── application/ # commands.py, queries.py, dtos.py
│   │   │   └── infrastructure/ # sql_repository.py, routes.py
│   │   └── muestras/        # Feature: Muestras (structure created)
│   ├── routes/              # Legacy blueprints (migration in progress)
│   ├── services/            # Legacy services (migration in progress)
│   ├── static/              # CSS, JS, images
│   ├── templates/           # Jinja2 templates
│   └── utils/               # Utilities
├── config/                  # Flask configuration
└── docs/                    # Documentation
```

**Note:** The old structure with `app/database/models.py` is being migrated to the feature-based hexagonal structure.

---

## Current Data Models

### 1. Cliente
Client management with unique code, contact, address.

### 2. Pedido
Work orders linked to clients.  
**Status values:** `pendiente` | `en_proceso` | `completado`

### 3. OrdenTrabajo
Specific work orders with analysis type, priority, dates.

### 4. SystemConfig
General system configuration.

### Relationships
```
Cliente 1:N Pedidos
    Pedido 1:N Órdenes de Trabajo
```

---

## Current Status

### ✅ Implemented

- Base project structure with Flask
- Fundamental database models
- Basic blueprints and routes
- Base templates with sidebar, header, modals
- Dashboard with static metrics
- Global search system (UI)
- Orders page (in development)
- Modular CSS with variables, reusable components

### 🚧 In Progress

- Fix visual errors on initial page
- Structure refactoring
- Main and dashboard styles
- Orders page

### ❌ Missing

- Authentication/Authorization (no users or login)
- Complete CRUD API
- PDF report generation
- Chemical analysis/test management
- Notifications
- Tests
- All reference tables from Access (areas, organisms, UTEs, etc.)
- Factory (Fabrica) management
- Product catalog
- Test catalogs (Ensayos, EnsayosES)
- Entry/sample tracking system
- Test assignment workflow
- Usage/billing tracking
- Official report generation workflow
- All reference tables from Access (areas, organisms, UTEs, etc.)
- Factory (Fabrica) management
- Product catalog
- Test catalogs (Ensayos, EnsayosES)
- Entry/sample tracking system
- Test assignment workflow
- Usage/billing tracking
- Official report generation workflow

---

## Recommended Next Phases

### Phase 1: Foundations

- [ ] Authentication system (login/logout)
- [ ] User profiles (admin, technician, client)
- [ ] Complete CRUD for clients, orders, and work orders

### Phase 2: Core Functionality

- [ ] Test/analysis management
- [ ] PDF report generation
- [ ] Laboratory workflow

### Phase 3: Optimization

- [ ] Dashboard with real data
- [ ] Advanced search
- [ ] Data export

---

## Access Database Analysis

### System Overview
- Application: RM2026 Laboratory Management System
- Platform: Microsoft Access (accdb format)
- Architecture: Frontend/Backend split
- Database Size: 10MB total (6.2MB frontend, 3.8MB backend)

### Data Volume Summary
| Category | Tables | Records | Priority |
|----------|--------|---------|----------|
| Reference Data | 9 | 73 | High |
| Master Data | 3 | 729 | High |
| Test Catalogs | 3 | 172 | High |
| Transactions | 5 | 1,260 | High |
| Reports | 5 | 20 | Low |

### Entity Relationships
```
Clientes (166) 1:N Fabricas (403)
Clientes (166) 1:N Pedidos (49)
Pedidos (49) 1:N Entradas (109)
Entradas (109) 1:N Detalles de ensayos (563)
Entradas (109) 1:1 Utilizado R (632)
Productos (160) linked to Entradas
Ensayos (143) linked to Detalles
```

### Key Findings
1. Well-structured relational database
2. Clear separation of concerns (reference, master, transaction data)
3. Multi-area laboratory support (FQ, MB, ES)
4. Billing/usage tracking with archived records
5. Official report generation workflow
6. Lot and part number tracking

### Gaps in Current Web Implementation
1. ❌ Missing all reference tables
2. ❌ Missing factory model
3. ❌ Missing product catalog
4. ❌ Missing test catalogs (Ensayos, EnsayosES)
5. ❌ Missing entry/sample tracking
6. ❌ Missing test assignment (Detalles)
7. ❌ Missing usage/billing tracking
8. ❌ Missing report generation
9. ❌ Missing authentication

---

## Hexagonal Architecture Implementation

The project has adopted **Hexagonal Architecture** (Ports & Adapters) combined with **Clean Architecture** principles to achieve:
- **Testability**: Business logic isolated from frameworks
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy to swap adapters (e.g., SQLite ↔ PostgreSQL)

### The Three Layers

#### 1. Domain Layer (Innermost)
- **Pure Python entities** with no framework dependencies
- **Repository interfaces** (abstract base classes)
- **Domain events** and business rules
- Location: `features/{feature}/domain/`
- Example: `Cliente` entity with validation logic

#### 2. Application Layer (Middle)
- **Use cases** (Commands and Queries)
- **DTOs** for data transfer
- **Application services** orchestrating domain objects
- Location: `features/{feature}/application/`
- Examples: `CrearClienteCommand`, `ListarClientesQuery`, `ClienteDTO`

#### 3. Infrastructure Layer (Outermost)
- **Adapters** implementing domain interfaces
- **Flask routes** (HTTP adapters)
- **SQLAlchemy repositories** (database adapters)
- **External service integrations**
- Location: `features/{feature}/infrastructure/`
- Examples: `ClienteSQLRepository`, `clientes_bp` routes

### Dependency Rule
Dependencies point **inward only**:
```
Infrastructure → Application → Domain
     (Flask)        (Use Cases)   (Entities)
```

### Detailed Project Structure

```
app/
├── core/                    # Shared Kernel
│   ├── domain/
│   │   ├── base.py          # Entity base class, Repository ABC
│   │   └── audit.py         # AuditMixin for created_at/updated_at
│   └── infrastructure/
│       └── db.py            # SQLAlchemy adapters
├── features/                # Business domains
│   ├── clientes/            # ✅ Feature piloto (complete)
│   │   ├── domain/
│   │   │   └── models.py    # Cliente entity (pure Python)
│   │   ├── application/
│   │   │   ├── commands.py  # CrearClienteCommand
│   │   │   ├── queries.py   # ListarClientesQuery
│   │   │   └── dtos.py      # ClienteDTO
│   │   └── infrastructure/
│   │       ├── sql_repository.py  # SQLAlchemy adapter
│   │       └── routes.py          # Flask blueprint
│   ├── muestras/            # 🟡 Structure created
│   ├── ensayos/             # 🟡 Structure created
│   ├── ordenes/             # 🟡 Structure created
│   └── reportes/            # 🟡 Structure created
└── config.py
```

### Migration Strategy

The migration from the old structure follows a **feature-by-feature** approach:

1. **Each Access table** becomes a domain feature
2. **Clientes feature** is the completed pilot demonstrating the pattern
3. **Other features** have directory structure created and need implementation
4. **Legacy code** in `app/routes/` and `app/services/` will be gradually migrated

### Feature Status

| Feature | Domain | Application | Infrastructure | Status |
|---------|--------|-------------|----------------|--------|
| Clientes | ✅ Models | ✅ Commands/Queries/DTOs | ✅ Repository + Routes | ✅ Complete |
| Muestras | 🟡 Empty | 🟡 Empty | 🟡 Empty | 🟡 Structure only |
| Ensayos | 🟡 Empty | 🟡 Empty | 🟡 Empty | 🟡 Structure only |
| Ordenes | 🟡 Empty | 🟡 Empty | 🟡 Empty | 🟡 Structure only |
| Reportes | 🟡 Empty | 🟡 Empty | 🟡 Empty | 🟡 Structure only |

### Recommended Model Updates

The current Flask models (Cliente, Pedido, OrdenTrabajo) are being migrated to the hexagonal structure. Each Access table will become a feature that needs:
- Add all reference tables
- Add Fabrica model
- Add Producto model
- Add Ensayo and EnsayoES models
- Expand Entrada model with all fields
- Add DetalleEnsayo model
- Add Utilizado model
- Add Informe model

### Migration Complexity Assessment
- **Low**: Reference tables (simple lookup data)
- **Medium**: Master data (clients, factories, products)
- **High**: Transactions (entries, test details, usage)
- **Critical**: Ensuring FK integrity during migration

### Next Steps for Architecture Rollout
1. Implement remaining features following the Clientes pattern
2. Migrate legacy routes to infrastructure layer
3. Add comprehensive tests for domain layer
4. Implement integration tests for infrastructure adapters
