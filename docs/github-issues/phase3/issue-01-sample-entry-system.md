# [Phase 3] Sample Entry System (Entradas)

**Labels:** `phase-3`, `database`, `backend`, `frontend`, `sample-management`, `high-priority`
**Milestone:** Phase 3: Sample Management (Weeks 5-6)
**Estimated Effort:** 4 days

---

## Description

Create a comprehensive sample entry management system (Entradas) that replaces the Access database entry tracking functionality. This is the **core operational module** of the laboratory management system, handling 109 sample entries with lot tracking, balance calculations, and status workflows.

The Entradas system must support the complete sample lifecycle from receipt through delivery, with accurate balance tracking (CantidadRecib - CantidadEntreg = Saldo) and lot number format validation (X-XXXX).

---

## Acceptance Criteria

### Model Creation (Entrada)
- [ ] Create `Entrada` model with all fields from Access:
  - `id` (PK) - Sample entry ID
  - `pedido_id` (FK) - Link to Pedido
  - `producto_id` (FK) - Link to Producto
  - `fabrica_id` (FK) - Link to Fabrica (via Cliente)
  - `cliente_id` (FK) - Link to Cliente
  - `rama_id` (FK) - Industry sector
  - `codigo` - Entry code/sample ID
  - `lote` - Lot number (format: X-XXXX)
  - `nro_parte` - Part number tracking
  - `cantidad_recib` - Quantity received (CantidadRecib)
  - `cantidad_entreg` - Quantity delivered (CantidadEntreg)
  - `saldo` - Balance (calculated: CantidadRecib - CantidadEntreg)
  - `cantidad_muest` - Sample quantity
  - `unidad_medida_id` - FK to UnidadMedida
  - `fech_fab` - Manufacturing date
  - `fech_venc` - Expiration date
  - `fech_muestreo` - Sampling date
  - `fech_entrada` - Entry date
  - `status` - Entry status (Received/In Process/Completed/Delivered)
  - `en_os` - In work order flag
  - `anulado` - Cancelled flag
  - `ent_entregada` - Delivered flag
  - `observaciones` - Observations/notes

### Status Workflow
- [ ] Implement entry status states:
  - `RECIBIDO` (Received) - Initial state on creation
  - `EN_PROCESO` (In Process) - Analysis started
  - `COMPLETADO` (Completed) - Testing finished
  - `ENTREGADO` (Delivered) - Sample delivered to client
- [ ] Status transition validation (prevent invalid transitions)
- [ ] Automatic status updates based on related test completion

### Business Logic
- [ ] Automatic balance calculation: `saldo = cantidad_recib - cantidad_entreg`
- [ ] Prevent negative balance (validation)
- [ ] Lot number format validation: `X-XXXX` pattern (e.g., A-1234)
- [ ] Part number tracking integration
- [ ] Date validation (FechVenc > FechFab)

### API Endpoints
- [ ] `POST /api/entradas` - Create sample entry
- [ ] `GET /api/entradas` - List entries with pagination
- [ ] `GET /api/entradas/{id}` - Get entry details
- [ ] `PUT /api/entradas/{id}` - Update entry
- [ ] `DELETE /api/entradas/{id}` - Soft delete (mark anulado)
- [ ] `POST /api/entradas/{id}/cambiar-estado` - Change status with validation
- [ ] `GET /api/entradas/{id}/saldo` - Get current balance
- [ ] `POST /api/entradas/{id}/entregar` - Record delivery (updates CantidadEntreg)

### Frontend Components
- [ ] Sample entry registration form
- [ ] Entry list view with filters
- [ ] Entry detail view with status history
- [ ] Balance display widget
- [ ] Status transition buttons
- [ ] Delivery recording interface

---

## Technical Notes

### Access Schema Mapping

```python
class Entrada(db.Model):
    """Sample entry - CORE TABLE (109 records)
    
    Represents samples received from clients for testing.
    Balance calculation: cantidad_recib - cantidad_entreg = saldo
    Lot format: X-XXXX (letter-4digits)
    """
    __tablename__ = 'entradas'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fabrica_id = db.Column(db.Integer, db.ForeignKey('fabricas.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    rama_id = db.Column(db.Integer, db.ForeignKey('ramas.id'), nullable=True)
    unidad_medida_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id'), nullable=True)
    
    # Core Fields
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    lote = db.Column(db.String(10), nullable=True)  # Format: X-XXXX
    nro_parte = db.Column(db.String(50), nullable=True)
    
    # Quantities
    cantidad_recib = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cantidad_entreg = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    saldo = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cantidad_muest = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Dates
    fech_fab = db.Column(db.Date, nullable=True)
    fech_venc = db.Column(db.Date, nullable=True)
    fech_muestreo = db.Column(db.Date, nullable=True)
    fech_entrada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Status Flags
    status = db.Column(
        db.Enum('RECIBIDO', 'EN_PROCESO', 'COMPLETADO', 'ENTREGADO', name='entrada_status'),
        default='RECIBIDO',
        nullable=False
    )
    en_os = db.Column(db.Boolean, default=False)  # In work order
    anulado = db.Column(db.Boolean, default=False)  # Cancelled
    ent_entregada = db.Column(db.Boolean, default=False)  # Delivered
    
    # Metadata
    observaciones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    pedido = db.relationship('Pedido', back_populates='entradas')
    producto = db.relationship('Producto', back_populates='entradas')
    fabrica = db.relationship('Fabrica', back_populates='entradas')
    cliente = db.relationship('Cliente', back_populates='entradas')
    rama = db.relationship('Rama', back_populates='entradas')
    unidad_medida = db.relationship('UnidadMedida', back_populates='entradas')
    
    def __repr__(self):
        return f'<Entrada {self.codigo}>'
    
    def calcular_saldo(self):
        """Calculate current balance"""
        self.saldo = self.cantidad_recib - self.cantidad_entreg
        return self.saldo
    
    @validates('lote')
    def validate_lote(self, key, lote):
        """Validate lot format X-XXXX"""
        if lote and not re.match(r'^[A-Z]-\d{4}$', lote):
            raise ValueError('Lot format must be X-XXXX (e.g., A-1234)')
        return lote
    
    @validates('fech_venc')
    def validate_fech_venc(self, key, fech_venc):
        """Validate expiration > manufacturing"""
        if fech_venc and self.fech_fab and fech_venc < self.fech_fab:
            raise ValueError('Expiration date must be after manufacturing date')
        return fech_venc
```

