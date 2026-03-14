# DataLab — Liquid Glass + Glassmorphism Design System Refactor

**Fecha:** 14 de marzo de 2026  
**Estado:** Aprobado  
**Autor:** UI/UX Pro Max + Brainstorming Skills  
**Prioridad:** Calidad Perfecta (5-6 semanas)

---

## 📋 Resumen Ejecutivo

Refactorización global del sistema de diseño de DataLab para implementar un **sistema híbrido Liquid Glass + Glassmorphism** utilizando **TailwindCSS CLI Standalone** (sin Node.js) integrado con Flask. La migración comenzará por el Dashboard y seguirá un enfoque de calidad perfecta con atención exhaustiva a detalles de refracción, animaciones de fondo, y consistencia visual en todos los 24 templates.

### Decisiones Clave Aprobadas

| Decisión | Selección | Razonamiento |
|----------|-----------|--------------|
| **Enfoque** | TailwindCSS CLI Standalone | Sin Node.js en producción, solo ejecutable, limpio |
| **Estilo** | Híbrido Liquid Glass + Glassmorphism | Combina refracción avanzada (kube.io) con estética glassmorphism probada |
| **Prioridad** | Dashboard primero | Página principal, mayor visibilidad |
| **Tiempo** | 5-6 semanas (Perfecto) | Calidad sobre velocidad, pulir cada detalle |
| **Flask CLI** | Sí, comandos personalizados | `flask tailwind:watch`, `flask tailwind:build` |
| **Plugins** | Forms + Typography | Incluidos en configuración inicial |

---

## 🎨 Sistema de Diseño

### 1. Filosofía de Diseño

**Liquid Glass (kube.io) + Glassmorphism = "Liquid Glassmorphism"**

| Característica | Liquid Glass | Glassmorphism | Híbrido DataLab |
|----------------|--------------|---------------|-----------------|
| **Refracción** | SVG displacement maps | backdrop-filter blur | SVG + blur fallback |
| **Bordes** | Squircle convex | Border-radius simple | Squircle 2-4px |
| **Sombras** | Specular highlight | Drop shadow suave | Specular + drop |
| **Background** | Orbs estáticos | Gradientes mesh | Orbs animados + mesh |
| **Transparencia** | 4-11% opacidad | 10-30% opacidad | 7-15% (balance) |
| **Blur** | 8-28px | 10-40px | 12-24px (sweet spot) |

---

### 2. Tokens de Diseño

#### 2.1 Colores Base

```javascript
// Tailwind Config Extension
colors: {
  // Primary: Sky Blue (científico, preciso)
  primary: {
    50:  'rgba(56, 189, 248, 0.08)',
    100: 'rgba(56, 189, 248, 0.15)',
    200: 'rgba(56, 189, 248, 0.25)',
    300: '#7dd3fc',
    400: '#38bdf8',  // Accent principal
    500: '#0ea5e9',  // Base
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },
  
  // Secondary: Violet (autoridad gubernamental)
  secondary: {
    50:  'rgba(167, 139, 250, 0.08)',
    100: 'rgba(167, 139, 250, 0.15)',
    200: 'rgba(167, 139, 250, 0.22)',
    300: '#c4b5fd',
    400: '#a78bfa',  // Accent
    500: '#8b5cf6',  // Base
    600: '#7c3aed',
    700: '#6d28d9',
    800: '#5b21b6',
    900: '#4c1d95',
  },

  // Glass Tokens (transparencias calibradas)
  glass: {
    1:  'rgba(255, 255, 255, 0.040)',  // Fondos sutiles
    2:  'rgba(255, 255, 255, 0.070)',  // Cards estándar
    3:  'rgba(255, 255, 255, 0.110)',  // Elementos elevados
    hover:  'rgba(255, 255, 255, 0.130)',
    active: 'rgba(255, 255, 255, 0.170)',
    
    // Bordes (crítico para definición)
    border:        'rgba(255, 255, 255, 0.110)',
    'border-subtle': 'rgba(255, 255, 255, 0.060)',
    'border-strong': 'rgba(255, 255, 255, 0.190)',
  },

  // Estado (semántico, accesible)
  success: { 500: '#34d399', 600: '#10b981', 700: '#059669' },
  warning: { 500: '#fbbf24', 600: '#f59e0b', 700: '#d97706' },
  error:   { 500: '#f87171', 600: '#ef4444', 700: '#dc2626' },
  info:    { 500: '#22d3ee', 600: '#06b6d4', 700: '#0891b2' },
}
```

