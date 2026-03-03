# Phased Workflow Strategy

A comprehensive guide for managing multi-phase projects using local-first issue management with phased GitHub publishing.

---

## 1. Strategy Overview

This workflow implements a **phased, local-first approach** to issue management that keeps the team focused while maintaining flexibility for future planning.

### Core Principle

**Create ALL issues locally first, then publish phase by phase.**

### Workflow Flow

```
Phase 1: Plan & Create (Local) ──► Develop Phase 1 ──► Publish Phase 1 ──► Merge to Main
                                          │
                                          ▼
Phase 2: Plan & Create (Local) ◄── Develop Phase 2 ◄── Publish Phase 2 ◄── Merge to Main
                                          │
                                          ▼
                                  [Continue for Phases 3-7...]
```

### Detailed Steps

1. **Phase Planning**: Create ALL issues for ALL phases locally in `docs/github-issues/`
2. **Phase Development**: Work only on current phase issues in the dev branch
3. **Phase Completion**: When Phase N is complete, publish only Phase N issues to GitHub
4. **Phase Merge**: Create PR from dev → main, merge Phase N code
5. **Phase Release**: Tag and release v0.N.0
6. **Next Phase**: Publish Phase N+1 issues to GitHub and repeat

### Why This Approach?

- **Prevents premature work**: Team can't start Phase 3 if issues aren't published yet
- **Maintains clean main**: Only completed, tested phase code reaches main
- **Reduces cognitive load**: Team sees only current phase issues in GitHub
- **Enables iteration**: Future phase issues can be refined locally before publishing

---

## 2. Benefits of This Approach

### Issue Management Benefits

| Benefit | Description |
|---------|-------------|
| **Local Modification** | Future phase issues can be edited, reorganized, or rewritten before publishing |
| **Reduced Overwhelm** | Team members see only current phase issues in GitHub (typically 5-15 issues vs 50+) |
| **Prevent Premature Work** | No one can accidentally start Phase 4 work if issues aren't published yet |
| **Progress Tracking** | Clear phase boundaries make it easy to see exactly where the project stands |
| **Stakeholder Communication** | External stakeholders see progress phase by phase, not a overwhelming backlog |

### Technical Benefits

| Benefit | Description |
|---------|-------------|
| **Reduced Merge Conflicts** | Smaller, phase-focused PRs are easier to review and merge |
| **Phase-Based Testing** | Each phase can be fully tested before moving to the next |
| **Incremental Releases** | Each phase can be deployed independently if needed |
| **Clean Rollback** | If a phase has issues, you only rollback that phase's changes |
| **Parallel Preparation** | While Phase N is being coded, Phase N+1 issues can be refined locally |

### Team Benefits

| Benefit | Description |
|---------|-------------|
| **Focused Development** | Team concentrates on one phase at a time |
| **Clear Priorities** | No confusion about what to work on next |
| **Better Estimation** | Phase-based planning improves time estimates |
| **Knowledge Transfer** | Phase handoff meetings ensure context is shared |
| **Reduced Context Switching** | Developers stay in one phase's context longer |

---

## 3. Directory Structure for Issues

```
docs/github-issues/
├── phase1/                    # Current phase - published to GitHub
│   ├── README.md              # Phase 1 overview and progress
│   ├── issue-01-setup.md      # Individual issues
│   ├── issue-02-config.md
│   └── issue-03-database.md
│
├── phase2/                    # Next phase - local only
│   ├── README.md              # Phase 2 overview (DRAFT)
│   ├── issue-04-auth.md
│   ├── issue-05-api.md
│   └── issue-06-tests.md
│
├── phase3/                    # Future phase - local only
│   ├── README.md
│   └── issue-*.md
│
├── phase4/
│   └── ...
│
├── phase5/
│   └── ...
│
├── phase6/
│   └── ...
│
└── phase7/
    └── ...
```

### Directory Structure Details

#### Phase README.md Template

Each phase directory contains a `README.md`:

