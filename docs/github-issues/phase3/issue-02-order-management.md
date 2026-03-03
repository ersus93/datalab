# [Phase 3] Order Management (Pedidos)

**Labels:** `phase-3`, `database`, `backend`, `frontend`, `order-management`, `high-priority`
**Milestone:** Phase 3: Sample Management (Weeks 5-6)
**Estimated Effort:** 3 days

---

## Description

Create a comprehensive order management system (Pedidos) for tracking client orders and their associated sample entries. The system handles 49 order records with lot information, manufacturing dates, and optional work order linking.

Orders serve as the parent entity for sample entries and link clients to their testing requests.

---

## Acceptance Criteria

### Model Creation (Pedido)
- [ ] Expand existing `Pedido` model with all fields from Access:
  - `id` (PK)
  - `cliente_id` (FK) - Link to Cliente
  - `producto_id` (FK) - Link to Producto
  - `orden_trabajo_id` (FK, optional) - Link to OrdenTrabajo
  - `codigo` - Order code
  - `lote` - Lot number (Lote)
  - `fech_fab` - Manufacturing date (FechFab)
  - `fech_venc` - Expiration date (FechVenc)
  - `cantidad` - Order quantity
  - `unidad_medida_id` - FK to UnidadMedida
  - `observaciones` - Order observations
  - `status` - Order status (Pending/In Progress/Completed)
  - `fech_pedido` - Order date
  - `created_at`, `updated_at` - Timestamps

### Relationships
- [ ] One-to-many: `Cliente` → `Pedido`
- [ ] One-to-many: `Producto` → `Pedido`
- [ ] One-to-many: `OrdenTrabajo` → `Pedido` (optional)
- [ ] One-to-many: `Pedido` → `Entrada` (existing)

### API Endpoints
- [ ] `GET /api/pedidos` - List orders with filters
  - Filter by: cliente_id, status, date range, producto_id
  - Include: client name, product name, entry count
- [ ] `GET /api/pedidos/{id}` - Get order detail
  - Include: related entradas, cliente info, producto info
- [ ] `POST /api/pedidos` - Create order
- [ ] `PUT /api/pedidos/{id}` - Update order
- [ ] `DELETE /api/pedidos/{id}` - Soft delete
- [ ] `GET /api/clientes/{id}/pedidos` - Get orders by client
- [ ] `GET /api/pedidos/{id}/entradas` - Get related sample entries

### Frontend Components
- [ ] Order list view with filtering
  - Filters: Client, Status, Date range, Product
  - Columns: Code, Client, Product, Lot, Status, Entries
- [ ] Order creation form
  - Client selector (with autocomplete)
  - Product selector
  - Lot information fields
  - Date pickers for FechFab, FechVenc
  - Optional Work Order linking
- [ ] Order detail view
  - Order information display
  - Related entries list
  - Status history
  - Actions: Edit, Delete, Create Entry
- [ ] Order edit form
- [ ] Client's order history view

### Order Status Workflow
- [ ] Status states:
  - `PENDIENTE` - Order created, awaiting samples
  - `EN_PROCESO` - Samples received, analysis started
  - `COMPLETADO` - All samples completed
- [ ] Automatic status updates based on related entries

---

## Technical Notes

### Access Schema Mapping

```python
class Pedido(db.Model):
    """Client orders/requests (49 records)
    
    Links clients to their testing requests. Orders can have
    multiple sample entries (Entradas) and optionally link
    to work orders (OrdenesTrabajo).
    """
    __tablename__ = 'pedidos'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    orden_trabajo_id = db.Column(db.Integer, db.ForeignKey('ordenes_trabajo.id'), nullable=True)
    unidad_medida_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id'), nullable=True)
    
    # Order Information
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    lote = db.Column(db.String(20), nullable=True)
    
    # Dates
    fech_fab = db.Column(db.Date, nullable=True)
    fech_venc = db.Column(db.Date, nullable=True)
    fech_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Quantity
    cantidad = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Status
    status = db.Column(
        db.Enum('PENDIENTE', 'EN_PROCESO', 'COMPLETADO', name='pedido_status'),
        default='PENDIENTE',
        nullable=False
    )
    
    # Metadata
    observaciones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='pedidos')
    producto = db.relationship('Producto', back_populates='pedidos')
    orden_trabajo = db.relationship('OrdenTrabajo', back_populates='pedidos')
    unidad_medida = db.relationship('UnidadMedida', back_populates='pedidos')
    entradas = db.relationship('Entrada', back_populates='pedido', lazy='dynamic')
    
    def __repr__(self):
        return f'<Pedido {self.codigo}>'
    
    @property
    def entradas_count(self):
        """Count related sample entries"""
        return self.entradas.count()
    
    @property
    def entradas_completadas(self):
        """Count completed sample entries"""
        return self.entradas.filter_by(status='COMPLETADO').count()
    
    def actualizar_estado(self):
        """Auto-update status based on related entries"""
        if self.entradas_count == 0:
            self.status = 'PENDIENTE'
        elif self.entradas_completadas == self.entradas_count:
            self.status = 'COMPLETADO'
        else:
            self.status = 'EN_PROCESO'
```