#### 2.2 Efectos de Vidrio

```javascript
// Backdrop Blur (capas de profundidad)
backdropBlur: {
  sm:  'blur(8px) saturate(140%)',   // Elementos sutiles
  md:  'blur(18px) saturate(180%)',  // Cards estándar
  lg:  'blur(28px) saturate(200%)',  // Modals, overlays
  xl:  'blur(40px) saturate(220%)',  // Backgrounds profundos
}

// Sombras Glass (inset + drop)
boxShadow: {
  'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.07)',
  'glass-md': '0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.09)',
  'glass-lg': '0 16px 50px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255,255,255,0.12)',
  'glass-xl': '0 25px 60px rgba(0, 0, 0, 0.58), inset 0 1px 0 rgba(255,255,255,0.15)',
  'glass-glow': '0 0 30px rgba(56, 189, 248, 0.18), 0 8px 32px rgba(0, 0, 0, 0.45)',
  'glass-glow-success': '0 0 30px rgba(52, 211, 153, 0.18)',
  'glass-glow-warning': '0 0 30px rgba(251, 191, 36, 0.18)',
  'glass-glow-error':   '0 0 30px rgba(248, 113, 113, 0.18)',
}

// Border Radius (Squircle convex - kube.io)
borderRadius: {
  'none': '0',
  'sm':   '0.25rem',   // 4px
  'md':   '0.5rem',    // 8px
  'lg':   '0.75rem',   // 12px
  'xl':   '1rem',      // 16px (standard glass)
  '2xl':  '1.25rem',   // 20px (large cards)
  '3xl':  '1.75rem',   // 28px (modals)
  'full': '9999px',
}
```

#### 2.3 Background System

```css
/* Gradiente base de página */
--bg-gradient: linear-gradient(
  135deg,
  #070c18 0%,      /* Navy más oscuro */
  #0c1330 30%,     /* Navy medio */
  #10103a 60%,     /* Indigo profundo */
  #080e20 100%     /* Navy oscuro */
);

/* Orbs animados (2-3 capas de profundidad) */
@keyframes orb-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 30px) scale(0.9); }
}

.orb-blue {
  background: radial-gradient(
    circle,
    rgba(56, 189, 248, 0.22) 0%,
    transparent 65%
  );
  filter: blur(90px);
  animation: orb-float 12s ease-in-out infinite;
}

.orb-violet {
  background: radial-gradient(
    circle,
    rgba(139, 92, 246, 0.20) 0%,
    transparent 65%
  );
  filter: blur(90px);
  animation: orb-float 15s ease-in-out infinite reverse;
}

.orb-success {
  background: radial-gradient(
    circle,
    rgba(52, 211, 153, 0.15) 0%,
    transparent 65%
  );
  filter: blur(80px);
  animation: orb-float 18s ease-in-out infinite;
}
```

---

### 3. Componentes Base

#### 3.1 GlassCard

```html
<!-- Variante estándar (md) -->
<div class="glass-card glass-md hover:shadow-glass-glow transition-all duration-200 ease-out">
  <!-- Top highlight sheen (automático con ::before) -->
  <div class="p-6">
    <h3 class="text-lg font-semibold text-white">Título</h3>
    <p class="text-gray-300 mt-2">Descripción del contenido</p>
  </div>
</div>

<!-- Variante pequeña (sm) -->
<div class="glass-card glass-sm hover:border-glass-border-strong transition-all duration-200">
  <div class="p-4">Contenido compacto</div>
</div>

<!-- Variante grande (lg) -->
<div class="glass-card glass-lg hover:shadow-glass-xl transition-all duration-300">
  <div class="p-8">Contenido destacado</div>
</div>

<!-- Con acento de color -->
<div class="glass-card glass-md border-primary-500/30 shadow-glow-primary">
  <div class="p-6">Contenido con glow azul</div>
</div>
```