```markdown
# Phase N: [Phase Name]

## Status
- **Current State**: DRAFT / READY / PUBLISHED / COMPLETE
- **GitHub Milestone**: Phase N (created when published)

## Phase Goals
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

## Issues Summary
| Issue | Title | Status | Assignee |
|-------|-------|--------|----------|
| #1 | Setup project | Done | @alice |
| #2 | Configure CI | In Progress | @bob |

## Dependencies
- Depends on: Phase N-1 (must be complete)
- Blocks: Phase N+1 (cannot start until this is done)

## Definition of Done
- [ ] All issues resolved
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Deployed to staging
```

#### Issue File Naming Convention

```
issue-{NN}-{short-description}.md
```

Examples:
- `issue-01-project-setup.md`
- `issue-02-ci-configuration.md`
- `issue-03-database-schema.md`

#### Issue File Template

```markdown
---
title: "[Phase N] Issue Title"
labels: ["enhancement", "phase-N"]
milestone: "Phase N"
assignees: []
---

## Description
Clear description of what needs to be done.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
Any implementation details, considerations, or notes.

## Dependencies
- Blocked by: #X
- Blocks: #Y

## Estimated Effort
- Story Points: X
- Estimated Hours: Y
```

---

## 4. Publishing Workflow Per Phase

### Phase 1: Complete Development

Before publishing any issues, ensure:

- [ ] All Phase N issues are resolved in the dev branch
- [ ] All tests are passing (`npm test`, `pytest`, etc.)
- [ ] Code coverage meets minimum threshold
- [ ] Documentation is updated (README, API docs, etc.)
- [ ] No linting errors (`npm run lint`, `ruff check`, etc.)
- [ ] Type checking passes (`tsc --noEmit`, `mypy`, etc.)
- [ ] Manual QA completed (if applicable)

**Verification Commands:**

```bash
# Run all checks before proceeding
npm run lint
npm run typecheck
npm test
npm run test:coverage
npm run build
```

### Phase 2: Create GitHub Issues

#### Option A: Manual Copy (Recommended for 1-5 issues)

1. Open `docs/github-issues/phaseN/issue-*.md`
2. Copy title and body content
3. Go to GitHub → Issues → New Issue
4. Paste content
5. Apply labels: `enhancement`, `phase-N`
6. Set milestone: "Phase N"
7. Assign to team members
8. Create issue
9. Update local file with GitHub issue number:
   ```markdown
   ---
   github_issue: #42
   status: published
   ---
   ```

#### Option B: GitHub CLI (Recommended for 5+ issues)

```bash
# Create issue from file
gh issue create \
  --title "[Phase 1] Setup Project Structure" \
  --body-file docs/github-issues/phase1/issue-01-setup.md \
  --label "enhancement,phase-1" \
  --milestone "Phase 1" \
  --assignee "@username"
```

#### Creating a Milestone

```bash
# Create milestone for the phase
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  --field title="Phase 1" \
  --field state="open" \
  --field description="Foundation and Core Setup"
```

### Phase 3: Merge to Main

#### Step 1: Prepare the PR

```bash
# Ensure dev branch is up to date
git checkout dev
git pull origin dev

# Create PR to main
git checkout main
git pull origin main
git checkout dev

# Create PR (do this via GitHub UI or gh CLI)
gh pr create \
  --base main \
  --head dev \
  --title "Phase 1: Foundation and Core Setup" \
  --body-file .github/PULL_REQUEST_TEMPLATE/phase-completion.md
```

#### Step 2: PR Requirements

The PR should:
- Include ONLY Phase 1 changes
- Exclude `docs/github-issues/phase2/` and beyond
- Reference all Phase 1 GitHub issues (`Closes #1, closes #2, closes #3`)
- Include updated CHANGELOG.md
- Pass all CI checks

#### Step 3: Code Review

- At least 1-2 reviewers must approve
- All CI checks must pass
- All discussions must be resolved

#### Step 4: Merge

```bash
# Squash and merge via GitHub UI, or:
git checkout main
git merge --no-ff dev -m "Phase 1: Foundation and Core Setup

- Project structure and tooling
- CI/CD pipeline
- Database schema
- Basic API endpoints

Closes #1, closes #2, closes #3"
```

### Phase 4: Tag Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Phase 1: Foundation and Core Setup

Features:
- Project initialization
- CI/CD pipeline
- Database schema
- Basic API

See CHANGELOG.md for details"

