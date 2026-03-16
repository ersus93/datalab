# [Phase 7] Parallel Running & Cutover

## Issue Type
Phase 7 - Testing & Go-Live

## Status
Open - Ready for Development

## Labels
`phase-7`, `go-live`, `cutover`, `critical`

## Assignees
Project Manager, DevOps Lead, Database Admin

## Milestone
Phase 7: Testing & Go-Live

## Priority
Critical

## Estimated Effort
5 days (spread across 2 weeks)

---

## User Story
As a DataLab operations manager, I need a carefully planned and executed cutover from Microsoft Access to the web-based system with parallel running validation, so that business continuity is maintained and we can confidently switch to the new system with minimal risk.

## Background
Parallel running allows both systems to operate simultaneously, enabling comparison of outputs and ensuring the new system produces correct results before fully decommissioning Access. This reduces risk and provides a safety net during the transition period.

## Acceptance Criteria

### Parallel Running Setup
- [ ] Configure parallel running period (recommend 2 weeks)
- [ ] Set up data synchronization mechanism:
  - [ ] Access → Web (new data entered in Access)
  - [ ] Handle new records created in Access during parallel period
- [ ] Train users on dual-entry procedures
- [ ] Create parallel running schedule
- [ ] Establish daily comparison routine
- [ ] Set up communication channels for issues
- [ ] Document parallel running procedures

### Daily Comparison of Outputs
- [ ] Define comparison checkpoints:
  - [ ] Daily sample counts
  - [ ] Daily test completion counts
  - [ ] Billing amounts
  - [ ] Client balances
- [ ] Create automated comparison scripts
- [ ] Generate daily comparison reports
- [ ] Schedule daily review meetings
- [ ] Track comparison metrics over time
- [ ] Document trends and patterns

### Discrepancy Logging and Resolution
- [ ] Create discrepancy tracking log
- [ ] Define severity levels:
  - [ ] Critical: Data mismatch affecting billing/results
  - [ ] High: Count mismatch > 5%
  - [ ] Medium: Minor calculation differences
  - [ ] Low: Formatting/presentation differences
- [ ] Establish resolution workflow:
  - [ ] Identify root cause
  - [ ] Determine correct value
  - [ ] Fix in web system if needed
  - [ ] Document decision
- [ ] Track resolution SLA (24-48 hours)
- [ ] Maintain discrepancy resolution log

### Go-Live Checklist Implementation
Create comprehensive go-live checklist:

#### Technical Checks
- [ ] All P1/P2 bugs resolved
- [ ] Performance targets met
- [ ] Security audit passed
- [ ] Backup procedures tested
- [ ] Monitoring alerts configured
- [ ] SSL certificates valid
- [ ] DNS records ready

#### Data Checks
- [ ] Final data migration completed
- [ ] Data validation passed
- [ ] Row counts verified
- [ ] Critical reports tested
- [ ] Integration points verified

#### User Readiness
- [ ] All users trained
- [ ] User guides distributed
- [ ] Support contact list shared
- [ ] Feedback channels established
- [ ] Go-live communication sent

#### Operations
- [ ] Support team on standby
- [ ] Rollback plan reviewed
- [ ] Escalation contacts confirmed
- [ ] War room scheduled (if needed)

### Final Data Sync Procedure
- [ ] Schedule final sync window (recommend weekend)
- [ ] Duration: 4-6 hours
- [ ] Steps:
  1. [ ] Freeze Access database (read-only)
  2. [ ] Export final Access data
  3. [ ] Run incremental migration
  4. [ ] Validate migrated data
  5. [ ] Update web system to production mode
  6. [ ] Enable write access in web system
  7. [ ] Update DNS/load balancer
  8. [ ] Verify connectivity
  9. [ ] Send go-live announcement
  10. [ ] Monitor closely for 24 hours

