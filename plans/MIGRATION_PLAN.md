# DataLab Access to Web Migration Plan
## Laboratory Information Management System (LIMS) Feature-Based Migration Strategy

**Migration Date:** March 2026  
**Estimated Duration:** 14 Weeks  
**Target Go-Live:** June 2026  
**Databases:** RM2026.accdb (Frontend) + RM2026_be.accdb (Backend)  
**Total Records:** ~2,632 rows across 25 tables

---

## Executive Summary

This migration plan outlines the complete transition of the Access-based RM2026 laboratory management system to a modern web-based DataLab application. The migration follows a **Feature-based approach** to minimize risk and ensure business continuity, delivering value incrementally with each feature.

**Current State:**
- Split Access architecture (frontend + backend)
- 25 tables, ~2,632 records
- 18 Access queries for reporting
- Multi-area laboratory (FQ, MB, ES, OS)

**Target State:**
- Web-based Flask application
- PostgreSQL database
- Modern UI with real-time dashboards
- Advanced reporting and analytics
- Multi-user concurrent access

**Migration Strategy:**
- Feature-based incremental delivery
- Each Access table → One Domain Feature
- Dependencies mapped and respected
- Pilot feature (Clientes) completed successfully

---

## Feature Dependency Map

The system is organized into independent and dependent features based on domain relationships:

```
Reference Data (independent)
├── areas (4 rows)              → All features
├── organismos (12 rows)        → Clientes
├── provincias (4 rows)         → Fabricas
├── destinos (7 rows)           → Productos
├── ramas (13 rows)             → Productos
├── meses (12 rows)             → Ordenes, Entradas, Informes
├── annos (10 rows)             → Ordenes, Entradas, Informes
├── unidades_medida (3 rows)    → Ensayos
└── tipo_es (4 rows)            → EnsayosES

Master Data (depends on Reference Data)
├── Clientes (166 rows)         → Depends on organismos
│   └── Factory → Clientes
└── Productos (160 rows)        → Depends on ramas, destinos

Test Catalogs (depends on Reference Data)
├── Ensayos (143 rows)          → Depends on areas
└── EnsayosES (29 rows)         → Depends on areas, tipo_es

Transactional Data (depends on Master Data & Test Catalogs)
├── Ordenes de Trabajo (37 rows) → Depends on clientes
├── Pedidos (49 rows)            → Depends on clientes, productos, OT
├── Entradas (109 rows)          → Depends on pedidos, fabricas, productos
├── Detalles de Ensayos (563 rows) → Depends on entradas, ensayos
├── Utilizado (632 rows)         → Depends on entradas, ensayos
└── Informes (20 rows)           → Depends on entradas
```

### Feature Dependency Matrix

| Feature | Dependencies | Dependents |
|---------|--------------|------------|
| Areas | None | All features |
| Clientes | organismos, areas | Fabricas, Pedidos, Ordenes, Entradas |
| Fabricas | clientes, provincias | Entradas |
| Productos | ramas, destinos | Pedidos, Entradas |
| Ensayos | areas, unidades_medida | Detalles de Ensayos |
| EnsayosES | areas, tipo_es | Detalles de Ensayos |
| Ordenes de Trabajo | clientes | Pedidos |
| Pedidos | clientes, productos, ordenes | Entradas |
| Entradas | pedidos, fabricas, productos | Detalles de Ensayos, Informes |
| Detalles de Ensayos | entradas, ensayos | Utilizado, Informes |
| Utilizado | entradas, ensayos, detalles_ensayos | Reports |
| Informes | entradas, detalles_ensayos | Reports |

---

## Migration Phases Overview

| Phase | Duration | Feature | Status | Focus Area |
|-------|----------|---------|--------|------------|
| Phase 1 | Weeks 1-2 | Core Infrastructure + Reference Data | ✅ Complete | Foundation & Schema |
| Phase 2 | Weeks 3-4 | Clientes Feature | ✅ Completed Pilot | CRUD + Data Migration |
| Phase 3 | Weeks 5-6 | Muestras Feature | 🔄 Pending | Sample Management |
| Phase 4 | Weeks 7-8 | Ensayos Feature | 📋 Pending | Test Management |
| Phase 5 | Weeks 9-10 | Ordenes y Reportes | 📋 Pending | Orders & Reports |
| Phase 6 | Weeks 11-12 | Data Migration from Access | 📋 Pending | Per-feature migration |
| Phase 7 | Weeks 13-14 | Testing & Go-Live | 📋 Pending | UAT & Production |

---

## Phase 1: Core Infrastructure + Reference Data (Weeks 1-2)

**Priority:** CRITICAL  
**Status:** ✅ Complete  
**Success Criteria:** Database schema deployed, reference data migrated, basic connectivity verified

