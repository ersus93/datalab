---
title: "[Phase 6] Notifications System"
labels: ["phase-6", "advanced", "notifications", "epic"]
---

## Overview
Implement a comprehensive notifications system with both email and in-app notifications, supporting multiple notification types, user preferences, and customizable email templates.

## Notification Channels

### 1. Email Notifications (Flask-Mail)
**Library:** `Flask-Mail`
**Configuration:**
```python
# config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'noreply@datalab.com'
```

**Features:**
- HTML and plain text email support
- Attachment support
- Bulk email capability
- Email queue for high volume
- Delivery tracking

### 2. In-App Notification Center
**Features:**
- Real-time notification badge
- Notification dropdown/panel
- Read/unread status
- Mark all as read
- Archive old notifications
- Delete notifications

**UI Design:**
```
┌─────────────────────────────────────┐
│ 🔔  Notifications (5)              │
├─────────────────────────────────────┤
│ [Test] Lote ABC123 completed   🆕  │
│ [Report] Informe #456 ready    🆕  │
│ [Alert] Low balance warning         │
│ [Entry] Entrada #789 delivered      │
├─────────────────────────────────────┤
│ View All    Settings    Mark Read  │
└─────────────────────────────────────┘
```

## Notification Types

### 1. Test Completed
**Trigger:** When a test changes status to "completed"
**Recipients:**
- Client (associated with the entrada)
- Assigned technician

**Email Content:**
- Test name and details
- Result summary
- Link to full report
- PDF attachment (optional)

### 2. Report Ready
**Trigger:** When an informe is finalized
**Recipients:**
- Client
- Contact persons

**Email Content:**
- Report summary
- Download link
- Validity period
- Contact information

### 3. Low Balance Alert
**Trigger:** When client balance falls below threshold
**Recipients:**
- Client primary contact
- Billing department

**Email Content:**
- Current balance
- Pending charges
- Payment instructions
- Service impact warning

### 4. Entry Delivered
**Trigger:** When entrada status changes to "delivered"
**Recipients:**
- Client
- Requested contacts

**Email Content:**
- Entry details
- Delivery confirmation
- Sample disposition info
- Related reports

## Notification Preferences

### Per-User Settings
```python
class NotificationPreferences(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    
    # Email preferences
    email_test_completed = db.Column(db.Boolean, default=True)
    email_report_ready = db.Column(db.Boolean, default=True)
    email_low_balance = db.Column(db.Boolean, default=True)
    email_entry_delivered = db.Column(db.Boolean, default=True)
    
    # In-app preferences
    app_test_completed = db.Column(db.Boolean, default=True)
    app_report_ready = db.Column(db.Boolean, default=True)
    app_low_balance = db.Column(db.Boolean, default=True)
    app_entry_delivered = db.Column(db.Boolean, default=True)
    
    # Digest settings
    digest_enabled = db.Column(db.Boolean, default=False)
    digest_frequency = db.Column(db.String(20))  # daily, weekly
    digest_day = db.Column(db.Integer)  # 0-6 for weekly
    digest_time = db.Column(db.Time)
```

### Preference UI
```
┌──────────────────────────────────────────────┐
│ Notification Settings                         │
├──────────────────────────────────────────────┤
│                                               │
│ Email Notifications:                          │
│ ☑ Test completed                              │
│ ☑ Report ready                                │
│ ☑ Low balance alert                           │
│ ☐ Entry delivered                             │
│                                               │
│ In-App Notifications:                         │
│ ☑ Test completed                              │
│ ☑ Report ready                                │
│ ☑ Low balance alert                           │
│ ☑ Entry delivered                             │
│                                               │
│ Digest Email:                                 │
│ ☐ Enable daily digest at [09:00 ▼]           │
│                                               │
│ [Save Changes]                                │
└──────────────────────────────────────────────┘
```

## Email Templates

