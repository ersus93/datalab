# DataLab Access to Web Migration Plan
## Laboratory Information Management System (LIMS) Migration Strategy

**Migration Date:** March 2026  
**Estimated Duration:** 14 Weeks  
**Target Go-Live:** June 2026  
**Databases:** RM2026.accdb (Frontend) + RM2026_be.accdb (Backend)  
**Total Records:** ~2,632 rows across 25 tables

---

## Executive Summary

This migration plan outlines the complete transition of the Access-based RM2026 laboratory management system to a modern web-based DataLab application. The migration follows a phased approach to minimize risk and ensure business continuity.

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

---

## Migration Phases Overview

| Phase | Duration | Priority | Focus Area |
|-------|----------|----------|------------|
| Phase 1 | Weeks 1-2 | CRITICAL | Foundation & Schema |
| Phase 2 | Weeks 3-4 | HIGH | Core Entities & CRUD |
| Phase 3 | Weeks 5-6 | HIGH | Sample Management |
| Phase 4 | Weeks 7-8 | HIGH | Test Management |
| Phase 5 | Weeks 9-10 | MEDIUM | Reporting & Billing |
| Phase 6 | Weeks 11-12 | MEDIUM | Advanced Features |
| Phase 7 | Weeks 13-14 | CRITICAL | Testing & Go-Live |

---

## Phase 1: Foundation & Schema (Weeks 1-2)
**Priority:** CRITICAL  
**Success Criteria:** Database schema deployed, reference data migrated, basic connectivity verified

### 1.1 Database Schema Creation

#### Week 1: Schema Design & Implementation
| Task | Duration | Owner | Deliverable |
|------|----------|-------|-------------|
| Create PostgreSQL database | 1 day | DBA | Empty database |
| Implement reference tables | 2 days | Backend | 8 reference tables |
| Implement core business tables | 2 days | Backend | Clientes, Fabricas, Productos |
| Create foreign key relationships | 1 day | Backend | Complete FK graph |
| Add indexes and constraints | 1 day | DBA | Optimized schema |

**Reference Tables to Create:**
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

**Core Business Tables:**
```sql
-- Priority: HIGH (Load Second)
clientes (166 rows)      - Client registry
fabricas (403 rows)      - Factory locations
productos (160 rows)     - Product catalog
```

#### Week 2: Test Catalogs & Audit Infrastructure
| Task | Duration | Owner | Deliverable |
|------|----------|-------|-------------|
| Create test catalog tables | 2 days | Backend | Ensayos, EnsayosES |
| Implement audit trail tables | 1 day | Backend | Audit logging schema |
| Create migration scripts | 2 days | DBA | Automated migration tools |
| Schema validation | 1 day | QA | Validated schema |

**Test Catalog Tables:**
```sql
ensayos (143 rows)       - Physical-chemical tests (FQ area)
ensayos_es (29 rows)     - Sensory evaluation tests (ES area)
```

### 1.2 Data Migration - Phase 1

**Migration Order:**
1. Reference data (78 rows total)
2. Master data (729 rows total)
3. Verify row counts and FK integrity

**Validation Checkpoints:**
- [ ] All 8 reference tables loaded
- [ ] 166 clients migrated with organizations
- [ ] 403 factories linked to clients and provinces
- [ ] 160 products with destinations
- [ ] 143 FQ tests with pricing
- [ ] 29 sensory tests with pricing
- [ ] Foreign key relationships validated

### 1.3 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| Schema deployment | 100% | All tables created |
| Data accuracy | 100% | Row count match |
| FK integrity | 100% | No orphaned records |
| Query performance | <100ms | Standard queries |

---

## Phase 2: Core Entities (Weeks 3-4)
**Priority:** HIGH  
**Success Criteria:** Full CRUD for clients, factories, products; user authentication working

### 2.1 CRUD Implementation

#### Week 3: Client Management Module
| Feature | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| Client List | Paginated client directory | Search, filter, sort |
| Create Client | New client registration | Validation, duplicate check |
| Edit Client | Modify client details | Audit trail |
| Delete Client | Soft delete | Preserve history |
| Client Detail | Full client view | Factory associations |

**Client Data Structure:**
```python
{
  "id": 1,
  "nombre": "Empresa Cárnica de Pinar del Río",
  "organismo_id": 1,
  "tipo_cliente": 1,
  "activo": true,
  "fabricas": [...],
  "total_pedidos": 15
}
```