# Push tag
git push origin v0.1.0

# Create GitHub release
gh release create v0.1.0 \
  --title "Phase 1: Foundation and Core Setup" \
  --notes-file CHANGELOG.md \
  --latest
```

### Phase 5: Prepare Next Phase

```bash
# Update Phase 2 README
# Change status from DRAFT to READY
# Remove any DRAFT markers from issues

# Create milestone for Phase 2
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  --field title="Phase 2" \
  --field state="open"
```

---

## 5. Git Workflow Commands

### Publishing Issues to GitHub

#### Single Issue

```bash
# Read issue content and create
cat docs/github-issues/phase1/issue-01.md | gh issue create \
  --title "[Phase 1] Setup Project" \
  --body - \
  --label "enhancement,phase-1" \
  --milestone "Phase 1"
```

#### Batch Publish (All Phase N Issues)

```bash
#!/bin/bash
# publish-phase.sh - Publish all issues in a phase

PHASE=$1
PHASE_DIR="docs/github-issues/phase${PHASE}"

if [ ! -d "$PHASE_DIR" ]; then
  echo "Error: $PHASE_DIR not found"
  exit 1
fi

for issue in "$PHASE_DIR"/issue-*.md; do
  if [ -f "$issue" ]; then
    title=$(head -n 1 "$issue" | sed 's/^# //')
    echo "Publishing: $title"
    
    gh issue create \
      --title "$title" \
      --body-file "$issue" \
      --label "phase-${PHASE}" \
      --milestone "Phase ${PHASE}"
  fi
done

echo "Phase $PHASE issues published!"
```

Usage:
```bash
chmod +x publish-phase.sh
./publish-phase.sh 1
```

### Creating Phase-Based PRs

```bash
# Create PR for phase completion
gh pr create \
  --base main \
  --head dev \
  --title "Phase N: [Phase Name]" \
  --body "## Summary
Complete implementation of Phase N.

## Changes
- Feature A
- Feature B
- Feature C

## Issues Closed
Closes #X, closes #Y, closes #Z

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual QA complete

## Checklist
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated"
```

### Tagging Releases

```bash
# Standard version tag
git tag -a v0.N.0 -m "Phase N: [Phase Name]"

# Hotfix tag
git tag -a v0.N.1-hotfix -m "Hotfix for Phase N"

# Push tags
git push origin --tags

# List tags
git tag -l

# Delete local tag
git tag -d v0.N.0

# Delete remote tag
git push --delete origin v0.N.0
```

### Switching Between Phases

```bash
# Start work on new phase
git checkout -b phase-2-work

# Or if continuing on dev
git checkout dev

# View current phase status
cat docs/github-issues/current-phase.txt

# Update current phase
echo "2" > docs/github-issues/current-phase.txt
```

### Syncing Local Issues with GitHub

```bash
# Update local issue with GitHub number after publishing
# Add to top of issue-*.md:
# ---
# github_issue: #42
# github_url: https://github.com/owner/repo/issues/42
# ---

# List all open phase issues
gh issue list --label "phase-1" --state open

# Close completed issues in bulk
gh issue list --label "phase-1" --state open --json number | \
  jq -r '.[].number' | \
  xargs -I {} gh issue close {} --comment "Completed in Phase 1"
```

---

## 6. Issue Lifecycle

```
┌─────────────┐
│ Local Draft │◄─────────────────────────────────────┐
└──────┬──────┘                                      │
       │                                             │
       │ 1. Phase N-1 complete                       │
       ▼                                             │
┌──────────────────┐                                 │
│ Published to     │                                 │
│ GitHub           │                                 │
│ (with labels &   │                                 │
│  milestone)      │                                 │
└──────┬───────────┘                                 │
       │                                             │
       │ 2. Developer assigns self                   │
       ▼                                             │
┌──────────────────┐                                 │
│ In Progress      │                                 │
│ (branch created) │                                 │
└──────┬───────────┘                                 │
       │                                             │
       │ 3. Work complete, PR opened                 │
       ▼                                             │
┌──────────────────┐                                 │
│ In Review        │                                 │
│ (PR pending)     │                                 │
└──────┬───────────┘                                 │
       │                                             │
       │ 4. PR merged                                │
       ▼                                             │