### 1.1 Database Schema Creation

#### Week 1: Schema Design & Implementation
| Task | Duration | Owner | Deliverable |
|------|----------|-------|-------------|
| Create PostgreSQL database | 1 day | DBA | Empty database |
| Implement reference tables | 2 days | Backend | 9 reference tables |
| Create foreign key relationships | 1 day | Backend | Complete FK graph |
| Add indexes and constraints | 1 day | DBA | Optimized schema |
| Implement audit trail tables | 1 day | Backend | Audit logging schema |
| Create migration scripts | 2 days | DBA | Automated migration tools |

**Reference Tables Created:**
```sql
-- Priority: HIGH (Load First)
areas (4 rows)           - Laboratory areas (FQ, MB, ES, OS)
organismos (12 rows)     - Client organizations
provincias (4 rows)      - Geographic regions
destinos (7 rows)        - Product destinations
ramas (13 rows)          - Industry sectors
meses (12 rows)          - Calendar months
annos (10 rows)          - Active years
unidades_medida (3 rows) - Measurement units
tipo_es (4 rows)         - Sensory evaluation types
```

### 1.2 Data Migration - Phase 1

**Migration Order:**
1. Reference data (78 rows total)
2. Verify row counts and FK integrity

**Validation Checkpoints:**
- [x] All 9 reference tables loaded
- [x] Foreign key relationships validated
- [x] Indexes created

### 1.3 Success Criteria
| Criteria | Target | Status |
|----------|--------|--------|
| Schema deployment | 100% | ✅ Complete |
| Data accuracy | 100% | ✅ Row count match |
| FK integrity | 100% | ✅ No orphaned records |
| Query performance | <100ms | ✅ Standard queries |

---

## Phase 2: Clientes Feature (Weeks 3-4)

**Priority:** HIGH  
**Status:** ✅ Completed (Pilot Feature)  
**Success Criteria:** Full CRUD for clients, factories; user authentication working; domain-driven architecture established

### 2.1 Feature Implementation Pattern Established

The Clientes feature established the implementation pattern for all subsequent features:

```
Clientes Feature Structure:
├── domain/
│   ├── models.py          - Cliente, Fabrica entities with validation
│   ├── repositories.py    - ClienteRepository, FabricaRepository (ports)
│   └── exceptions.py      - Domain-specific exceptions
├── application/
│   ├── dtos.py           - ClienteDTO, FabricaDTO, ClienteListDTO
│   ├── commands.py       - CreateClienteCommand, UpdateClienteCommand
│   └── queries.py        - ListClientesQuery, GetClienteByIdQuery
├── infrastructure/
│   └── persistence/
│       └── sql_repository.py - SQLClienteRepository, SQLFabricaRepository
│   └── web/
│       └── routes.py     - Flask routes for clientes, fabricas
└── tests/
    ├── unit/             - Domain tests (no DB)
    └── integration/      - Repository tests (with DB)
```

### 2.2 Clientes Domain

**Entities:**
```python
# domain/models.py
class Cliente:
    id: int
    nombre: str
    organismo_id: int
    tipo_cliente: int
    activo: bool
    fabricas: List[Fabrica]

class Fabrica:
    id: int
    nombre: str
    cliente_id: int
    provincia_id: int
    direccion: Optional[str]
```

**Repository Port:**
```python
# domain/repositories.py
class ClienteRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Cliente]: ...
    @abstractmethod
    def list_all(self) -> List[Cliente]: ...
    @abstractmethod
    def save(self, cliente: Cliente) -> Cliente: ...
    @abstractmethod
    def delete(self, id: int) -> bool: ...
```

### 2.3 Data Migration - Clientes Feature

**Master Data Migration:**
| Table | Rows | Migration Method | Validation |
|-------|------|------------------|------------|
| clientes | 166 | CSV export/import | Row count + sample validation |
| fabricas | 403 | CSV export/import | FK to clientes verified |

**Migration Statistics:**
- Total: 569 records (166 clients + 403 factories)
- Average factories per client: 2.4
- By province: Distribution maintained

### 2.4 User Authentication System

| Component | Implementation | Priority | Status |
|-----------|----------------|----------|--------|
| User Model | Flask-Login + SQLAlchemy | HIGH | ✅ Complete |
| Login/Logout | Session-based auth | HIGH | ✅ Complete |
| Role Management | Admin, Technician, Client | HIGH | ✅ Complete |
| Password Security | Bcrypt hashing | CRITICAL | ✅ Complete |

**User Roles:**
- **Admin:** Full system access
- **Technician:** Test execution, result entry
- **Client:** View own data, reports only

