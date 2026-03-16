# DataLab — Plan de Implementación: Liquid Glass Design System
**Skill aplicada:** `ui-ux-pro-max`  
**Estilo:** Liquid Glass Minimalism  
**Paleta:** Navy-Indigo oscuro + Sky Blue (`#38bdf8`) + Violet (`#a78bfa`)  
**Tipografía:** Plus Jakarta Sans + JetBrains Mono  

---

## Contexto del proyecto

DataLab es un LIMS (Laboratory Information Management System) gubernamental de Flask con Jinja2 templates.  
La arquitectura de estilos es modular: un `style.css` principal que importa todos los parciales con `@import`.

### Estado actual (ya completado ✅)

| Archivo | Estado |
|---|---|
| `app/static/css/base/variables.css` | ✅ Reescrito — tokens glass, paleta dark, tipografía |
| `app/static/css/base/glass.css` | ✅ Creado nuevo — sistema de clases `.glass-*` |
| `app/static/css/base/reset.css` | ✅ Reescrito — body con `bg-gradient fixed` |
| `app/static/css/style.css` | ✅ Actualizado — importa `glass.css` |
| `app/static/css/layouts/sidebar.css` | ✅ Reescrito — glass blur 28px, nav-link glow azul |
| `app/static/css/layouts/header.css` | ✅ Reescrito — header translúcido glass |
| `app/static/css/components/buttons.css` | ✅ Reescrito — gradientes líquidos, glow en hover |

---

## Archivos pendientes (orden de ejecución)

> **Regla para el agente:** Leer el archivo antes de reescribirlo. Respetar todos los nombres de clase existentes para no romper los templates Jinja2. Añadir clases nuevas, no eliminar las que ya están en uso en los templates.

---

## FASE 1 — HTML Base (prioridad máxima)

### 1.1 `app/templates/base.html`

**Problema actual:** Usa `class="bg-gray-100 min-h-screen flex flex-col"` en `<body>` (Tailwind) que pisa el fondo glass. El `<head>` no carga las Google Fonts nuevas. El `theme-color` es incorrecto.

**Cambios exactos a realizar:**

1. **Agregar Google Fonts** — Insertar en `<head>` ANTES del `<link rel="stylesheet" href="...style.css">`:
   ```html
   <!-- Google Fonts: Plus Jakarta Sans + JetBrains Mono -->
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
   <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
   ```

2. **Cambiar `theme-color`** en el meta tag:
   ```html
   <meta name="theme-color" content="#070c18">
   ```

3. **Cambiar el `<body>`** — quitar las clases Tailwind de fondo:
   ```html
   <!-- ANTES -->
   <body class="bg-gray-100 min-h-screen flex flex-col">
   
   <!-- DESPUÉS -->
   <body class="min-h-dvh flex flex-col">
   ```

4. **Cambiar el `<main>`** — quitar clases Tailwind de contenedor que pisarían el layout glass:
   ```html
   <!-- ANTES -->
   <main class="flex-grow container mx-auto px-4 py-8">
   
   <!-- DESPUÉS -->
   <main class="flex-grow main-content">
       <div class="main-body">
   ```
   Y cerrar el `</div>` antes del `</main>`.

---

### 1.2 `app/templates/partials/navbar.html`

**Problema actual:** Usa Tailwind `bg-blue-600 text-white shadow-lg`. Este navbar es la barra TOP del proyecto (visible solo en mobile o cuando no hay sidebar). Debe convertirse en glass.

**Cambios exactos:**

