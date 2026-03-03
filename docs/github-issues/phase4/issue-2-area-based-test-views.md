# [Phase 4] Area-Based Test Views

## Description
Create specialized views for each laboratory area to manage their specific test catalogs and assignments. Each area has different types of tests, pricing models, and workflows.

## Area Specifications

### 1. FQ (Fisicoquímica) - Physical Chemistry
- **Ensayos**: 143 different tests
- **Characteristics**: Priced tests, quantitative results
- **Examples**: pH, density, viscosity, moisture content
- **View Features**:
  - Display test prices
  - Sort/filter by test category
  - Bulk price updates
  - Test assignment with cost preview

### 2. MB (Microbiología) - Microbiology
- **Ensayos**: Subset of general tests
- **Characteristics**: Colony counts, presence/absence tests
- **Examples**: Total plate count, coliforms, pathogens
- **View Features**:
  - Incubation period tracking
  - Colony count input
  - Binary (positive/negative) result options
  - Media lot tracking

### 3. ES (Sensorial) - Sensory Analysis
- **EnsayosES**: 29 specialized sensory tests
- **Characteristics**: Panel-based evaluation
- **Examples**: Taste tests, odor assessment, visual inspection
- **View Features**:
  - Panelist assignment
  - Scoring sheets
  - Sensory evaluation forms
  - Statistical aggregation

### 4. OS (Otros Servicios) - Other Services
- **Ensayos**: Subset for non-routine services
- **Characteristics**: Custom pricing, specialized work
- **Examples**: Consulting, special sampling, external lab coordination
- **View Features**:
  - Custom pricing entry
  - Service description
  - Time tracking

## Requirements

### 1. Tabbed Interface
```
┌─────────────────────────────────────────────────┐
│ [FQ: 143] [MB: XX] [ES: 29] [OS: XX]            │
├─────────────────────────────────────────────────┤
│                                                 │
│ Area-specific content based on selected tab     │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2. FQ View Components
- Test catalog with prices
- Price editing capability (with permissions)
- Test assignment workflow
- Cost summary per sample

### 3. MB View Components
- Microbiology-specific test list
- Colony count input fields
- Result interpretation (acceptable/unacceptable)
- Media preparation tracking

### 4. ES View Components
- Sensory test catalog
- Panelist management
- Evaluation form generation
- Results aggregation dashboard

### 5. OS View Components
- Custom service entry
- Hourly rate calculation
- External service markup
- Invoice notes

## Acceptance Criteria
- [ ] Tabbed navigation for 4 areas implemented
- [ ] FQ view displays 143 tests with prices
- [ ] MB view shows microbiology-specific tests
- [ ] ES view displays 29 EnsayosES
- [ ] OS view for other services
- [ ] Area-specific assignment workflows
- [ ] Role-based access to areas
- [ ] Mobile-responsive design

## Technical Notes
- Use URL routing: `/lab/fq/`, `/lab/mb/`, `/lab/es/`, `/lab/os/`
- Permission groups: `fq_tech`, `mb_tech`, `es_panelist`, `os_admin`
- Cache area test lists for performance
- Different form templates per area

## Labels
`phase-4`, `testing`, `laboratory`, `ui/ux`, `frontend`

## Estimated Effort
**Story Points**: 8
**Time Estimate**: 3-4 days
