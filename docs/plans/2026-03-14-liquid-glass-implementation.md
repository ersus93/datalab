# Liquid Glass + TailwindCSS Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactorizar completamente el sistema de diseño de DataLab implementando un sistema híbrido Liquid Glass + Glassmorphism utilizando **TailwindCSS CLI Standalone** (sin Node.js) integrado con Flask, comenzando por el Dashboard.

**Architecture:** TailwindCSS CLI Standalone se descarga como ejecutable único, compila CSS desde `input.css` hacia `output.css`. Flask CLI proporciona comandos `flask tailwind:watch` y `flask tailwind:build`. Los componentes glass se implementan como clases utilitarias de Tailwind + CSS custom para efectos avanzados.

**Tech Stack:** TailwindCSS CLI Standalone, Python/Flask, Jinja2, Plotly.js

**Design System Reference:** `docs/plans/2026-03-14-liquid-glass-refactor-design.md`

**Estimated Time:** 5-6 semanas (35-42 días laborables)

**Priority:** Calidad Perfecta - pulir cada detalle

---

## Fase 1: Configuración del Build System (Días 1-5)

### Task 1: Descargar TailwindCSS CLI Standalone

**Files:**
- Create: `tailwindcss.exe` (descargar desde GitHub)
- Modify: `.gitignore` (agregar tailwindcss.exe y output.css)

**Step 1: Descargar TailwindCSS CLI para Windows**

URL: https://github.com/tailwindlabs/tailwindcss/releases/latest

Buscar: `tailwindcss-windows-x64.exe`

**Step 2: Renombrar y ubicar ejecutable**

```bash
# En raíz del proyecto
mv tailwindcss-windows-x64.exe tailwindcss.exe
```

**Step 3: Verificar ejecutable**

```bash
./tailwindcss --version
```

Expected: `tailwindcss v3.x.x` o `v4.x.x`

**Step 4: Actualizar .gitignore**

Agregar al final de `.gitignore`:

```gitignore
# Tailwind CSS
tailwindcss.exe              # Ejecutable (opcional - puede descargar cada dev)
app/static/css/output.css    # CSS compilado (regenerado en build)
```

**Step 5: Commit**

```bash
git add .gitignore
git commit -m "chore: add TailwindCSS CLI executable and update gitignore"
```

---

### Task 2: Crear Archivos de Entrada CSS

**Files:**
- Create: `app/static/css/input.css`
- Create: `app/static/css/liquid-glass/background-orbs.css`
- Create: `app/static/css/liquid-glass/svg-filters.css`

**Step 1: Crear app/static/css/input.css (entry point)**

```css
/* ============================================================
   DATALAB — TailwindCSS Input File
   Liquid Glass + Glassmorphism Design System
   ============================================================ */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ============================================================
   BASE STYLES
   ============================================================ */

@layer base {
  /* Background gradient de página */
  body {
    @apply bg-bg-page;
    background: var(--bg-gradient) fixed;
    background-attachment: fixed;
    min-height: 100dvh;
    position: relative;
  }

  /* Background gradient (variable CSS) */
  :root {
    --bg-gradient: linear-gradient(
      135deg,
      #070c18 0%,
      #0c1330 30%,
      #10103a 60%,
      #080e20 100%
    );
  }

  /* Focus visible global */
  :focus-visible {
    @apply outline-2 outline-primary-500/70 outline-offset-2 rounded-sm;
  }

  /* Selection */
  ::selection {
    @apply bg-primary-500/30 text-text-primary;
  }

  /* Scrollbar glass (Webkit) */
  ::-webkit-scrollbar {
    @apply w-2 h-2;
  }

  ::-webkit-scrollbar-track {
    @apply bg-transparent;
  }

  ::-webkit-scrollbar-thumb {
    @apply bg-white/15 rounded;
  }

  ::-webkit-scrollbar-thumb:hover {
    @apply bg-white/25;
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
}
```

**Step 2: Crear carpeta liquid-glass**

```bash
mkdir -p app/static/css/liquid-glass
```

**Step 3: Crear app/static/css/liquid-glass/background-orbs.css**