Reemplazar completamente el contenido por:
```html
<nav class="top-header" role="navigation" aria-label="Navegación principal">
    <div class="header-left">
        <!-- Botón menú móvil -->
        <button class="mobile-menu-btn" id="sidebarToggle" aria-label="Abrir menú">
            <i class="fas fa-bars" aria-hidden="true"></i>
        </button>

        <!-- Brand solo en mobile (el sidebar ya lo tiene en desktop) -->
        <a href="{{ url_for('dashboard.index') }}" class="sidebar-brand hidden-desktop" aria-label="DataLab inicio">
            <i class="fas fa-flask" style="color: #38bdf8; filter: drop-shadow(0 0 6px rgba(56,189,248,0.6));" aria-hidden="true"></i>
            <span class="sidebar-title">DataLab</span>
        </a>
    </div>

    {% if current_user.is_authenticated %}
    <div class="header-right">
        <!-- Informes -->
        <a href="{{ url_for('informes.listar') }}" class="header-btn" title="{{ _('Informes Oficiales') }}" aria-label="{{ _('Informes Oficiales') }}">
            <i class="fas fa-file-alt" aria-hidden="true"></i>
        </a>

        <!-- Analytics -->
        <a href="{{ url_for('analytics.index') }}" class="header-btn" title="{{ _('Analytics') }}" aria-label="{{ _('Analytics') }}">
            <i class="fas fa-chart-bar" aria-hidden="true"></i>
        </a>

        <!-- Facturación -->
        <a href="{{ url_for('billing.billing_index') }}" class="header-btn" title="{{ _('Facturación') }}" aria-label="{{ _('Facturación') }}">
            <i class="fas fa-file-invoice-dollar" aria-hidden="true"></i>
        </a>

        <!-- Notificaciones -->
        {% from 'components/notifications/notification_dropdown.html' import notification_dropdown %}
        {{ notification_dropdown() }}

        <!-- Usuario -->
        <span class="header__user-name" aria-label="{{ _('Usuario actual') }}">
            <i class="fas fa-user-circle mr-1" style="color: #38bdf8;" aria-hidden="true"></i>
            {{ current_user.nombre_completo or current_user.username }}
        </span>

        <!-- Logout -->
        <a href="{{ url_for('auth.logout') }}" class="header-btn" title="{{ _('Cerrar Sesión') }}" aria-label="{{ _('Cerrar Sesión') }}">
            <i class="fas fa-sign-out-alt" aria-hidden="true"></i>
        </a>
    </div>
    {% endif %}
</nav>
```

Agregar CSS en `header.css` para `.hidden-desktop`:
```css
@media (min-width: 769px) {
    .hidden-desktop { display: none; }
}
```

---

### 1.3 `app/templates/partials/footer.html`

**Problema actual:** Usa Tailwind `bg-gray-800 text-white`. Debe ser glass compacto.

**Reemplazar completamente por:**
```html
<footer class="footer" role="contentinfo">
    <div class="footer__container">
        <div class="footer__bottom">
            <p class="footer__copyright">
                <i class="fas fa-flask mr-1" style="color: #38bdf8;" aria-hidden="true"></i>
                &copy; {{ now.year if now else '2026' }} DataLab &mdash; {{ _('Sistema de Gestión de Laboratorio') }}
            </p>
            <p class="footer__org">
                ONIE &mdash; Oficina Nacional de Inspección Estatal
            </p>
        </div>
    </div>
</footer>
```

---

### 1.4 `app/templates/partials/flash_messages.html`

**Problema actual:** Clases Tailwind hardcodeadas (`bg-green-100 text-green-800 border-green-200` etc.). Quedan como parches claros sobre fondo oscuro.

**Reemplazar completamente por:**
```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <div class="flash-messages" role="region" aria-label="{{ _('Notificaciones') }}">
            {% for category, message in messages %}
                {% set cat = category if category in ['success','error','danger','warning','info'] else 'info' %}
                {% set mapped = 'danger' if cat == 'error' else cat %}
                <div class="alert alert--{{ mapped }} alert--dismissible" role="alert" aria-live="polite">
                    <span class="alert__icon" aria-hidden="true">
                        {% if mapped == 'success' %}<i class="fas fa-check-circle"></i>
                        {% elif mapped == 'danger' %}<i class="fas fa-exclamation-circle"></i>
                        {% elif mapped == 'warning' %}<i class="fas fa-exclamation-triangle"></i>
                        {% else %}<i class="fas fa-info-circle"></i>
                        {% endif %}
                    </span>
                    <div class="alert__content">
                        <p class="alert__message">{{ message }}</p>
                    </div>
                    <button class="alert__close" onclick="this.parentElement.remove()" aria-label="{{ _('Cerrar') }}">
                        <i class="fas fa-times alert__close-icon" aria-hidden="true"></i>
                    </button>
                </div>
            {% endfor %}
        </div>
    {% endif %}
{% endwith %}
```

---

## FASE 2 — CSS de Tipografía y Layout Base

### 2.1 `app/static/css/base/typography.css`

**Problema actual:** Los headings usan `color: var(--gray-900)` que en dark mode es `rgba(15,23,42,0.95)` (casi negro), haciendo el texto invisible. Los `a` apuntan a `--primary-600` que en dark theme es azul muy oscuro.