### 2.5 Success Criteria
| Criteria | Target | Status |
|----------|--------|--------|
| CRUD operations | 100% | ✅ All features working |
| Data migration | 100% | ✅ 569 records migrated |
| Authentication | 100% | ✅ Login/logout functional |
| UI responsiveness | <2s | ✅ Page load time |
| Architecture pattern | Established | ✅ DDD pattern ready |

---

## Phase 3: Muestras Feature (Weeks 5-6)

**Priority:** HIGH  
**Status:** 📋 Pending  
**Success Criteria:** Sample entry workflow complete, balance tracking accurate, all transactional entities for sample management working

### 3.1 Feature Scope

The Muestras feature includes:
- Productos (160 records) - Product catalog
- Ordenes de Trabajo (37 records) - Work orders
- Pedidos (49 records) - Orders
- Entradas (109 records) - Sample entries (CORE ENTITY)

### 3.2 Productos Domain

**Entity:**
```python
class Producto:
    id: int
    nombre: str
    rama_id: int
    destino_id: int
    unidad_medida_id: int
    activo: bool
```

### 3.3 Ordenes de Trabajo Domain

**Entity:**
```python
class OrdenTrabajo:
    id: int
    cliente_id: int
    numero_oficial: str
    fecha_ot: date
    anno: str
    completada: bool
    anulada: bool
```

### 3.4 Pedidos Domain

**Entity:**
```python
class Pedido:
    id: int
    cliente_id: int
    orden_trabajo_id: Optional[int]
    producto_id: int
    fecha_solicitud: date
    cantidad_solicitada: int
    lote: str           # Format: X-XXXX
    fecha_fabricacion: Optional[date]
    fecha_vencimiento: Optional[date]
```

### 3.5 Entradas Domain (Core Entity)

**Entity:**
```python
class Entrada:
    id: int
    pedido_id: int
    fabrica_id: int
    producto_id: int
    fecha_entrada: date
    numero_oficial: str
    anno: str
    mes: int
    lote: str               # Format: X-XXXX
    numero_parte: int
    fecha_fabricacion: date
    fecha_vencimiento: date
    fecha_muestreo: date
    cantidad_recibida: int
    cantidad_entregada: int
    saldo: int              # Calculated: CantidadRecib - CantidadEntreg
    en_orden_servicio: bool
    anulado: bool
    rama_id: int
    otra_rama: Optional[str]
    entrada_entregada: bool
    provincia_id: int

    def calcular_saldo(self) -> int:
        return self.cantidad_recibida - self.cantidad_entregada
```

### 3.6 Sample Status Workflow
```
[Received] → [In Process] → [Completed] → [Delivered]
     ↓              ↓              ↓             ↓
  Balance       Assigned      Results      Saldo=0
  Created       Tests         Recorded     EntryEntregada=True
```

**Status Tracking:**
- `EnOS`: In Work Order (Boolean)
- `Anulado`: Cancelled (Boolean)
- `EntEntregada`: Entry Delivered (Boolean)
- `Saldo`: Balance calculation

### 3.7 Data Migration - Muestras Feature

**Master Data:**
| Table | Rows | Dependencies | Priority |
|-------|------|--------------|----------|
| productos | 160 | ramas, destinos | HIGH |

**Transactional Data:**
| Table | Rows | Dependencies | Priority |
|-------|------|--------------|----------|
| ordenes_trabajo | 37 | clientes | HIGH |
| pedidos | 49 | clientes, productos, OT | HIGH |
| entradas | 109 | pedidos, fabricas, productos | CRITICAL |

**Migration Validation:**
- [ ] All 37 work orders migrated
- [ ] All 49 orders with proper FKs
- [ ] All 109 entries with balance calculations verified
- [ ] Lot numbers preserved (X-XXXX format)
- [ ] Date fields converted properly

### 3.8 Implementation Tasks

| Week | Task | Duration | Owner |
|------|------|----------|-------|
| 5 | Productos CRUD | 2 days | Backend |
| 5 | Ordenes de Trabajo CRUD | 2 days | Backend |
| 5 | Pedidos CRUD | 1 day | Backend |
| 6 | Entradas CRUD + Balance calc | 3 days | Backend |
| 6 | Sample entry workflow UI | 2 days | Frontend |

### 3.9 Success Criteria
| Criteria | Target |
|----------|--------|
| Entry workflow | 100% End-to-end functional |
| Balance accuracy | 100% Calculations verified |
| Lot tracking | 100% Format preserved |
| Data migration | 100% 355 records migrated |

---

## Phase 4: Ensayos Feature (Weeks 7-8)

**Priority:** HIGH  
**Status:** 📋 Pending  
**Success Criteria:** Test assignment working, result recording functional, all test catalogs migrated