#### Week 3-4: Factory Management
| Feature | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| Factory CRUD | Manage factory locations | Linked to clients |
| Province Filter | Filter by province | 4 provinces supported |
| Factory History | View associated samples | Timeline view |

**Factory Statistics:**
- Total: 403 factories
- Average per client: 2.4 factories
- By province: Distribution maintained

#### Week 4: Product Catalog
| Feature | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| Product CRUD | Manage product catalog | 160 products |
| Sector Classification | Assign to ramas | 13 sectors |
| Destination Tracking | Product destinations | 7 destinations |
| Test Associations | Link tests to products | FQ, MB, ES tests |

### 2.2 Data Migration - Phase 2

**Master Data Migration:**
| Table | Rows | Migration Method | Validation |
|-------|------|------------------|------------|
| clientes | 166 | CSV export/import | Row count + sample validation |
| fabricas | 403 | CSV export/import | FK to clientes verified |
| productos | 160 | CSV export/import | FK to destinos verified |

### 2.3 User Authentication System

| Component | Implementation | Priority |
|-----------|----------------|----------|
| User Model | Flask-Login + SQLAlchemy | HIGH |
| Login/Logout | Session-based auth | HIGH |
| Role Management | Admin, Technician, Client | HIGH |
| Password Security | Bcrypt hashing | CRITICAL |

**User Roles:**
- **Admin:** Full system access
- **Technician:** Test execution, result entry
- **Client:** View own data, reports only

### 2.4 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| CRUD operations | 100% | All features working |
| Data migration | 100% | 729 records migrated |
| Authentication | 100% | Login/logout functional |
| UI responsiveness | <2s | Page load time |

---

## Phase 3: Sample Management (Weeks 5-6)
**Priority:** HIGH  
**Success Criteria:** Sample entry workflow complete, balance tracking accurate

### 3.1 Core Entity: Entradas (Sample Entries)

The `Entradas` table is the **CORE ENTITY** of the system with 109 existing records.

#### Week 5: Sample Entry System
| Feature | Description | Priority |
|---------|-------------|----------|
| Entry Registration | New sample intake | CRITICAL |
| Lot Tracking | Lote field (X-XXXX format) | HIGH |
| Part Number | NroParte tracking | HIGH |
| Balance Calculation | CantidadRecib - CantidadEntreg = Saldo | CRITICAL |

**Entry Data Model:**
```python
{
  "id": 1,
  "pedido_id": 1,              # FK to pedidos
  "fabrica_id": 1,             # FK to fabricas
  "producto_id": 1,            # FK to productos
  "fecha_entrada": "2026-03-01",
  "numero_oficial": "OF-2026-001",
  "anno": "2026",
  "mes": 3,
  "lote": "A-1234",            # Format: X-XXXX
  "numero_parte": 1,
  "fecha_fabricacion": "2026-01-15",
  "fecha_vencimiento": "2026-07-15",
  "fecha_muestreo": "2026-03-01",
  "cantidad_recibida": 100,
  "cantidad_entregada": 50,
  "saldo": 50,                 # Calculated
  "en_orden_servicio": false,
  "anulado": false,
  "rama_id": 1,
  "otra_rama": null,
  "entrada_entregada": false,
  "provincia_id": 1
}
```

#### Week 5: Pedidos (Orders) Module
| Feature | Description | Records |
|---------|-------------|---------|
| Order Creation | New sample requests | 49 existing |
| Lot Information | Lote, FechFab, FechVenc | Required |
| Work Order Link | Associate with OT | Optional |
| Client Association | Link to cliente | Required |

**Order Statistics:**
- Total orders: 49
- Average per client: ~0.3
- With work orders: Linked to 37 OTs

#### Week 6: Ordenes de Trabajo (Work Orders)
| Feature | Description | Records |
|---------|-------------|---------|
| OT Creation | New work orders | 37 existing |
| Official Number | NroOfic tracking | Unique |
| Client Assignment | Link to cliente | Required |
| Date Tracking | FechOT | Required |

#### Week 6: Sample Status Workflow
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

### 3.2 Data Migration - Phase 3

**Transactional Data Migration:**
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

### 3.3 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| Entry workflow | 100% | End-to-end functional |
| Balance accuracy | 100% | Calculations verified |
| Lot tracking | 100% | Format preserved |
| Data migration | 100% | 195 records migrated |

---

## Phase 4: Test Management (Weeks 7-8)
**Priority:** HIGH  
**Success Criteria:** Test assignment working, result recording functional

### 4.1 Test Execution System

#### Week 7: Test Assignment (Detalles de Ensayos)

