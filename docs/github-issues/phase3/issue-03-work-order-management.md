# [Phase 3] Work Order Management (Ordenes de Trabajo)

**Labels:** `phase-3`, `database`, `backend`, `frontend`, `work-order`, `medium-priority`
**Milestone:** Phase 3: Sample Management (Weeks 5-6)
**Estimated Effort:** 3 days

---

## Description

Create a work order management system (Ordenes de Trabajo) for grouping and tracking client work orders. The system handles 37 work order records with official number tracking (NroOfic), client assignment, and status management.

Work orders provide a higher-level organizational unit that can contain multiple orders (Pedidos) and serve as a billing/delivery unit.

---

## Acceptance Criteria

### Model Creation (OrdenTrabajo)
- [ ] Expand existing `OrdenTrabajo` model with all fields from Access:
  - `id` (PK)
  - `cliente_id` (FK) - Link to Cliente
  - `nro_ofic` - Official work order number (NroOfic)
  - `codigo` - Internal work order code
  - `descripcion` - Work order description
  - `status` - Status (Pendiente/En Progreso/Completada)
  - `fech_creacion` - Creation date
  - `fech_completado` - Completion date
  - `observaciones` - Notes
  - `created_at`, `updated_at` - Timestamps

### Relationships
- [ ] One-to-many: `Cliente` → `OrdenTrabajo`
- [ ] One-to-many: `OrdenTrabajo` → `Pedido`
- [ ] Many-to-many: `OrdenTrabajo` → `Entrada` (indirectly via Pedidos)

### Official Number Tracking
- [ ] Format validation for `nro_ofic` (organization-specific format)
- [ ] Unique constraint on `nro_ofic`
- [ ] Search by official number

### Status Workflow
- [ ] Status states:
  - `PENDIENTE` - Created, awaiting orders
  - `EN_PROGRESO` - Orders assigned, work started
  - `COMPLETADA` - All work finished
- [ ] Automatic status based on related orders
- [ ] Manual status override capability

### API Endpoints
- [ ] `GET /api/ordenes-trabajo` - List work orders
  - Filters: cliente_id, status, date range, nro_ofic
- [ ] `GET /api/ordenes-trabajo/{id}` - Get work order detail
  - Include: cliente info, related pedidos, summary statistics
- [ ] `POST /api/ordenes-trabajo` - Create work order
- [ ] `PUT /api/ordenes-trabajo/{id}` - Update work order
- [ ] `DELETE /api/ordenes-trabajo/{id}` - Soft delete
- [ ] `GET /api/clientes/{id}/ordenes-trabajo` - Get client's work orders
- [ ] `POST /api/ordenes-trabajo/{id}/pedidos` - Assign order to work order
- [ ] `DELETE /api/ordenes-trabajo/{id}/pedidos/{pedido_id}` - Remove order
- [ ] `GET /api/ordenes-trabajo/buscar?nro_ofic={number}` - Search by official number

### Frontend Components
- [ ] Work order list view
  - Filters: Client, Status, Official Number
  - Columns: NroOfic, Client, Status, Orders Count, Created
- [ ] Work order creation form
  - Client selector
  - Official number input
  - Description field
- [ ] Work order detail view
  - Work order information
  - Assigned orders list with entries
  - Status timeline
  - Summary statistics
- [ ] Work order edit form
- [ ] Assign orders interface
- [ ] Client's work order history

### Dashboard Widgets
- [ ] Work orders by status (pie chart)
- [ ] Recent work orders list
- [ ] Work orders requiring attention

---

## Technical Notes

### Access Schema Mapping

```python
class OrdenTrabajo(db.Model):
    """Work orders for organizing client requests (37 records)
    
    Work orders group multiple orders (Pedidos) and serve as
    the primary unit for billing and delivery tracking.
    Official number (NroOfic) is used for external reference.
    """
    __tablename__ = 'ordenes_trabajo'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Identification
    nro_ofic = db.Column(db.String(30), unique=True, nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    
    # Content
    descripcion = db.Column(db.Text, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    
    # Status
    status = db.Column(
        db.Enum('PENDIENTE', 'EN_PROGRESO', 'COMPLETADA', name='ot_status'),
        default='PENDIENTE',
        nullable=False
    )
    
    # Dates
    fech_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fech_completado = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='ordenes_trabajo')
    pedidos = db.relationship('Pedido', back_populates='orden_trabajo', lazy='dynamic')
    
    def __repr__(self):
        return f'<OrdenTrabajo {self.nro_ofic}>'
    
    @property
    def pedidos_count(self):
        """Count related orders"""
        return self.pedidos.count()
    
    @property
    def entradas_count(self):
        """Count total entries across all orders"""
        return sum(p.entradas_count for p in self.pedidos)
    
    @property
    def progreso(self):
        """Calculate completion percentage"""
        if self.pedidos_count == 0:
            return 0
        completados = sum(1 for p in self.pedidos if p.status == 'COMPLETADO')
        return int((completados / self.pedidos_count) * 100)
    
    def actualizar_estado(self):
        """Auto-update status based on related orders"""
        if self.pedidos_count == 0:
            self.status = 'PENDIENTE'
            self.fech_completado = None
        elif all(p.status == 'COMPLETADO' for p in self.pedidos):
            self.status = 'COMPLETADA'
            if not self.fech_completado:
                self.fech_completado = datetime.utcnow()
        else:
            self.status = 'EN_PROGRESO'
            self.fech_completado = None
```

