# Phase 2 GitHub Issues - Core Entities & CRUD

**Phase:** 2 - Core Entities & CRUD  
**Duration:** Weeks 3-4  
**Milestone:** Core CRUD Complete, Master Data Migrated  
**Total Issues:** 6  
**Total Estimated Effort:** ~16 days

---

## Issues Overview

| Issue | Title | Effort | Priority | Dependencies |
|-------|-------|--------|----------|--------------|
| #1 | [Phase 2] Client Management Module | 3 days | High | Phase 1 Models |
| #2 | [Phase 2] Factory Management Module | 3 days | High | Issue #1 |
| #3 | [Phase 2] Product Catalog Module | 3 days | High | Phase 1 Models |
| #4 | [Phase 2] User Authentication & Role Management | 3 days | High | Phase 1 Auth |
| #5 | [Phase 2] Master Data Import from Access | 3 days | High | Issue #1-3 |
| #6 | [Phase 2] Dashboard for Master Data | 2 days | Medium | Issue #1-3 |

---

## Phase Goals

### Primary Objectives
1. **Full CRUD Implementation** for all master data entities (Clients, Factories, Products)
2. **User Management** with role-based access control (RBAC)
3. **Data Migration** - Import 729 records from Access with validation
4. **Dashboard** - Visual overview of master data with Plotly

### Success Criteria
- [ ] All 166 clients manageable via web UI
- [ ] All 403 factories manageable via web UI  
- [ ] All 160 products manageable via web UI
- [ ] User authentication with 5 roles working
- [ ] 729 records successfully imported from Access
- [ ] Dashboard with statistics and charts functional
- [ ] All FK relationships validated

---

## Data Migration Summary

### Records to Migrate
| Entity | Records | Source Table | Destination Table |
|--------|---------|--------------|-------------------|
| Clientes | 166 | Clientes | clientes |
| Fábricas | 403 | Fabricas | fabricas |
| Productos | 160 | Productos | productos |
| **Total** | **729** | - | - |

### Migration Order
```
1. Clientes (166) - Parent entity
2. Fabricas (403) - Depends on Clientes
3. Productos (160) - Independent
```

---

## User Roles

| Role | ID | Capabilities |
|------|-----|--------------|
| Admin | 1 | Full system access |
| Laboratory Manager | 2 | All data + reports |
| Technician | 3 | CRUD on assigned work |
| Client | 4 | View own data only |
| Viewer | 5 | Read-only all data |

---

## Issue Dependencies

```
Phase 1 Issues
├── #1 Reference Data Models
├── #2 Master Data Models
├── #3 Test Catalog Models
├── #5 Authentication System
└── #6 Base Templates
    ↓
Phase 2 Issues
├── #1 Client Management ─┬──→ #2 Factory Management
│                         │
├── #3 Product Catalog ───┼──→ #5 Master Data Import
│                         │
├── #4 User Auth & RBAC ──┤    (needs all CRUD)
│                         │
└── #6 Dashboard ─────────┘    (needs all CRUD)
```

---

## Implementation Order

### Week 3
1. **Day 1-2:** Issue #1 - Client Management
2. **Day 2-3:** Issue #2 - Factory Management
3. **Day 3-4:** Issue #3 - Product Catalog

### Week 4
4. **Day 5-6:** Issue #4 - User Auth & RBAC
5. **Day 6-7:** Issue #5 - Master Data Import
6. **Day 7-8:** Issue #6 - Dashboard

---

## Technical Stack Used

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0, SQLAlchemy 2.0 |
| Frontend | Jinja2, Bootstrap 5, Vanilla JS |
| Charts | Plotly.js |
| Auth | Flask-Login, Bcrypt |
| Forms | Flask-WTF |
| DB | PostgreSQL (Production), SQLite (Dev) |

---

## Deliverables

- [ ] 6 fully functional CRUD modules
- [ ] 729 records imported and validated
- [ ] Role-based access control enforced
- [ ] Interactive dashboard with Plotly
- [ ] Complete audit trail
- [ ] Import/ETL scripts
- [ ] Documentation

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| FK violations during import | High | Validate all FKs before import, report orphans |
| Data encoding issues | Medium | UTF-8 conversion, test with sample data |
| Performance with 400+ factories | Low | Pagination, indexing, query optimization |
| Role permission gaps | Medium | Comprehensive permission matrix, testing |

---

## Related Documentation

- `../PRD.md` - Product Requirements Document
- `../../plans/MIGRATION_PLAN.md` - Migration Plan (Phase 2)
- `../PROJECT_ANALYSIS.md` - Current Project Status
- `../ACCESS_MIGRATION_ANALYSIS.md` - Access Database Analysis

---

## Notes

- All issues should reference Phase 1 issues for context
- Each issue includes code examples and templates
- Testing requirements specified in each issue
- Definition of Done checklist provided