```css
/* ============================================================
   BACKGROUND ORBS - Liquid Glass
   Orbes animados de fondo para profundidad visual
   ============================================================ */

@layer components {
  /* Orb base */
  .orb {
    @apply fixed rounded-full pointer-events-none -z-10;
    filter: blur(90px);
  }

  /* Orb Azul (esquina superior izquierda) */
  .orb--blue {
    @apply orb;
    @apply w-[700px] h-[700px] -top-[200px] -left-[100px];
    background: radial-gradient(
      circle,
      rgba(56, 189, 248, 0.22) 0%,
      transparent 65%
    );
    animation: orb-float 12s ease-in-out infinite;
  }

  /* Orb Violet (esquina inferior derecha) */
  .orb--violet {
    @apply orb;
    @apply w-[600px] h-[600px] -bottom-[100px] -right-[80px];
    background: radial-gradient(
      circle,
      rgba(139, 92, 246, 0.20) 0%,
      transparent 65%
    );
    animation: orb-float 15s ease-in-out infinite reverse;
  }

  /* Orb Success (decorativo) */
  .orb--success {
    @apply orb;
    @apply w-[500px] h-[500px] top-1/2 right-0;
    background: radial-gradient(
      circle,
      rgba(52, 211, 153, 0.15) 0%,
      transparent 65%
    );
    animation: orb-float 18s ease-in-out infinite;
  }
}

@keyframes orb-float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 30px) scale(0.9);
  }
}
```

**Step 4: Crear app/static/css/liquid-glass/svg-filters.css**

```css
/* ============================================================
   SVG FILTERS - Liquid Glass Refraction
   Filtros SVG para refracción avanzada (Chrome/Edge only)
   Fallback: backdrop-filter blur para Firefox/Safari
   ============================================================ */

@layer components {
  /* Glass con refracción SVG (Chrome/Edge) */
  .glass-refract {
    backdrop-filter: url(#liquid-glass-refraction);
    -webkit-backdrop-filter: url(#liquid-glass-refraction);
  }

  /* Fallback para Firefox/Safari */
  @supports not (backdrop-filter: url(#liquid-glass-refraction)) {
    .glass-refract {
      backdrop-filter: blur(18px) saturate(180%);
      -webkit-backdrop-filter: blur(18px) saturate(180%);
    }
  }
}

/* SVG Filter Container (inyectar en base.html) */
/*
<svg class="fixed inset-0 w-0 h-0 pointer-events-none">
  <defs>
    <filter id="liquid-glass-refraction">
      <feImage href="data:image/png;base64,DISPLACEMENT_MAP" result="displacement"/>
      <feDisplacementMap in="SourceGraphic" in2="displacement" scale="8" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
*/
```

**Step 5: Commit**

```bash
git add app/static/css/
git commit -m "feat: create TailwindCSS input file with Liquid Glass base styles"
```

---

### Task 3: Configurar tailwind.config.js

**Files:**
- Create: `tailwind.config.js`