### Status State Machine

```
                    +-----------+
       +---------->| PENDIENTE |
       |            +-----+-----+
       |                  |
       |    +-------------+
       |    |
       |    v
       |   +------------+
       +---+ EN_PROGRESO|<---------------+
           +------+-----+                |
                  |                      |
                  v                      |
           +------------+   (all orders |
           | COMPLETADA |    completed)  |
           +------------+                 |
                  |                      |
                  +----------------------+
             (new orders added)
```

### API Response Format

```json
{
  "id": 1,
  "nro_ofic": "OT-2024-001",
  "codigo": "OT-001",
  "cliente": {
    "id": 5,
    "nombre": "Empresa ABC",
    "codigo": "CLI-005"
  },
  "descripcion": "Análisis mensual Q1",
  "observaciones": "Prioridad alta",
  "status": "EN_PROGRESO",
  "progreso": 65,
  "pedidos_count": 3,
  "entradas_count": 12,
  "fech_creacion": "2024-01-01T09:00:00",
  "fech_completado": null,
  "pedidos": [
    {
      "id": 1,
      "codigo": "PED-001",
      "producto": "Leche",
      "status": "COMPLETADO",
      "entradas_count": 5
    },
    {
      "id": 2,
      "codigo": "PED-002",
      "producto": "Yogurt",
      "status": "EN_PROCESO",
      "entradas_count": 4
    }
  ]
}
```

### Search by Official Number

```python
@ordenes_trabajo_bp.route('/buscar')
def buscar_por_nro_ofic():
    """Search work orders by official number"""
    nro_ofic = request.args.get('nro_ofic', '').strip()
    if not nro_ofic:
        return jsonify({'error': 'NroOfic required'}), 400
    
    # Partial match support
    ordenes = OrdenTrabajo.query.filter(
        OrdenTrabajo.nro_ofic.ilike(f'%{nro_ofic}%')
    ).all()
    
    return jsonify({
        'results': [ot.to_dict() for ot in ordenes],
        'count': len(ordenes)
    })
```

### File Locations

```
app/
├── database/
│   └── models/
│       └── orden_trabajo.py      # Expand existing
├── api/
│   └── routes/
│       └── ordenes_trabajo.py    # API endpoints
├── services/
│   └── orden_trabajo_service.py  # Business logic
├── schemas/
│   └── orden_trabajo_schema.py   # Serialization schemas
app/templates/
├── ordenes-trabajo/
│   ├── list.html                 # Work order list
│   ├── form.html                 # Work order form
│   ├── detail.html               # Work order detail
│   └── asignar-pedidos.html      # Assign orders interface
```

---

## Dependencies

**Blocked by:**
- Issue #[Phase 1] Create Master Data Models (Cliente)

**Blocks:**
- Issue #[Phase 3] Order Management (Pedidos OT FK)
- Issue #[Phase 3] Transactional Data Import
- Issue #[Phase 5] Reports (OT summaries)

---

## Related Documentation

- `docs/PRD.md` Section 2.2: OrdenTrabajo model
- `docs/PROJECT_ANALYSIS.md` Line 153: OrdenesTrabajo relationships
- Access table: `ordenes_trabajo` (37 records)

---

## Data Migration Notes

| Access Field | Python Model | Notes |
|--------------|--------------|-------|
| Id | id | Auto-increment |
| NroOfic | nro_ofic | Official number |
| IdCliente | cliente_id | FK to clientes |
| Descripcion | descripcion | Text |
| Observaciones | observaciones | Text |
| FechCreacion | fech_creacion | DateTime |

---

## Testing Requirements

- [ ] Test work order creation
- [ ] Test official number uniqueness
- [ ] Test status auto-update from orders
- [ ] Test order assignment/removal
- [ ] Test search by official number
- [ ] Test progress calculation
- [ ] Test completion date auto-set

---

## Definition of Done

- [ ] OrdenTrabajo model expanded with all fields
- [ ] Official number tracking implemented
- [ ] Status workflow working
- [ ] API endpoints functional
- [ ] Frontend forms complete
- [ ] Dashboard widgets created
- [ ] Tests passing
- [ ] Code review completed