**Cambios:**
- Reemplazar TODOS los `color: var(--gray-900)` en headings por `color: var(--text-primary)`
- Reemplazar `color: var(--gray-700)` en párrafos por `color: var(--text-secondary)`
- Reemplazar `color: var(--gray-600)` en `.text-secondary` por `color: var(--text-secondary)`
- Reemplazar `color: var(--gray-500)` en `.text-muted` por `color: var(--text-muted)`
- Reemplazar `color: var(--primary-600)` en `a` y `.link` por `color: var(--primary-400)`
- `a:hover` → `color: var(--primary-300)`
- `blockquote` → cambiar `background-color: var(--gray-50)` por `background: var(--glass-1)`, `border-left-color` a `var(--primary-400)`, `color` a `var(--text-secondary)`, `backdrop-filter: blur(8px)`
- `code, pre` → cambiar `background-color: var(--gray-100)` por `background: var(--glass-1)`, `color: var(--primary-400)`, agregar `border: 1px solid var(--glass-border-subtle)`, `backdrop-filter: blur(8px)`
- `mark, .highlight` → cambiar background a `rgba(251,191,36,0.20)`, color a `var(--warning-500)`

**Añadir al final del archivo** el siguiente bloque de utilidades glass:
```css
/* ─── GRADIENT TEXT (glass design system) ─── */
.text-gradient-primary {
    background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.text-gradient-success {
    background: linear-gradient(135deg, #34d399 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ─── COLOR OVERRIDES para dark theme ─── */
.text-primary   { color: var(--primary-400) !important; }
.text-secondary { color: var(--text-secondary) !important; }
.text-muted     { color: var(--text-muted) !important; }
.text-success   { color: var(--success-500) !important; }
.text-warning   { color: var(--warning-500) !important; }
.text-danger    { color: var(--error-500) !important; }
.text-info      { color: var(--info-500) !important; }

/* Todos los grises apuntan a rgba sobre fondo oscuro */
.text-gray-50  { color: rgba(248,250,252,0.04) !important; }
.text-gray-100 { color: rgba(248,250,252,0.08) !important; }
.text-gray-200 { color: rgba(248,250,252,0.12) !important; }
.text-gray-300 { color: rgba(248,250,252,0.20) !important; }
.text-gray-400 { color: rgba(148,163,184,0.75) !important; }
.text-gray-500 { color: rgba(148,163,184,0.55) !important; }
.text-gray-600 { color: var(--text-tertiary) !important; }
.text-gray-700 { color: var(--text-secondary) !important; }
.text-gray-800 { color: var(--text-primary) !important; }
.text-gray-900 { color: var(--text-primary) !important; }
```

---

### 2.2 `app/static/css/pages/base.css`

**Problema actual:** `.main-content` tiene `background-color: var(--background-secondary)` que pone un fondo sólido blanco sobre el gradiente glass. También faltan estilos para `.flash-messages` en el nuevo diseño.

**Cambios:**
- `.main-content` → eliminar `background-color`, agregar `position: relative; z-index: 1`
- `.main-header` → cambiar `background-color: var(--background-primary)` y `border-bottom` por los tokens glass:
  ```css
  background: rgba(7, 12, 24, 0.70);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border-bottom: 1px solid var(--glass-border-subtle);
  box-shadow: 0 1px 0 var(--glass-border-subtle), 0 4px 24px rgba(0,0,0,0.30);
  ```
- `.menu-toggle:hover` → cambiar `background-color: var(--gray-100)` por `background: var(--glass-2)`
- `.breadcrumb` → `color: var(--text-tertiary)` (ya correcto, verificar)
- `.breadcrumb-link:hover` → `color: var(--primary-400)` (no `var(--primary-600)`)
- `.search-input` → reemplazar por:
  ```css
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  border-radius: var(--radius-full);
  ```
- `.search-input:focus` → border `rgba(56,189,248,0.45)`, box-shadow `0 0 0 3px rgba(56,189,248,0.10)`
- `.notification-btn:hover` → cambiar `background-color: var(--gray-100)` por `background: var(--glass-2)`
- `.user-btn:hover` → cambiar `background-color: var(--gray-100)` por `background: var(--glass-2)`
- `.user-name` → `color: var(--text-primary)` (ya correcto, verificar)
- `.user-role` → `color: var(--text-tertiary)` (ya correcto)

**Flash messages** — reemplazar los 4 variantes `.flash-message.*` por:
```css
.flash-messages {
    margin: var(--spacing-4) var(--spacing-6) 0;
}

.flash-message {
    padding: var(--spacing-4);
    border-radius: var(--radius-xl);
    margin-bottom: var(--spacing-3);
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    background: var(--glass-2);
    backdrop-filter: var(--glass-blur-md);
    -webkit-backdrop-filter: var(--glass-blur-md);
    border: 1px solid var(--glass-border);
}

.flash-message.success { border-color: rgba(52,211,153,0.30); box-shadow: 0 0 20px rgba(52,211,153,0.10); color: var(--success-500); }
.flash-message.error   { border-color: rgba(248,113,113,0.30); box-shadow: 0 0 20px rgba(248,113,113,0.10); color: var(--error-500); }
.flash-message.warning { border-color: rgba(251,191,36,0.30);  box-shadow: 0 0 20px rgba(251,191,36,0.10);  color: var(--warning-500); }
.flash-message.info    { border-color: rgba(56,189,248,0.30);  box-shadow: 0 0 20px rgba(56,189,248,0.10);  color: var(--info-500); }
```