### 4.1 Feature Scope

The Ensayos feature includes:
- Ensayos (143 records) - Physical-chemical tests (FQ area)
- EnsayosES (29 records) - Sensory evaluation tests (ES area)
- Detalles de Ensayos (563 records) - Test assignments
- Utilizado (632 records) - Usage/billing records

### 4.2 Ensayos Domain (FQ Tests)

**Entity:**
```python
class Ensayo:
    id: int
    nombre_oficial: str
    nombre_corto: str
    area_id: int          # =1 (FQ)
    precio: Decimal
    unidad_medida: str
    activo: bool
    es_ensayo: bool
```

### 4.3 EnsayosES Domain (Sensory Tests)

**Entity:**
```python
class EnsayoES:
    id: int
    nombre_oficial: str
    nombre_corto: str
    area_id: int          # =3 (ES)
    tipo_es_id: int
    precio: Decimal
    unidad_medida: str
    activo: bool
```

### 4.4 Detalles de Ensayos Domain

**Entity:**
```python
class DetalleEnsayo:
    id: int
    entrada_id: int
    ensayo_id: Optional[int]       # For FQ tests
    ensayo_es_id: Optional[int]    # For ES tests
    cantidad: int
    fecha_realizacion: Optional[date]
    estado: str                     # pendiente | en_proceso | completado

class DetalleEnsayoEnsayoES:
    id: int
    entrada_id: int
    ensayo_es_id: int
    tipo_ensayo_id: int
    cantidad: int
    fecha_realizacion: Optional[date]
```

### 4.5 Area-Specific Test Views

| Area | Table | Tests | View Name |
|------|-------|-------|-----------|
| Físico-Químico | Ensayos | 143 | Análisis FQ |
| Microbiología | Ensayos | Subset | Análisis MB |
| Evaluación Sensorial | EnsayosES | 29 | Análisis ES |
| Otros Servicios | Ensayos | Subset | Otros |

### 4.6 Test Execution Tracking

**Test States:**
```
Pendiente → Asignado → En Proceso → Completado → Reportado
    ↓            ↓           ↓            ↓            ↓
   New      Scheduled   In Lab      Results      Official
                               Entered       Report
```

### 4.7 Utilizado Domain (Billing)

**Entity:**
```python
class Utilizado:
    id: int
    entrada_id: int
    ensayo_id: int
    cantidad: int
    fecha: date
    hora: time
    precio: Decimal
    importe: Decimal      # cantidad * precio
    unidad_medida: str
    anno: str
```

### 4.8 Data Migration - Ensayos Feature

**Test Catalogs:**
| Table | Rows | Dependencies | Priority |
|-------|------|--------------|----------|
| ensayos | 143 | areas, unidades_medida | HIGH |
| ensayos_es | 29 | areas, tipo_es | HIGH |

**Transactional Data:**
| Table | Rows | Dependencies | Priority |
|-------|------|--------------|----------|
| detalles_ensayos | 563 | entradas, ensayos | HIGH |
| utilizado_r | 632 | entradas, ensayos | MEDIUM |

### 4.9 Implementation Tasks

| Week | Task | Duration | Owner |
|------|------|----------|-------|
| 7 | Ensayos CRUD | 2 days | Backend |
| 7 | EnsayosES CRUD | 1 day | Backend |
| 7 | Detalles de Ensayos CRUD | 2 days | Backend |
| 8 | Utilizado CRUD + Billing | 2 days | Backend |
| 8 | Test assignment UI | 2 days | Frontend |

### 4.10 Success Criteria
| Criteria | Target |
|----------|--------|
| Test assignment | 100% All 563 migrated |
| Area filtering | 100% 4 areas working |
| Result recording | 100% Functional |
| Billing accuracy | 100% Calculations verified |
| Usage migration | 100% 632 records migrated |

---

## Phase 5: Ordenes y Reportes (Weeks 9-10)

**Priority:** MEDIUM  
**Status:** 📋 Pending  
**Success Criteria:** Reports generating, billing calculations accurate, informes workflow complete

### 5.1 Feature Scope

The Ordenes y Reportes feature includes:
- Informes (20 records) - Official reports
- Report generation system
- PDF generation
- Analytics dashboards

### 5.2 Informes Domain

**Entity:**
```python
class Informe:
    id: int
    entrada_id: int
    fecha: date
    numero_oficial: str
    anno: str
    ensayos: List[DetalleEnsayo]
```

### 5.3 Reports Module

**Current Access Queries to Migrate:**