**CSS Subyacente:**
```css
.glass-card {
  background: var(--glass-2);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--glass-shadow-md);
  transition: all var(--duration-200) var(--ease-out);
  position: relative;
  overflow: hidden;
}

/* Top highlight sheen */
.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  top: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255,255,255,0.18) 40%,
    rgba(255,255,255,0.22) 50%,
    rgba(255,255,255,0.18) 60%,
    transparent 100%
  );
  pointer-events: none;
  border-radius: inherit;
  z-index: 1;
}

.glass-card:hover {
  background: var(--glass-hover);
  border-color: var(--glass-border-strong);
  box-shadow: var(--glass-shadow-glow);
  transform: translateY(-3px);
}
```

---

#### 3.2 GlassButton

```html
<!-- Primary (gradiente Sky Blue) -->
<button class="btn btn-primary">
  <i class="fas fa-plus"></i>
  <span>Nuevo Cliente</span>
</button>

<!-- Secondary (glass outline) -->
<button class="btn btn-secondary">
  <i class="fas fa-filter"></i>
  <span>Filtrar</span>
</button>

<!-- Ghost (minimal) -->
<button class="btn btn-ghost">
  <i class="fas fa-ellipsis-v"></i>
</button>

<!-- Loading state -->
<button class="btn btn-primary btn-loading" disabled>
  <span class="spinner"></span>
  <span>Guardando...</span>
</button>
```

**CSS Subyacente:**
```css
.btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-200) var(--ease-out);
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: #ffffff;
  border: 1px solid transparent;
  box-shadow: 
    0 4px 16px rgba(14,165,233,0.30),
    inset 0 1px 0 rgba(255,255,255,0.20);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  box-shadow: 
    0 6px 24px rgba(56,189,248,0.40),
    inset 0 1px 0 rgba(255,255,255,0.25);
  transform: translateY(-2px);
}

/* Top sheen en hover */
.btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(255,255,255,0.06) 0%,
    transparent 55%
  );
  pointer-events: none;
  border-radius: inherit;
  opacity: 0;
  transition: opacity var(--duration-150) ease;
}

.btn:hover:not(:disabled)::after {
  opacity: 1;
}
```

---

#### 3.3 GlassInput

```html
<!-- Input estándar -->
<div class="form-group">
  <label class="form-label">Nombre del Cliente</label>
  <input 
    type="text" 
    class="glass-input w-full"
    placeholder="Ej: Laboratorio Central"
  />
</div>

<!-- Con validación (error) -->
<div class="form-group">
  <label class="form-label form-label--required">Email</label>
  <input 
    type="email" 
    class="glass-input glass-input--error w-full"
    value="invalid-email"
  />
  <span class="form-error">
    <i class="fas fa-exclamation-circle"></i>
    Email inválido
  </span>
</div>

<!-- Con icono -->
<div class="form-search">
  <i class="fas fa-search search-icon"></i>
  <input 
    type="text" 
    class="glass-input w-full pl-10"
    placeholder="Buscar..."
  />
</div>
```

**CSS Subyacente:**
```css
.glass-input {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--text-primary);
  transition: all var(--duration-200) var(--ease-out);
}

.glass-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(56, 189, 248, 0.50);
  box-shadow: 
    0 0 0 3px rgba(56, 189, 248, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.glass-input--error {
  border-color: rgba(248, 113, 113, 0.50);
  background: rgba(248, 113, 113, 0.05);
}

.glass-input--error:focus {
  box-shadow: 0 0 0 3px rgba(248, 113, 113, 0.12);
}
```

---

#### 3.4 GlassTable

