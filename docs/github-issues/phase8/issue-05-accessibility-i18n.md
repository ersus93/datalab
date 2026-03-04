# [Phase 8] Accesibilidad (WCAG 2.1 AA) & Internacionalización

**Labels:** `phase-8`, `frontend`, `accessibility`, `i18n`, `ux`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 4 días
**Depends on:** Phase 6 #05 (UI/UX Enhancements)

---

## Descripción

Un sistema LIMS gubernamental debe cumplir estándares de accesibilidad. Los técnicos de laboratorio pueden pasar 6-8 horas al día interactuando con el sistema — una interfaz que fatiga, confunde, o excluye usuarios con discapacidades visuales o motoras es un problema real, no cosmético.

Esta issue implementa:
1. **WCAG 2.1 nivel AA** — estándar internacional de accesibilidad
2. **Internacionalización (i18n)** — preparación para español de Cuba y potencialmente otros idiomas
3. **Accesibilidad de formularios** — área crítica donde técnicos pasan más tiempo

---

## Acceptance Criteria

### 1. Contraste y Colores (WCAG 1.4.3)

```css
/* Ratio de contraste mínimo: 4.5:1 para texto normal, 3:1 para texto grande */

/* Paleta accesible: */
:root {
    /* Texto principal sobre fondo blanco: ratio 14.7:1 ✓ */
    --color-text-primary: #1a1a2e;
    
    /* Texto secundario sobre fondo blanco: ratio 5.9:1 ✓ */
    --color-text-secondary: #4a5568;
    
    /* Accent / botones primarios: ratio 4.6:1 sobre blanco ✓ */
    --color-accent: #1d4ed8;
    
    /* Estado de error: ratio 5.1:1 ✓ */
    --color-error: #b91c1c;
    
    /* Estado de éxito: ratio 4.8:1 ✓ */
    --color-success: #15803d;
    
    /* Estado de advertencia — PROBLEMA COMÚN: amarillo puro tiene ratio 1.07:1 ❌ */
    /* Solución: usar texto oscuro sobre fondo amarillo claro */
    --color-warning-bg: #fef3c7;
    --color-warning-text: #92400e;  /* ratio 5.8:1 sobre --color-warning-bg ✓ */
}

/* No usar color como ÚNICO indicador de estado: */
/* ❌ MAL: solo cambiar el color del borde para indicar error */
input.error { border-color: red; }

/* ✅ BIEN: color + icono + mensaje de texto */
input.error { 
    border-color: var(--color-error);
    padding-right: 2.5rem; /* Espacio para icono */
}
input.error + .error-icon { display: block; }  /* Icono ⚠ */
input.error ~ .error-message { display: block; } /* Texto de error */
```

