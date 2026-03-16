# Phase 2 Pending Components Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Complete 3 pending components from Phase 2: CSV audit export, factory sample history, and password strength indicator.

**Architecture:** Inline implementation reusing existing routes, models, and templates. Minimal changes approach for consistency.

**Tech Stack:** Flask, SQLAlchemy, Jinja2 templates, JavaScript (vanilla)

---

## Component Overview

| # | Component | Issue | Priority |
|---|-----------|-------|----------|
| 1 | Export CSV Audit Log | #1 (Client Management) | High |
| 2 | Factory Sample History | #2 (Factory Management) | Medium |
| 3 | Password Strength Indicator | #4 (User Auth) | Medium |

---

## Task 1: Export CSV Audit Log

**Goal:** Add export button to client detail view that downloads audit history as CSV.

**Files:**
- Modify: `app/routes/clientes.py` (add export route)
- Modify: `app/templates/clientes/ver.html` (add export button)

### Step 1: Add export route to clientes.py

Add this route after the existing `ver` route (around line 65):

```python
@clientes_bp.route('/<int:id>/export-audit', methods=['GET'])
@login_required
def exportar_audit(id):
    """Exportar historial de auditoría a CSV."""
    cliente = Cliente.query.get_or_404(id)
    
    # Obtener todas las entradas de auditoría para este cliente
    audit_entries = (
        AuditLog.query
        .filter_by(table_name='clientes', record_id=id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    
    # Generar CSV
    import csv
    import io
    from flask import make_response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Fecha', 'Usuario', 'Acción', 'Valores Anteriores', 'Valores Nuevos', 'IP'])
    
    # Data
    for entry in audit_entries:
        writer.writerow([
            entry.created_at.strftime('%Y-%m-%d %H:%M:%S') if entry.created_at else '',
            entry.user.username if entry.user else '',
            entry.action,
            str(entry.old_values) if entry.old_values else '',
            str(entry.new_values) if entry.new_values else '',
            entry.ip_address or ''
        ])
    
    # Response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=auditoria_cliente_{id}.csv'
    
    return response
```

### Step 2: Add export button to ver.html

Add after the "Historial" section header in `app/templates/clientes/ver.html`:

```html
<div class="card-header d-flex justify-content-between align-items-center">
    <h5 class="mb-0">Historial de Auditoría</h5>
    <a href="{{ url_for('clientes.exportar_audit', id=cliente.id) }}" class="btn btn-sm btn-outline-primary">
        <i class="fas fa-download"></i> Exportar CSV
    </a>
</div>
```

---

## Task 2: Factory Sample History Widget

**Goal:** Add sample history table to factory detail view, showing last 10 entries from that factory.

**Files:**
- Modify: `app/routes/fabricas.py:75-85` (update stats dict)
- Modify: `app/templates/fabricas/ver.html` (add history widget)

### Step 1: Update factory detail route to fetch sample history

In `app/routes/fabricas.py`, find the `ver` function and update the stats dict:

```python
@fabricas_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de fábrica."""
    fabrica = Fabrica.query.get_or_404(id)
    
    # Obtener últimas 10 entradas de esta fábrica
    from app.database.models.entrada import Entrada
    ultimas_entradas = (
        Entrada.query
        .filter_by(fabrica_id=id)
        .filter_by(anulado=False)
        .order_by(Entrada.fech_entrada.desc())
        .limit(10)
        .all()
    )
    
    # Estadísticas
    stats = {
        'total_muestras': Entrada.query.filter_by(fabrica_id=id, anulado=False).count(),
        'muestras_anio': Entrada.query.filter(
            Entrada.fabrica_id == id,
            Entrada.anulado == False,
            db.func.extract('year', Entrada.fech_entrada) == datetime.now().year
        ).count(),
        'ensayos_pendientes': 0,  # Phase 3+
        'ultimas_entradas': ultimas_entradas
    }
    
    return render_template('fabricas/ver.html',
                         fabrica=fabrica,
                         stats=stats)
```

### Step 2: Add history widget to ver.html template

In `app/templates/fabricas/ver.html`, add after the statistics card:

```html
<!-- Sample History -->
<div class="card mt-3">
    <div class="card-header">
        <h5 class="mb-0">Historial de Muestras</h5>
    </div>
    <div class="card-body p-0">
        {% if stats.ultimas_entradas %}
        <table class="table table-sm mb-0">
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Fecha</th>
                    <th>Producto</th>
                    <th>Lote</th>
                    <th>Cantidad</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {% for entrada in stats.ultimas_entradas %}
                <tr>
                    <td>
                        <a href="{{ url_for('entradas.ver', id=entrada.id) }}">
                            {{ entrada.codigo }}
                        </a>
                    </td>
                    <td>{{ entrada.fech_entrada.strftime('%d/%m/%Y') }}</td>
                    <td>{{ entrada.producto.nombre[:30] }}...</td>
                    <td>{{ entrada.lote or '-' }}</td>
                    <td>{{ entrada.cantidad_recib }}</td>
                    <td>
                        {% if entrada.status == 'RECIBIDO' %}
                        <span class="badge badge-primary">Recibido</span>
                        {% elif entrada.status == 'EN_PROCESO' %}
                        <span class="badge badge-warning">En Proceso</span>
                        {% elif entrada.status == 'COMPLETADO' %}
                        <span class="badge badge-info">Completado</span>
                        {% elif entrada.status == 'ENTREGADO' %}
                        <span class="badge badge-success">Entregado</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-muted p-3 mb-0">No hay muestras registradas para esta fábrica.</p>
        {% endif %}
    </div>
</div>
```

