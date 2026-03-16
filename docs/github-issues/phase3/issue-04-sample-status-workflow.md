# [Phase 3] Sample Status Workflow

**Labels:** `phase-3`, `backend`, `frontend`, `workflow`, `status-management`, `medium-priority`
**Milestone:** Phase 3: Sample Management (Weeks 5-6)
**Estimated Effort:** 3 days

---

## Description

Implement a comprehensive sample status workflow system that tracks the lifecycle of samples through the laboratory. This includes three key status flags (EnOS, Anulado, EntEntregada), status transition validation, audit trails, and notification systems.

The status system ensures proper tracking from sample receipt through delivery, with full visibility and accountability.

---

## Acceptance Criteria

### Status Flags Implementation
- [ ] Implement `EnOS` (En Orden de Servicio) flag:
  - Boolean field on Entrada
  - Indicates sample is assigned to a work order
  - Auto-set when linked to Pedido with OT
- [ ] Implement `Anulado` flag:
  - Boolean field on Entrada
  - Marks cancelled/voided samples
  - Prevents further processing
- [ ] Implement `EntEntregada` flag:
  - Boolean field on Entrada
  - Indicates sample has been delivered
  - Auto-set when saldo reaches 0

### Status Workflow Engine
- [ ] Create `StatusWorkflow` service class:
  ```python
  class StatusWorkflow:
      """Manages status transitions for Entradas"""
      
      VALID_TRANSITIONS = {
          'RECIBIDO': ['EN_PROCESO', 'ANULADO'],
          'EN_PROCESO': ['COMPLETADO', 'ANULADO'],
          'COMPLETADO': ['ENTREGADO'],
          'ENTREGADO': [],  # Terminal
          'ANULADO': []     # Terminal
      }
      
      @classmethod
      def can_transition(cls, from_status, to_status):
          return to_status in cls.VALID_TRANSITIONS.get(from_status, [])
  ```
- [ ] Status transition validation with clear error messages
- [ ] Batch status update capability
- [ ] Automatic status progression rules

### Status History / Audit Trail
- [ ] Create `StatusHistory` model:
  - `id` (PK)
  - `entrada_id` (FK)
  - `from_status` - Previous status
  - `to_status` - New status
  - `changed_by` - User who made change
  - `changed_at` - Timestamp
  - `reason` - Change reason/notes
  - `metadata` - JSON additional data
- [ ] Automatic history recording on status change
- [ ] Status history API endpoints:
  - `GET /api/entradas/{id}/historial-estados`
  - Include user info and timestamps
- [ ] Status history view in frontend
  - Timeline display
  - Change reasons
  - User attribution

### Notifications on Status Changes
- [ ] Create notification system:
  - `Notification` model
  - Email notifications
  - In-app notifications
  - Notification preferences
- [ ] Notification triggers:
  - Status change to COMPLETADO (notify client)
  - Status change to ENTREGADO (notify client)
  - Sample assigned to work order
  - Delivery pending (saldo low)
- [ ] Notification templates
- [ ] Unread notification indicators

### Dashboard Widgets
- [ ] Create status count widgets:
  ```
  +------------------+
  | Samples by Status|
  +------------------+
  | Recibido    | 25 |
  | En Proceso  | 42 |
  | Completado  | 18 |
  | Entregado   | 24 |
  | Anulado     | 3  |
  +------------------+
  ```
- [ ] Status trend chart (last 30 days)
- [ ] Status transition timeline
- [ ] Quick action buttons for common transitions

### Batch Operations
- [ ] Batch status update interface:
  - Select multiple samples
  - Apply status change to all
  - Confirm with reason
- [ ] Validation for batch operations
- [ ] Progress indicator for large batches

---

## Technical Notes

### StatusHistory Model

```python
class StatusHistory(db.Model):
    """Audit trail for sample status changes"""
    __tablename__ = 'status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    entrada_id = db.Column(db.Integer, db.ForeignKey('entradas.id'), nullable=False)
    
    # Status change
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    
    # Who and when
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Why
    reason = db.Column(db.Text, nullable=True)
    metadata = db.Column(db.JSON, nullable=True)  # Additional context
    
    # Relationships
    entrada = db.relationship('Entrada', back_populates='status_history')
    changed_by = db.relationship('User', back_populates='status_changes')
    
    def __repr__(self):
        return f'<StatusHistory {self.entrada_id}: {self.from_status} -> {self.to_status}>'

# Add to Entrada model:
status_history = db.relationship('StatusHistory', 
                                  back_populates='entrada', 
                                  order_by='StatusHistory.changed_at.desc()',
                                  lazy='dynamic')
```

### Automatic History Recording

