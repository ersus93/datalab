# [Phase 1] Create Test Catalog Models

**Labels:** `phase-1`, `database`, `backend`, `sqlalchemy`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days
**Depends on:** Issue #1 ([Phase 1] Create Reference Data Models)

---

## Description

Create SQLAlchemy models for the test catalog system that defines all laboratory tests available for assignment to samples. The test catalog is split into two main categories:

1. **Ensayos (Físico-Químico)** - 143 physical-chemical tests for the FQ (Físico-Químico) and MB (Microbiología) areas
2. **EnsayosES (Evaluación Sensorial)** - 29 sensory evaluation tests for the ES (Evaluación Sensorial) area

Additionally, create the linking table `EnsayosXProductos` that associates tests with specific products.

### Laboratory Areas Supported

| Area ID | Code | Name | Test Count |
|---------|------|------|------------|
| 1 | FQ | Físico-Químico | 143 |
| 2 | MB | Microbiología | subset of 143 |
| 3 | ES | Evaluación Sensorial | 29 |
| 4 | OS | Otros Servicios | subset of 143 |

### Data Volume
| Table | Records | Description |
|-------|---------|-------------|
| `ensayos` | 143 | Physical-chemical tests with pricing |
| `ensayos_es` | 29 | Sensory evaluation tests with pricing |
| `ensayos_x_productos` | 0 | Test-product associations (currently empty in Access) |

**Total: 172 test definitions + linking table**

---

## Acceptance Criteria

### Model Creation

#### Ensayo Model (Physical-Chemical Tests)
- [ ] Create `Ensayo` model with all fields from Access:
  - `id` (PK, matches Access IdEns INTEGER)
  - `nombre_oficial` (VARCHAR 500, official test name)
  - `nombre_corto` (VARCHAR 200, short name for UI)
  - `area_id` (FK to Areas, required, defaults to 1 for FQ)
  - `precio` (DECIMAL 10,2, test price for billing)
  - `unidad_medida` (VARCHAR 10, e.g., "USD", "%")
  - `activo` (Boolean, default True - whether test is offered)
  - `es_ensayo` (Boolean, default True - flag for test vs. service)
  - `creado_en` (DateTime, auto)
- [ ] Add index on `area_id` for area-filtered queries
- [ ] Add index on `activo` for filtering active tests
- [ ] Add index on `precio` for billing reports

#### EnsayoES Model (Sensory Evaluation Tests)
- [ ] Create `EnsayoES` model with all fields from Access:
  - `id` (PK, matches Access IdEnsES INTEGER)
  - `nombre_oficial` (VARCHAR 500, official test name)
  - `nombre_corto` (VARCHAR 200, short name for UI)
  - `area_id` (FK to Areas, required, defaults to 3 for ES)
  - `tipo_es_id` (FK to TipoES, sensory evaluation type)
  - `precio` (DECIMAL 10,2, test price)
  - `unidad_medida` (VARCHAR 10)
  - `activo` (Boolean, default True)
  - `creado_en` (DateTime, auto)
- [ ] Add index on `tipo_es_id` for type-filtered queries

#### EnsayoXProducto Model (Linking Table)
- [ ] Create `EnsayoXProducto` linking table:
  - `producto_id` (FK to Productos, PK component)
  - `ensayo_id` (FK to Ensayos, PK component)
  - Composite primary key on `(producto_id, ensayo_id)`
  - `creado_en` (DateTime, auto)
- [ ] Add index on `producto_id` for product test lookups
- [ ] Add index on `ensayo_id` for test product lookups

### Relationships

#### Ensayo Relationships
- [ ] `area` -> many-to-one with `Area`
- [ ] `detalles` -> one-to-many with `DetalleEnsayo`
- [ ] `productos` -> many-to-many with `Producto` (via linking table)
- [ ] `utilizados` -> one-to-many with `Utilizado` (billing records)

#### EnsayoES Relationships
- [ ] `area` -> many-to-one with `Area` (typically ES area)
- [ ] `tipo_es` -> many-to-one with `TipoES`
- [ ] Consider if ES tests need separate detail tracking