---

## FASE 3 — Componentes CSS

### 3.1 `app/static/css/components/tables.css`

**Problema actual:** Fondo blanco sólido (`.table { background-color: var(--bg-primary) }`), headers con `var(--bg-secondary)`, hover con `var(--bg-secondary)`. Todo pisa el glass.

**Reescribir completamente.** El agente debe preservar todos los nombres de clase existentes. Implementar según estas reglas:

- `.table-wrapper` / `.table__wrapper` → `background: var(--glass-1); backdrop-filter: var(--glass-blur-md); border: 1px solid var(--glass-border); border-radius: var(--radius-xl); overflow: hidden`
- `.table` → `background: transparent; width: 100%; border-collapse: collapse`
- `thead tr` → `background: rgba(255,255,255,0.04); border-bottom: 1px solid var(--glass-border)`
- `th` → `color: var(--text-muted); font-size: var(--font-size-xs); font-weight: var(--font-weight-semibold); text-transform: uppercase; letter-spacing: 0.07em; padding: var(--spacing-3) var(--spacing-4); background: transparent`
- `td` → `color: var(--text-secondary); font-size: var(--font-size-sm); padding: var(--spacing-3) var(--spacing-4); border-bottom: 1px solid var(--glass-border-subtle)`
- `tbody tr:last-child td` → `border-bottom: none`
- `tbody tr:hover` → `background: var(--glass-hover); td { color: var(--text-primary) }`
- `.table__status--active` → `background: var(--success-50); color: var(--success-500); border: 1px solid rgba(52,211,153,0.20); border-radius: var(--radius-full); padding: 2px 10px; font-size: 0.7rem`
- `.table__status--inactive` → `background: rgba(148,163,184,0.10); color: var(--text-muted)`
- `.table__status--pending` → `background: var(--warning-50); color: var(--warning-500); border: 1px solid rgba(251,191,36,0.20)`
- `.table__status--error` → `background: var(--error-50); color: var(--error-500); border: 1px solid rgba(248,113,113,0.20)`
- `.table__action:hover` → `background: var(--glass-2); color: var(--primary-400)`

---

### 3.2 `app/static/css/components/metrics-cards.css`

**Problema actual:** Cards blancas (`.metric-card { background-color: var(--white) }`) con `border: 1px solid var(--gray-200)`. El `::before` top-bar es lo único que diferencia cada card.

**Reescribir completamente.** Preservar todos los nombres de clase. Implementar:

- `.metric-card` → convertir a glass card:
  ```css
  .metric-card {
      background: var(--glass-2);
      backdrop-filter: var(--glass-blur-md);
      -webkit-backdrop-filter: var(--glass-blur-md);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-xl);
      box-shadow: var(--glass-shadow-md);
      padding: var(--spacing-5);
      position: relative;
      overflow: hidden;
      transition: all var(--duration-200) var(--ease-spring);
  }
  ```
- Eliminar el `::before` top-bar. En su lugar, cada variante de color usará un **glow lateral izquierdo**:
  ```css
  .metric-card::before {
      content: '';
      position: absolute;
      left: 0; top: 15%; bottom: 15%;
      width: 3px;
      background: var(--metric-accent, var(--primary-400));
      border-radius: 0 2px 2px 0;
      box-shadow: 0 0 12px var(--metric-accent, var(--primary-400));
  }
  ```
- Variantes de color (setean `--metric-accent`):
  ```css
  .metric-card-primary { --metric-accent: #38bdf8; border-color: rgba(56,189,248,0.20); }
  .metric-card-success { --metric-accent: #34d399; border-color: rgba(52,211,153,0.20); }
  .metric-card-warning { --metric-accent: #fbbf24; border-color: rgba(251,191,36,0.20); }
  .metric-card-info    { --metric-accent: #22d3ee; border-color: rgba(34,211,238,0.20); }
  ```