### DNS Switchover Plan
- [ ] Prepare DNS changes in advance
- [ ] Lower TTL 24 hours before cutover (300 seconds)
- [ ] Document current and new DNS records
- [ ] Prepare rollback DNS configuration
- [ ] Test DNS propagation tools ready
- [ ] Coordinate exact switchover time
- [ ] Monitor DNS propagation post-switch
- [ ] Verify SSL certificates on new domain

### Rollback Procedure Documentation
- [ ] Define rollback triggers:
  - [ ] Critical data loss or corruption
  - [ ] System unavailable > 2 hours
  - [ ] Critical security breach
  - [ ] Business operations severely impacted
- [ ] Document rollback steps:
  1. [ ] Announce rollback to stakeholders
  2. [ ] Restore Access database to write mode
  3. [ ] Revert DNS to Access system
  4. [ ] Enable Access for all users
  5. [ ] Export any data entered in web system
  6. [ ] Import to Access (if needed)
  7. [ ] Post-incident review
- [ ] Test rollback procedure (dry run)
- [ ] Estimate rollback time: 30-60 minutes

## Cutover Timeline

### T-7 Days
- [ ] Finalize go-live checklist
- [ ] Confirm all team availability
- [ ] Schedule dry run

### T-3 Days
- [ ] Run dry run of cutover procedure
- [ ] Address any issues found
- [ ] Final communication to users

### T-1 Day
- [ ] Lower DNS TTL
- [ ] Prepare monitoring dashboards
- [ ] Brief support team

### Go-Live Day (Saturday recommended)
| Time | Activity | Owner |
|------|----------|-------|
| 00:00 | Freeze Access database | DBA |
| 00:30 | Begin final data sync | Migration Team |
| 03:00 | Complete validation | QA |
| 04:00 | Update DNS records | DevOps |
| 04:30 | Verify web system live | All |
| 05:00 | Send go-live notice | PM |
| 06:00 | Begin active monitoring | Support Team |
| 24h | Continue monitoring | Support Team |

### T+1 to T+7 Days
- [ ] Daily status calls
- [ ] Monitor for issues
- [ ] Rapid response to problems
- [ ] Gather user feedback
- [ ] Track system metrics

## Communication Plan

### Pre-Cutover
- Email to all users (T-7, T-3, T-1)
- Management briefing
- Support team preparation

### During Cutover
- Real-time updates to stakeholders
- War room chat channel
- Status page updates

### Post-Cutover
- Go-live announcement
- Daily status updates (first week)
- Lessons learned session

## Dependencies
- [ ] UAT completed and signed off
- [ ] Performance testing passed
- [ ] Data validation completed
- [ ] All critical bugs resolved
- [ ] Users trained on new system
- [ ] Support team ready
- [ ] Rollback plan tested

## Risks & Mitigation
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Data sync failure | Critical | Low | Tested procedure, backups ready |
| DNS propagation delays | High | Low | Lower TTL, monitor propagation |
| User resistance/confusion | Medium | Medium | Training, support availability |
| Unexpected critical bug | High | Low | Rollback plan, war room ready |
| Extended downtime | High | Low | Weekend cutover, monitoring |

## Success Criteria
- Cutover completed within scheduled window
- Zero data loss
- < 2 hours of downtime
- All users able to access new system
- No critical issues in first 24 hours
- Management sign-off obtained

## Definition of Done
- [ ] Parallel running completed successfully
- [ ] Discrepancies resolved (or documented)
- [ ] Go-live checklist fully executed
- [ ] Final data sync completed
- [ ] DNS switchover successful
- [ ] New system live and accessible
- [ ] Rollback procedure documented and tested
- [ ] Post-go-live monitoring active
- [ ] Access database decommissioned (T+30 days)

## Related Issues
- [Phase 7] User Acceptance Testing
- [Phase 7] Performance Testing
- [Phase 7] Documentation & Training

---
*Created for Phase 7: Testing & Go-Live*
