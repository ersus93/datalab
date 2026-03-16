# [Phase 1] Create Reference Data Models

**Labels:** `phase-1`, `database`, `backend`, `sqlalchemy`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days

---

## Description

Create SQLAlchemy models for all 9 reference (lookup) tables from the legacy Access database. These tables provide the foundational configuration data required by all other entities in the laboratory management system. Reference data includes laboratory areas, organizations, geographic provinces, product destinations, industry sectors, time periods, measurement units, and sensory evaluation types.

This is a **critical foundation task** - all other models depend on these reference tables through foreign key relationships.

### Tables to Implement

| Table | Records | Description | Priority |
|-------|---------|-------------|----------|
| `areas` | 4 | Laboratory areas (FQ, MB, ES, OS) | Critical |
| `organismos` | 12 | Client organizations/entities | High |
| `provincias` | 4 | Geographic provinces | High |
| `destinos` | 7 | Product destinations (CF, AC, ME, CD, DE, etc.) | High |
| `ramas` | 13 | Industry sectors (Carne, Lácteos, Vegetales, Bebidas, etc.) | High |
| `meses` | 12 | Calendar months for temporal organization | Medium |
| `annos` | 10 | Years configuration for reporting periods | Medium |
| `tipo_es` | 4 | Sensory evaluation types | High |
| `unidades_medida` | 3 | Measurement units | High |

**Total: 73 reference records to migrate**

---

## Acceptance Criteria

### Model Creation
- [ ] Create `Area` model with fields: `id` (PK), `nombre`, `sigla`
- [ ] Create `Organismo` model with fields: `id` (PK), `nombre`
- [ ] Create `Provincia` model with fields: `id` (PK), `nombre`, `sigla`
- [ ] Create `Destino` model with fields: `id` (PK), `nombre`, `sigla`
- [ ] Create `Rama` model with fields: `id` (PK), `nombre`
- [ ] Create `Mes` model with fields: `id` (PK), `nombre`, `sigla`
- [ ] Create `Anno` model with fields: `anno` (PK), `activo`
- [ ] Create `TipoES` model with fields: `id` (PK), `nombre`
- [ ] Create `UnidadMedida` model with fields: `id` (PK), `codigo`, `nombre`

### Constraints & Indexes
- [ ] Add unique constraints on name fields where appropriate
- [ ] Add indexes on frequently queried fields (e.g., `sigla`)
- [ ] Set up appropriate nullable/not-null constraints matching Access schema
- [ ] Add `__repr__` methods for debugging

### Integration
- [ ] Register all models in Flask-SQLAlchemy
- [ ] Create model imports in `app/database/__init__.py`
- [ ] Verify models load correctly with `flask db` commands

### Documentation
- [ ] Add docstrings to all model classes
- [ ] Document field types and constraints
- [ ] Create ERD diagram snippet showing reference tables

---

## Technical Notes

### Access Schema Mapping

```python
# From ACCESS_MIGRATION_ANALYSIS.md

class Area(db.Model):
    """Laboratory areas: FQ (Físico-Químico), MB (Microbiología), 
    ES (Evaluación Sensorial), OS (Otros Servicios)"""
    __tablename__ = 'areas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False)
    
    # Relationships
    ensayos = db.relationship('Ensayo', back_populates='area')

class Organismo(db.Model):
    """Client organizations/entities"""
    __tablename__ = 'organismos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)
    
    # Relationships
    clientes = db.relationship('Cliente', back_populates='organismo')

class Provincia(db.Model):
    """Geographic provinces"""
    __tablename__ = 'provincias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False)
    
    # Relationships
    fabricas = db.relationship('Fabrica', back_populates='provincia')

class Destino(db.Model):
    """Product destinations: CF (Canasta Familiar), AC (Amplio Consumo), 
    ME (Merienda Escolar), CD (Captación Divisas), DE (Destinos Especiales)"""
    __tablename__ = 'destinos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False)
    
    # Relationships
    productos = db.relationship('Producto', back_populates='destino')

class Rama(db.Model):
    """Industry sectors: Carne, Lácteos, Vegetales, Bebidas, etc."""
    __tablename__ = 'ramas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    entradas = db.relationship('Entrada', back_populates='rama')

class Mes(db.Model):
    """Calendar months for temporal organization"""
    __tablename__ = 'meses'
    
    id = db.Column(db.Integer, primary_key=True)  # 1-12
    nombre = db.Column(db.String(20), nullable=False)
    sigla = db.Column(db.String(5), nullable=False)

class Anno(db.Model):
    """Active years for reporting periods"""
    __tablename__ = 'annos'
    
    anno = db.Column(db.String(4), primary_key=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

class TipoES(db.Model):
    """Sensory evaluation types"""
    __tablename__ = 'tipo_es'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    ensayos_es = db.relationship('EnsayoES', back_populates='tipo_es')

class UnidadMedida(db.Model):
    """Measurement units"""
    __tablename__ = 'unidades_medida'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
```

### Field Type Mappings from Access

| Access Type | PostgreSQL | SQLAlchemy |
|-------------|------------|------------|
| COUNTER (Auto) | SERIAL | db.Integer, primary_key=True |
| BYTE | SMALLINT | db.SmallInteger |
| VARCHAR | VARCHAR | db.String(n) |
| BIT | BOOLEAN | db.Boolean |
| DATETIME | TIMESTAMP | db.DateTime |

### File Locations

```
app/
├── database/
│   ├── __init__.py          # Update imports
│   ├── models/
│   │   ├── __init__.py      # Model exports
│   │   ├── reference.py     # <-- NEW: All reference models
│   │   ├── cliente.py         # (existing)
│   │   └── pedido.py          # (existing)
```

### Naming Conventions

- **Spanish names**: Maintain Spanish field names from Access for consistency with user domain
- **Snake_case**: Use Python naming conventions (e.g., `organismo_id` not `OrganismoId`)
- **Singular table names**: SQLAlchemy convention, Alembic will handle plurals

---

## Dependencies

**Blocked by:** None (this is a foundational task)

**Blocks:**
- Issue #2: [Phase 1] Create Master Data Models (Clientes, Fabricas, Productos need FKs to these tables)
- Issue #3: [Phase 1] Create Test Catalog Models (Ensayos needs Area FK)
- Issue #4: [Phase 1] Database Migration Scripts (depends on all models)

---

## Related Documentation

- `docs/PRD.md` Section 2.3.1: Reference Data tables
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Lines 68-143: Complete schema for all reference tables
- `plans/MIGRATION_PLAN.md` Phase 1.1: Database Schema Creation

---

## Testing Requirements

- [ ] Verify all models can be instantiated in Flask shell
- [ ] Check that foreign key relationships work correctly
- [ ] Confirm table names match planned PostgreSQL schema
- [ ] Test that indexes are created correctly

---

## Definition of Done

- [ ] All 9 models created and committed
- [ ] Models registered with SQLAlchemy
- [ ] Code review completed
- [ ] No breaking changes to existing models
- [ ] Ready for Alembic migration generation