- `.metric-card:hover` → `transform: translateY(-4px); box-shadow: 0 0 30px rgba(56,189,248,0.15), var(--glass-shadow-lg); border-color: var(--glass-border-strong)`
- `.metric-title` → `color: var(--text-muted)`
- `.metric-value` → `color: var(--text-primary); font-family: var(--font-family-mono)` (datos numéricos en mono)
- `.metric-icon-users`      → `background: rgba(56,189,248,0.12); color: #38bdf8`
- `.metric-icon-revenue`    → `background: rgba(52,211,153,0.12); color: #34d399`
- `.metric-icon-sessions`   → `background: rgba(251,191,36,0.12); color: #fbbf24`
- `.metric-icon-conversion` → `background: rgba(34,211,238,0.12); color: #22d3ee`
- `.metric-change-positive` → `color: var(--success-500); background: var(--success-50)`
- `.metric-change-negative` → `color: var(--error-500); background: var(--error-50)`
- `.metric-change-neutral`  → `color: var(--text-muted); background: var(--glass-1)`

---

### 3.3 `app/static/css/components/forms.css`

**Advertencia:** El archivo tiene un error de sintaxis — hay CSS flotante (`font-family: inherit; line-height...`) después del bloque `.select-sm:focus`. Debes eliminarlo al reescribir.

**Cambios principales:**

- `.form__input, .form__textarea, .form__select` → reemplazar fondo blanco por glass:
  ```css
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  border-radius: var(--radius-lg);
  ```
- `::placeholder` → `color: var(--text-muted)`
- `:focus` → `border-color: rgba(56,189,248,0.50); background: rgba(255,255,255,0.08); box-shadow: 0 0 0 3px rgba(56,189,248,0.12), inset 0 1px 0 rgba(255,255,255,0.06)`
- `:hover:not(:disabled)` → `border-color: var(--glass-border-strong)`
- `:disabled` → `background: rgba(255,255,255,0.02); opacity: 0.38; cursor: not-allowed`
- `--input--error` → `border-color: rgba(248,113,113,0.50); background: rgba(248,113,113,0.05)`; focus: `box-shadow: 0 0 0 3px rgba(248,113,113,0.12)`
- `--input--success` → `border-color: rgba(52,211,153,0.50); background: rgba(52,211,153,0.05)`
- `.form__label` → `color: var(--text-secondary)`
- `.form__label--required::after` → `color: var(--error-500)`
- `.form__help` → `color: var(--text-muted)`
- `.form__error` → `color: var(--error-500)`; eliminar el `::before` con emoji, usar clase FA
- `.form__success` → `color: var(--success-500)`
- `.select-sm` → mismo glass que `.form__select`
- `.form__select` → arrow SVG: cambiar stroke color de `%236b7280` a `%2394a3b8` (gris claro para dark)
- `.form__file-label` → `background: var(--glass-1); border: 2px dashed var(--glass-border); color: var(--text-muted)`; hover: `border-color: rgba(56,189,248,0.45); background: var(--primary-50); color: var(--primary-400)`
- `.form__actions` → `border-top: 1px solid var(--glass-border-subtle)`
- `.form__checkbox input, .form__radio input` → `accent-color: var(--primary-400)`

---

### 3.4 `app/static/css/components/alerts.css`

**Problema actual:** Las 4 variantes usan fondos claros pastel (`#dbeafe`, `#d1fae5`, `#fef3c7`, `#fee2e2`) — completamente incompatibles con dark theme.

**Reescribir las 4 variantes** usando glass + glow semántico:

```css
/* Base glass para todas las alertas */
.alert {
    background: var(--glass-2);
    backdrop-filter: var(--glass-blur-md);
    -webkit-backdrop-filter: var(--glass-blur-md);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    color: var(--text-primary);
    /* conservar display, padding, gap, position existentes */
}

.alert--info {
    border-color: rgba(56, 189, 248, 0.25);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.08);
}
.alert--info .alert__title   { color: var(--primary-300); }
.alert--info .alert__message { color: var(--text-secondary); }
.alert--info .alert__icon    { color: var(--primary-400); }

.alert--success {
    border-color: rgba(52, 211, 153, 0.25);
    box-shadow: 0 0 20px rgba(52, 211, 153, 0.08);
}
.alert--success .alert__title   { color: var(--success-500); }
.alert--success .alert__message { color: var(--text-secondary); }
.alert--success .alert__icon    { color: var(--success-500); }

.alert--warning {
    border-color: rgba(251, 191, 36, 0.25);
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.08);
}
.alert--warning .alert__title   { color: var(--warning-500); }
.alert--warning .alert__message { color: var(--text-secondary); }
.alert--warning .alert__icon    { color: var(--warning-500); }

.alert--danger {
    border-color: rgba(248, 113, 113, 0.25);
    box-shadow: 0 0 20px rgba(248, 113, 113, 0.08);
}
.alert--danger .alert__title   { color: var(--error-500); }
.alert--danger .alert__message { color: var(--text-secondary); }
.alert--danger .alert__icon    { color: var(--error-500); }
```