**Current State:** 563 test assignments exist

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Test Assignment | Assign tests to samples | Multi-select by area |
| Area Filtering | FQ, MB, ES views | Tab-based interface |
| Quantity Tracking | Cantidad field | Default 1 |
| Date Assignment | FechReal | Planned date |

**Assignment Workflow:**
```python
# Test Assignment Model
{
  "id": 1,
  "entrada_id": 1,        # Sample entry
  "ensayo_id": 1,         # FQ test (or ensayo_es_id for ES)
  "cantidad": 1,
  "fecha_realizacion": "2026-03-15",
  "estado": "pendiente"   # pendiente | en_proceso | completado
}
```

**Area-Specific Test Views:**
| Area | Table | Tests | View Name |
|------|-------|-------|-----------|
| Físico-Químico | Ensayos | 143 | Análisis FQ |
| Microbiología | Ensayos | Subset | Análisis MB |
| Evaluación Sensorial | EnsayosES | 29 | Análisis ES |
| Otros Servicios | Ensayos | Subset | Otros |

#### Week 7: Test Catalog Management

**Ensayos (FQ Tests) - 143 records:**
| Field | Type | Description |
|-------|------|-------------|
| IdEns | INTEGER | Test ID |
| NomOfic | VARCHAR | Official name |
| NomEns | VARCHAR | Short name |
| IdArea | INTEGER | =1 (FQ) |
| Precio | CURRENCY | Test price |
| UM | VARCHAR | Unit |
| Activo | BIT | Active flag |
| EsEnsayo | BIT | Is test flag |

**EnsayosES (Sensory Tests) - 29 records:**
| Field | Type | Description |
|-------|------|-------------|
| IdEnsES | INTEGER | Test ID |
| NomOfic | VARCHAR | Official name |
| NomEnsES | VARCHAR | Short name |
| IdArea | INTEGER | =3 (ES) |
| IdTipoES | BYTE | Sensory type |
| Precio | CURRENCY | Test price |
| UM | VARCHAR | Unit |
| Activo | BIT | Active flag |

#### Week 8: Test Execution Tracking

**Test States:**
```
Pendiente → Asignado → En Proceso → Completado → Reportado
   ↓            ↓           ↓            ↓            ↓
  New      Scheduled   In Lab      Results      Official
                              Entered       Report
```

**Features:**
- Batch test assignment
- Test completion tracking
- Result recording
- Historical view

### 4.2 Data Migration - Phase 4

**Test Data Migration:**
| Table | Rows | Dependencies | Priority |
|-------|------|--------------|----------|
| detalles_ensayos | 563 | entradas, ensayos | HIGH |

**Usage Data Migration:**
| Table | Rows | Description | Priority |
|-------|------|-------------|----------|
| utilizado_r | 632 | Archived usage | MEDIUM |

### 4.3 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| Test assignment | 100% | All 563 migrated |
| Area filtering | 100% | 4 areas working |
| Result recording | 100% | Functional |
| Usage migration | 100% | 632 records migrated |

---

## Phase 5: Reporting & Billing (Weeks 9-10)
**Priority:** MEDIUM  
**Success Criteria:** Reports generating, billing calculations accurate

### 5.1 Reports Module (Informes)

**Current State:** 20 reports exist

#### Week 9: Official Reports
| Report Type | Description | Format |
|-------------|-------------|--------|
| Informe Oficial | Official lab report | PDF |
| Resultados | Test results summary | PDF/Excel |
| Entrada Detail | Sample entry report | PDF |

**Report Data Model:**
```python
{
  "id": 1,
  "entrada_id": 1,
  "fecha": "2026-03-15",
  "numero_oficial": "INF-2026-001",
  "anno": "2026",
  "ensayos": [...]  # Linked tests
}
```

#### Week 9: Usage Tracking (Utilizado)

**Billing Calculation:**
```python
# From utilizado_r table (632 records)
{
  "entrada_id": 1,
  "ensayo_id": 1,
  "cantidad": 1,
  "fecha": "2026-03-15",
  "hora": "10:30:00",
  "precio": 150.00,
  "importe": 150.00,  # cantidad * precio
  "unidad_medida": "USD",
  "anno": "2026"
}
```

**Billing Reports:**
- Usage by client
- Usage by period
- Usage by test type
- Invoice generation

#### Week 10: Analytics Dashboards

**Key Metrics:**
| Metric | Source | Visualization |
|--------|--------|---------------|
| Samples per month | Entradas | Line chart |
| Tests by area | Detalles de ensayos | Pie chart |
| Client activity | Utilizado | Bar chart |
| Pending tests | Detalles de ensayos | Counter |