| Access Query | Web Implementation | Priority |
|--------------|-------------------|----------|
| Analisis a realizar ES | Pending sensory tests view | HIGH |
| Analisis a realizar FQ | Pending FQ tests view | HIGH |
| Analisis a realizar MB | Pending microbiology tests view | HIGH |
| Determinaciones realizadas | Completed tests report | HIGH |
| Lotes Analizados | Analyzed batches report | MEDIUM |
| Muestreos por tipo de cliente | Client type analytics | MEDIUM |

### 5.4 Analytics Dashboards

**Key Metrics:**
| Metric | Source | Visualization |
|--------|--------|---------------|
| Samples per month | Entradas | Line chart |
| Tests by area | Detalles de ensayos | Pie chart |
| Client activity | Utilizado | Bar chart |
| Pending tests | Detalles de ensayos | Counter |
| Revenue by period | Utilizado | Area chart |
| Top clients | Pedidos | Table |

### 5.5 PDF Generation

**Templates:**
- Official report template (Informe Oficial)
- Usage consultation report
- Statistical summaries

**Technology:**
- WeasyPrint or ReportLab
- HTML/CSS templates
- Header/footer with lab info

### 5.6 Data Migration - Ordenes y Reportes

| Table | Rows | Dependencies | Priority |
|-------|------|--------------|----------|
| informes | 20 | entradas, detalles_ensayos | MEDIUM |

### 5.7 Implementation Tasks

| Week | Task | Duration | Owner |
|------|------|----------|-------|
| 9 | Informes CRUD | 2 days | Backend |
| 9 | Report templates | 2 days | Backend |
| 9 | PDF generation | 1 day | Backend |
| 10 | Analytics dashboards | 3 days | Frontend |
| 10 | Billing reports | 2 days | Backend |

### 5.8 Success Criteria
| Criteria | Target |
|----------|--------|
| Report generation | 100% All templates working |
| Billing accuracy | 100% Calculations verified |
| PDF quality | High Professional format |
| Dashboard metrics | 6+ Key metrics displayed |

---

## Phase 6: Data Migration from Access (Weeks 11-12)

**Priority:** MEDIUM  
**Status:** 📋 Pending  
**Success Criteria:** All historical data migrated, validation scripts passing, row counts matching

### 6.1 Per-Feature Data Migration

Data migration is performed incrementally as each feature is completed:

| Feature | Tables | Records | Migration Method |
|---------|--------|---------|------------------|
| Phase 1: Reference Data | 9 tables | 78 | CSV Export/Import |
| Phase 2: Clientes | 2 tables | 569 | CSV Export/Import |
| Phase 3: Muestras | 4 tables | 355 | CSV Export/Import |
| Phase 4: Ensayos | 4 tables | 1,367 | CSV Export/Import |
| Phase 5: Ordenes y Reportes | 1 table | 20 | CSV Export/Import |
| **Total** | **20 tables** | **2,389** | **Per-feature** |

*Note: 25 total tables - 5 intermediate/junction tables counted within features*

### 6.2 Migration Timeline

| Feature | Migration Days | Testing Days | Total |
|---------|---------------|--------------|-------|
| Reference Data | 1 | 1 | 2 |
| Clientes | 1 | 1 | 2 |
| Muestras | 2 | 1 | 3 |
| Ensayos | 2 | 1 | 3 |
| Ordenes y Reportes | 1 | 1 | 2 |
| **Total** | **7** | **5** | **12** |

### 6.3 Migration Methods

**Method 1: CSV Export/Import**
- Best for: Reference data, master data, transactional data
- Tools: Access export → Python script → PostgreSQL
- Validation: Row count, FK integrity

**Method 2: Direct Database Connection**
- Best for: Complex relationships requiring transformation
- Tools: pyodbc → SQLAlchemy
- Validation: Real-time during migration

**Method 3: API Migration**
- Best for: Transactional data with business logic
- Tools: Custom API endpoints
- Validation: Business logic validation

### 6.4 Verification Steps

1. **Row Count Matching**
   ```sql
   -- Compare source and target counts
   SELECT 'clientes' as table_name, COUNT(*) as count FROM clientes
   UNION ALL
   SELECT 'fabricas', COUNT(*) FROM fabricas
   -- etc.
   ```

2. **Foreign Key Validation**
   ```sql
   -- Check for orphaned records
   SELECT e.* FROM entradas e
   LEFT JOIN clientes c ON e.cliente_id = c.id
   WHERE c.id IS NULL;
   ```

3. **Data Sampling**
   - Random sample 10% of each table
   - Manual verification of accuracy
   - Check critical fields

### 6.5 Migration Scripts

```python
# migration_toolkit.py
class AccessToPostgresMigration:
    def migrate_feature(self, feature_name: str, tables: List[str]):
        """Migrate all tables for a feature"""
        pass
    
    def validate_migration(self, table: str) -> MigrationResult:
        """Validate row counts and FK integrity"""
        pass
    
    def rollback_feature(self, feature_name: str):
        """Rollback a feature migration"""
        pass
```