**Step 1: Crear tailwind.config.js en raíz del proyecto**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Primary: Sky Blue (científico, preciso)
        primary: {
          50: 'rgba(56, 189, 248, 0.08)',
          100: 'rgba(56, 189, 248, 0.15)',
          200: 'rgba(56, 189, 248, 0.25)',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        
        // Secondary: Violet (autoridad gubernamental)
        secondary: {
          50: 'rgba(167, 139, 250, 0.08)',
          100: 'rgba(167, 139, 250, 0.15)',
          200: 'rgba(167, 139, 250, 0.22)',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },

        // Glass Tokens
        glass: {
          1: 'rgba(255, 255, 255, 0.040)',
          2: 'rgba(255, 255, 255, 0.070)',
          3: 'rgba(255, 255, 255, 0.110)',
          hover: 'rgba(255, 255, 255, 0.130)',
          active: 'rgba(255, 255, 255, 0.170)',
          border: 'rgba(255, 255, 255, 0.110)',
          'border-subtle': 'rgba(255, 255, 255, 0.060)',
          'border-strong': 'rgba(255, 255, 255, 0.190)',
        },

        // Estado (semántico)
        success: {
          50: 'rgba(52, 211, 153, 0.10)',
          100: 'rgba(52, 211, 153, 0.18)',
          500: '#34d399',
          600: '#10b981',
          700: '#059669',
        },
        warning: {
          50: 'rgba(251, 191, 36, 0.10)',
          100: 'rgba(251, 191, 36, 0.18)',
          500: '#fbbf24',
          600: '#f59e0b',
          700: '#d97706',
        },
        error: {
          50: 'rgba(248, 113, 113, 0.10)',
          100: 'rgba(248, 113, 113, 0.18)',
          500: '#f87171',
          600: '#ef4444',
          700: '#dc2626',
        },
        info: {
          50: 'rgba(34, 211, 238, 0.10)',
          100: 'rgba(34, 211, 238, 0.18)',
          500: '#22d3ee',
          600: '#06b6d4',
          700: '#0891b2',
        },

        // Texto
        text: {
          primary: 'rgba(248, 250, 252, 0.92)',
          secondary: 'rgba(148, 163, 184, 0.85)',
          tertiary: 'rgba(100, 116, 139, 0.90)',
          muted: 'rgba(148, 163, 184, 0.50)',
          inverse: '#070c18',
        },

        // Background
        bg: {
          page: '#070c18',
        },
      },

      backdropBlur: {
        sm: 'blur(8px) saturate(140%)',
        md: 'blur(18px) saturate(180%)',
        lg: 'blur(28px) saturate(200%)',
        xl: 'blur(40px) saturate(220%)',
      },

      borderRadius: {
        none: '0',
        sm: '0.25rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.25rem',
        '3xl': '1.75rem',
        full: '9999px',
      },

      boxShadow: {
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.07)',
        'glass-md': '0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.09)',
        'glass-lg': '0 16px 50px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255,255,255,0.12)',
        'glass-xl': '0 25px 60px rgba(0, 0, 0, 0.58), inset 0 1px 0 rgba(255,255,255,0.15)',
        'glass-glow': '0 0 30px rgba(56, 189, 248, 0.18), 0 8px 32px rgba(0, 0, 0, 0.45)',
        'glass-glow-success': '0 0 30px rgba(52, 211, 153, 0.18)',
        'glass-glow-warning': '0 0 30px rgba(251, 191, 36, 0.18)',
        'glass-glow-error': '0 0 30px rgba(248, 113, 113, 0.18)',
      },

      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'orb-blue': 'radial-gradient(circle, rgba(56, 189, 248, 0.22) 0%, transparent 65%)',
        'orb-violet': 'radial-gradient(circle, rgba(139, 92, 246, 0.20) 0%, transparent 65%)',
        'orb-success': 'radial-gradient(circle, rgba(52, 211, 153, 0.15) 0%, transparent 65%)',
      },

      fontFamily: {
        base: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        heading: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },

      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },

      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
      },

      lineHeight: {
        tight: '1.25',
        snug: '1.375',
        normal: '1.5',
        relaxed: '1.625',
        loose: '2',
      },

      spacing: {
        0: '0',
        1: '0.25rem',
        2: '0.5rem',
        3: '0.75rem',
        4: '1rem',
        5: '1.25rem',
        6: '1.5rem',
        8: '2rem',
        10: '2.5rem',
        12: '3rem',
        16: '4rem',
        20: '5rem',
      },

      animation: {
        'orb-float': 'orb-float 12s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'spin': 'spin 700ms linear infinite',
      },

      keyframes: {
        'orb-float': {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 30px) scale(0.9)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(56, 189, 248, 0.18)' },
          '50%': { boxShadow: '0 0 40px rgba(56, 189, 248, 0.28)' },
        },
      },

      transitionDuration: {
        75: '75ms',
        100: '100ms',
        150: '150ms',
        200: '200ms',
        300: '300ms',
        500: '500ms',
      },

      transitionTimingFunction: {
        linear: 'linear',
        in: 'cubic-bezier(0.4, 0, 1, 1)',
        out: 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [
    // Forms plugin (estilos para inputs, selects, checkboxes)
    function({ addBase, theme }) {
      addBase({
        'input[type="text"]': { borderRadius: theme('borderRadius.lg') },
        'input[type="email"]': { borderRadius: theme('borderRadius.lg') },
        'input[type="password"]': { borderRadius: theme('borderRadius.lg') },
        'select': { borderRadius: theme('borderRadius.lg') },
        'textarea': { borderRadius: theme('borderRadius.lg') },
      })
    },
    // Typography plugin (contenido rico)
    function({ addBase, theme }) {
      addBase({
        '.prose': { maxWidth: theme('maxWidth.4xl') },
      })
    },
  ],
};
```

**Step 2: Verificar configuración**

```bash
./tailwindcss -i app/static/css/input.css -o app/static/css/test-output.css --minify
```

Expected: `app/static/css/test-output.css` creado sin errores

**Step 3: Limpiar test file**

```bash
del app/static/css/test-output.css
```

**Step 4: Commit**

```bash
git add tailwind.config.js
git commit -m "feat: configure TailwindCSS with Liquid Glass design tokens"
```

---

### Task 4: Agregar Flask CLI Commands

**Files:**
- Modify: `app/cli.py` (o crear si no existe)
- Modify: `app/__init__.py` (registrar comandos)

**Step 1: Verificar estructura actual de app/cli.py**

```bash
type app\cli.py
```

**Step 2: Agregar comandos Tailwind a app/cli.py**

```python
import subprocess
import click
from flask import current_app