```python
@event.listens_for(Entrada, 'before_update')
def record_status_change(mapper, connection, entrada):
    """Automatically record status changes"""
    # Get the current state from DB
    previous = db.session.query(Entrada).get(entrada.id)
    
    if previous and previous.status != entrada.status:
        # Record the change
        history = StatusHistory(
            entrada_id=entrada.id,
            from_status=previous.status,
            to_status=entrada.status,
            changed_by_id=current_user.id,  # Requires Flask-Login
            reason=getattr(entrada, '_status_reason', None)
        )
        db.session.add(history)
        
        # Send notification
        notify_status_change(entrada, previous.status, entrada.status)
```

### Notification System

```python
class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Content
    type = db.Column(db.String(50), nullable=False)  # 'status_change', 'delivery', etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Link to related entity
    entity_type = db.Column(db.String(50), nullable=True)  # 'entrada', 'pedido', etc.
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Status
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_read(self):
        self.read = True
        self.read_at = datetime.utcnow()

def notify_status_change(entrada, from_status, to_status):
    """Create notifications for status changes"""
    # Notify responsible lab technician
    notify_lab_tech(entrada, f"Sample {entrada.codigo} changed to {to_status}")
    
    # Notify client on completion/delivery
    if to_status in ['COMPLETADO', 'ENTREGADO']:
        notify_client(entrada.cliente, entrada)
```

### Status Transition API

```python
@entradas_bp.route('/<int:id>/cambiar-estado', methods=['POST'])
def cambiar_estado(id):
    """Change sample status with validation"""
    entrada = Entrada.query.get_or_404(id)
    data = request.get_json()
    
    nuevo_estado = data.get('status')
    razon = data.get('razon', '')
    
    # Validate transition
    if not StatusWorkflow.can_transition(entrada.status, nuevo_estado):
        return jsonify({
            'error': f'Cannot transition from {entrada.status} to {nuevo_estado}',
            'valid_transitions': StatusWorkflow.VALID_TRANSITIONS[entrada.status]
        }), 400
    
    # Store reason for history
    entrada._status_reason = razon
    entrada.status = nuevo_estado
    
    # Update related flags
    if nuevo_estado == 'ENTREGADO':
        entrada.ent_entregada = True
    elif nuevo_estado == 'ANULADO':
        entrada.anulado = True
    
    db.session.commit()
    
    return jsonify({
        'message': 'Status updated',
        'entrada': entrada.to_dict(),
        'history_recorded': True
    })
```

### Batch Status Update

```python
@entradas_bp.route('/batch/cambiar-estado', methods=['POST'])
def batch_cambiar_estado():
    """Update status for multiple samples"""
    data = request.get_json()
    entrada_ids = data.get('entrada_ids', [])
    nuevo_estado = data.get('status')
    razon = data.get('razon', '')
    
    results = {'success': [], 'failed': []}
    
    for entrada_id in entrada_ids:
        entrada = Entrada.query.get(entrada_id)
        if not entrada:
            results['failed'].append({'id': entrada_id, 'error': 'Not found'})
            continue
            
        if not StatusWorkflow.can_transition(entrada.status, nuevo_estado):
            results['failed'].append({
                'id': entrada_id,
                'error': f'Invalid transition from {entrada.status}'
            })
            continue
        
        entrada._status_reason = razon
        entrada.status = nuevo_estado
        results['success'].append(entrada_id)
    
    db.session.commit()
    
    return jsonify({
        'processed': len(entrada_ids),
        'successful': len(results['success']),
        'failed': len(results['failed']),
        'results': results
    })
```

### File Locations

```
app/
├── services/
│   ├── status_workflow.py        # Status workflow engine
│   └── notification_service.py   # Notification handling
├── models/
│   ├── status_history.py         # Audit trail model
│   └── notification.py           # Notification model
├── api/
│   └── routes/
│       ├── entradas.py           # Status change endpoints
│       └── notifications.py      # Notification endpoints
app/templates/
├── components/
│   ├── status-badge.html         # Status display component
│   ├── status-timeline.html      # History timeline
│   └── notification-dropdown.html
├── entradas/
│   └── _status-history.html      # Status history subview
```

---

## Dependencies

**Blocked by:**
- Issue #[Phase 3] Sample Entry System (Entrada model)
- Issue #[Phase 1] Authentication System (User model for history)

**Blocks:**
- Issue #[Phase 5] Reports (status reports)
- Issue #[Phase 6] Notifications (email templates)

---

## Related Documentation

- `docs/PRD.md` Section 3.1.1: Sample status workflow
- Access fields: `EnOS`, `Anulado`, `EntEntregada`

---

## Testing Requirements

- [ ] Test valid status transitions
- [ ] Test invalid status transition blocking
- [ ] Test automatic history recording
- [ ] Test notification triggering
- [ ] Test batch status updates
- [ ] Test status count dashboard widgets
- [ ] Test audit trail retrieval

---

## Definition of Done

- [ ] Status flags working (EnOS, Anulado, EntEntregada)
- [ ] Status workflow engine implemented
- [ ] Status history model and recording
- [ ] Notification system created
- [ ] Dashboard widgets functional
- [ ] Batch operations working
- [ ] Tests passing
- [ ] Code review completed
