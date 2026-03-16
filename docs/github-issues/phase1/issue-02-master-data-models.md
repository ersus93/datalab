# [Phase 1] Create Master Data Models

**Labels:** `phase-1`, `database`, `backend`, `sqlalchemy`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 2 days
**Depends on:** Issue #1 ([Phase 1] Create Reference Data Models)

---

## Description

Create SQLAlchemy models for the three core master data entities: **Clientes** (Clients), **Fabricas** (Factories), and **Productos** (Products). These tables form the backbone of the laboratory management system, storing information about clients, their factory locations, and the products they manufacture.

These models expand significantly on the basic `Cliente` model currently in the codebase and introduce new `Fabrica` and `Producto` models with proper relationships to reference data.

### Current State
- Basic `Cliente` model exists with minimal fields
- No `Fabrica` model exists
- No `Producto` model exists

### Target State
- Expanded `Cliente` model with full Access schema
- New `Fabrica` model linked to Clientes and Provincias
- New `Producto` model linked to Destinos
- All proper foreign key relationships established

### Data Volume
| Table | Records | Description |
|-------|---------|-------------|
| `clientes` | 166 | Client organizations |
| `fabricas` | 403 | Factory locations per client |
| `productos` | 160 | Products with sector classification |

**Total: 729 master records to migrate**

---

## Acceptance Criteria

### Model Creation

#### Cliente Model (Expanded)
- [ ] Update `Cliente` model with all fields from Access schema:
  - `id` (PK, auto-increment)
  - `nombre` (VARCHAR 300, required, unique)
  - `organismo_id` (FK to Organismos)
  - `tipo_cliente` (Integer, client type classification)
  - `activo` (Boolean, default True)
  - `creado_en` (DateTime, auto)
  - `actualizado_en` (DateTime, auto)
- [ ] Add unique constraint on `nombre`
- [ ] Add index on `organismo_id`
- [ ] Add index on `activo` for filtering

#### Fabrica Model (New)
- [ ] Create `Fabrica` model with fields:
  - `id` (PK, auto-increment)
  - `cliente_id` (FK to Clientes, required, cascade delete)
  - `nombre` (VARCHAR 300, required)
  - `provincia_id` (FK to Provincias)
  - `activo` (Boolean, default True)
  - `creado_en` (DateTime, auto)
- [ ] Add unique constraint on `(cliente_id, nombre)` - same client can't have duplicate factory names
- [ ] Add index on `cliente_id` for quick lookup
- [ ] Add index on `provincia_id` for geographic queries

#### Producto Model (New)
- [ ] Create `Producto` model with fields:
  - `id` (PK, auto-increment)
  - `nombre` (VARCHAR 300, required, unique)
  - `destino_id` (FK to Destinos)
  - `activo` (Boolean, default True)
  - `creado_en` (DateTime, auto)
- [ ] Add unique constraint on `nombre`
- [ ] Add index on `destino_id`

### Relationships

#### Cliente Relationships
- [ ] `organismo` -> many-to-one with `Organismo`
- [ ] `fabricas` -> one-to-many with `Fabrica` (back_populates="cliente")
- [ ] `pedidos` -> one-to-many with `Pedido` (existing)
- [ ] `ordenes_trabajo` -> one-to-many with `OrdenTrabajo`
- [ ] Property: `total_fabricas` (computed count)
- [ ] Property: `total_pedidos` (computed count)

#### Fabrica Relationships
- [ ] `cliente` -> many-to-one with `Cliente` (back_populates="fabricas")
- [ ] `provincia` -> many-to-one with `Provincia`
- [ ] `entradas` -> one-to-many with `Entrada`

#### Producto Relationships
- [ ] `destino` -> many-to-one with `Destino`
- [ ] `pedidos` -> one-to-many with `Pedido`
- [ ] `entradas` -> one-to-many with `Entrada`
- [ ] `ensayos_productos` -> many-to-many with `Ensayo` (via linking table)

### Constraints & Validation

- [ ] Ensure `Cliente.nombre` cannot be empty or null
- [ ] Ensure `Fabrica.nombre` cannot be empty or null within same client
- [ ] Ensure `Producto.nombre` cannot be empty or null
- [ ] Add `check` constraint: `tipo_cliente >= 1 AND tipo_cliente <= 5` (if applicable)
- [ ] Add `__repr__` methods for debugging
- [ ] Add `__str__` methods for display

### Backward Compatibility

- [ ] Preserve existing `Cliente` relationships with `Pedido`
- [ ] Ensure existing code doesn't break with model changes
- [ ] Update any existing seed data scripts

---

## Technical Notes

### Access Schema Mapping