@click.command('tailwind:watch')
def tailwind_watch():
    """
    Watch and rebuild Tailwind CSS during development.
    
    Runs TailwindCSS CLI in watch mode, automatically rebuilding
    output.css when input files change.
    
    Usage:
        flask tailwind:watch
    
    Opens a separate terminal for this long-running process.
    """
    click.echo('🎨 Starting TailwindCSS watch mode...')
    click.echo('📁 Input: app/static/css/input.css')
    click.echo('📁 Output: app/static/css/output.css')
    click.echo('⚡ Press CTRL+C to stop watching\n')
    
    try:
        subprocess.run(
            [
                './tailwindcss',
                '-i', 'app/static/css/input.css',
                '-o', 'app/static/css/output.css',
                '--watch'
            ],
            shell=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f'❌ Error: {e}', fg='red'))
        raise click.Abort()
    except KeyboardInterrupt:
        click.echo('\n✨ Stopped watching. CSS changes will no longer auto-rebuild.')

@click.command('tailwind:build')
def tailwind_build():
    """
    Build Tailwind CSS for production (minified).
    
    Compiles input.css to output.css with full purging and minification.
    Run this before deploying to production.
    
    Usage:
        flask tailwind:build
    """
    click.echo('🏗️  Building TailwindCSS for production...')
    click.echo('📁 Input: app/static/css/input.css')
    click.echo('📁 Output: app/static/css/output.css')
    click.echo('⚡ Minification enabled\n')
    
    try:
        result = subprocess.run(
            [
                './tailwindcss',
                '-i', 'app/static/css/input.css',
                '-o', 'app/static/css/output.css',
                '--minify'
            ],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Show build stats
        import os
        output_path = 'app/static/css/output.css'
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            click.echo(click.style(f'✅ Build complete!', fg='green'))
            click.echo(f'📦 Output size: {size:,} bytes ({size/1024:.1f} KB)')
        
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f'❌ Build failed: {e.stderr}', fg='red'))
        raise click.Abort()

def register_cli_commands(app):
    """Register CLI commands with Flask app."""
    app.cli.add_command(tailwind_watch)
    app.cli.add_command(tailwind_build)
```

**Step 3: Registrar comandos en app/__init__.py**

Buscar la función `create_app()` y agregar:

```python
from app.cli import register_cli_commands

def create_app(config_class=Config):
    # ... existing code ...
    
    # Register CLI commands
    register_cli_commands(app)
    
    return app
```

**Step 4: Verificar comandos**

```bash
flask --help
```

Expected: Ver `tailwind:watch` y `tailwind:build` en la lista de comandos

**Step 5: Probar build**

```bash
flask tailwind:build
```

Expected: `app/static/css/output.css` creado, mensaje de éxito

**Step 6: Commit**

```bash
git add app/cli.py app/__init__.py
git commit -m "feat: add Flask CLI commands for TailwindCSS (watch/build)"
```

---

### Task 5: Actualizar base.html

**Files:**
- Modify: `app/templates/base.html`

**Step 1: Reemplazar link CSS actual**

Buscar:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

Reemplazar con:
```html
<!-- TailwindCSS Output (Liquid Glass Design System) -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/output.css') }}">

<!-- Liquid Glass Custom Styles -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/liquid-glass/background-orbs.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/liquid-glass/svg-filters.css') }}">
```

**Step 2: Agregar background orbs al body**

Después de `<body class="...">`:

```html
<!-- Background Orbs (Liquid Glass) -->
<div class="orb orb--blue"></div>
<div class="orb orb--violet"></div>
```

**Step 3: Agregar SVG filters (para refracción)**

Antes de `</body>`:

```html
<!-- SVG Filters for Liquid Glass (Chrome/Edge only) -->
<svg class="fixed inset-0 w-0 h-0 pointer-events-none" aria-hidden="true">
  <defs>
    <filter id="liquid-glass-refraction">
      <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="3" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="3" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
```

**Step 4: Actualizar main container**

Buscar:
```html
<main class="flex-grow main-content">
```

Reemplazar con:
```html
<main class="flex-grow main-content relative z-10">
  <div class="container mx-auto px-4 py-6">