#### Producto Relationships (from Issue #2)
- [ ] Update to add: `ensayos` -> many-to-many with `Ensayo`
- [ ] Update to add: `ensayos_es` -> many-to-many with `EnsayoES` (if applicable)

### Constraints & Validation

- [ ] Ensure `nombre_oficial` cannot be empty (required field)
- [ ] Ensure `precio` is non-negative (DECIMAL 10,2)
- [ ] Add check: `area_id` must be 1, 2, or 4 for Ensayo (FQ, MB, OS)
- [ ] Add check: `area_id` must be 3 for EnsayoES (ES area)
- [ ] Ensure linking table prevents duplicate associations
- [ ] Add `__repr__` methods: `<Ensayo 1: pH (FQ) - $50.00>`

### Helper Methods

- [ ] Add `get_precio_formateado()` - returns formatted price string
- [ ] Add `get_nombre_completo()` - returns "Nombre Corto (Oficial)"
- [ ] Add class method `get_activos_por_area(area_id)` - query active tests by area
- [ ] Add class method `get_con_precio()` - returns tests with pricing info

---

## Technical Notes

### Access Schema Mapping

```python
# From ACCESS_MIGRATION_ANALYSIS.md Lines 235-266

class Ensayo(db.Model):
    """
    Physical-chemical tests for FQ/MB/OS areas.
    
    Access Mapping:
    - IdEns (INTEGER) -> id (PK)
    - NomOfic (VARCHAR) -> nombre_oficial
    - NomEns (VARCHAR) -> nombre_corto
    - IdArea (INTEGER) -> area_id (FK, typically 1 for FQ)
    - Precio (CURRENCY) -> precio (DECIMAL)
    - UM (VARCHAR) -> unidad_medida
    - Activo (BIT) -> activo
    - EsEnsayo (BIT) -> es_ensayo
    """
    __tablename__ = 'ensayos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_oficial = db.Column(db.String(500), nullable=False)
    nombre_corto = db.Column(db.String(200), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=True)
    unidad_medida = db.Column(db.String(10), default='USD')
    activo = db.Column(db.Boolean, default=True, nullable=False)
    es_ensayo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    area = db.relationship('Area', back_populates='ensayos')
    detalles = db.relationship('DetalleEnsayo', back_populates='ensayo')
    productos = db.relationship('Producto', secondary='ensayos_x_productos',
                                 back_populates='ensayos')
    utilizados = db.relationship('Utilizado', back_populates='ensayo')
    
    def __repr__(self):
        return f'<Ensayo {self.id}: {self.nombre_corto} ({self.area.sigla if self.area else "?"})>'
    
    def get_precio_formateado(self):
        if self.precio:
            return f"{self.unidad_medida} {self.precio:.2f}"
        return "N/A"
    
    @classmethod
    def get_activos_por_area(cls, area_id):
        return cls.query.filter_by(area_id=area_id, activo=True).all()


class EnsayoES(db.Model):
    """
    Sensory evaluation tests for ES area.
    
    Access Mapping:
    - IdEnsES (INTEGER) -> id (PK)
    - NomOfic (VARCHAR) -> nombre_oficial
    - NomEnsES (VARCHAR) -> nombre_corto
    - IdArea (INTEGER) -> area_id (FK, =3 for ES)
    - IdTipoES (BYTE) -> tipo_es_id (FK)
    - Precio (CURRENCY) -> precio (DECIMAL)
    - UM (VARCHAR) -> unidad_medida
    - Activo (BIT) -> activo
    """
    __tablename__ = 'ensayos_es'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_oficial = db.Column(db.String(500), nullable=False)
    nombre_corto = db.Column(db.String(200), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False, default=3)
    tipo_es_id = db.Column(db.Integer, db.ForeignKey('tipo_es.id'))
    precio = db.Column(db.Numeric(10, 2), nullable=True)
    unidad_medida = db.Column(db.String(10), default='USD')
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    area = db.relationship('Area', back_populates='ensayos_es')
    tipo_es = db.relationship('TipoES', back_populates='ensayos_es')
    
    def __repr__(self):
        return f'<EnsayoES {self.id}: {self.nombre_corto} (ES)>'


class EnsayoXProducto(db.Model):
    """
    Linking table: Associates tests with products.
    
    Note: Currently empty in Access (0 records), but schema exists.
    Will be used for product-specific test recommendations.
    """
    __tablename__ = 'ensayos_x_productos'
    
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), primary_key=True)
    ensayo_id = db.Column(db.Integer, db.ForeignKey('ensayos.id'), primary_key=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    producto = db.relationship('Producto', backref='ensayos_asociados')
    ensayo = db.relationship('Ensayo', backref='productos_asociados')
```

