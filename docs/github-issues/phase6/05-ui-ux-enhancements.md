---
title: "[Phase 6] UI/UX Enhancements"
labels: ["phase-6", "advanced", "ui", "ux", "epic"]
---

## Overview
Implement comprehensive UI/UX improvements including mobile responsiveness, dark mode, keyboard shortcuts, bulk actions, advanced filtering, enhanced data tables, and toast notifications.

## 1. Mobile Responsive Improvements

### Breakpoints
```css
/* Tailwind breakpoints */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

### Responsive Components

#### Navigation
- **Mobile:** Hamburger menu with slide-out drawer
- **Tablet:** Collapsible sidebar
- **Desktop:** Full sidebar

```
Mobile View:
┌─────────────────────┐
│ ≡  DataLab    👤   │
├─────────────────────┤
│ [Content Area]      │
│                     │
└─────────────────────┘

Drawer Open:
┌─────────────────────┐
│ ≡  DataLab    👤   │
├────────┬────────────┤
│ Clientes│            │
│ Productos│ [Content]  │
│ Entradas│            │
│ ...    │            │
└────────┴────────────┘
```

#### Data Tables
- Horizontal scroll with sticky first column
- Card view option for mobile
- Collapsible row details
- Touch-friendly action buttons

#### Forms
- Stacked layout on mobile
- Full-width inputs
- Larger touch targets (min 44px)
- Bottom-aligned action buttons

### Responsive Images
```html
<img src="logo.png" 
     srcset="logo-small.png 300w, logo-large.png 800w"
     sizes="(max-width: 600px) 300px, 800px"
     alt="Logo">
```

## 2. Dark Mode Toggle

### Implementation
```javascript
// Theme management
const themeManager = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // System preference listener
        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', e => {
                if (!localStorage.getItem('theme')) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
    },
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.classList.toggle('dark', theme === 'dark');
    },
    
    toggle() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        this.setTheme(next);
        localStorage.setItem('theme', next);
    }
};
```

### Tailwind Dark Mode
```javascript
// tailwind.config.js
module.exports = {
    darkMode: 'class',
    // ...
}
```

### Color Palette
```css
/* Light mode (default) */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --accent-color: #3b82f6;
}

/* Dark mode */
.dark {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --border-color: #334155;
    --accent-color: #60a5fa;
}
```

### Toggle Component
```html
<button id="theme-toggle" class="btn btn-ghost">
    <span class="dark:hidden">🌙</span>
    <span class="hidden dark:inline">☀️</span>
</button>
```

## 3. Keyboard Shortcuts

### Global Shortcuts
| Shortcut | Action |
|----------|--------|
| `?` | Show keyboard shortcuts help |
| `/` or `Ctrl+K` | Focus search |
| `Ctrl+N` | New item (context-dependent) |
| `Ctrl+S` | Save form |
| `Esc` | Close modal / Cancel |
| `G then H` | Go to Home |
| `G then C` | Go to Clientes |
| `G then E` | Go to Entradas |
| `G then P` | Go to Productos |
| `G then I` | Go to Informes |

### List View Shortcuts
| Shortcut | Action |
|----------|--------|
| `J` | Next item |
| `K` | Previous item |
| `Enter` | Open selected item |
| `E` | Edit selected item |
| `D` | Delete selected item (with confirmation) |
| `Shift+A` | Select all |
| `Shift+D` | Deselect all |

### Implementation
```javascript
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.sequence = [];
        this.setupListener();
    }
    
    register(key, callback, context = 'global') {
        if (!this.shortcuts.has(context)) {
            this.shortcuts.set(context, new Map());
        }
        this.shortcuts.get(context).set(key, callback);
    }
    
    setupListener() {
        document.addEventListener('keydown', (e) => {
            // Ignore if in input/textarea
            if (e.target.matches('input, textarea')) {
                if (e.key !== 'Escape') return;
            }
            
            const context = this.getCurrentContext();
            const shortcuts = this.shortcuts.get(context) || 
                             this.shortcuts.get('global');
            
            const key = this.getKeyCombo(e);
            const callback = shortcuts?.get(key);
            
            if (callback) {
                e.preventDefault();
                callback();
            }
        });
    }
    
    getKeyCombo(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('Ctrl');
        if (e.altKey) parts.push('Alt');
        if (e.shiftKey) parts.push('Shift');
        parts.push(e.key.toUpperCase());
        return parts.join('+');
    }
}