```

Y cerrar antes de `</main>`:
```html
  </div>
</main>
```

**Step 5: Commit**

```bash
git add app/templates/base.html
git commit -m "feat: integrate TailwindCSS output and background orbs in base template"
```

---

## Fase 2: Componentes Reutilizables (Días 6-9)

### Task 6: Crear Macros Jinja2 para Componentes

**Files:**
- Create: `app/templates/components/glass_card.html`
- Create: `app/templates/components/glass_button.html`
- Create: `app/templates/components/glass_input.html`

**Step 1: Crear glass_card.html**

```jinja2
{# app/templates/components/glass_card.html #}

{% macro glass_card(variant='md', class='', hover=True, id='') %}
{% set variants = {
    'sm': 'glass-sm p-4',
    'md': 'glass-card glass-md p-6',
    'lg': 'glass-lg p-8',
} %}
<div 
    id="{{ id }}"
    class="{{ variants[variant] }} {{ 'hover:shadow-glass-glow hover:-translate-y-1' if hover else '' }} {{ class }}"
>
    {% if caller %}{{ caller() }}{% endif %}
</div>
{% endmacro %}

{% macro glass_card_header(class='') %}
<div class="border-b border-glass-border-subtle pb-4 mb-4 {{ class }}">
    {% if caller %}{{ caller() }}{% endif %}
</div>
{% endmacro %}

{% macro glass_card_body(class='') %}
<div class="{{ class }}">
    {% if caller %}{{ caller() }}{% endif %}
</div>
{% endmacro %}

{% macro glass_card_footer(class='') %}
<div class="border-t border-glass-border-subtle pt-4 mt-4 {{ class }}">
    {% if caller %}{{ caller() }}{% endif %}
</div>
{% endmacro %}
```

**Step 2: Crear glass_button.html**

```jinja2
{# app/templates/components/glass_button.html #}

{% macro glass_button(variant='primary', size='md', icon='', loading=False, disabled=False, class='', type='button', **kwargs) %}
{% set variants = {
    'primary': 'btn-primary',
    'secondary': 'btn-secondary',
    'ghost': 'btn-ghost',
    'outline': 'btn-outline',
    'success': 'btn-success',
    'danger': 'btn-danger',
    'warning': 'btn-warning',
    'info': 'btn-info',
} %}
{% set sizes = {
    'xs': 'btn-xs px-2 py-1 text-xs',
    'sm': 'btn-sm px-3 py-1.5 text-sm',
    'md': 'btn px-4 py-2 text-sm',
    'lg': 'btn-lg px-6 py-3 text-base',
    'xl': 'btn-xl px-8 py-4 text-lg',
} %}
<button 
    type="{{ type }}"
    class="btn {{ variants.get(variant, 'btn-primary') }} {{ sizes.get(size, 'btn') }} {{ 'opacity-38 cursor-not-allowed' if disabled else '' }} {{ class }}"
    {% if disabled %}disabled{% endif %}
    {% if loading %}aria-busy="true"{% endif %}
    {% for key, value in kwargs.items() %}{{ key }}="{{ value }}"{% endfor %}
>
    {% if loading %}
    <span class="spinner"></span>
    {% elif icon %}
    <i class="{{ icon }}"></i>
    {% endif %}
    {% if caller %}{{ caller() }}{% endif %}
</button>
{% endmacro %}

{% macro glass_button_icon(icon, variant='ghost', size='sm', class='', **kwargs) %}
<button 
    class="btn {{ 'btn-' + variant if variant else 'btn-ghost' }} btn-square {{ 'btn-' + size if size else 'btn-sm' }} {{ class }}"
    {% for key, value in kwargs.items() %}{{ key }}="{{ value }}"{% endfor %}
>
    <i class="{{ icon }}"></i>
</button>
{% endmacro %}
```

**Step 3: Crear glass_input.html**

```jinja2
{# app/templates/components/glass_input.html #}

{% macro glass_input(name, label='', type='text', placeholder='', required=False, error='', help_text='', icon='', class='', value='', **kwargs) %}
<div class="form-group {{ class }}">
    {% if label %}
    <label for="{{ name }}" class="block text-sm font-medium text-text-secondary mb-2 {{ 'form-label--required' if required else '' }}">
        {{ label }}
    </label>
    {% endif %}
    
    <div class="relative">
        {% if icon %}
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="{{ icon }} text-text-muted"></i>
        </div>
        {% endif %}
        
        <input
            type="{{ type }}"
            name="{{ name }}"
            id="{{ name }}"
            value="{{ value }}"
            placeholder="{{ placeholder }}"
            {% if required %}required{% endif %}
            class="glass-input w-full {{ 'pl-10' if icon else '' }} {{ 'glass-input--error' if error else '' }}"
            {% for key, value in kwargs.items() %}{{ key }}="{{ value }}"{% endfor %}
        />
    </div>
    
    {% if error %}
    <p class="mt-2 text-sm text-error-500 flex items-center gap-1">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
    </p>
    {% elif help_text %}
    <p class="mt-2 text-sm text-text-muted">
        {{ help_text }}
    </p>
    {% endif %}
</div>
{% endmacro %}

{% macro glass_textarea(name, label='', placeholder='', rows=4, required=False, error='', help_text='', class='', value='', **kwargs) %}
<div class="form-group {{ class }}">
    {% if label %}
    <label for="{{ name }}" class="block text-sm font-medium text-text-secondary mb-2 {{ 'form-label--required' if required else '' }}">
        {{ label }}
    </label>
    {% endif %}
    
    <textarea
        name="{{ name }}"
        id="{{ name }}"
        rows="{{ rows }}"
        placeholder="{{ placeholder }}"
        {% if required %}required{% endif %}
        class="glass-input w-full {{ 'glass-input--error' if error else '' }}"
        {% for key, value in kwargs.items() %}{{ key }}="{{ value }}"{% endfor %}
    >{{ value }}</textarea>
    
    {% if error %}
    <p class="mt-2 text-sm text-error-500 flex items-center gap-1">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
    </p>
    {% elif help_text %}
    <p class="mt-2 text-sm text-text-muted">
        {{ help_text }}
    </p>
    {% endif %}
</div>
{% endmacro %}

{% macro glass_select(name, label='', options=[], required=False, error='', help_text='', class='', value='', **kwargs) %}
<div class="form-group {{ class }}">
    {% if label %}
    <label for="{{ name }}" class="block text-sm font-medium text-text-secondary mb-2 {{ 'form-label--required' if required else '' }}">
        {{ label }}
    </label>
    {% endif %}
    
    <select
        name="{{ name }}"
        id="{{ name }}"
        class="glass-input w-full {{ 'glass-input--error' if error else '' }}"
        {% if required %}required{% endif %}
        {% for key, value in kwargs.items() %}{{ key }}="{{ value }}"{% endfor %}
    >
        {% for option in options %}
        <option value="{{ option.value }}" {{ 'selected' if option.value == value else '' }}>{{ option.label }}</option>
        {% endfor %}
    </select>
    
    {% if error %}
    <p class="mt-2 text-sm text-error-500 flex items-center gap-1">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
    </p>
    {% elif help_text %}
    <p class="mt-2 text-sm text-text-muted">
        {{ help_text }}
    </p>
    {% endif %}
</div>
{% endmacro %}
```

**Step 4: Commit**

```bash
git add app/templates/components/
git commit -m "feat: create reusable glass components as Jinja2 macros (card, button, input)"
```

---

## Fase 3: Refactorizar Dashboard (Días 10-14)

### Task 7: Refactorizar Dashboard Stats Grid

**Files:**
- Modify: `app/templates/dashboard/index.html`

**Step 1: Importar macros al inicio del template**

Agregar al inicio de `app/templates/dashboard/index.html`:

```jinja2
{% extends 'base.html' %}
{% from 'components/glass_card.html' import glass_card, glass_card_header, glass_card_body, glass_card_footer %}
{% from 'components/glass_button.html' import glass_button, glass_button_icon %}
{% from 'components/glass_input.html' import glass_input, glass_textarea, glass_select %}

{% block title %}{{ _('Dashboard') }} - DataLab{% endblock %}

{% block content %}
```

**Step 2: Reemplazar header del dashboard**

Buscar:
```html
<div class="mb-6">
    <h1 class="text-2xl font-bold">{{ _('Dashboard de Datos Maestros') }}</h1>
    <p class="text-gray-600">{{ _('Resumen de clientes, fábricas y productos') }}</p>
</div>
```

Reemplazar con:
```jinja2
<!-- Header del Dashboard -->
<div class="mb-8">
    <h1 class="text-3xl font-bold text-gradient mb-2">
        {{ _('Dashboard de Datos Maestros') }}
    </h1>
    <p class="text-text-muted">
        {{ _('Resumen de clientes, fábricas y productos') }}
    </p>
</div>
```

**Step 3: Reemplazar stats grid**

Buscar el bloque de cards de estadísticas y reemplazar con:

```jinja2
<!-- Stats Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <!-- Clientes Card -->
    <a href="{{ url_for('clientes.listar') }}" class="block group">
        {% call glass_card(variant='md', hover=True) %}
        <div class="flex items-center">
            <div class="p-3 rounded-full bg-primary-50 text-primary-400 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
            </div>
            <div class="ml-4">
                <p class="text-sm text-text-secondary">{{ _('Clientes') }}</p>
                <p class="text-2xl font-bold text-text-primary font-mono">{{ stats.total_clientes }}</p>
            </div>
        </div>
        {% endcall %}
    </a>

    <!-- Fábricas Card -->
    <a href="{{ url_for('fabricas.listar') }}" class="block group">
        {% call glass_card(variant='md', hover=True) %}
        <div class="flex items-center">
            <div class="p-3 rounded-full bg-success-50 text-success-500 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
            </div>
            <div class="ml-4">
                <p class="text-sm text-text-secondary">{{ _('Fábricas') }}</p>
                <p class="text-2xl font-bold text-text-primary font-mono">{{ stats.total_fabricas }}</p>
                {% if stats.total_clientes > 0 %}
                <p class="text-xs text-text-muted mt-1">
                    ~{{ (stats.total_fabricas / stats.total_clientes)|round(1) }} {{ _('por cliente') }}
                </p>
                {% endif %}
            </div>
        </div>
        {% endcall %}
    </a>

    <!-- Productos Card -->
    <a href="{{ url_for('productos.listar') }}" class="block group">
        {% call glass_card(variant='md', hover=True) %}
        <div class="flex items-center">
            <div class="p-3 rounded-full bg-secondary-50 text-secondary-400 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
            </div>
            <div class="ml-4">
                <p class="text-sm text-text-secondary">{{ _('Productos') }}</p>
                <p class="text-2xl font-bold text-text-primary font-mono">{{ stats.total_productos }}</p>
            </div>
        </div>
        {% endcall %}
    </a>

    <!-- Provincias Card -->
    {% call glass_card(variant='md') %}
    <div class="flex items-center">
        <div class="p-3 rounded-full bg-warning-50 text-warning-500">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
        </div>
        <div class="ml-4">
            <p class="text-sm text-text-secondary">{{ _('Provincias') }}</p>
            <p class="text-2xl font-bold text-text-primary font-mono">{{ stats.total_provincias }}</p>
            <p class="text-xs text-text-muted mt-1">{{ _('Cobertura total') }}</p>
        </div>
    </div>
    {% endcall %}
</div>
```

**Step 4: Reemplazar botones de acción rápida**

Buscar la sección de botones y reemplazar con:

```jinja2
<!-- Botones de Acción Rápida -->
<div class="flex flex-wrap gap-3 mb-8">
    {% call glass_button(variant='primary', icon='fas fa-plus') %}
    {{ _('Nuevo Cliente') }}
    {% endcall %}
    
    {% call glass_button(variant='success', icon='fas fa-plus') %}
    {{ _('Nueva Fábrica') }}
    {% endcall %}
    
    {% call glass_button(variant='secondary', icon='fas fa-plus') %}
    {{ _('Nuevo Producto') }}
    {% endcall %}
</div>
```

**Step 5: Reemplazar gráficas**

Buscar el bloque de gráficas y reemplazar:

```jinja2
<!-- Gráficos -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
    <!-- Distribución por Provincia -->
    {% call glass_card(variant='lg') %}
    {% call glass_card_header() %}
    <h3 class="text-lg font-semibold text-text-primary">
        {{ _('Distribución por Provincia') }}
    </h3>
    {% endcall %}
    {% call glass_card_body() %}
    <div id="provincia-chart" style="height: 300px;"></div>
    {% endcall %}
    {% endcall %}

    <!-- Top Clientes -->
    {% call glass_card(variant='lg') %}
    {% call glass_card_header() %}
    <h3 class="text-lg font-semibold text-text-primary">
        {{ _('Top 10 Clientes') }}
    </h3>
    {% endcall %}
    {% call glass_card_body() %}
    <div id="clientes-chart" style="height: 300px;"></div>
    {% endcall %}
    {% endcall %}
</div>
```

**Step 6: Eliminar referencias a CSS legacy**

Buscar y eliminar cualquier referencia a `dashboard.css` o estilos inline heredados.

**Step 7: Probar visualmente**

```bash
# Terminal 1: Flask
flask run

# Terminal 2: Tailwind watch
flask tailwind:watch

# Abrir http://localhost:5000/dashboard
# Verificar:
# - Cards con efecto glass correcto
# - Hover states funcionando
# - Background orbs visibles
# - Responsive en 320px, 768px, 1024px
# - Sin errores de consola
```

**Step 8: Commit**

```bash
git add app/templates/dashboard/index.html
git commit -m "feat: refactor dashboard with glass components and TailwindCSS"
```

---

## Fase 4: Testing y Optimización (Días 33-36)

### Task 8: Testing Cross-Browser

**Files:**
- Test en: Chrome, Edge, Firefox, Safari

**Step 1: Probar en Chrome/Edge**

```bash
# Abrir Chrome/Edge
# Navegar a: http://localhost:5000/dashboard
```

Verificar:
- ✅ SVG filters funcionando (refracción avanzada)
- ✅ Backdrop-filter url() soportado
- ✅ Background orbs animados
- ✅ Glass cards con efecto completo

**Step 2: Probar en Firefox**

```bash
# Abrir Firefox
# Navegar a: http://localhost:5000/dashboard
```

Verificar:
- ✅ Fallback backdrop-filter blur funcionando
- ✅ Glass cards visibles (sin refracción SVG)
- ✅ Background orbs animados
- ✅ Estilos consistentes

**Step 3: Probar en Safari**

```bash
# Abrir Safari
# Navegar a: http://localhost:5000/dashboard
```

Verificar:
- ✅ -webkit-backdrop-filter funcionando
- ✅ Glass cards visibles
- ✅ Background orbs animados
- ✅ Estilos consistentes

**Step 4: Documentar resultados**

Crear `docs/testing/browser-compatibility.md`:

```markdown
# Browser Compatibility Report

## Test Date: YYYY-MM-DD

### Chrome 120+
- ✅ SVG filters: Working
- ✅ Backdrop-filter: Working
- ✅ Animations: Working
- ✅ Overall: Excellent

### Firefox 120+
- ✅ SVG filters: Fallback (blur)
- ✅ Backdrop-filter: Working
- ✅ Animations: Working
- ✅ Overall: Good

### Safari 17+
- ✅ -webkit-backdrop-filter: Working
- ✅ Animations: Working
- ✅ Overall: Good
```

**Step 5: Commit**

```bash
git add docs/testing/browser-compatibility.md
git commit -m "docs: add browser compatibility report"
```

---

## Testing y Verificación

### Comandos de Testing

```bash
# 1. Build de producción
flask tailwind:build

# 2. Verificar output CSS
ls -lh app/static/css/output.css

# 3. Iniciar watch mode (desarrollo)
flask tailwind:watch

# 4. Lighthouse audit (Chrome DevTools)
# Performance: >90
# Accessibility: >95
# Best Practices: >90
# SEO: >90
```

### Checklist de Aceptación

- [ ] TailwindCSS CLI descargado y funcional
- [ ] `input.css` con tokens Liquid Glass
- [ ] `tailwind.config.js` configurado
- [ ] Flask CLI commands (`flask tailwind:watch/build`)
- [ ] `base.html` actualizado con output.css
- [ ] Background orbs animados visibles
- [ ] Componentes glass (card, button, input) creados
- [ ] Dashboard refactorizado
- [ ] 95%+ clases Tailwind en templates
- [ ] Sin estilos inline (`style="..."`)
- [ ] Responsive probado (320px, 768px, 1024px, 1440px)
- [ ] Lighthouse score >90 en todas las categorías
- [ ] Testing cross-browser completado
- [ ] Sin errores de consola

---

## Próximas Fases (No incluidas en este plan)

**Fase 5:** Migrar Clientes CRUD (Días 15-18)  
**Fase 6:** Migrar Pedidos formulario (Días 19-22)  
**Fase 7:** Migrar Muestras + Entradas (Días 23-26)  
**Fase 8:** Migrar Órdenes de Trabajo (Días 27-30)  
**Fase 9:** Eliminar CSS legacy (Días 31-32)  
**Fase 10:** Documentación final (Días 37-42)

---

**Plan complete and saved to `docs/plans/2026-03-14-liquid-glass-implementation.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - Dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
