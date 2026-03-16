# [Phase 7] Data Validation & Verification

## Issue Type
Phase 7 - Testing & Go-Live

## Status
Open - Ready for Development

## Labels
`phase-7`, `testing`, `go-live`, `critical`

## Assignees
Database Team, QA Lead

## Milestone
Phase 7: Testing & Go-Live

## Priority
Critical

## Estimated Effort
5 days

---

## User Story
As a DataLab administrator, I need comprehensive data validation and verification processes to ensure all 2,632 migrated records are accurate, complete, and maintain referential integrity so that the new system can be trusted for production use.

## Background
Following the data migration from Microsoft Access to the web-based system, we need rigorous validation to ensure no data corruption occurred during the migration process. This includes verifying row counts, foreign key relationships, data accuracy, and calculation integrity.

## Acceptance Criteria

### Row Count Matching Validation
- [ ] Verify total record count matches source (2,632 total records)
- [ ] Validate counts for each entity type:
  - [ ] Clients/Companies
  - [ ] Factories/Locations
  - [ ] Products/SKUs
  - [ ] Test Methods
  - [ ] Sample Orders
  - [ ] Test Executions
  - [ ] Usage/Billing Records
- [ ] Document any discrepancies with explanations
- [ ] Generate reconciliation report

### Foreign Key Integrity Checks
- [ ] Verify all foreign key constraints are respected
- [ ] Check for orphaned records:
  - [ ] Samples without valid orders
  - [ ] Tests without valid samples
  - [ ] Billing records without valid tests
  - [ ] Users without valid company associations
- [ ] Validate cascading deletes work correctly
- [ ] Test constraint enforcement

### Data Accuracy Sampling
- [ ] Random sampling of 5% of records (minimum 100 records per table)
- [ ] Field-by-field comparison with source data
- [ ] Target: 95%+ accuracy rate
- [ ] Document any data transformation issues
- [ ] Create accuracy report with statistics

### Calculation Accuracy Tests
- [ ] Verify billing calculations:
  - [ ] Test usage totals
  - [ ] Discount calculations
  - [ ] Tax calculations (if applicable)
  - [ ] Invoice totals
- [ ] Validate balance calculations:
  - [ ] Client balances
  - [ ] Prepaid credits
  - [ ] Outstanding amounts
- [ ] Check date calculations (turnaround times, aging)
- [ ] Compare 20+ sample calculations with Access system

### Automated Validation Scripts
- [ ] Create Python/TypeScript validation scripts
- [ ] Implement row count validation function
- [ ] Build foreign key checker utility
- [ ] Create data comparison tool
- [ ] Set up automated daily validation job
- [ ] Configure email alerts for validation failures
- [ ] Generate JSON/CSV validation reports

### Validation Report Generation
- [ ] Design validation report template
- [ ] Include summary statistics
- [ ] List all discrepancies found
- [ ] Provide remediation recommendations
- [ ] Create executive summary
- [ ] Export to PDF format
- [ ] Store reports in project documentation

## Technical Requirements

### Validation Script Architecture
```
scripts/
├── validation/
│   ├── __init__.py
│   ├── row_counter.py
│   ├── fk_validator.py
│   ├── data_sampler.py
│   ├── calc_checker.py
│   └── report_generator.py
├── config/
│   └── validation_rules.yaml
└── output/
    └── validation_reports/
```

### Database Validation Queries
```sql
-- Row count verification
SELECT 'clients' as table_name, COUNT(*) as count FROM clients
UNION ALL
SELECT 'factories', COUNT(*) FROM factories
UNION ALL
SELECT 'products', COUNT(*) FROM products
-- etc.

-- Orphaned record detection
SELECT s.sample_id, s.order_id 
FROM samples s 
LEFT JOIN orders o ON s.order_id = o.order_id 
WHERE o.order_id IS NULL;
```

### Data Sampling Strategy
- Random sampling using `TABLESAMPLE` or `ORDER BY RANDOM()`
- Stratified sampling by date ranges
- Focus on recent high-value transactions
- Include edge cases (first/last records)

## Dependencies
- [ ] Phase 5 data migration completed
- [ ] Phase 6 Go-Live System features deployed
- [ ] Access to source Access database for comparison
- [ ] PostgreSQL database with migrated data

## Out of Scope
- Data correction (handled in separate issue if needed)
- Performance testing (separate issue)
- User acceptance testing (separate issue)

## Risks & Mitigation
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Significant data discrepancies | High | Medium | Early sampling to identify issues quickly |
| Missing foreign key relationships | High | Low | Comprehensive FK mapping from Phase 1 |
| Calculation differences | Medium | Medium | Document business rule changes |
| Time consuming manual validation | Medium | High | Automated scripts for 90% of checks |

## Test Plan
1. Run automated row count validation
2. Execute FK integrity checks
3. Perform random sampling comparison
4. Validate 20+ calculation scenarios
5. Generate and review validation report
6. Address any critical findings
7. Re-run validation after fixes

## Definition of Done
- [ ] All row counts match source data
- [ ] No orphaned records found (or documented with justification)
- [ ] 95%+ data accuracy achieved
- [ ] All calculations verified correct
- [ ] Automated validation scripts deployed
- [ ] Validation report generated and approved
- [ ] Sign-off from DataLab management

## Related Issues
- Phase 5: Data Migration
- Phase 6: Go-Live System
- [Phase 7] User Acceptance Testing

---
*Created for Phase 7: Testing & Go-Live*