┌──────────────────┐                                 │
│ Done             │─────────────────────────────────┘
│ (closed)         │ 5. If changes needed,
└──────────────────┘    update local file
```

### State Transitions

| From | To | Trigger | Action |
|------|-----|---------|--------|
| Local Draft | Published | Phase N-1 complete | Create GitHub issue |
| Published | In Progress | Developer starts | Assign issue, create branch |
| In Progress | In Review | Work complete | Open PR, link issue |
| In Review | Done | PR merged | Close issue, tag release |
| Done | Local Draft | Changes needed | Update local file for next iteration |

---

## 7. Managing Changes to Future Phases

### Scenario 1: Requirement Change

**Situation**: Business requirement changes for Phase 3 while Phase 1 is in progress.

**Process**:
1. Update `docs/github-issues/phase3/issue-XX.md`
2. Add note at bottom:
   ```markdown
   ## Change Log
   - 2024-01-15: Updated acceptance criteria due to requirement change
   - 2024-01-20: Added new task for email notifications
   ```
3. Update Phase 3 README.md if scope changes significantly

### Scenario 2: Technical Discovery

**Situation**: While working on Phase 2, you discover something that affects Phase 4.

**Process**:
1. Create/update `docs/github-issues/phase4/issue-XX.md`
2. Document the discovery and required changes
3. Add dependency note in affected issues
4. Update Phase 4 README with technical note

### Scenario 3: Phase Reprioritization

**Situation**: Phase 5 needs to happen before Phase 4.

**Process**:
1. Rename directories:
   ```bash
   mv docs/github-issues/phase4 docs/github-issues/temp
   mv docs/github-issues/phase5 docs/github-issues/phase4
   mv docs/github-issues/temp docs/github-issues/phase5
   ```
2. Update all issue files with new phase numbers
3. Update all internal references
4. Update README.md files

### Scenario 4: Issue Split/Merge

**Splitting an Issue**:
1. Rename original: `issue-05-auth.md` → `issue-05a-login.md`
2. Create new: `issue-05b-signup.md`
3. Update both with proper scope
4. Update Phase README

**Merging Issues**:
1. Combine content into `issue-05-auth.md`
2. Delete `issue-06-signup.md`
3. Add note about merge to issue file
4. Update Phase README

---

## 8. Team Coordination

### Daily Workflow

**Developers**:
1. Check GitHub for assigned Phase N issues
2. Work in dev branch on assigned issues
3. Update issue status in GitHub as you progress

**Tech Lead**:
1. Monitor Phase N progress in GitHub
2. Refine Phase N+1 issues locally based on learnings
3. Prepare for phase transition

### Phase Handoff Meeting

**When**: When Phase N-1 is complete and Phase N issues are being published

**Attendees**: All team members

**Agenda**:
1. Phase N-1 retrospective (5 min)
   - What went well?
   - What could be improved?
2. Phase N overview (10 min)
   - Goals and scope
   - Key technical decisions
   - Dependencies and risks
3. Issue assignment (10 min)
   - Assign Phase N issues to team members
   - Discuss blockers and dependencies
4. Questions (5 min)

### Communication Channels

| Channel | Purpose | Content |
|---------|---------|---------|
| GitHub Issues | Current phase work | Active issues, comments, PRs |
| Local Issues | Future phase planning | Draft issues, refinements |
| Slack/Teams | Daily coordination | Quick questions, blockers |
| Phase Handoff | Phase transitions | Planning, assignment, context |
| Sprint Planning | Weekly coordination | Phase progress, adjustments |

### Visibility Rules

- **Everyone can see**: Current phase issues (GitHub)
- **Tech Lead + PM can see**: Next 2 phases (local files)
- **Full plan exists in**: All 7 phases (local files)

---

## 9. Rollback Strategy

### When to Rollback

- Critical bug found in production after phase release
- Business decision to revert a feature
- Technical issue requiring immediate reversal

### Rollback Process

#### Step 1: Assess Impact

```bash
# Check what was in the release
git log v0.N.0 --oneline

# See what files changed
git diff v0.{N-1}.0 v0.N.0 --stat