---

## Phase 7: Testing & Go-Live (Weeks 13-14)

**Priority:** CRITICAL  
**Status:** 📋 Pending  
**Success Criteria:** All tests passing, users trained, Access retired

### 7.1 Testing Phase

#### Week 13: Validation & Verification

**Data Validation:**
| Check | Method | Target |
|-------|--------|--------|
| Row count matching | Automated script | 100% match |
| FK integrity | Database constraints | 0 orphans |
| Data accuracy | Sampling | 95%+ accurate |
| Calculation accuracy | Unit tests | 100% correct |

**User Acceptance Testing (UAT) - Per Feature:**
| Feature | Test Scenario | Users | Duration |
|---------|---------------|-------|----------|
| Clientes | Client CRUD, factory management | 2 technicians | 1 day |
| Muestras | Sample entry workflow | 3 technicians | 2 days |
| Ensayos | Test execution | 2 analysts | 2 days |
| Ordenes y Reportes | Report generation | 1 admin | 1 day |
| Client Portal | View own data, reports | 2 clients | 1 day |

**Parallel Running:**
- Run both Access and web system simultaneously
- Compare outputs daily
- Log discrepancies
- Fix issues immediately

#### Week 13: Performance Testing

**Load Testing:**
| Metric | Target | Test |
|--------|--------|------|
| Concurrent users | 20 | Load test |
| Page load time | <2s | All pages |
| Report generation | <5s | Standard reports |
| Search response | <1s | Global search |

### 7.2 Go-Live Phase

#### Week 14: Final Migration

**Pre-Go-Live Checklist:**
- [ ] All data validated
- [ ] UAT passed
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] Training completed
- [ ] Backup verified
- [ ] Rollback plan ready

**Go-Live Steps:**
| Step | Duration | Action |
|------|----------|--------|
| 1. Final sync | 4 hours | Migrate latest data |
| 2. Verification | 2 hours | Validate final data |
| 3. DNS switch | 30 min | Point to new system |
| 4. Smoke test | 1 hour | Critical path test |
| 5. Monitoring | 24 hours | Watch for issues |

**Post Go-Live:**
- Access system in read-only mode for 1 week
- Daily check-ins with users
- Issue tracking and resolution
- Performance monitoring

### 7.3 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| Data validation | 100% | All checks passed |
| UAT completion | 100% | All scenarios passed |
| User training | 100% | All users trained |
| System availability | 99.5% | Uptime target |
| Issue resolution | <24h | Average fix time |

---

## Feature Implementation Pattern

For each feature, the implementation follows this architecture:

```
1. domain/models.py      - Entity with validation
2. domain/repositories.py - Port (interface)
3. application/dtos.py    - Input/output DTOs
4. application/commands.py - Write use cases
5. application/queries.py  - Read use cases
6. infrastructure/persistence/sql_repository.py - Adapter
7. infrastructure/web/routes.py - Flask adapter
8. tests/unit/ - Domain tests (no DB)
9. tests/integration/ - Repository tests (with DB)
```

### Example: Clientes Feature

```python
# 1. domain/models.py
@dataclass
class Cliente:
    id: int
    nombre: str
    organismo_id: int
    tipo_cliente: int
    activo: bool = True

# 2. domain/repositories.py
class ClienteRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Cliente]: ...
    @abstractmethod
    def save(self, cliente: Cliente) -> Cliente: ...

# 3. application/dtos.py
@dataclass
class ClienteDTO:
    id: int
    nombre: str
    organismo_nombre: str

# 4. application/commands.py
class CreateClienteCommand:
    nombre: str
    organismo_id: int
    tipo_cliente: int

# 5. application/queries.py
class ListClientesQuery:
    def execute(self) -> List[ClienteDTO]: ...

# 6. infrastructure/persistence/sql_repository.py
class SQLClienteRepository(ClienteRepository):
    def get_by_id(self, id: int) -> Optional[Cliente]:
        # SQLAlchemy implementation
        pass

# 7. infrastructure/web/routes.py
@app.route('/clientes', methods=['GET'])
def list_clientes():
    query = ListClientesQuery()
    return jsonify(query.execute())
```

---

## Updated Timeline

### Revised Estimates (Based on Pilot)

| Feature | Duration | Estimation Basis |
|---------|----------|------------------|
| Feature pilot (Clientes) | 1 week | ✅ Actual |
| Each additional feature | 3-5 days | 2x pilot efficiency |
| Data migration per feature | 1-2 days | Validated approach |
| Testing per feature | 1 day | Parallel with dev |