- `.alert__close:hover` → `background: var(--glass-2); color: var(--text-primary)` (ya no `rgba(0,0,0,0.1)`)
- `.alerts-container .alert` → agregar `backdrop-filter: var(--glass-blur-md)` + shadow glow
- Variante `.alert--solid.*` → usar gradientes del design system (igual que botones)
- Variante `.alert--outline.*` → glass transparente + border de color semántico

---

### 3.5 `app/static/css/components/modals.css`

**Problema actual:** `.modal` usa `background-color: var(--background-primary)` (blanco), `.modal-footer` usa `background-color: var(--gray-50)`. `.modal-overlay` es `rgba(0,0,0,0.5)` sin blur.

**Cambios:**

- `.modal-overlay` → agregar `backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); background: rgba(0,0,0,0.55)`
- `.modal` → convertir a glass:
  ```css
  background: rgba(10, 16, 38, 0.85);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow-lg), 0 0 60px rgba(0,0,0,0.50);
  border-radius: var(--radius-2xl);
  ```
- `.modal-header` → `border-bottom: 1px solid var(--glass-border-subtle)`
- `.modal-title` → `color: var(--text-primary)`
- `.modal-close` → `color: var(--text-muted)`; hover: `background: var(--glass-2); color: var(--text-primary)`
- `.modal-footer` → `background: rgba(0,0,0,0.20); border-top: 1px solid var(--glass-border-subtle)`
- `.modal-confirm-icon` → `color: var(--warning-500)` + `filter: drop-shadow(0 0 8px rgba(251,191,36,0.40))`
- `.modal-confirm-title` → `color: var(--text-primary)`
- `.modal-confirm-message` → `color: var(--text-secondary)`

---

### 3.6 `app/static/css/components/navigation.css`

**Problema actual:** `.nav-link:hover` usa `background-color: var(--gray-100)` (claro), `.nav-link-active` usa `background-color: var(--primary-100)` (azul pálido claro), `.nav-pills .nav-link-active` usa `background-color: var(--primary-600)`.

**Cambios:**

- `.nav-link` → `color: var(--text-secondary)`
- `.nav-link:hover` → `background: var(--glass-1); border: 1px solid var(--glass-border-subtle); color: var(--text-primary)`; eliminar el hover con `background-color: var(--gray-100)`
- `.nav-link-active` → `background: var(--primary-50); color: var(--primary-400); border: 1px solid rgba(56,189,248,0.22); box-shadow: 0 0 12px rgba(56,189,248,0.08)`
- `.breadcrumb` → `color: var(--text-tertiary)`
- `.breadcrumb-item::after` → `color: var(--glass-border-strong)`
- `.breadcrumb-link` → `color: var(--text-secondary)`; hover: `color: var(--primary-400)`
- `.breadcrumb-current` → `color: var(--text-primary)`
- `.nav-tabs` → `border-bottom: 1px solid var(--glass-border-subtle)`
- `.nav-tabs .nav-link` → `border-bottom: 2px solid transparent`
- `.nav-tabs .nav-link:hover` → `background: var(--glass-1); border-bottom-color: var(--glass-border)`
- `.nav-tabs .nav-link-active` → `background: transparent; border-bottom-color: var(--primary-400); color: var(--primary-400)`
- `.nav-pills .nav-link-active` → `background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; border: none; box-shadow: 0 4px 14px rgba(14,165,233,0.30)`

---

## FASE 4 — Layouts restantes

### 4.1 `app/static/css/layouts/footer.css`

**Reescribir completamente** adaptando glass. Preservar los nombres de clase. Reglas clave:

- `.footer` → `background: rgba(7,12,24,0.80); backdrop-filter: var(--glass-blur-md); border-top: 1px solid var(--glass-border-subtle); padding: var(--spacing-4) 0`
- `.footer__title` → `color: var(--text-primary)`
- `.footer__link, .footer__description` → `color: var(--text-muted)`
- `.footer__link:hover` → `color: var(--primary-400)`
- `.footer__social-link` → `background: var(--glass-1); border: 1px solid var(--glass-border); color: var(--text-muted)` ; hover: `background: var(--primary-500); border-color: var(--primary-500); color: white; box-shadow: 0 0 16px rgba(14,165,233,0.30)`
- `.footer__bottom` → `border-top: 1px solid var(--glass-border-subtle)`
- `.footer__copyright, .footer__legal-link` → `color: var(--text-muted)`
- `.footer__legal-link:hover` → `color: var(--primary-400)`
- Añadir clase `.footer__org` (usada en el nuevo `footer.html`): `color: var(--text-muted); font-size: var(--font-size-xs)`