- [ ] Auditar todos los colores con [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [ ] Corregir todos los fallos de contraste (ratio < 4.5:1 para texto)
- [ ] Estado de error/éxito/advertencia: nunca solo por color (agregar icono + texto)
- [ ] Modo alto contraste compatible con `prefers-contrast: high`

### 2. Navegación por Teclado (WCAG 2.1.1, 2.4.3, 2.4.7)

```html
<!-- Skip link — permite a usuarios de teclado saltar la navegación repetitiva -->
<body>
  <a href="#main-content" class="skip-link">
    Saltar al contenido principal
  </a>
  
  <nav><!-- navegación --></nav>
  
  <main id="main-content" tabindex="-1">
    <!-- contenido -->
  </main>
</body>

<style>
.skip-link {
    position: absolute;
    top: -100%;
    left: 0;
    /* Se vuelve visible cuando tiene foco (Tab key): */
    &:focus {
        top: 0;
        padding: 8px 16px;
        background: var(--color-accent);
        color: white;
        z-index: 9999;
        text-decoration: none;
    }
}
</style>
```

```javascript
// Focus visible y coherente en toda la app
// Nunca usar `outline: none` sin alternativa accesible:

/* ❌ MAL */
button:focus { outline: none; }

/* ✅ BIEN */
button:focus-visible {
    outline: 3px solid var(--color-accent);
    outline-offset: 2px;
    border-radius: 2px;
}
/* :focus-visible solo aplica cuando el usuario navega por teclado, no con ratón */
```

#### Orden de Tabulación en Formularios

```html
<!-- El orden de Tab debe seguir el flujo visual lógico -->
<form>
    <label for="cliente">Cliente *</label>
    <select id="cliente" name="cliente_id" tabindex="1">...</select>
    
    <label for="producto">Producto *</label>
    <select id="producto" name="producto_id" tabindex="2">...</select>
    
    <label for="lote">Número de Lote</label>
    <input id="lote" name="lote" tabindex="3" 
           pattern="[A-Z]-[0-9]{4}"
           aria-describedby="lote-format-hint">
    <small id="lote-format-hint">Formato: X-XXXX (ej: A-0123)</small>
    
    <!-- Botones al final -->
    <button type="submit" tabindex="10">Guardar</button>
    <button type="button" tabindex="11">Cancelar</button>
</form>
```

- [ ] Agregar "skip to main content" link al inicio de cada página
- [ ] Verificar que todos los elementos interactivos tienen `focus-visible` estilo claro
- [ ] Auditar orden de Tab en formularios críticos: nueva entrada, nuevo ensayo
- [ ] Modales: trapping de foco dentro del modal mientras está abierto
- [ ] Al cerrar un modal: foco regresa al elemento que lo abrió

### 3. ARIA y Semántica HTML (WCAG 4.1.2)

```html
<!-- Navegación principal con ARIA landmarks -->
<header role="banner">
    <nav role="navigation" aria-label="Navegación principal">
        <ul role="list">
            <li><a href="/entradas" aria-current="page">Entradas</a></li>
        </ul>
    </nav>
</header>

<main role="main" id="main-content">
    <!-- contenido -->
</main>

<footer role="contentinfo"><!-- pie --></footer>

<!-- Tablas de datos: siempre con caption y scope -->
<table>
    <caption>Entradas pendientes de análisis - Área FQ</caption>
    <thead>
        <tr>
            <th scope="col">ID</th>
            <th scope="col">Lote</th>
            <th scope="col">Cliente</th>
            <th scope="col">Estado</th>
            <th scope="col">Acciones</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>001</td>
            <td>A-0123</td>
            <td>Empresa XYZ</td>
            <td>
                <!-- Estado con texto, no solo color/icono -->
                <span class="badge badge-warning" aria-label="Estado: Pendiente">
                    <span aria-hidden="true">⏳</span>
                    Pendiente
                </span>
            </td>
            <td>
                <a href="/entradas/1" aria-label="Ver entrada 001">Ver</a>
                <button aria-label="Editar entrada 001">Editar</button>
            </td>
        </tr>
    </tbody>
</table>

<!-- Formularios: siempre label asociado, errores vinculados -->
<div class="form-group" role="group" aria-labelledby="lote-label">
    <label id="lote-label" for="lote">
        Número de Lote <span aria-label="campo requerido">*</span>
    </label>
    <input 
        id="lote" 
        name="lote"
        aria-required="true"
        aria-describedby="lote-hint lote-error"
        aria-invalid="true"  <!-- cuando hay error -->
    >
    <small id="lote-hint">Formato: X-XXXX</small>
    <span id="lote-error" role="alert" class="error-msg">
        El formato del lote es inválido
    </span>
</div>

<!-- Notificaciones dinámicas — anunciadas por lectores de pantalla -->
<div aria-live="polite" aria-atomic="true" id="notifications-region">
    <!-- Las notificaciones se insertan aquí dinámicamente -->
</div>

<!-- Loading states -->
<button id="save-btn" aria-busy="false">
    <span class="spinner" aria-hidden="true"></span>
    Guardar
</button>
<!-- Al guardar: aria-busy="true", texto cambia a "Guardando..." -->
```

- [ ] Agregar ARIA landmarks en layout base (`header`, `main`, `nav`, `footer`)
- [ ] Todas las tablas con `caption` y `scope` en `<th>`
- [ ] Todos los formularios: `label` asociado a cada `input`, errores con `aria-describedby`
- [ ] Iconos decorativos: `aria-hidden="true"`. Iconos informativos: `aria-label`
- [ ] Región `aria-live` para notificaciones dinámicas (toasts)
- [ ] Botones con `aria-busy` durante operaciones async

### 4. Internacionalización (i18n)

```python
# app/core/i18n/setup.py
from flask_babel import Babel, lazy_gettext as _l

babel = Babel()

def configure_i18n(app):
    babel.init_app(app, locale_selector=get_locale)

def get_locale():
    # 1. Preferencia del usuario (guardada en su perfil)
    if current_user.is_authenticated and current_user.locale:
        return current_user.locale
    # 2. Preferencia del navegador
    return request.accept_languages.best_match(['es', 'es_CU', 'en'])
```

```python
# En Python: usar lazy_gettext para strings traducibles
from flask_babel import lazy_gettext as _l, gettext as _

class EntradaForm(FlaskForm):
    cliente_id = SelectField(_l('Cliente'), validators=[DataRequired()])
    lote = StringField(
        _l('Número de Lote'),
        validators=[DataRequired(message=_l('Este campo es requerido'))]
    )
```

```html
<!-- En Jinja2: -->
<h1>{{ _('Gestión de Entradas') }}</h1>
<p>{{ _('%(count)s entradas pendientes', count=pending_count) }}</p>
```

```
# Estructura de traducciones:
app/translations/
├── es/
│   └── LC_MESSAGES/
│       ├── messages.po   ← Strings en español (idioma base)
│       └── messages.mo   ← Compilado
└── en/
    └── LC_MESSAGES/
        ├── messages.po   ← Strings en inglés
        └── messages.mo
```

- [ ] Instalar y configurar `flask-babel`
- [ ] Extraer todos los strings del código Python y templates a archivos `.po`
- [ ] Crear traducción base `es` (español estándar, idioma principal)
- [ ] Crear traducción `es_CU` si hay términos específicos cubanos (terminología de ONIE)
- [ ] Selector de idioma en perfil de usuario y en footer
- [ ] Formateo de fechas y números según locale (decimal: `,` o `.`)
- [ ] Soporte para plural correcto: "1 entrada" vs "5 entradas"

### 5. Formularios Accesibles — Foco en Entradas y Ensayos

Los formularios de entrada de muestras y asignación de ensayos son los más usados. Mejoras específicas:

```html
<!-- Autocompletar cliente con accesibilidad completa -->
<div role="combobox" 
     aria-expanded="false" 
     aria-haspopup="listbox"
     aria-owns="clientes-listbox">
    <input 
        type="text" 
        id="cliente-search"
        aria-autocomplete="list"
        aria-controls="clientes-listbox"
        placeholder="Escriba para buscar cliente..."
    >
    <ul id="clientes-listbox" role="listbox" aria-label="Clientes sugeridos">
        <li role="option" aria-selected="false">Empresa XYZ</li>
    </ul>
</div>

<!-- Validación en tiempo real con feedback accesible -->
<script>
document.getElementById('lote').addEventListener('input', function() {
    const valid = /^[A-Z]-\d{4}$/.test(this.value);
    this.setAttribute('aria-invalid', !valid);
    
    const errorEl = document.getElementById('lote-error');
    if (!valid && this.value.length > 0) {
        errorEl.textContent = 'Formato inválido. Use: A-0123';
        errorEl.style.display = 'block';
    } else {
        errorEl.style.display = 'none';
    }
});
</script>
```

- [ ] Autocompletar de cliente/producto completamente accesible con ARIA combobox pattern
- [ ] Validación inline con `aria-invalid` y `role="alert"`
- [ ] Mensajes de error descriptivos (no solo "Campo inválido" — explicar qué se espera)
- [ ] Campos requeridos marcados con `aria-required="true"` + indicador visual
- [ ] Confirmaciones de acciones destructivas: modal con foco atrapado

---

## Testing de Accesibilidad

```bash
# Herramientas automáticas (detectan ~40% de problemas):
npm install -g @axe-core/cli
axe http://localhost:5000 --exit

# En CI:
npx pa11y http://localhost:5000/entradas --standard WCAG2AA
npx pa11y http://localhost:5000/entradas/nueva --standard WCAG2AA

# Objetivo:
# Lighthouse Accessibility Score ≥ 90 en todas las páginas principales
```

```python
# Tests de accesibilidad automatizados:
def test_homepage_accessibility(client):
    """Verificar que la página principal pasa auditoría básica de a11y"""
    response = client.get('/')
    assert response.status_code == 200
    # Usar axe-core via pytest-playwright para verificar a11y
```

- [ ] Ejecutar `axe` en todas las páginas principales y resolver errores
- [ ] Lighthouse score ≥ 90 en accesibilidad
- [ ] Test manual con lector de pantalla (NVDA + Firefox, o VoiceOver en macOS)
- [ ] Integrar `pa11y` en pipeline CI (no bloquear build, sino reportar)

---

## Tareas

- [ ] Auditar contrastes con herramienta automatizada, corregir fallos
- [ ] Implementar skip links y ARIA landmarks
- [ ] Auditar y corregir tablas, formularios e iconos
- [ ] Configurar `flask-babel` e integrar strings traducibles
- [ ] Ejecutar `axe` y `pa11y`, resolver todos los errores críticos
- [ ] Test manual con lector de pantalla en formulario de nueva entrada

---

## Librerías

```txt
flask-babel==4.0.0
```

```json
// package.json (dev dependencies):
{
    "@axe-core/cli": "^4.8.0",
    "pa11y": "^8.0.0"
}
```

## Estimated Effort
**Story Points:** 8
**Estimated Time:** 4 días

## Related Issues
- Phase 6 #05 - UI/UX Enhancements (dark mode, responsive — base para esta issue)
- Phase 8 #06 - CI/CD (integrar pa11y en pipeline)