### Detailed Timeline

| Week | Phase | Feature | Key Activities | Deliverables |
|------|-------|---------|----------------|--------------|
| 1-2 | 1 | Reference Data | PostgreSQL setup; Reference tables; Migration scripts | Database schema v1 |
| 3-4 | 2 | Clientes | CRUD; Factory management; Auth system | Client module complete ✅ |
| 5-6 | 3 | Muestras | Productos; OT; Pedidos; Entradas; Balance calc | Sample management complete |
| 7-8 | 4 | Ensayos | Test catalogs; Assignment; Usage; Billing | Test management complete |
| 9-10 | 5 | Ordenes y Reportes | Informes; PDF generation; Dashboards | Reporting complete |
| 11-12 | 6 | Data Migration | Historical data migration; Validation | All data migrated |
| 13 | 7 | Testing | Data validation; UAT; Parallel running | Testing complete |
| 14 | 7 | Go-Live | Final migration; Training; System live | Production ready |

### Milestones

| Milestone | Date | Criteria |
|-----------|------|----------|
| M1: Foundation Complete | Week 2 | Schema deployed, reference data loaded ✅ |
| M2: Clientes Complete | Week 4 | CRUD complete, 569 records migrated ✅ |
| M3: Muestras Complete | Week 6 | Sample workflow functional, 355 records migrated |
| M4: Ensayos Complete | Week 8 | Test management working, 1,367 records migrated |
| M5: Ordenes y Reportes | Week 10 | All reports generating, dashboards live |
| M6: Migration Complete | Week 12 | All 2,632 records migrated |
| M7: Go-Live | Week 14 | System production ready |

---

## Data Migration Strategy

### Migration Order by Feature

```
Phase 1: Reference Data (78 rows) ✅
├── areas (4)
├── organismos (12)
├── provincias (4)
├── destinos (7)
├── ramas (13)
├── meses (12)
├── annos (10)
├── unidades_medida (3)
└── tipo_es (4)

Phase 2: Clientes Feature (569 rows) ✅
├── clientes (166)
└── fabricas (403)

Phase 3: Muestras Feature (355 rows)
├── productos (160)
├── ordenes_trabajo (37)
├── pedidos (49)
└── entradas (109)

Phase 4: Ensayos Feature (1,367 rows)
├── ensayos (143)
├── ensayos_es (29)
├── detalles_ensayos (563)
└── utilizado_r (632)

Phase 5: Ordenes y Reportes (20 rows)
└── informes (20)

Total: 2,389 records across 20 main tables
```

### Data Volumes by Table

| Table | Current Rows | Estimated Growth/Year | Feature |
|-------|--------------|----------------------|---------|
| areas | 4 | Static | Reference |
| organismos | 12 | +2 | Reference |
| provincias | 4 | Static | Reference |
| destinos | 7 | +1 | Reference |
| ramas | 13 | +2 | Reference |
| meses | 12 | Static | Reference |
| annos | 10 | +1 | Reference |
| unidades_medida | 3 | +1 | Reference |
| tipo_es | 4 | Static | Reference |
| clientes | 166 | +20 | Clientes |
| fabricas | 403 | +50 | Clientes |
| productos | 160 | +30 | Muestras |
| ordenes_trabajo | 37 | +100 | Muestras |
| pedidos | 49 | +150 | Muestras |
| entradas | 109 | +500 | Muestras |
| ensayos | 143 | +20 | Ensayos |
| ensayos_es | 29 | +5 | Ensayos |
| detalles_ensayos | 563 | +2000 | Ensayos |
| utilizado_r | 632 | +2500 | Ensayos |
| informes | 20 | +100 | Ordenes y Reportes |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Data Loss** | Low | Critical | Multiple backups before migration; validation scripts; rollback plan |
| **Relationship Errors** | Medium | High | Careful FK mapping; feature dependency order; constraint validation |
| **Business Disruption** | Medium | High | Parallel running; feature-by-feature rollout; weekend cutover |
| **User Adoption** | Medium | Medium | Training sessions; familiar UI patterns; help documentation |
| **Performance Issues** | Low | Medium | Proper indexing; query optimization; load testing |
| **Scope Creep** | High | Medium | Strict backlog management; change control process per feature |
| **Integration Failures** | Low | High | Early integration testing; API versioning; fallback mechanisms |
| **Security Breach** | Low | Critical | Security audit; penetration testing; encryption at rest/transit |

### Contingency Plans

**Rollback Plan:**
1. Maintain Access database in sync for 2 weeks
2. Daily backups of PostgreSQL
3. Documented rollback procedure (<4 hours)
4. Emergency contact list

