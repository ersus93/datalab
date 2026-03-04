# Development Workflow Guidelines

This document defines the development workflow for the DataLab project to ensure consistent collaboration and code quality.

---

## 1. Branch Naming Conventions

### 1.1 Main Branches
| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Production-ready code | Protected - PR required |
| `develop` | Integration branch for features | Protected - PR required |

### 1.2 Feature Branches
All feature branches must follow this naming convention:

```
<type>/<ticket-id>-<short-description>
```

**Types:**
| Prefix | Use For | Example |
|--------|---------|---------|
| `feature/` | New features | `feature/DL-123-client-crud` |
| `bugfix/` | Bug fixes | `bugfix/DL-456-login-error` |
| `hotfix/` | Critical production fixes | `hotfix/DL-789-security-patch` |
| `refactor/` | Code refactoring | `refactor/DL-101-service-layer` |
| `docs/` | Documentation updates | `docs/DL-202-api-guide` |
| `chore/` | Maintenance tasks | `chore/DL-303-update-deps` |

### 1.3 Naming Rules
- Use lowercase letters only
- Use hyphens (-) to separate words
- Keep description under 5 words
- Include ticket ID when applicable
- Be descriptive but concise

**Examples:**
```bash
# Good
feature/DL-15-add-client-search
bugfix/DL-22-fix-pagination
refactor/DL-30-extract-validators

# Bad
feature/new_stuff          # No ticket, underscores
fix-bug                    # No type prefix, too vague
Feature-Add-Client-Form    # Wrong case, too long
```

---

## 2. Commit Message Format

We follow the **Conventional Commits** specification for clear commit history.

### 2.1 Format
```
<type>(<scope>): <subject>

<body> (optional)

<footer> (optional)
```

### 2.2 Types
| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(clientes): add search functionality` |
| `fix` | Bug fix | `fix(pedidos): correct status update` |
| `docs` | Documentation only | `docs(readme): update setup instructions` |
| `style` | Code style (formatting) | `style(models): fix indentation` |
| `refactor` | Code refactoring | `refactor(services): extract common logic` |
| `test` | Adding/updating tests | `test(clientes): add unit tests` |
| `chore` | Maintenance tasks | `chore(deps): update flask version` |
| `perf` | Performance improvements | `perf(queries): add database indexes` |

### 2.3 Scopes
Common scopes for DataLab:
- `clientes` - Client management
- `pedidos` - Order management
- `ordenes` - Work orders
- `dashboard` - Dashboard and metrics
- `models` - Database models
- `api` - API endpoints
- `ui` - User interface
- `docs` - Documentation
- `config` - Configuration

### 2.4 Subject Rules
- Use imperative mood ("Add" not "Added" or "Adds")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### 2.5 Examples
```bash
# Feature commit
feat(clientes): add client search with filters

Implement search functionality for clients allowing
filtering by name, code, and status.

Closes DL-123

# Bug fix commit
fix(pedidos): resolve status transition bug

Prevent orders from transitioning to invalid states.
Add validation before status update.

Fixes DL-456

# Documentation commit
docs(api): document order endpoints

Add OpenAPI-style documentation for all order
management API endpoints.

# Refactor commit
refactor(models): extract base model mixin

Create BaseModel mixin with common timestamp fields
to reduce duplication across models.
```

---

## 3. Pull Request Process

### 3.1 Before Creating a PR
- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] Self-review completed
- [ ] Related issue linked
- [ ] Documentation updated if needed

### 3.2 PR Title Format
```
[<type>] <ticket-id>: <description>
```

Examples:
```
[Feature] DL-123: Add client search functionality
[Bugfix] DL-456: Fix order status transition
[Refactor] DL-789: Extract validation logic
```

### 3.3 PR Description Template
```markdown
## Description
Brief description of changes

## Related Issue
Fixes DL-XXX

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console errors

## Screenshots (if applicable)
Add screenshots for UI changes

## Testing Instructions
1. Step 1
2. Step 2
3. Expected result
```

### 3.4 Review Requirements
- Minimum **1 approval** required
- All review comments must be resolved
- CI checks must pass
- No merge conflicts

### 3.5 Reviewer Guidelines
**As a reviewer, check:**
- Code correctness and logic
- Adherence to coding standards
- Test coverage
- Performance implications
- Security considerations
- Documentation completeness

**Review comments should be:**
- Constructive and specific
- Categorized as:
  - `nit:` Minor suggestions
  - `question:` Need clarification
  - `blocking:` Must fix before merge

### 3.6 Merging
- Use **Squash and Merge** for feature branches
- Use **Merge Commit** only for release branches
- Delete feature branches after merging
- Ensure commit message follows convention

---

## 4. Issue Creation Guidelines

### 4.1 Issue Types
| Label | Use For | Example |
|-------|---------|---------|
| `bug` | Something is broken | Form validation not working |
| `feature` | New functionality | Add export to PDF |
| `enhancement` | Improve existing feature | Better error messages |
| `tech-debt` | Refactoring needed | Extract duplicate code |
| `docs` | Documentation needed | API documentation |

### 4.2 Bug Report Template
```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.2.3]

**Additional Context**
Any other information
```

### 4.3 Feature Request Template
```markdown
**Description**
Clear description of the feature

**User Story**
As a [role], I want [feature] so that [benefit]

**Acceptance Criteria**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Priority**
High / Medium / Low

**Estimated Effort**
Story points or time estimate

**Additional Context**
Mockups, references, etc.
```

### 4.4 Issue Labels
Use labels to categorize issues:
- **Priority:** `priority-high`, `priority-medium`, `priority-low`
- **Type:** `bug`, `feature`, `enhancement`, `tech-debt`
- **Component:** `clientes`, `pedidos`, `ordenes`, `dashboard`, `api`, `ui`
- **Status:** `ready`, `in-progress`, `blocked`, `review`

---

## 5. Development Workflow Summary

### 5.1 Daily Workflow
```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/DL-123-add-search

# 3. Make changes and commit
git add .
git commit -m "feat(clientes): add search functionality"

# 4. Push branch
git push -u origin feature/DL-123-add-search

# 5. Create Pull Request
# Use GitHub/GitLab UI

# 6. After approval, merge and cleanup
git checkout develop
git pull origin develop
git branch -d feature/DL-123-add-search
```

### 5.2 Release Workflow
```bash
# 1. Create release branch from develop
git checkout -b release/v1.0.0

# 2. Version bump and final fixes
# ...

# 3. Merge to main
git checkout main
git merge release/v1.0.0
git tag v1.0.0

# 4. Merge back to develop
git checkout develop
git merge release/v1.0.0
```

---

## 6. Communication Guidelines

### 6.1 Daily Standups
- What did you work on yesterday?
- What are you working on today?
- Any blockers?

### 6.2 Code Review Notifications
- Tag relevant team members
- Respond to reviews within 24 hours
- Resolve discussions before merging

### 6.3 Emergency Hotfixes
1. Create branch from `main`: `hotfix/DL-XXX-description`
2. Fix the issue
3. PR to `main` with expedited review
4. Merge and tag new version
5. Cherry-pick to `develop`

---

*Last Updated:* March 2026