```html
<div class="glass-card overflow-hidden">
  <div class="table-container">
    <table class="glass-table">
      <thead>
        <tr>
          <th class="px-6 py-4 text-left">Cliente</th>
          <th class="px-6 py-4 text-left">Fábrica</th>
          <th class="px-6 py-4 text-left">Estado</th>
          <th class="px-6 py-4 text-right">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr class="hover:bg-glass-1 transition-colors">
          <td class="px-6 py-4">Laboratorio Central</td>
          <td class="px-6 py-4">Fábrica Havana</td>
          <td class="px-6 py-4">
            <span class="status-dot status-dot--active"></span>
            Activo
          </td>
          <td class="px-6 py-4 text-right">
            <button class="btn btn-ghost btn-sm">
              <i class="fas fa-ellipsis-v"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

**CSS Subyacente:**
```css
.glass-table {
  width: 100%;
  border-collapse: collapse;
}

.glass-table thead tr {
  background: var(--glass-3);
  border-bottom: 1px solid var(--glass-border-strong);
}

.glass-table thead th {
  padding: var(--spacing-4) var(--spacing-6);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  letter-spacing: 0.02em;
}

.glass-table tbody tr {
  border-bottom: 1px solid var(--glass-border-subtle);
  transition: background var(--duration-150) ease;
}

.glass-table tbody tr:last-child {
  border-bottom: none;
}

.glass-table tbody tr:hover {
  background: var(--glass-1);
}

.glass-table tbody td {
  padding: var(--spacing-4) var(--spacing-6);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}
```

---

### 4. SVG Filters (Refracción Avanzada)

**Implementación kube.io para Chrome/Edge:**

```svg
<svg class="fixed inset-0 w-0 h-0 pointer-events-none">
  <defs>
    <filter id="liquid-glass-refraction">
      <!-- Displacement Map (RGBA encoding) -->
      <feImage 
        href="data:image/png;base64,DISPLACEMENT_MAP_DATA" 
        x="0" y="0" 
        width="200" height="200"
        result="displacement-map"
      />
      
      <!-- Specular Highlight -->
      <feImage
        href="data:image/png;base64,SPECULAR_HIGHLIGHT_DATA"
        result="specular"
      />
      
      <!-- Apply Displacement -->
      <feDisplacementMap
        in="SourceGraphic"
        in2="displacement-map"
        scale="8"
        xChannelSelector="R"
        yChannelSelector="G"
      />
      
      <!-- Blend Specular -->
      <feBlend
        in="displaced"
        in2="specular"
        mode="overlay"
        result="final"
      />
    </filter>
  </defs>
</svg>
```

**JavaScript Generator (simplificado):**

```javascript
// liquid-glass.js
class LiquidGlassGenerator {
  constructor() {
    this.surfaceFunction = 'squircle-convex';
    this.refractionIndex = 1.5; // Glass
    this.bezelWidth = 16; // px
    this.glassThickness = 4; // px
  }

  generateDisplacementMap(radius, samples = 127) {
    const map = [];
    for (let i = 0; i < samples; i++) {
      const distance = i / samples;
      const displacement = this.calculateDisplacement(distance);
      map.push(this.encodeRGBA(displacement));
    }
    return this.mapToDataURL(map);
  }

  calculateDisplacement(distanceFromEdge) {
    // Snell-Descartes: n1*sin(θ1) = n2*sin(θ2)
    const normal = this.calculateNormal(distanceFromEdge);
    const incidence = Math.atan2(normal.y, normal.x);
    const refraction = Math.asin(Math.sin(incidence) / this.refractionIndex);
    return Math.tan(refraction) * this.glassThickness;
  }