### Status Auto-Update Logic

```python
@event.listens_for(Entrada, 'after_insert')
@event.listens_for(Entrada, 'after_update')
def update_pedido_status(mapper, connection, entrada):
    """Update parent order status when entry changes"""
    if entrada.pedido_id:
        pedido = Pedido.query.get(entrada.pedido_id)
        if pedido:
            pedido.actualizar_estado()
            db.session.commit()
```

### API Response Format

```json
{
  "id": 1,
  "codigo": "PED-2024-001",
  "cliente": {
    "id": 5,
    "nombre": "Empresa ABC"
  },
  "producto": {
    "id": 12,
    "nombre": "Leche Entera"
  },
  "orden_trabajo": {
    "id": 3,
    "nro_ofic": "OT-2024-003"
  },
  "lote": "A-1234",
  "fech_fab": "2024-01-15",
  "fech_venc": "2024-02-15",
  "cantidad": 1000,
  "unidad_medida": {
    "id": 1,
    "codigo": "L"
  },
  "status": "EN_PROCESO",
  "observaciones": "Urgente",
  "entradas_count": 3,
  "entradas_completadas": 1,
  "fech_pedido": "2024-01-10T10:30:00"
}
```

### Filter Parameters

```python
# GET /api/pedidos?cliente_id=5&status=EN_PROCESO&desde=2024-01-01&hasta=2024-01-31
QUERY_PARAMS = {
    'cliente_id': 'Filter by client',
    'producto_id': 'Filter by product',
    'status': 'PENDIENTE | EN_PROCESO | COMPLETADO',
    'desde': 'Date from (YYYY-MM-DD)',
    'hasta': 'Date to (YYYY-MM-DD)',
    'orden_trabajo_id': 'Filter by work order',
    'page': 'Page number',
    'per_page': 'Items per page (default: 20)'
}
```

### File Locations

```
app/
├── database/
│   └── models/
│       └── pedido.py             # Update/expand existing
├── api/
│   └── routes/
│       └── pedidos.py            # API endpoints
├── services/
│   └── pedido_service.py         # Business logic
├── schemas/
│   └── pedido_schema.py          # Serialization schemas
app/templates/
├── pedidos/
│   ├── list.html                 # Order list
│   ├── form.html                 # Order form
│   ├── detail.html               # Order detail
│   └── _entradas_list.html       # Related entries subview
```

---

## Dependencies

**Blocked by:**
- Issue #[Phase 1] Create Master Data Models (Cliente, Producto)
- Issue #[Phase 1] Create Reference Data Models (UnidadMedida)
- Issue #[Phase 3] Work Order Management (optional FK relationship)

**Blocks:**
- Issue #[Phase 3] Sample Entry System (Entradas → Pedidos FK)
- Issue #[Phase 3] Transactional Data Import
- Issue #[Phase 5] Reports (Pedidos reports)

---

## Related Documentation

- `docs/PRD.md` Section 3.1.1: Order Management
- `docs/PROJECT_ANALYSIS.md` Lines 152-154: Pedidos relationships
- Access table: `pedidos` (49 records)

---

## Data Migration Notes

| Access Field | Python Model | Notes |
|--------------|--------------|-------|
| IdPedido | id | Auto-increment |
| IdCliente | cliente_id | FK to clientes |
| IdProducto | producto_id | FK to productos |
| Lote | lote | Lot number |
| FechFab | fech_fab | Manufacturing date |
| FechVenc | fech_venc | Expiration date |
| Cantidad | cantidad | Order quantity |
| UnidadMedida | unidad_medida_id | FK to unidades_medida |
| Observaciones | observaciones | Text |

---

## Testing Requirements

- [ ] Test order creation with all fields
- [ ] Test FK constraint validation (cliente, producto required)
- [ ] Test optional OrdenTrabajo linking
- [ ] Test date validation (FechVenc > FechFab)
- [ ] Test status auto-update from related entries
- [ ] Test list filtering by all parameters
- [ ] Test pagination

---

## Definition of Done

- [ ] Pedido model expanded with all fields
- [ ] OrdenTrabajo relationship added
- [ ] API endpoints functional with filtering
- [ ] Frontend forms complete
- [ ] Status auto-update working
- [ ] Tests passing
- [ ] Code review completed