---

## FASE 5 — Páginas específicas

### 5.1 `app/static/css/pages/dashboard.css`

**Problema actual:** `.dashboard-container` tiene `background-color: var(--gray-50)` y `min-height: calc(100vh...)`. Las clases son escasas, la mayoría del dashboard usa clases Tailwind en el template.

**Reescribir con las siguientes adiciones:**

```css
/* ─── CONTENEDOR ─── */
.dashboard-container {
    padding: var(--spacing-6);
    min-height: 100dvh;
    /* sin background-color — hereda el gradiente del body */
}

/* ─── HEADER ─── */
.dashboard-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-8);
    padding-bottom: var(--spacing-6);
    border-bottom: 1px solid var(--glass-border-subtle);
}

.dashboard-header__title {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    background: linear-gradient(135deg, #f8fafc 30%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}

.dashboard-header__subtitle {
    color: var(--text-muted);
    margin-top: var(--spacing-1);
    font-size: var(--font-size-sm);
}

/* ─── STATS GRID (Tailwind override para dark) ─── */
/* Las cards del dashboard usan clases Tailwind inline. Sobreescribir: */
.bg-white {
    background: var(--glass-2) !important;
    backdrop-filter: var(--glass-blur-md) !important;
    -webkit-backdrop-filter: var(--glass-blur-md) !important;
    border: 1px solid var(--glass-border) !important;
}

.shadow { box-shadow: var(--glass-shadow-sm) !important; }
.shadow-lg { box-shadow: var(--glass-shadow-lg) !important; }

/* Colores de icon backgrounds Tailwind → dark glass */
.bg-blue-100   { background: rgba(56,189,248,0.12) !important; }
.bg-green-100  { background: rgba(52,211,153,0.12) !important; }
.bg-purple-100 { background: rgba(167,139,250,0.12) !important; }
.bg-orange-100 { background: rgba(251,146,60,0.12)  !important; }

.text-blue-600   { color: #38bdf8 !important; }
.text-green-600  { color: #34d399 !important; }
.text-purple-600 { color: #a78bfa !important; }
.text-orange-600 { color: #fb923c !important; }

/* Texto en cards */
.text-gray-500 { color: var(--text-muted) !important; }
.text-gray-600 { color: var(--text-secondary) !important; }
.text-gray-400 { color: var(--text-muted) !important; }
.text-2xl.font-bold { color: var(--text-primary) !important; font-family: var(--font-family-mono); }

/* Botones de acción rápida Tailwind */
.bg-blue-600   { background: linear-gradient(135deg, #0ea5e9, #0284c7) !important; }
.bg-green-600  { background: linear-gradient(135deg, #10b981, #059669) !important; }
.bg-purple-600 { background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important; }

.hover\:bg-blue-700:hover   { background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important; }
.hover\:bg-green-700:hover  { background: linear-gradient(135deg, #34d399, #10b981) !important; }
.hover\:bg-purple-700:hover { background: linear-gradient(135deg, #a78bfa, #8b5cf6) !important; }

/* Panels de gráficas */
.border-b { border-bottom: 1px solid var(--glass-border-subtle) !important; }
.font-semibold { color: var(--text-primary) !important; }

/* Hover en tabla de registros recientes */
.border-b.last\:border-0 { border-bottom-color: var(--glass-border-subtle) !important; }
.font-medium { color: var(--text-primary) !important; }

/* ─── RESPONSIVE ─── */
@media (max-width: 1024px) {
    .dashboard-container { padding: var(--spacing-4); }
}

@media (max-width: 640px) {
    .dashboard-container { padding: var(--spacing-3); }
}
```

---

## FASE 6 — Utilidades

### 6.1 `app/static/css/utilities/animations.css`

**Agregar al final del archivo** (sin eliminar nada existente):