# Review the actual changes
git diff v0.{N-1}.0 v0.N.0
```

#### Step 2: Create Hotfix Branch

```bash
# From main, create hotfix branch
git checkout main
git pull origin main
git checkout -b hotfix/phase-N-rollback
```

#### Step 3: Revert Changes

```bash
# Revert the entire merge commit
git revert -m 1 <merge-commit-hash>

# Or revert specific commits
git revert <commit-hash-1>
git revert <commit-hash-2>
```

#### Step 4: Update Issues

1. Reopen relevant GitHub issues
2. Add rollback note:
   ```
   ## Rollback
   - Date: 2024-01-20
   - Reason: Critical bug in authentication flow
   - Action: Feature reverted, will be fixed in Phase N.1
   ```

3. Update local issue files with rollback notes

#### Step 5: Deploy Hotfix

```bash
# Tag hotfix
git tag -a v0.N.1-hotfix -m "Hotfix: Rollback Phase N features"

# Push and deploy
git push origin hotfix/phase-N-rollback
git push origin v0.N.1-hotfix

# Create PR to main
gh pr create --base main --head hotfix/phase-N-rollback
```

#### Step 6: Update Local Files

1. Update `docs/github-issues/phaseN/README.md`:
   ```markdown
   ## Rollback History
   - v0.N.0: Initial release (rolled back)
   - v0.N.1-hotfix: Rolled back due to [reason]
   ```

2. Update affected issue files with rollback context

### Post-Rollback Actions

1. **Root Cause Analysis**: Document why rollback was needed
2. **Fix Development**: Create fix in dev branch
3. **Re-release**: Deploy fixed version as v0.N.2
4. **Process Improvement**: Update workflow if needed to prevent similar issues

### Rollback Checklist

- [ ] Impact assessment complete
- [ ] Hotfix branch created
- [ ] Changes reverted
- [ ] Tests passing
- [ ] GitHub issues updated
- [ ] Local issue files updated
- [ ] Hotfix tagged and released
- [ ] Team notified
- [ ] Post-mortem scheduled

---

## Quick Reference

### Common Commands

```bash
# Publish phase issues
./scripts/publish-phase.sh 1

# Create phase milestone
gh api repos/{owner}/{repo}/milestones --method POST --field title="Phase 1"

# Create phase PR
gh pr create --base main --head dev --title "Phase N: ..."

# Tag release
git tag -a v0.N.0 -m "Phase N"
git push origin v0.N.0

# List phase issues
gh issue list --label "phase-1"
```

### File Locations

| File | Purpose |
|------|---------|
| `docs/github-issues/phaseN/` | Phase N issue files |
| `docs/github-issues/phaseN/README.md` | Phase overview |
| `docs/github-issues/current-phase.txt` | Current phase tracker |
| `plans/phased-workflow-strategy.md` | This document |

### Phase Checklist Template

```markdown
## Phase N Checklist

### Before Publishing
- [ ] All issues written and reviewed
- [ ] Technical approach approved
- [ ] Dependencies identified

### During Development
- [ ] Issues assigned to team
- [ ] Development in progress
- [ ] Regular status updates

### Before Publishing to GitHub
- [ ] All issues resolved
- [ ] Tests passing
- [ ] Documentation updated

### After Publishing
- [ ] Issues created in GitHub
- [ ] Milestone created
- [ ] Issues assigned

### Merge to Main
- [ ] PR created
- [ ] Code reviewed
- [ ] PR merged

### Release
- [ ] Version tagged
- [ ] Release notes created
- [ ] Deployed to production

### Next Phase Prep
- [ ] Phase N+1 issues reviewed
- [ ] DRAFT markers removed
- [ ] Team briefed
```

---

## Conclusion

This phased workflow strategy enables:

- **Focused development** on one phase at a time
- **Flexible planning** with local issue management
- **Clean releases** with phase-based tagging
- **Reduced confusion** for team members
- **Better stakeholder communication**

By keeping future phases local and only publishing the current phase to GitHub, teams can maintain focus while still having a comprehensive plan for the entire project.

---

*Document Version: 1.0*
*Last Updated: 2024-01-15*
*Maintained by: Tech Lead*