### Index Strategy

```python
# For quick lookups by area and active status
__table_args__ = (
    db.Index('ix_ensayo_area_id', 'area_id'),
    db.Index('ix_ensayo_activo', 'activo'),
    db.Index('ix_ensayo_area_activo', 'area_id', 'activo'),  # Common query pattern
)
```

### Area Filtering Logic

```python
# Common queries needed for Access migration:
# - Análisis a realizar FQ (Pending FQ tests)
# - Análisis a realizar MB (Pending microbiology tests)  
# - Análisis a realizar ES (Pending sensory tests)

# Implementation approach:
def get_tests_by_area(area_code):
    """Get active tests for a specific laboratory area"""
    area_map = {'FQ': 1, 'MB': 2, 'ES': 3, 'OS': 4}
    area_id = area_map.get(area_code)
    
    if area_code == 'ES':
        return EnsayoES.query.filter_by(area_id=area_id, activo=True).all()
    else:
        return Ensayo.query.filter_by(area_id=area_id, activo=True).all()
```

### Sample Data (Access)

**Ensayos (143 FQ Tests):**
Common tests include pH, acidity, moisture, fat content, protein analysis, etc.
Each has pricing for billing purposes.

**EnsayosES (29 Sensory Tests):**
Organoleptic evaluation tests for color, odor, taste, texture assessment.

### File Locations

```
app/
├── database/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── reference.py       # (from Issue #1)
│   │   ├── cliente.py         # (from Issue #2)
│   │   ├── ensayo.py          # <-- NEW: Ensayo, EnsayoES, EnsayoXProducto
│   │   └── ...
```

---

## Dependencies

**Blocked by:**
- Issue #1: [Phase 1] Create Reference Data Models (Areas, TipoES FKs required)

**Blocks:**
- Issue #4: [Phase 1] Database Migration Scripts
- Issue #7: [Phase 1] CRUD API for Reference Data (if including test CRUD)
- Issue #8: [Phase 1] Import Access Data (need models to import 143+29 test records)
- Phase 2: Test assignment and management features

---

## Related Documentation

- `docs/PRD.md` Section 2.3.3: Test Catalogs
- `docs/PRD.md` Section 3.1.2: Test Assignment requirements
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Lines 235-266: Complete test schema
- `plans/MIGRATION_PLAN.md` Phase 1.1 Week 2: Test Catalogs

---

## Testing Requirements

- [ ] Test that 143 Ensayo records can be created
- [ ] Test that 29 EnsayoES records can be created
- [ ] Verify area filtering works (FQ vs ES tests)
- [ ] Test price formatting helper methods
- [ ] Verify many-to-many relationships via linking table
- [ ] Test that `activo=False` excludes tests from active queries

---

## UI Considerations

These models support the following UI patterns:

1. **Test Selection Dropdown**: Filtered by area (FQ/MB/ES/OS)
2. **Price Display**: Formatted with currency symbol
3. **Test Catalog Grid**: Show active/inactive status
4. **Product-Test Association**: Many-to-many selection interface

Coordinate with Issue #6 (Base Templates) for test selection components.

---

## Definition of Done

- [ ] All 3 test-related models created
- [ ] 143 FQ test records can be imported
- [ ] 29 ES test records can be imported
- [ ] Area relationships working
- [ ] Price fields properly typed (DECIMAL)
- [ ] Indexes created for performance
- [ ] Helper methods implemented and tested
- [ ] Code review completed
- [ ] Ready for Alembic migration generation