```python
# From ACCESS_MIGRATION_ANALYSIS.md Lines 146-203

class Cliente(db.Model):
    """
    Access Mapping:
    - IdCli (COUNTER) -> id (PK)
    - NomCli (VARCHAR) -> nombre
    - IdOrg (BYTE) -> organismo_id (FK)
    - IdTipoCli (BYTE) -> tipo_cliente
    - CliActivo (BIT) -> activo
    """
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(300), nullable=False, unique=True)
    organismo_id = db.Column(db.Integer, db.ForeignKey('organismos.id'))
    tipo_cliente = db.Column(db.Integer, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organismo = db.relationship('Organismo', back_populates='clientes')
    fabricas = db.relationship('Fabrica', back_populates='cliente', 
                                 cascade='all, delete-orphan')
    pedidos = db.relationship('Pedido', back_populates='cliente')
    ordenes_trabajo = db.relationship('OrdenTrabajo', back_populates='cliente')
    
    @property
    def total_fabricas(self):
        return len(self.fabricas)
    
    @property
    def total_pedidos(self):
        return len(self.pedidos)


class Fabrica(db.Model):
    """
    Access Mapping:
    - IdFca (COUNTER) -> id (PK)
    - IdCli (INTEGER) -> cliente_id (FK)
    - Fabrica (VARCHAR) -> nombre
    - IdProv (INTEGER) -> provincia_id (FK)
    """
    __tablename__ = 'fabricas'
    __table_args__ = (
        db.UniqueConstraint('cliente_id', 'nombre', name='uix_fabrica_cliente_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nombre = db.Column(db.String(300), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincias.id'))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='fabricas')
    provincia = db.relationship('Provincia', back_populates='fabricas')
    entradas = db.relationship('Entrada', back_populates='fabrica')


class Producto(db.Model):
    """
    Access Mapping:
    - IdProd (COUNTER) -> id (PK)
    - Producto (VARCHAR) -> nombre
    - IdDest (INTEGER) -> destino_id (FK)
    """
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(300), nullable=False, unique=True)
    destino_id = db.Column(db.Integer, db.ForeignKey('destinos.id'))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    destino = db.relationship('Destino', back_populates='productos')
    pedidos = db.relationship('Pedido', back_populates='producto')
    entradas = db.relationship('Entrada', back_populates='producto')
    
    # Many-to-many with tests
    ensayos = db.relationship('Ensayo', secondary='ensayos_x_productos', 
                              back_populates='productos')


# Linking table for Producto-Ensayo many-to-many
class EnsayoXProducto(db.Model):
    """Linking table: Ensayos X Productos from Access"""
    __tablename__ = 'ensayos_x_productos'
    
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), primary_key=True)
    ensayo_id = db.Column(db.Integer, db.ForeignKey('ensayos.id'), primary_key=True)
```

### Sample Data from Access

**Clientes (166 records):**
- Empresa Cárnica de Pinar del Río
- Empresa de Productos Lácteos y Confiterías Pinar del Río
- Empresa de Bebidas y Refrescos de Pinar del Río
- ...

**Fabricas Statistics:**
- Total: 403 factories
- Average per client: 2.4 factories
- Range: Some clients have 1, others have 20+ factories

### File Locations

```
app/
├── database/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── reference.py       # (from Issue #1)
│   │   ├── cliente.py         # <-- UPDATE: Expand existing
│   │   ├── fabrica.py         # <-- NEW
│   │   ├── producto.py        # <-- NEW
│   │   └── pedido.py          # (update relationships)
```

### Index Strategy

```python
# Recommended indexes for performance with 400+ factories and 160+ products

__table_args__ = (
    db.Index('ix_fabrica_cliente_id', 'cliente_id'),
    db.Index('ix_fabrica_provincia_id', 'provincia_id'),
    db.Index('ix_fabrica_activo', 'activo'),
)
```

---

## Dependencies

**Blocked by:**
- Issue #1: [Phase 1] Create Reference Data Models (Organismos, Provincias, Destinos FKs required)

**Blocks:**
- Issue #3: [Phase 1] Create Test Catalog Models (Producto-Ensayo linking)
- Issue #4: [Phase 1] Database Migration Scripts
- Issue #8: [Phase 1] Import Access Data - Reference & Master (depends on models existing)

---

## Related Documentation

- `docs/PRD.md` Section 2.3.2: Master Data tables
- `docs/ACCESS_MIGRATION_ANALYSIS.md` Lines 146-203: Complete schema for Clientes, Fabricas, Productos
- `plans/MIGRATION_PLAN.md` Phase 1.1: Core Business Tables

---

## Testing Requirements

- [ ] Test that `Cliente` can have multiple `Fabrica` records
- [ ] Verify cascade delete: deleting Cliente deletes associated Fabricas
- [ ] Test unique constraint: same client cannot have duplicate factory names
- [ ] Verify computed properties (`total_fabricas`, `total_pedidos`)
- [ ] Test foreign key constraints reject invalid references

---

## Migration Notes

**Important:** This updates the existing `Cliente` model. Coordinate with team to:
1. Back up existing database
2. Create Alembic migration after this issue is complete
3. Test migration on development database first
4. Verify no data loss in existing `Cliente` records

---

## Definition of Done

- [ ] All 3 models created/updated and committed
- [ ] All foreign key relationships working
- [ ] All indexes created
- [ ] Existing `Cliente` code still functional
- [ ] Relationships with `Pedido` preserved
- [ ] Code review completed
- [ ] Ready for Alembic migration generation