```css
/* ─── GLASS ANIMATIONS ─── */

/* Shimmer para loading states */
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
}

.skeleton {
    background: linear-gradient(
        90deg,
        var(--glass-1) 25%,
        rgba(255,255,255,0.08) 50%,
        var(--glass-1) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.8s ease-in-out infinite;
    border-radius: var(--radius-md);
}

/* Glow pulse para elementos activos */
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 8px rgba(56,189,248,0.30); }
    50%       { box-shadow: 0 0 20px rgba(56,189,248,0.55), 0 0 40px rgba(56,189,248,0.20); }
}

.animate-glow {
    animation: glow-pulse 2.5s ease-in-out infinite;
}

/* Float suave para elementos destacados */
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-6px); }
}

.animate-float {
    animation: float 4s ease-in-out infinite;
}

/* Fade in con slide desde abajo (para cards de página) */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-up {
    animation: fadeInUp 0.4s var(--ease-out) both;
}

/* Stagger helper (usar con delay-*) */
.stagger-children > * {
    animation: fadeInUp 0.35s var(--ease-out) both;
}

.stagger-children > *:nth-child(1) { animation-delay: 0ms; }
.stagger-children > *:nth-child(2) { animation-delay: 60ms; }
.stagger-children > *:nth-child(3) { animation-delay: 120ms; }
.stagger-children > *:nth-child(4) { animation-delay: 180ms; }
.stagger-children > *:nth-child(5) { animation-delay: 240ms; }
.stagger-children > *:nth-child(6) { animation-delay: 300ms; }
```

---

## Checklist de verificación final

Antes de dar por terminado, verificar punto por punto:

### Visual
- [ ] El fondo gradiente Navy-Indigo oscuro es visible en todas las páginas
- [ ] Las cards tienen efecto blur visible (no fondos sólidos blancos)
- [ ] Los textos tienen contraste mínimo 4.5:1 sobre los fondos glass (verificar con DevTools)
- [ ] Los números en métricas usan `JetBrains Mono`
- [ ] Los headings del dashboard tienen el degradado sky→white
- [ ] Los botones primarios muestran glow azul en hover
- [ ] El sidebar tiene el título "DataLab" con degradado sky→violet

### Tailwind overrides
- [ ] No hay fondos blancos visibles (`bg-white`, `bg-gray-50`, `bg-gray-100`)
- [ ] Los colores de iconos Tailwind (`text-blue-600`, `text-green-600`) son luminosos sobre dark
- [ ] Los hover de botones Tailwind funcionan

### Accesibilidad
- [ ] Focus rings visibles (`outline: 2px solid rgba(56,189,248,0.65)`)
- [ ] Alerts usan `role="alert"` y `aria-live="polite"`
- [ ] Todos los botones icon-only tienen `aria-label`
- [ ] El contraste de texto secundario (`--text-muted`) es al menos 3:1

### Responsive
- [ ] En mobile (<768px) el sidebar se oculta y aparece el botón hamburguesa
- [ ] Las metric-cards colapsan a 1 columna en móvil
- [ ] La barra de búsqueda se oculta en <480px

---

## Notas importantes para el agente

1. **No usar Tailwind CDN** — El proyecto no carga Tailwind como framework completo. Los overrides de clases Tailwind en `dashboard.css` son la solución para las clases ya existentes en los templates.

2. **Preservar nombres de clase** — No renombrar ninguna clase existente. El agente puede añadir clases nuevas pero los templates Jinja2 referencian las clases actuales.

3. **Variables CSS** — Usar siempre los tokens de `variables.css`. Nunca escribir hex directamente en los componentes salvo en `glass.css` y `variables.css`.

4. **`backdrop-filter`** — Siempre incluir el prefijo `-webkit-backdrop-filter` junto a `backdrop-filter` para compatibilidad con Safari.

5. **`min-height: 100dvh`** — Usar `dvh` (dynamic viewport height) en lugar de `vh` para evitar el problema del browser chrome en iOS.

6. **Orden de importación** — `glass.css` debe estar importado DESPUÉS de `reset.css` y ANTES de `typography.css` en `style.css`. (Ya está correcto.)

7. **Plotly charts** — Los gráficos del dashboard usan Plotly con colores hardcodeados en el template JS. Para que sean consistentes con el dark theme, añadir en `dashboard/index.html` al final del script de Plotly:
   ```js
   var darkLayout = {
       paper_bgcolor: 'rgba(0,0,0,0)',
       plot_bgcolor:  'rgba(0,0,0,0)',
       font: { color: 'rgba(148,163,184,0.85)', family: 'Plus Jakarta Sans, sans-serif' },
       xaxis: { gridcolor: 'rgba(255,255,255,0.06)', zerolinecolor: 'rgba(255,255,255,0.10)' },
       yaxis: { gridcolor: 'rgba(255,255,255,0.06)', zerolinecolor: 'rgba(255,255,255,0.10)' }
   };
   ```
   Y aplicarlo con `Plotly.relayout('provincia-chart', darkLayout)` etc. después de cada `newPlot`.

---

*Generado por UI/UX Pro Max Skill — DataLab Liquid Glass Design System*  
*Fecha: 2026-03-14*