---

## Task 3: Password Strength Indicator

**Goal:** Add visual password strength indicator to user creation form.

**Files:**
- Modify: `app/templates/admin/crear_usuario.html` (add strength meter)
- Create: `app/static/js/password-strength.js` (strength calculation)

### Step 1: Create password strength JavaScript

Create file `app/static/js/password-strength.js`:

```javascript
/**
 * Password Strength Indicator
 * Calculates and displays password strength visually
 */

(function() {
    'use strict';
    
    function calculateStrength(password) {
        let score = 0;
        
        if (!password) return { score: 0, level: 'none', text: '' };
        
        // Length checks
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;
        if (password.length >= 16) score += 1;
        
        // Character type checks
        if (/[a-z]/.test(password)) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^a-zA-Z0-9]/.test(password)) score += 1;
        
        // Common patterns (penalty)
        if (/^(.)\1+$/.test(password)) score -= 1; // repeated chars
        if (/^(password|123456|qwerty)/i.test(password)) score = 0; // common passwords
        
        // Normalize to 0-100
        const maxScore = 8;
        const percentage = Math.max(0, Math.min(100, (score / maxScore) * 100));
        
        // Determine level
        let level, color, text;
        if (percentage < 25) {
            level = 'weak';
            color = '#dc3545'; // red
            text = 'Débil';
        } else if (percentage < 50) {
            level = 'fair';
            color = '#ffc107'; // yellow
            text = 'Regular';
        } else if (percentage < 75) {
            level = 'good';
            color = '#17a2b8'; // cyan
            text = 'Buena';
        } else {
            level = 'strong';
            color = '#28a745'; // green
            text = 'Fuerte';
        }
        
        return { score: percentage, level: level, color: color, text: text };
    }
    
    function updateStrengthMeter(password, meterId) {
        const meter = document.getElementById(meterId);
        if (!meter) return;
        
        const strength = calculateStrength(password);
        
        // Update bar
        meter.style.width = strength.score + '%';
        meter.style.backgroundColor = strength.color;
        meter.setAttribute('data-level', strength.level);
        
        // Update text
        const textEl = document.getElementById(meterId + '-text');
        if (textEl) {
            textEl.textContent = strength.text;
            textEl.style.color = strength.color;
        }
    }
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        const passwordInput = document.getElementById('password');
        const confirmInput = document.getElementById('confirmar_password');
        
        if (passwordInput) {
            // Add strength meter HTML
            const meterContainer = document.createElement('div');
            meterContainer.className = 'password-strength mt-2';
            meterContainer.innerHTML = `
                <div class="progress" style="height: 8px;">
                    <div id="password-strength-bar" class="progress-bar" 
                         role="progressbar" style="width: 0%"></div>
                </div>
                <small id="password-strength-bar-text" class="text-muted"></small>
            `;
            passwordInput.parentNode.appendChild(meterContainer);
            
            // Add event listener
            passwordInput.addEventListener('input', function() {
                updateStrengthMeter(this.value, 'password-strength-bar');
            });
        }
        
        // Match indicator
        if (confirmInput && passwordInput) {
            confirmInput.addEventListener('input', function() {
                const matchEl = document.getElementById('password-match');
                if (!matchEl) {
                    const el = document.createElement('small');
                    el.id = 'password-match';
                    el.className = 'd-block mt-1';
                    confirmInput.parentNode.appendChild(el);
                }
                
                const match = document.getElementById('password-match');
                if (this.value && this.value === passwordInput.value) {
                    match.textContent = '✓ Las contraseñas coinciden';
                    match.className = 'd-block mt-1 text-success';
                } else if (this.value) {
                    match.textContent = '✗ Las contraseñas no coinciden';
                    match.className = 'd-block mt-1 text-danger';
                }
            });
        }
    });
})();
```

### Step 2: Add script include to crear_usuario.html

Add before closing `</body>` tag in `app/templates/admin/crear_usuario.html`:

```html
{% block scripts %}
{{ super() }}
<script src="{{ url_for('static', filename='js/password-strength.js') }}"></script>
{% endblock %}
```

---

## Execution Order

1. **Task 1: Export CSV Audit** - Simpler, immediate value
2. **Task 2: Factory Sample History** - Depends on Entrada model (already exists)
3. **Task 3: Password Strength** - Frontend enhancement, lowest priority

---

## Testing Commands

After each task, run:

```bash
# Task 1 & 2: Check routes work
flask routes | grep -E "exportar|ver"

# Task 3: Check static file exists
ls -la app/static/js/password-strength.js

# Run relevant tests
pytest tests/unit/test_clientes.py -v
pytest tests/unit/ -k "fabrica" -v
```

---

## Plan Complete

**Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**