# DataLab Migration Project - GitHub Issues Index

> Central hub for tracking all GitHub issues across the DataLab migration from Microsoft Access (RM2026) to Web (Flask/PostgreSQL).

---

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Project Name** | DataLab Migration Project |
| **Source System** | Microsoft Access (RM2026) |
| **Target System** | Web Application (Flask/PostgreSQL) |
| **Total Issues** | 41 issues across 7 phases |
| **Total Estimated Effort** | ~144 days |
| **Total Records** | 3,113 records |

---

## Issues Summary Table

| Phase | Issues | Effort | Records | Status |
|-------|--------|--------|---------|--------|
| Phase 1 | 8 | 17 days | 974 | Ready |
| Phase 2 | 6 | 16 days | 729 | Ready |
| Phase 3 | 6 | 20 days | 195 | Ready |
| Phase 4 | 6 | 24 days | 1,195 | Ready |
| Phase 5 | 5 | 15 days | 20 | Ready |
| Phase 6 | 5 | 20 days | - | Ready |
| Phase 7 | 5 | 32 days | All | Ready |
| Phase 8 | 7 | 35 days | - | Local |
| **Total** | **48** | **~179 days** | **3,113** | **All Local** |

---

## Phase Dependency Graph

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Phase 1  │────▶│ Phase 2  │────▶│ Phase 3  │────▶│ Phase 4  │
│Foundation│     │  Core    │     │  Sample  │     │   Test   │
│ & Schema │     │ Entities │     │Management│     │Management│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                          │
                                                          ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Phase 7  │◀────│ Phase 6  │◀────│ Phase 5  │◀────│ Phase 4  │
│ Go-Live  │     │ Advanced │     │Reporting │     │   Test   │
│& Testing │     │ Features │     │& Billing │     │Management│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

| **Phase 8** | [`phase8/`](phase8/README.md) | 7 issues | Production Hardening - API REST, seguridad avanzada, observabilidad, CI/CD, accesibilidad, rendimiento |