**Reports to Implement:**
1. Análisis a realizar ES (Sensory pending)
2. Análisis a realizar FQ (FQ pending)
3. Análisis a realizar MB (Microbiology pending)
4. Determinaciones realizadas (Completed tests)
5. Lotes Analizados (Analyzed batches)
6. Muestreos por tipo de cliente (Sampling by client type)

### 5.2 PDF Generation

**Templates:**
- Official report template
- Usage consultation report
- Statistical summaries

**Technology:**
- WeasyPrint or ReportLab
- HTML/CSS templates
- Header/footer with lab info

### 5.3 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| Report generation | 100% | All templates working |
| Billing accuracy | 100% | Calculations verified |
| PDF quality | High | Professional format |
| Dashboard metrics | 6+ | Key metrics displayed |

---

## Phase 6: Advanced Features (Weeks 11-12)
**Priority:** MEDIUM  
**Success Criteria:** Search, export, notifications working

### 6.1 Global Search

**Search Scope:**
| Entity | Fields | Priority |
|--------|--------|----------|
| Clientes | nombre, id | HIGH |
| Fabricas | nombre, id | HIGH |
| Productos | nombre, id | HIGH |
| Entradas | lote, numero_oficial | HIGH |
| Pedidos | numero_oficial | MEDIUM |
| Informes | numero_oficial | MEDIUM |

**Search Features:**
- Fuzzy matching
- Filter by date range
- Filter by area
- Results categorization

### 6.2 Data Export

**Export Formats:**
| Format | Use Case | Priority |
|--------|----------|----------|
| Excel | Analysis, reporting | HIGH |
| CSV | Data migration, backup | HIGH |
| PDF | Official documents | HIGH |
| JSON | API integration | MEDIUM |

### 6.3 Notifications System

**Notification Types:**
| Event | Recipients | Channel |
|-------|------------|---------|
| Test completed | Client, Technician | Email, In-app |
| Report ready | Client | Email |
| Low balance | Technician | In-app |
| Entry delivered | Client | Email |

### 6.4 User Roles & Permissions

**Role Matrix:**
| Feature | Admin | Technician | Client |
|---------|-------|------------|--------|
| Client management | CRUD | View | - |
| Sample entry | CRUD | CRUD | View own |
| Test execution | View | CRUD | - |
| Report generation | CRUD | CRUD | View own |
| Billing | CRUD | View | View own |
| System config | CRUD | - | - |

### 6.5 Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| Search coverage | 100% | All entities searchable |
| Export formats | 4 | Excel, CSV, PDF, JSON |
| Notifications | 4 types | All working |
| Role separation | 3 roles | Access control verified |

---

## Phase 7: Testing & Go-Live (Weeks 13-14)
**Priority:** CRITICAL  
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

**User Acceptance Testing (UAT):**
| Test Scenario | Users | Duration |
|---------------|-------|----------|
| Sample entry workflow | 3 technicians | 2 days |
| Test execution | 2 analysts | 2 days |
| Report generation | 1 admin | 1 day |
| Client portal | 2 clients | 1 day |

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

## Data Migration Strategy

### Migration Order

```
Phase 1: Reference Data (78 rows)
├── areas (4)
├── organismos (12)
├── provincias (4)
├── destinos (7)
├── ramas (13)
├── meses (12)
├── annos (10)
├── unidades_medida (3)
└── tipo_es (4)

Phase 2: Master Data (729 rows)
├── clientes (166)
├── fabricas (403)
└── productos (160)

Phase 3: Test Catalogs (172 rows)
├── ensayos (143)
└── ensayos_es (29)

Phase 4: Work Orders (37 rows)
└── ordenes_trabajo (37)

Phase 5: Orders (49 rows)
└── pedidos (49)

Phase 6: Sample Entries (109 rows)
└── entradas (109)

Phase 7: Test Assignments (563 rows)
└── detalles_ensayos (563)

Phase 8: Usage Data (632 rows)
└── utilizado_r (632)

Phase 9: Reports (20 rows)
└── informes (20)
```

### Migration Methods

**Method 1: CSV Export/Import**
- Best for: Reference data, master data
- Tools: Access export → Python script → PostgreSQL
- Validation: Row count, FK integrity

**Method 2: Direct Database Connection**
- Best for: Large tables, complex relationships
- Tools: pyodbc → SQLAlchemy
- Validation: Real-time during migration

**Method 3: API Migration**
- Best for: Transactional data
- Tools: Custom API endpoints
- Validation: Business logic validation