### Status State Machine

```
                    +-----------+
                    | RECIBIDO  |
                    +-----+-----+
                          |
              +-----------+-----------+
              |                       |
              v                       v
       +------------+          +------------+
       | ANULADO    |          | EN_PROCESO |
       +------------+          +------+-----+
                                      |
                                      v
                               +------------+
                               | COMPLETADO |
                               +------+-----+
                                      |
                                      v
                               +------------+
                               | ENTREGADO  |
                               +------------+
```

### Valid Transitions

| From | To | Allowed |
|------|-----|---------|
| RECIBIDO | EN_PROCESO | Yes |
| RECIBIDO | ANULADO | Yes |
| EN_PROCESO | COMPLETADO | Yes |
| EN_PROCESO | ANULADO | Yes (with warning) |
| COMPLETADO | ENTREGADO | Yes |
| COMPLETADO | ANULADO | No |
| ENTREGADO | * | No (terminal) |
| ANULADO | * | No (terminal) |

### Balance Calculation Rules

```python
# Auto-calculate on save
@event.listens_for(Entrada, 'before_insert')
@event.listens_for(Entrada, 'before_update')
def calculate_balance(mapper, connection, target):
    target.saldo = target.cantidad_recib - target.cantidad_entreg
    
    # Update ent_entregada flag
    target.ent_entregada = (target.saldo <= 0)
    
    # Update status if fully delivered
    if target.ent_entregada and target.status == 'COMPLETADO':
        target.status = 'ENTREGADO'
```

### File Locations

```
app/
├── database/
│   └── models/
│       └── entrada.py          # Entrada model
├── api/
│   └── routes/
│       └── entradas.py         # API endpoints
├── services/
│   └── entrada_service.py      # Business logic
├── schemas/
│   └── entrada_schema.py       # Marshmallow/Pydantic schemas
app/templates/
├── entradas/
│   ├── list.html               # Entry list
│   ├── form.html               # Entry form
│   └── detail.html             # Entry detail
```

---

## Dependencies

**Blocked by:**
- Issue #[Phase 1] Create Master Data Models (Cliente, Fabrica, Producto)
- Issue #[Phase 1] Create Reference Data Models (Rama, UnidadMedida)
- Issue #[Phase 3] Order Management (Pedidos) - for FK relationship

**Blocks:**
- Issue #[Phase 3] Sample Status Workflow
- Issue #[Phase 3] Transactional Data Import
- Issue #[Phase 4] Test Results Management (DetallesEnsayo needs Entrada FK)

---

## Related Documentation

- `docs/PRD.md` Section 3.1.1: Sample Management
- `docs/PROJECT_ANALYSIS.md` Line 154: Entradas relationships
- Access table: `entradas` (109 records)

---

## Data Migration Notes

| Access Field | Python Model | Notes |
|--------------|--------------|-------|
| Id | id | Auto-increment |
| Codigo | codigo | Unique sample code |
| Lote | lote | Format: X-XXXX |
| NroParte | nro_parte | Part number |
| CantidadRecib | cantidad_recib | Decimal |
| CantidadEntreg | cantidad_entreg | Decimal |
| Saldo | saldo | Calculated |
| FechFab | fech_fab | Date |
| FechVenc | fech_venc | Date |
| FechMuestreo | fech_muestreo | Date |
| EnOS | en_os | Boolean |
| Anulado | anulado | Boolean |
| EntEntregada | ent_entregada | Boolean |

---

## Testing Requirements

- [ ] Test balance calculation accuracy
- [ ] Test lot format validation (X-XXXX)
- [ ] Test status transitions (valid and invalid)
- [ ] Test date validations (FechVenc > FechFab)
- [ ] Test delivery recording updates balance
- [ ] Test negative balance prevention
- [ ] Verify FK constraints work correctly

---

## Definition of Done

- [ ] Entrada model created with all fields
- [ ] Status workflow implemented
- [ ] Balance calculation working
- [ ] Lot validation in place
- [ ] API endpoints functional
- [ ] Frontend forms complete
- [ ] Tests passing
- [ ] Code review completed