**Data Recovery:**
1. Point-in-time recovery enabled
2. Transaction logs retained 30 days
3. Offsite backup storage
4. Tested restore procedures

---

## Resource Requirements

### Team Composition

| Role | Count | Allocation | Responsibilities |
|------|-------|------------|------------------|
| Project Manager | 1 | 50% | Coordination, planning, stakeholder management |
| Technical Lead | 1 | 100% | Architecture, technical decisions, code review |
| Backend Developer | 2 | 100% | API development, database, migrations |
| Frontend Developer | 1 | 100% | UI/UX, client-side logic |
| Database Administrator | 1 | 25% | Schema design, optimization, migration |
| QA Engineer | 1 | 50% | Testing, validation, UAT coordination |
| DevOps Engineer | 1 | 25% | CI/CD, deployment, monitoring |

### Infrastructure Requirements

**Development Environment:**
| Component | Specification | Cost |
|-----------|---------------|------|
| Development server | 4 vCPU, 8GB RAM | $100/mo |
| PostgreSQL | 2 vCPU, 4GB RAM | $50/mo |
| Storage | 100GB SSD | $20/mo |

**Production Environment:**
| Component | Specification | Cost |
|-----------|---------------|------|
| Application server | 4 vCPU, 8GB RAM | $200/mo |
| PostgreSQL | 4 vCPU, 16GB RAM | $300/mo |
| Storage | 500GB SSD | $100/mo |
| Backup storage | 1TB | $50/mo |
| Load balancer | 1 instance | $50/mo |

**Tools & Licenses:**
| Tool | Purpose | Cost |
|------|---------|------|
| JetBrains IDE | Development | $500/year |
| Figma | UI Design | $144/year |
| GitHub Teams | Code hosting | $48/year |
| Monitoring (Grafana) | Observability | Free |

### Total Budget Estimate

| Category | Amount |
|----------|--------|
| Personnel (14 weeks) | $85,000 |
| Infrastructure (6 months) | $4,920 |
| Tools & Licenses | $692 |
| Contingency (10%) | $9,061 |
| **Total** | **$99,673** |

---

## Success Criteria Summary

### Overall Project Success

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data migration accuracy | 100% | All 2,632 records migrated |
| System availability | 99.5% | Post go-live uptime |
| User adoption | 90% | Daily active users |
| Performance | <2s | Average page load |
| Bug resolution | <24h | Average fix time |

### Phase Success Criteria

| Phase | Feature | Success Criteria | Measurement |
|-------|---------|------------------|-------------|
| Phase 1 | Reference Data | Schema deployed, data loaded | Row count match |
| Phase 2 | Clientes | CRUD functional, auth working, DDD established | Feature tests pass |
| Phase 3 | Muestras | Sample workflow complete | End-to-end test |
| Phase 4 | Ensayos | Test management working | Assignment test |
| Phase 5 | Ordenes y Reportes | Reports generating | PDF output verified |
| Phase 6 | Data Migration | All data migrated | Validation scripts |
| Phase 7 | Go-Live | System live, users trained | Go-live checklist |

---

## Appendices

### Appendix A: Access Schema Reference

**Reference Tables:**
| Table | Rows | Description |
|-------|------|-------------|
| Areas | 4 | Laboratory areas (FQ, MB, ES, OS) |
| Organismos | 12 | Client organizations |
| Provincias | 4 | Geographic regions |
| Destinos | 7 | Product destinations |
| Ramas | 13 | Industry sectors |
| Meses | 12 | Calendar months |
| Annos | 10 | Active years |
| UnidadesMedida | 3 | Measurement units |
| TipoES | 4 | Sensory evaluation types |

**Master Data Tables:**
| Table | Rows | Description |
|-------|------|-------------|
| Clientes | 166 | Client registry |
| Fábricas | 403 | Factory locations |
| Productos | 160 | Product catalog |

**Transactional Tables:**
| Table | Rows | Description |
|-------|------|-------------|
| OrdenesTrabajo | 37 | Work orders |
| Pedidos | 49 | Orders |
| Entradas | 109 | Sample entries |
| Detalles de Ensayos | 563 | Test assignments |
| Utilizado | 632 | Usage/billing |
| Informes | 20 | Official reports |

### Appendix B: Data Retention Policy

| Data Type | Retention | Archive Strategy |
|-----------|-----------|------------------|
| Sample entries | 7 years | Archive after 2 years |
| Test results | 10 years | Permanent retention |
| Usage records | 7 years | Archive after 3 years |
| Audit logs | 3 years | Archive after 1 year |

---

*Plan Version:* 2.0 - Feature-Based Migration  
*Created:* March 2, 2026  
*Last Updated:* March 2, 2026  
*Next Review:* March 9, 2026