// Usage
const shortcuts = new KeyboardShortcuts();
shortcuts.register('Ctrl+K', () => document.getElementById('search').focus());
shortcuts.register('?', () => showShortcutsModal());
```

### Shortcuts Help Modal
```
┌─────────────────────────────────────────────────────────────┐
│ Keyboard Shortcuts                                    [X]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Global:                                                      │
│   ?           Show this help                                 │
│   /           Focus search                                   │
│   Ctrl+K      Focus search                                   │
│   Ctrl+N      Create new item                                │
│                                                              │
│ Navigation:                                                  │
│   G then H    Go to Home                                     │
│   G then C    Go to Clientes                                 │
│   G then E    Go to Entradas                                 │
│   G then P    Go to Productos                                │
│                                                              │
│ List View:                                                   │
│   J           Next item                                      │
│   K           Previous item                                  │
│   Enter       Open selected                                  │
│   E           Edit selected                                  │
│                                                              │
│                         [Close]                              │
└─────────────────────────────────────────────────────────────┘
```

## 4. Bulk Actions

### Selection Interface
```
┌─────────────────────────────────────────────────────────────┐
│ [x] 5 selected          [Delete] [Export] [Change Status ▼]│
├─────────────────────────────────────────────────────────────┤
│ ☐ │ ID  │ Nombre              │ Estado      │ Acciones     │
├───┼─────┼─────────────────────┼─────────────┼──────────────┤
│ ☑ │ 001 │ Cliente A           │ Activo      │ [Ver][Edit]  │
│ ☑ │ 002 │ Cliente B           │ Activo      │ [Ver][Edit]  │
│ ☐ │ 003 │ Cliente C           │ Inactivo    │ [Ver][Edit]  │
│ ☑ │ 004 │ Cliente D           │ Activo      │ [Ver][Edit]  │
└───┴─────┴─────────────────────┴─────────────┴──────────────┘
```

### JavaScript Implementation
```javascript
class BulkActions {
    constructor(tableId) {
        this.table = document.getElementById(tableId);
        this.selected = new Set();
        this.init();
    }
    
    init() {
        // Select all checkbox
        this.table.querySelector('.select-all').addEventListener('change', (e) => {
            this.toggleAll(e.target.checked);
        });
        
        // Individual checkboxes
        this.table.querySelectorAll('.select-row').forEach(cb => {
            cb.addEventListener('change', (e) => {
                this.toggleRow(e.target.dataset.id, e.target.checked);
            });
        });
    }
    
    toggleAll(checked) {
        this.table.querySelectorAll('.select-row').forEach(cb => {
            cb.checked = checked;
            this.toggleRow(cb.dataset.id, checked);
        });
    }
    
    toggleRow(id, checked) {
        if (checked) {
            this.selected.add(id);
        } else {
            this.selected.delete(id);
        }
        this.updateToolbar();
    }
    
    async delete() {
        if (!confirm(`Delete ${this.selected.size} items?`)) return;
        
        const response = await fetch('/api/bulk-delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: [...this.selected] })
        });
        
        if (response.ok) {
            showToast('Items deleted successfully');
            location.reload();
        }
    }
    
    updateToolbar() {
        const toolbar = document.getElementById('bulk-toolbar');
        toolbar.classList.toggle('hidden', this.selected.size === 0);
        toolbar.querySelector('.count').textContent = this.selected.size;
    }
}
```

## 5. Advanced Filtering UI

### Filter Panel
```
┌─────────────────────────────────────────────────────────────┐
│ Filters                                              [Clear] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Fecha:                                                       │
│   [Desde: __________] [Hasta: __________]                   │
│   [Hoy] [Semana] [Mes] [Año]                                │
│                                                              │
│ Estado:                                                      │
│   [x] Pendiente  [x] En progreso  [ ] Completado            │
│                                                              │
│ Área:                                                        │
│   [x] FQ  [x] MB  [ ] ES                                    │
│                                                              │
│ Cliente:                                                     │
│   [Seleccionar cliente...                    ▼]             │
│                                                              │
│ Ordenar por:                                                 │
│   [Fecha ▼] [Ascendente ▼]                                 │
│                                                              │
│ [Aplicar filtros]                                           │
└─────────────────────────────────────────────────────────────┘
```

### Filter State Management
```javascript
class FilterManager {
    constructor() {
        this.filters = new URLSearchParams(window.location.search);
    }
    