  squircleConvex(x) {
    // y = (1 - (1 - x)^4)^(1/4)
    return Math.pow(1 - Math.pow(1 - x, 4), 1/4);
  }
}
```

**Fallback para Firefox/Safari:**

```css
/* Fallback: backdrop-filter blur simple */
@supports not (backdrop-filter: url(#liquid-glass-refraction)) {
  .glass-card {
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
  }
}
```

---

### 5. Tipografía

```javascript
// Google Fonts (ya cargadas en base.html)
fontFamily: {
  base: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
  heading: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
  mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
}

fontSize: {
  xs:   '0.75rem',    // 12px
  sm:   '0.875rem',   // 14px
  base: '1rem',       // 16px
  md:   '1rem',       // 16px
  lg:   '1.125rem',   // 18px
  xl:   '1.25rem',    // 20px
  '2xl': '1.5rem',    // 24px
  '3xl': '1.875rem',  // 30px
  '4xl': '2.25rem',   // 36px
  '5xl': '3rem',      // 48px
}

fontWeight: {
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
}

lineHeight: {
  tight: '1.25',
  snug: '1.375',
  normal: '1.5',
  relaxed: '1.625',
  loose: '2',
}
```

**Reglas de Tipografía:**

| Elemento | Tamaño | Peso | Line Height | Uso |
|----------|--------|------|-------------|-----|
| H1 | 2.25rem (36px) | 700 | 1.25 | Títulos de página |
| H2 | 1.875rem (30px) | 600 | 1.3 | Secciones principales |
| H3 | 1.5rem (24px) | 600 | 1.375 | Subsecciones |
| H4 | 1.25rem (20px) | 600 | 1.4 | Cards, componentes |
| Body | 1rem (16px) | 400 | 1.5 | Texto principal |
| Small | 0.875rem (14px) | 400 | 1.5 | Labels, metadata |
| Caption | 0.75rem (12px) | 400 | 1.4 | Ayuda, tooltips |
| Mono | 0.9em | 400 | 1.6 | Código, datos técnicos |

---

### 6. Espaciado (8pt Grid)

```javascript
spacing: {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
}
```

**Reglas de Espaciado:**

| Contexto | Padding | Gap | Margen |
|----------|---------|-----|--------|
| Cards pequeñas | 1rem (16px) | 0.5rem (8px) | 1rem |
| Cards estándar | 1.5rem (24px) | 1rem (16px) | 1.5rem |
| Cards grandes | 2rem (32px) | 1.5rem (24px) | 2rem |
| Secciones | 3rem (48px) | 2rem (32px) | 3rem |
| Componentes inline | 0.5rem (8px) | 0.25rem (4px) | - |

---

### 7. Animaciones

```css
/* Transiciones estándar */
--duration-75: 75ms;
--duration-100: 100ms;
--duration-150: 150ms;
--duration-200: 200ms;
--duration-300: 300ms;
--duration-500: 500ms;

--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Animaciones keyframe */
@keyframes orb-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 30px) scale(0.9); }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.18); }
  50% { box-shadow: 0 0 40px rgba(56, 189, 248, 0.28); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

**Reglas de Animación:**

| Tipo | Duración | Easing | Uso |
|------|----------|--------|-----|
| Micro-interacción | 150ms | ease-out | Hover buttons, links |
| Transición estado | 200ms | ease-out | Focus inputs, toggle |
| Transición grande | 300ms | ease-in-out | Modals, panels |
| Animación fondo | 12-18s | ease-in-out infinite | Orbs |
| Loading spinner | 700ms | linear infinite | Spinners |
| Skeleton shimmer | 1.5s | linear infinite | Loading states |

---

### 8. Responsive Breakpoints

```javascript
screens: {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop pequeño
  xl: '1280px',  // Desktop estándar
  '2xl': '1536px', // Desktop grande
}
```

**Estrategia Mobile-First:**

| Breakpoint | Ancho | Layout | Navegación |
|------------|-------|--------|------------|
| < 640px | Mobile | 1 columna | Bottom nav / Hamburger |
| 640-767px | Mobile XL | 1-2 columnas | Bottom nav |
| 768-1023px | Tablet | 2-3 columnas | Sidebar colapsable |
| 1024-1279px | Desktop | 3-4 columnas | Sidebar visible |
| ≥ 1280px | Desktop+ | 4+ columnas | Sidebar + panels |

---

### 9. Accesibilidad (WCAG 2.2 AA)

**Contraste de Color:**

| Elemento | Ratio Mínimo | Verificación |
|----------|--------------|--------------|
| Texto normal | 4.5:1 | ✅ glass-2 sobre bg-gradient |
| Texto grande | 3:1 | ✅ Headings white |
| Iconos | 3:1 | ✅ Iconos primary-400 |
| Componentes UI | 3:1 | ✅ Bordes glass-border-strong |

**Focus States:**

```css
:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.70);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Skip link para keyboard navigation */
.skip-link {
  position: absolute;
  top: -9999px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  padding: 1rem 2rem;
  background: var(--primary-500);
  color: white;
  border-radius: var(--radius-lg);
}

.skip-link:focus {
  top: 1rem;
}
```

**Reduced Motion:**

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 📦 Stack Técnico

### Arquitectura de Integración

**TailwindCSS CLI Standalone + Flask (Sin Node.js)**

```
datalab/
├── app/
│   ├── static/
│   │   └── css/
│   │       ├── input.css       # @tailwind directives (fuente)
│   │       └── output.css      # Compilado (sirve Flask)
│   └── templates/
│       ├── base.html           # <link output.css>
│       └── components/         # Componentes reutilizables
├── tailwind.config.js          # Configuración Tailwind
├── tailwindcss.exe             # Ejecutable (Windows)
├── app/
│   └── cli.py                  # Comandos Flask CLI
└── .gitignore
```

### TailwindCSS Standalone CLI

**Descarga:**
- Windows: `tailwindcss-windows-x64.exe` desde [GitHub Releases](https://github.com/tailwindlabs/tailwindcss/releases)
- Renombrar: `tailwindcss.exe`
- Ubicar en raíz del proyecto

**Comandos:**
```bash
# Desarrollo (auto-rebuild on change)
./tailwindcss -i app/static/css/input.css -o app/static/css/output.css --watch

# Producción (minificado)
./tailwindcss -i app/static/css/input.css -o app/static/css/output.css --minify
```

### Plugins de Tailwind (Configuración Manual)

**tailwind.config.js:**
```javascript
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/**/*.html',
  ],
  theme: {
    extend: {
      // ... tokens de diseño
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
    // Typography plugin (contenido rico: artículos, documentación)
    function({ addBase, theme }) {
      addBase({
        '.prose': { maxWidth: theme('maxWidth.4xl') },
      })
    },
  ],
}
```

### Flask CLI Commands

**app/cli.py:**
```python
import subprocess
import click

@click.command('tailwind:watch')
def tailwind_watch():
    """Watch and rebuild Tailwind CSS during development."""
    subprocess.run([
        './tailwindcss',
        '-i', 'app/static/css/input.css',
        '-o', 'app/static/css/output.css',
        '--watch'
    ], shell=True)

@click.command('tailwind:build')
def tailwind_build():
    """Build Tailwind CSS for production (minified)."""
    subprocess.run([
        './tailwindcss',
        '-i', 'app/static/css/input.css',
        '-o', 'app/static/css/output.css',
        '--minify'
    ], shell=True)

def register_cli_commands(app):
    """Register CLI commands with Flask app."""
    app.cli.add_command(tailwind_watch)
    app.cli.add_command(tailwind_build)
```

**Uso:**
```bash
# Desarrollo (2 terminales)
# Terminal 1: Flask server
flask run

# Terminal 2: Tailwind watch
flask tailwind:watch

# Producción (pre-deploy)
flask tailwind:build
```

### Estructura de Archivos

```
datalab/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   ├── input.css               # @tailwind directives
│   │   │   ├── output.css              # Compilado (gitignored en dev)
│   │   │   ├── liquid-glass/
│   │   │   │   ├── svg-filters.css     # SVG filters (refracción)
│   │   │   │   └── background-orbs.css # Orbs animados
│   │   │   └── custom/
│   │   │       └── print.css           # Print styles
│   │   └── images/
│   │       └── backgrounds/
│   │           └── orb-textures.png
│   ├── templates/
│   │   ├── base.html                   # Layout principal
│   │   ├── components/                 # Componentes reutilizables
│   │   │   ├── glass_card.html
│   │   │   ├── glass_button.html
│   │   │   ├── glass_input.html
│   │   │   ├── glass_table.html
│   │   │   └── glass_modal.html
│   │   ├── dashboard/
│   │   │   └── index.html              # ✅ PRIMERO (prioridad 1)
│   │   ├── clientes/
│   │   ├── pedidos/
│   │   └── ...
│   └── cli.py                          # Comandos Flask CLI
├── tailwind.config.js                  # Configuración Tailwind
├── tailwindcss.exe                     # Ejecutable (Windows)
├── .gitignore
└── docs/plans/
    ├── 2026-03-14-liquid-glass-refactor-design.md
    └── 2026-03-14-liquid-glass-implementation.md
```

### .gitignore Actualizado

```gitignore
# Python
__pycache__/
*.py[cod]
.env
instance/

# Tailwind CSS (output compilado - opcional commit para simplicidad)
app/static/css/output.css

# Tailwind executable (commit para team consistency o descargar por dev)
tailwindcss.exe

# IDE
.vscode/
.idea/
*.swp
```

---

## 🗓️ Cronograma (5-6 Semanas)

### Semana 1: Configuración y Fundamentos

| Día | Tarea | Deliverable |
|-----|-------|-------------|
| 1 | Descargar Tailwind CLI Standalone | `tailwindcss.exe` |
| 2 | Crear `input.css` y `tailwind.config.js` | Configuración base |
| 3 | Agregar Flask CLI commands en `app/cli.py` | `flask tailwind:watch/build` |
| 4 | Crear `input.css` con tokens Liquid Glass | CSS base funcional |
| 5 | Implementar background orbs en `base.html` | Orbs animados |

| Día | Tarea | Deliverable |
|-----|-------|-------------|
| 1-2 | Clientes CRUD completo | ✅ Clientes migrado |
| 3-4 | Pedidos formulario complejo | ✅ Pedidos migrado |
| 5 | Muestras + Entradas | ✅ Muestras migrado |

### Semana 5: Features Secundarios

| Día | Tarea | Deliverable |
|-----|-------|-------------|
| 1-2 | Órdenes de Trabajo | ✅ OT migrado |
| 3 | Informes + Reportes | ✅ Reportes migrado |
| 4 | Configuración + Admin | ✅ Admin migrado |
| 5 | Auth (login, registro) | ✅ Auth migrado |

### Semana 6: Optimización y Testing

| Día | Tarea | Deliverable |
|-----|-------|-------------|
| 1-2 | Eliminar CSS legacy (20+ archivos) | Código limpio |
| 3 | Testing cross-browser | Reporte de compatibilidad |
| 4 | Optimización performance | Lighthouse scores |
| 5 | Documentación final | README + guías |

---

## 📊 Métricas de Éxito

### Antes vs Después (Objetivos)

| Métrica | Actual | Objetivo | Cómo Medir |
|---------|--------|----------|------------|
| **Archivos CSS** | 27 | 5 | `find app/static/css -name "*.css" \| wc -l` |
| **Líneas CSS** | ~2,500 | ~500 | `wc -l app/static/css/**/*.css` |
| **Tailwind en templates** | 30% | 95% | Grep de clases Tailwind |
| **LCP** | ~2.5s | <1.8s | Lighthouse |
| **CLS** | ~0.15 | <0.1 | Lighthouse |
| **Bundle CSS** | ~85KB | ~15KB | Webpack/Vite build analysis |
| **FID** | ~150ms | <100ms | Chrome DevTools |
| **Accesibilidad** | ~85 | >95 | Lighthouse Accessibility |

---

## ⚠️ Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Safari/Firefox sin SVG filters | Alta | Medio | Fallback con backdrop-filter blur |
| Templates legacy sin migrar | Media | Alto | Feature flags por módulo |
| Curva de aprendizaje Tailwind | Media | Bajo | Documentación + ejemplos inline |
| Performance en dispositivos viejos | Baja | Bajo | Lazy load SVG, reducir orbs |
| Inconsistencia visual | Media | Medio | Design tokens estrictos, code review |
| Regresión de accesibilidad | Baja | Alto | Testing WCAG en cada sprint |

---

## 🧪 Estrategia de Testing

### Testing Visual

```bash
# Chromatic (si se implementa)
npm run chromatic

# Percy (alternativa)
npm run percy
```

### Testing de Accesibilidad

```bash
# axe-core
npm install -D @axe-core/cli
axe http://localhost:5000/dashboard

# Lighthouse CI
npm install -D @lhci/cli
lhci autorun
```

### Testing de Performance

```bash
# Lighthouse CLI
lighthouse http://localhost:5000/dashboard \
  --output=html \
  --output-path=./lighthouse-report.html \
  --view
```

### Browser Testing

| Browser | Versión | Estado |
|---------|---------|--------|
| Chrome | 120+ | ✅ SVG filters soportado |
| Edge | 120+ | ✅ SVG filters soportado |
| Firefox | 120+ | ⚠️ Fallback blur |
| Safari | 17+ | ⚠️ Fallback blur |

---

## 📚 Documentación

### Guías a Crear

1. **`docs/design-system.md`** - Sistema de diseño completo
2. **`docs/components.md`** - Catálogo de componentes
3. **`docs/accessibility.md`** - Guía de accesibilidad
4. **`docs/performance.md`** - Optimización y mejores prácticas
5. **`docs/migration-guide.md`** - Migrar templates legacy

### Ejemplos de Código

Cada componente debe incluir:
- ✅ Ejemplo HTML
- ✅ Variantes disponibles
- ✅ Estados (hover, focus, disabled, loading)
- ✅ Ejemplos de accesibilidad
- ✅ Anti-patrones a evitar

---

## ✅ Checklist de Aceptación

### Criterios de Aceptación por Componente

- [ ] Sigue tokens de diseño (colores, spacing, typography)
- [ ] Responsive (mobile-first, 3 breakpoints mínimo)
- [ ] Accesible (WCAG 2.2 AA, keyboard nav, screen reader)
- [ ] Estados completos (hover, focus, active, disabled, loading)
- [ ] Animaciones suaves (150-300ms, ease-out)
- [ ] Reduced motion support
- [ ] Cross-browser (Chrome, Firefox, Safari, Edge)
- [ ] Documentado (ejemplos, variantes, anti-patrones)

### Criterios de Aceptación por Template

- [ ] 95%+ clases Tailwind (máximo 5% CSS custom)
- [ ] Sin estilos inline (style="...")
- [ ] Sin IDs únicos (usar clases reutilizables)
- [ ] Componentes extraídos a `components/`
- [ ] Responsive probado (320px, 768px, 1024px, 1440px)
- [ ] Lighthouse score >90 (Performance, Accessibility, Best Practices, SEO)

### Criterios de Aceptación Globales

- [ ] Todos los templates migrados (24 archivos)
- [ ] CSS legacy eliminado (20+ archivos borrados)
- [ ] Build process funcional (Vite + Tailwind)
- [ ] Documentación completa
- [ ] Testing cross-browser completado
- [ ] Métricas de performance alcanzadas

---

## 🔗 Referencias

- [Liquid Glass (kube.io)](https://kube.io/blog/liquid-glass-css-svg/)
- [TailwindCSS v4 Docs](https://tailwindcss.com/docs)
- [UI/UX Pro Max Guidelines](C:\Users\ernes\.qwen\skills\ui-ux-pro-max)
- [WCAG 2.2 AA](https://www.w3.org/WAI/WCAG22/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

---

**Documento aprobado por:** Usuario (Ernesto)  
**Fecha de aprobación:** 14 de marzo de 2026  
**Próximo paso:** Invocar skill `writing-plans` para plan de implementación detallado