**Sequential Flow:**

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
(Foundation) (Core)   (Sample)  (Test)    (Reports) (Advanced) (Go-Live)
```

---

## Quick Links to Each Phase

| Phase | Directory | Issues | Description |
|-------|-----------|--------|-------------|
| **Phase 1** | [`phase1/`](phase1/README.md) | 8 issues | Foundation & Schema - Database setup, core models, authentication, and data migration foundation |
| **Phase 2** | [`phase2/`](phase2/README.md) | 6 issues | Core Entities & CRUD - Client management, factory management, product catalog, and master data |
| **Phase 3** | [`phase3/`](phase3/README.md) | 6 issues | Sample Management - Sample entry system, order management, work orders, and workflow |
| **Phase 4** | [`phase4/`](phase4/README.md) | 6 issues | Test Management - Test assignment, execution tracking, area-based views, and billing integration |
| **Phase 5** | [`phase5/`](phase5/README.md) | 5 issues | Reporting & Billing - Official reports, PDF generation, analytics dashboard, and billing reports |
| **Phase 6** | [`phase6/`](phase6/README.md) | 5 issues | Advanced Features - Global search, data export, notifications, RBAC, and UI/UX enhancements |
| **Phase 7** | [`phase7/`](phase7/README.md) | 5 issues | Testing & Go-Live - Data validation, UAT, performance testing, parallel running, and documentation |

---

## Publishing Status

Track the lifecycle of each phase from local documentation to GitHub issues to completion.

| Phase | Local | Published to GitHub | In Progress | Completed |
|-------|-------|---------------------|-------------|-----------|
| Phase 1 | ✅ | ✅ | ⬜ | ⬜ |
| Phase 2 | ✅ | ⬜ | ⬜ | ⬜ |
| Phase 3 | ✅ | ⬜ | ⬜ | ⬜ |
| Phase 4 | ✅ | ⬜ | ⬜ | ⬜ |
| Phase 5 | ✅ | ⬜ | ⬜ | ⬜ |
| Phase 6 | ✅ | ⬜ | ⬜ | ⬜ |
| Phase 7 | ✅ | ⬜ | ⬜ | ⬜ |
| Phase 8 | ✅ | ⬜ | ⬜ | ⬜ |

**Legend:**
- ✅ Complete / Available
- ⬜ Not Started / Pending
- 🔄 In Progress

---

## How to Use This Documentation

### For Developers

1. **Identify Your Phase**: Check the current phase status in the Publishing Status table
2. **Read Issue Details**: Navigate to your phase directory and read the assigned issue files
3. **Understand Requirements**: Each issue file contains detailed specifications, acceptance criteria, and technical notes
4. **Work in Dev Branch**: Follow Git workflow - create feature branches from `dev`
5. **Update Documentation**: If requirements change during implementation, update the corresponding issue file

### For Project Managers

1. **Monitor Progress**: Use the Publishing Status table to track phase completion
2. **Publish Issues**: When a phase is ready, publish issues to GitHub using the phased workflow strategy
3. **Coordinate Teams**: Ensure teams only work on published/active phases
4. **Track Milestones**: Update status tables as phases move from Local → Published → In Progress → Completed

---

## Workflow Strategy

This project follows a **phased workflow strategy** designed to maintain focus, reduce context switching, and ensure quality delivery.

> 📖 **Full Details**: See [`../plans/phased-workflow-strategy.md`](../plans/phased-workflow-strategy.md)

### Key Principles

1. **Sequential Execution**: Phases must be completed in order (1 → 2 → 3 → ...)
2. **No Future Peeking**: Teams focus only on the current active phase
3. **Issue Lifecycle**: Local → Published → In Progress → Completed
4. **Quality Gates**: Each phase has defined completion criteria before moving to the next

---

## Important Notes

⚠️ **Critical Guidelines:**

- **All issues are currently LOCAL ONLY** - No issues have been published to GitHub yet
- **Do NOT publish future phase issues prematurely** - This creates noise and confusion
- **Follow the phased workflow strategy** - Sequential execution is mandatory
- **Update this README when phases change status** - Keep the central hub current
- **Phase dependencies must be respected** - Foundation phases must be stable before building on them

---

## Related Documents

| Document | Path | Description |
|----------|------|-------------|
| **Product Requirements** | [`../PRD.md`](../PRD.md) | Complete product requirements document |
| **Migration Plan** | [`../plans/MIGRATION_PLAN.md`](../plans/MIGRATION_PLAN.md) | Detailed migration strategy and timeline |
| **Workflow Strategy** | [`../plans/phased-workflow-strategy.md`](../plans/phased-workflow-strategy.md) | Phased development methodology |
| **Access Analysis** | [`../../ACCESS_MIGRATION_ANALYSIS.md`](../../ACCESS_MIGRATION_ANALYSIS.md) | Source system analysis and data mapping |

---

## Issue Files by Phase

### Phase 1: Foundation & Schema (8 issues)
- `issue-01-reference-data-models.md`
- `issue-02-master-data-models.md`
- `issue-03-test-catalog-models.md`
- `issue-04-database-migration-scripts.md`
- `issue-05-authentication-system.md`
- `issue-06-base-templates-crud.md`
- `issue-07-crud-api-reference-data.md`
- `issue-08-import-access-data.md`

### Phase 2: Core Entities & CRUD (6 issues)
- `issue-01-client-management.md`
- `issue-02-factory-management.md`
- `issue-03-product-catalog.md`
- `issue-04-user-auth-rbac.md`
- `issue-05-master-data-import.md`
- `issue-06-master-data-dashboard.md`

### Phase 3: Sample Management (6 issues)
- `issue-01-sample-entry-system.md`
- `issue-02-order-management.md`
- `issue-03-work-order-management.md`
- `issue-04-sample-status-workflow.md`
- `issue-05-transactional-data-import.md`
- `issue-06-sample-entry-ui.md`

### Phase 4: Test Management (6 issues)
- `issue-1-test-assignment-system.md`
- `issue-2-area-based-test-views.md`
- `issue-3-test-execution-tracking.md`
- `issue-4-usage-tracking-billing.md`
- `issue-5-test-data-import.md`
- `issue-6-laboratory-workflow-ui.md`

### Phase 5: Reporting & Billing (5 issues)
- `issue-1-official-reports-module.md`
- `issue-2-pdf-report-generation.md`
- `issue-3-analytics-dashboard.md`
- `issue-4-billing-reports.md`
- `issue-5-report-data-import-validation.md`

### Phase 6: Advanced Features (5 issues)
- `01-global-search.md`
- `02-data-export.md`
- `03-notifications.md`
- `04-rbac.md`
- `05-ui-ux-enhancements.md`

### Phase 7: Testing & Go-Live (5 issues)
- `issue-01-data-validation-verification.md`
- `issue-02-user-acceptance-testing.md`
- `issue-03-performance-testing.md`
- `issue-04-parallel-running-cutover.md`
- `issue-05-documentation-training.md`

---

## Maintenance

**Last Updated:** 2026-03-02

**Update Schedule:**
- Update Publishing Status table when phases are published or completed
- Update this README when new issues are added or phase scope changes
- Review quarterly to ensure accuracy

---

*This document serves as the single source of truth for all DataLab migration GitHub issues. For questions or updates, contact the project lead.*