    set(key, value) {
        this.filters.set(key, value);
        this.apply();
    }
    
    remove(key) {
        this.filters.delete(key);
        this.apply();
    }
    
    apply() {
        window.location.search = this.filters.toString();
    }
    
    clear() {
        window.location.search = '';
    }
}
```

## 6. Data Tables with Sorting

### Enhanced Table Component
```html
<table class="data-table">
    <thead>
        <tr>
            <th>
                <input type="checkbox" class="select-all">
            </th>
            <th class="sortable" data-column="id">
                ID ↕
            </th>
            <th class="sortable active asc" data-column="nombre">
                Nombre ↑
            </th>
            <th class="sortable" data-column="fecha">
                Fecha ↕
            </th>
            <th>Acciones</th>
        </tr>
    </thead>
    <tbody>
        <!-- Rows -->
    </tbody>
</table>

<div class="pagination">
    <span>Mostrando 1-25 de 156</span>
    <button disabled>Anterior</button>
    <button>1</button>
    <button>2</button>
    <button>3</button>
    <button>Siguiente</button>
</div>
```

### Sorting Implementation
```javascript
document.querySelectorAll('th.sortable').forEach(th => {
    th.addEventListener('click', () => {
        const column = th.dataset.column;
        const currentSort = new URLSearchParams(window.location.search).get('sort');
        const currentOrder = new URLSearchParams(window.location.search).get('order');
        
        let newOrder = 'asc';
        if (currentSort === column && currentOrder === 'asc') {
            newOrder = 'desc';
        }
        
        const params = new URLSearchParams(window.location.search);
        params.set('sort', column);
        params.set('order', newOrder);
        window.location.search = params.toString();
    });
});
```

## 7. Toast Notifications

### Toast System
```javascript
class ToastManager {
    constructor() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${this.getIcon(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close">&times;</button>
        `;
        
        this.container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
        
        // Auto dismiss
        const timeout = setTimeout(() => this.dismiss(toast), duration);
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(timeout);
            this.dismiss(toast);
        });
    }
    
    dismiss(toast) {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }
    
    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }
}

// Usage
const toasts = new ToastManager();
toasts.show('Cliente creado exitosamente', 'success');
toasts.show('Error al guardar', 'error');
toasts.show('Campos requeridos faltantes', 'warning');
```

### Toast Styles
```css
.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px;
    border-radius: 8px;
    background: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.3s ease;
}

.toast.show {
    transform: translateX(0);
    opacity: 1;
}

.toast-success { border-left: 4px solid #22c55e; }
.toast-error { border-left: 4px solid #ef4444; }
.toast-warning { border-left: 4px solid #f59e0b; }
.toast-info { border-left: 4px solid #3b82f6; }

.dark .toast {
    background: #1e293b;
    color: #f8fafc;
}
```

## Acceptance Criteria

- [ ] Mobile responsive on all screen sizes
- [ ] Dark mode toggle with persisted preference
- [ ] System dark mode preference respected
- [ ] Keyboard shortcuts implemented and documented
- [ ] Bulk actions (select, delete, export, status change)
- [ ] Advanced filtering UI with multiple filter types
- [ ] Data tables with column sorting
- [ ] Toast notifications for all CRUD operations
- [ ] Loading states for async operations
- [ ] Empty states for lists
- [ ] Error states with retry options
- [ ] Smooth transitions and animations
- [ ] Accessibility compliance (WCAG 2.1 AA)

## Related Issues
- #XX - Mobile design mockups
- #XX - Component library setup
- #XX - Accessibility audit

## Estimated Effort
**Story Points:** 8
**Estimated Time:** 1-2 weeks

## Dependencies
- Design system/tokens established
- Component library in place
- Icon library (FontAwesome/Heroicons)