### Verification Steps

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

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Data Loss** | Low | Critical | Multiple backups before migration; validation scripts; rollback plan |
| **Relationship Errors** | Medium | High | Careful FK mapping; test imports with small dataset; constraint validation |
| **Business Disruption** | Medium | High | Parallel running; phased rollout; weekend cutover |
| **User Adoption** | Medium | Medium | Training sessions; familiar UI patterns; help documentation |
| **Performance Issues** | Low | Medium | Proper indexing; query optimization; load testing |
| **Scope Creep** | High | Medium | Strict backlog management; change control process |
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

## Detailed Timeline

### Week-by-Week Breakdown

| Week | Phase | Key Activities | Deliverables |
|------|-------|----------------|--------------|
| 1 | 1 | PostgreSQL setup; Reference tables; Core tables | Database schema v1 |
| 2 | 1 | Test catalogs; Audit tables; Migration scripts | Migration tools ready |
| 3 | 2 | Client CRUD; Factory CRUD; Auth system | Client module complete |
| 4 | 2 | Product CRUD; User roles; Data migration | Core entities migrated |
| 5 | 3 | Sample entry form; Lot tracking; Balance calc | Entry system working |
| 6 | 3 | Orders module; Work orders; Status workflow | Sample management complete |
| 7 | 4 | Test assignment; Area filtering; Test catalogs | Test management 50% |
| 8 | 4 | Result recording; Usage migration; History | Test management complete |
| 9 | 5 | Report templates; PDF generation; Official reports | Reporting 50% |
| 10 | 5 | Billing calculations; Dashboards; Analytics | Reporting complete |
| 11 | 6 | Global search; Data export; Notifications | Advanced features 50% |
| 12 | 6 | Role permissions; UI polish; Performance tuning | Advanced features complete |
| 13 | 7 | Data validation; UAT; Parallel running | Testing complete |
| 14 | 7 | Final migration; Training; Go-live | System live |

### Milestones

| Milestone | Date | Criteria |
|-----------|------|----------|
| M1: Foundation Complete | Week 2 | Schema deployed, reference data loaded |
| M2: Core Entities Ready | Week 4 | CRUD complete, 729 records migrated |
| M3: Sample Tracking Live | Week 6 | Entry workflow functional, 195 records migrated |
| M4: Test Management Done | Week 8 | Test assignment working, 1195 records migrated |
| M5: Reporting Ready | Week 10 | All reports generating, dashboards live |
| M6: Feature Complete | Week 12 | All features implemented |
| M7: Go-Live | Week 14 | System production ready |

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

| Phase | Success Criteria | Measurement |
|-------|------------------|-------------|
| Phase 1 | Schema deployed, data loaded | Row count match |
| Phase 2 | CRUD functional, auth working | Feature tests pass |
| Phase 3 | Entry workflow complete | End-to-end test |
| Phase 4 | Test management working | Assignment test |
| Phase 5 | Reports generating | PDF output verified |
| Phase 6 | All features implemented | Feature checklist |
| Phase 7 | System live, users trained | Go-live checklist |

---

## Appendices

### Appendix A: Access Query Migration

| Access Query | Web Implementation | Priority |
|--------------|-------------------|----------|
| Analisis a realizar ES | Pending sensory tests view | HIGH |
| Analisis a realizar FQ | Pending FQ tests view | HIGH |
| Analisis a realizar MB | Pending microbiology tests view | HIGH |
| Determinaciones realizadas | Completed tests report | HIGH |
| Lotes Analizados | Analyzed batches report | MEDIUM |
| Muestreos por tipo de cliente | Client type analytics | MEDIUM |

### Appendix B: Database Size Estimation

| Table | Current Rows | Estimated Growth/Year |
|-------|--------------|----------------------|
| entradas | 109 | +500 |
| detalles_ensayos | 563 | +2000 |
| utilizado_r | 632 | +2500 |
| informes | 20 | +100 |
| clientes | 166 | +20 |
| fabricas | 403 | +50 |

### Appendix C: Data Retention Policy

| Data Type | Retention | Archive Strategy |
|-----------|-----------|------------------|
| Sample entries | 7 years | Archive after 2 years |
| Test results | 10 years | Permanent retention |
| Usage records | 7 years | Archive after 3 years |
| Audit logs | 3 years | Archive after 1 year |

---

*Plan Version:* 1.0  
*Created:* March 2, 2026  
*Last Updated:* March 2, 2026  
*Next Review:* March 9, 2026