### Template Structure
```
templates/emails/
├── base.html                 # Base template with styling
├── test_completed.html       # Test completed notification
├── test_completed.txt        # Plain text version
├── report_ready.html         # Report ready notification
├── report_ready.txt
├── low_balance.html          # Low balance alert
├── low_balance.txt
├── entry_delivered.html      # Entry delivered
├── entry_delivered.txt
└── digest.html               # Daily/weekly digest
```

### Template Variables
```html
<!-- test_completed.html -->
{% extends "emails/base.html" %}

{% block content %}
<h2>Test Completed</h2>
<p>Hello {{ client.name }},</p>

<p>The following test has been completed:</p>

<table class="details">
  <tr>
    <td>Test:</td>
    <td>{{ test.name }}</td>
  </tr>
  <tr>
    <td>Lote:</td>
    <td>{{ entrada.lote }}</td>
  </tr>
  <tr>
    <td>Completed:</td>
    <td>{{ test.completed_at }}</td>
  </tr>
  <tr>
    <td>Result:</td>
    <td>{{ test.result_summary }}</td>
  </tr>
</table>

<a href="{{ view_url }}" class="button">View Full Report</a>
{% endblock %}
```

## Database Schema

### Notifications Table
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- test_completed, report_ready, etc.
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSONB,  -- Additional notification data
    
    -- Delivery tracking
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,
    email_error TEXT,
    
    -- In-app tracking
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Archive
    archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, read);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
```

## API Endpoints

```
# Notification CRUD
GET    /api/notifications              # List notifications (with filters)
GET    /api/notifications/unread       # Get unread count
POST   /api/notifications/:id/read     # Mark as read
POST   /api/notifications/read-all     # Mark all as read
DELETE /api/notifications/:id          # Delete/archive notification

# Preferences
GET    /api/notifications/preferences  # Get user preferences
PUT    /api/notifications/preferences  # Update preferences
```

## Real-Time Notifications (Optional)

### WebSocket Implementation
```python
# Using Flask-SocketIO
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')

def send_notification(user_id, notification):
    socketio.emit('notification', notification, room=f'user_{user_id}')
```

## Implementation Tasks

### Phase 1: Basic Email
- [ ] Set up Flask-Mail configuration
- [ ] Create email templates (base + types)
- [ ] Implement notification service class
- [ ] Add email sending to relevant workflows

### Phase 2: In-App Notifications
- [ ] Create notification database schema
- [ ] Build notification service
- [ ] Create notification center UI
- [ ] Add notification badge to header

### Phase 3: Preferences
- [ ] Create preferences model
- [ ] Build preferences UI
- [ ] Respect preferences when sending

### Phase 4: Advanced Features
- [ ] Digest emails
- [ ] Real-time notifications (WebSocket)
- [ ] Push notifications (PWA)

## Security Considerations

- Email rate limiting per user
- Prevent email enumeration
- Secure email content (no sensitive data in plain text)
- Verify email addresses before sending
- Unsubscribe links in all emails

## Testing Strategy

- Unit tests for notification service
- Email template rendering tests
- Integration tests for notification triggers
- Mock email for testing environments

## Acceptance Criteria

- [ ] Email notifications sent via Flask-Mail
- [ ] All 4 notification types implemented
- [ ] In-app notification center functional
- [ ] User preferences respected
- [ ] Email templates for all types
- [ ] Plain text versions of all emails
- [ ] Unread notification badge updates
- [ ] Mark as read functionality works
- [ ] Digest email option available
- [ ] Email delivery tracking
- [ ] Preference settings UI
- [ ] Rate limiting implemented
- [ ] Unit and integration tests

## Related Issues
- #XX - Email service configuration
- #XX - Real-time features (WebSocket)
- #XX - PWA implementation

## Estimated Effort
**Story Points:** 8
**Estimated Time:** 1-2 weeks

## Dependencies
- Flask-Mail configuration
- SMTP server access
- Email templates design
