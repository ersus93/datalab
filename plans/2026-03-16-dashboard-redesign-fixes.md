# Plan: Correcciones y Mejoras al Dashboard Redesign

**Fecha:** 2026-03-16
**Basado en:** `plans/dashboard_redesign_plan.md`
**Estado:** Listo para implementar

---

## Resumen Ejecutivo

El plan original de rediseño del dashboard es sólido y ejecutable.
Este documento corrige **2 bugs reales** y **1 inconsistencia de diseño**
encontrados en el análisis, y propone **3 mejoras menores** que aprovechan
datos ya disponibles en el route sin trabajo adicional.

| Item | Tipo | Impacto |
|------|------|---------|
| Bug 1: Macro sin imports | Bug bloqueante | El componente falla al renderizar |
| Bug 2: Guard de permisos | Bug de UX | Usuario ve error 403 sin advertencia |
| Fix 3: Inconsistencia Fase 5/6 | Inconsistencia | El plan tenía dos diseños distintos |
| Mejora A: Entradas hoy | Mejora | Dato ya disponible, cero esfuerzo extra |
| Mejora B: Ver Pendientes | Mejora | Recupera funcionalidad del plan original |
| Mejora C: pending_deliveries badge | Mejora | Aprovecha dato del DashboardService |

---

## Bug 1 — `actions_panel.html` usa macros sin importarlas (BLOQUEANTE)

### Diagnóstico

El plan propone crear `components/dashboard/actions_panel.html` con un macro
que internamente llama a `glass_card`, `glass_card_header` y `glass_card_body`.

En Jinja2, cuando importas un macro desde otro archivo, ese macro se ejecuta
en el scope de su propio archivo de origen — NO en el scope del template que
lo importa. Por eso, las importaciones del template principal no ayudan:

```jinja2
{# dashboard.html importa glass_card, pero... #}
{% from 'components/glass_card.html' import glass_card %}
{% from 'components/dashboard/actions_panel.html' import actions_panel %}

{# ...cuando actions_panel() ejecuta internamente {% call glass_card() %},
   glass_card no existe en el scope de actions_panel.html → TemplateError #}
{{ actions_panel() }}
```

### Solución

Agregar los imports necesarios al inicio del archivo `actions_panel.html`:

```jinja2
{# app/templates/components/dashboard/actions_panel.html #}
{% from 'components/glass_card.html' import glass_card, glass_card_header, glass_card_body %}

{% macro actions_panel() %}
{# ... resto del macro sin cambios ... #}
{% endmacro %}
```

Hacer lo mismo para `status_count_glass.html` si este también usa macros glass.
En este caso el widget de estados NO usa macros glass (solo clases CSS directas),
así que ese archivo no necesita imports.

---

## Bug 2 — Botón "Nueva Fábrica" sin guard de permisos

### Diagnóstico

`fabricas.nueva` está protegida por `@laboratory_manager_required`, que permite:
- `UserRole.ADMIN`
- `UserRole.LABORATORY_MANAGER`

El `actions_panel` muestra ese botón a todos los usuarios autenticados.
Un usuario con rol `TECHNICIAN`, `CLIENT` o `VIEWER` que lo clickee recibe
un flash de error y redirect o 403 — experiencia confusa.

### Solución

Envolver el botón con un condicional en el template.
El modelo `User` expone `is_admin()` y `is_laboratory_manager()`, ambos
disponibles a través de `current_user` de Flask-Login:

```jinja2
{# En actions_panel.html, dentro del grid "Nuevo Registro" #}

{# Botones sin restricción de rol #}
<a href="{{ url_for('entradas.nueva') }}" ...>Nueva Entrada</a>
<a href="{{ url_for('pedidos.nuevo') }}" ...>Nuevo Pedido</a>
<a href="{{ url_for('clientes.nuevo') }}" ...>Nuevo Cliente</a>

{# Botón con restricción — solo para managers y admins #}
{% if current_user.is_admin() or current_user.is_laboratory_manager() %}
<a href="{{ url_for('fabricas.nueva') }}"
   class="p-3 rounded-lg bg-warning-50/20 border border-warning-500/30
          hover:bg-warning-50/30 transition-all text-center">
    <i class="fas fa-industry text-warning-500 mb-1"></i>
    <span class="text-sm text-text-primary block">Nueva Fábrica</span>
</a>
{% else %}
{# Mantener el grid balanceado ocupando el slot con otro botón útil #}
<a href="{{ url_for('ordenes_trabajo.nueva') }}"
   class="p-3 rounded-lg bg-info-50/20 border border-info-500/30
          hover:bg-info-50/30 transition-all text-center">
    <i class="fas fa-clipboard-check text-info-400 mb-1"></i>
    <span class="text-sm text-text-primary block">Nueva Orden</span>
</a>
{% endif %}
```

> **Nota:** Verificar que `ordenes_trabajo.nueva` no tenga restricción de rol
> antes de usarla como fallback.


---

## Fix 3 — Inconsistencia entre Fase 5 y Fase 6

### Diagnóstico

El plan define dos versiones distintas del widget "Entradas Recientes":

- **Fase 5**: Tabla completa con 5 columnas (código, producto, cliente, fecha, estado)
- **Fase 6**: Lista compacta tipo feed de 5 items

Son incompatibles entre sí. No se puede implementar ambas.

### Decisión

**Usar el diseño de la Fase 6** (lista compacta) y **descartar la tabla de la Fase 5**.

Razones:
1. La lista compacta encaja mejor en la columna lateral `col-span-1`
2. La tabla de 5 columnas queda apretada en un tercio del ancho de pantalla
3. La Fase 6 es el "template final" — tiene más peso en el plan

**Eliminar del plan** el bloque HTML de la Fase 5 con el `<table class="glass-table">`.
Reemplazarlo con una nota que apunte a la implementación de la Fase 6.

---

## Nota sobre el "Problema 1" del análisis previo (FALSO POSITIVO)

El análisis anterior advertía sobre las keys del `status_counts` dict.
Tras revisar el código, **no hay problema**:

- `EntradaStatus` es una clase Python con constantes string (`RECIBIDO = 'RECIBIDO'`)
- `get_sample_status_counts()` retorna `{'RECIBIDO': 0, 'EN_PROCESO': 0, ...}`
- En Jinja2, `status_counts.RECIBIDO` y `status_counts['RECIBIDO']` son equivalentes
- El `|default(0)` cubre el caso del fallback donde `status_counts = {}`

Las keys son correctas. No requiere ningún cambio.

---

## Mejora A — Agregar "Entradas hoy" al header del dashboard

### Por qué

El route ya calcula `entrada_stats.hoy` (entradas registradas hoy):

```python
entrada_stats = {
    'hoy': Entrada.query.filter(
        db.func.date(Entrada.fech_entrada) == today,
        Entrada.anulado == False,
    ).count(),
    ...
}
```

Este dato llega al template pero el plan no lo usa en ningún lugar visible.
Mostrarlo en el header le da al usuario contexto inmediato sin ninguna query extra.

### Implementación

En el header del dashboard (Fase 1 del plan original), agregar un pill informativo:

```jinja2
<div class="mb-8">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gradient">
                <i class="fas fa-tachometer-alt mr-2 text-primary-400"></i>
                Dashboard
            </h1>
            <p class="text-text-muted mt-1">
                Panel de control con métricas en tiempo real
            </p>
        </div>
        {# Pill "Entradas hoy" — dato ya disponible sin costo extra #}
        {% if entrada_stats.hoy > 0 %}
        <div class="flex items-center gap-2 px-4 py-2 rounded-full
                    bg-primary-50/30 border border-primary-500/30">
            <div class="w-2 h-2 rounded-full bg-primary-400 animate-pulse"></div>
            <span class="text-sm text-primary-400 font-medium font-mono">
                {{ entrada_stats.hoy }}
            </span>
            <span class="text-xs text-text-muted">
                {{ 'entrada' if entrada_stats.hoy == 1 else 'entradas' }} hoy
            </span>
        </div>
        {% endif %}
    </div>
</div>
```

---

## Mejora B — Recuperar el filtro "Ver Pendientes" con EN_PROCESO

### Por qué

El `quick_actions.html` original tenía este botón:
```html
<a href="{{ url_for('entradas.listar') }}?estado=EN_PROCESO">Ver Pendientes</a>
```

El nuevo `actions_panel` lo reemplaza con un botón genérico de "Entradas"
que va al listado sin filtro. Se pierde un acceso directo muy útil.

### Implementación

En la sección "Ver Listados" del `actions_panel`, sustituir el botón de Entradas
genérico por dos botones más específicos, o agregar el pendientes como acceso directo
en la sección "Nuevo Registro":

```jinja2
{# En la sección "Ver Listados" — reemplazar el botón genérico de Entradas #}
<a href="{{ url_for('entradas.listar') }}"
   class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
    <i class="fas fa-vials text-text-secondary mb-1"></i>
    <span class="text-sm text-text-secondary block">Todas las entradas</span>
</a>

<a href="{{ url_for('entradas.listar') }}?estado=EN_PROCESO"
   class="p-3 rounded-lg bg-warning-50/10 border border-warning-500/20
          hover:bg-warning-50/20 transition-all text-center">
    <i class="fas fa-clock text-warning-500 mb-1"></i>
    <span class="text-sm text-warning-400 block">En proceso</span>
</a>
```


---

## Mejora C — Badge de "pendientes de entrega" en métricas

### Por qué

El `DashboardService` ya calcula `pending_deliveries` — entradas con estado
`COMPLETADO` y `saldo > 0` (análisis listo, muestra aún no entregada al cliente).
Este dato llega al template pero el plan no lo expone visualmente.

Un badge discreto en la tarjeta de métricas convierte un número muerto
en información accionable.

### Implementación

Modificar la tarjeta de métricas de "Órdenes de Trabajo" (o crear una
quinta tarjeta) para incluir el conteo de pendientes de entrega:

```jinja2
{# Opción A: Badge sobre la tarjeta de Ensayos #}
<a href="{{ url_for('entradas.listar') }}?estado=COMPLETADO" class="block group relative">
    {% call glass_card(variant='md', class='bg-warning-50/50 border-warning-500/30
                                           hover:border-warning-400/50') %}
        <h5 class="text-sm font-medium text-warning-500 mb-2">Total Ensayos</h5>
        <h2 class="text-3xl font-bold text-text-primary font-mono">{{ total_ensayos }}</h2>
        {% if pending_deliveries %}
        <p class="text-xs text-warning-400 mt-2 font-mono">
            {{ pending_deliveries|length }} pendientes de entrega
        </p>
        {% endif %}
    {% endcall %}
</a>
```

> Si se prefiere no tocar las 4 tarjetas, se puede añadir como un banner
> de alerta debajo de las métricas (solo si `pending_deliveries` tiene items):
>
> ```jinja2
> {% if pending_deliveries %}
> <div class="flex items-center gap-3 px-4 py-3 rounded-xl
>             bg-warning-50/20 border border-warning-500/30 mb-8">
>     <i class="fas fa-exclamation-triangle text-warning-500"></i>
>     <span class="text-sm text-warning-400">
>         <strong class="font-mono">{{ pending_deliveries|length }}</strong>
>         muestras completadas pendientes de entrega al cliente
>     </span>
>     <a href="{{ url_for('entradas.listar') }}?estado=COMPLETADO"
>        class="ml-auto text-xs text-warning-400 hover:text-warning-300 underline">
>         Ver todas →
>     </a>
> </div>
> {% endif %}
> ```

---

## Orden de implementación recomendado

Seguir este orden minimiza el riesgo de tener el dashboard roto en estados intermedios:

### Paso 1 — Crear componentes nuevos (prerequisito para el resto)

```
Crear: app/templates/components/dashboard/status_count_glass.html
Crear: app/templates/components/dashboard/actions_panel.html
```

Al crear `actions_panel.html`, aplicar **Bug 1** y **Bug 2** desde el inicio.
No copiar el código del plan original sin más — usar las versiones corregidas.

**Checklist para `actions_panel.html`:**
- [ ] Tiene `{% from 'components/glass_card.html' import glass_card, glass_card_header, glass_card_body %}` al inicio
- [ ] El botón "Nueva Fábrica" tiene el `{% if current_user.is_admin() or current_user.is_laboratory_manager() %}`
- [ ] La sección "Ver Listados" incluye "En proceso" con filtro `?estado=EN_PROCESO`

**Checklist para `status_count_glass.html`:**
- [ ] No usa macros glass directamente (usa clases CSS) → no necesita imports
- [ ] Las 5 keys del dict coinciden con las constantes de `EntradaStatus`

### Paso 2 — Modificar el template principal

```
Modificar: app/templates/pages/dashboard/dashboard.html
```

Aplicar la Fase 6 del plan original con estas adiciones:
- [ ] Header incluye el pill "Entradas hoy" (**Mejora A**)
- [ ] Se usa la lista compacta de la Fase 6 (NO la tabla de la Fase 5) (**Fix 3**)
- [ ] Se agrega el banner de pending_deliveries si aplica (**Mejora C**)

### Paso 3 — Verificar en navegador

Comprobar con distintos roles de usuario:
- [ ] Como `ADMIN`: ve botón "Nueva Fábrica" ✓
- [ ] Como `LABORATORY_MANAGER`: ve botón "Nueva Fábrica" ✓
- [ ] Como `TECHNICIAN`: ve botón alternativo (no "Nueva Fábrica") ✓
- [ ] Como `VIEWER`: ídem ✓
- [ ] Todos los estados del widget de estados muestran números (no ceros) ✓
- [ ] El pill "Entradas hoy" aparece solo cuando `entrada_stats.hoy > 0` ✓

---

## Archivos a crear/modificar (tabla actualizada)

| Archivo | Acción | Cambios respecto al plan original |
|---------|--------|-----------------------------------|
| `components/dashboard/actions_panel.html` | **Crear** | + imports glass_card al inicio; + guard permisos fábrica; + botón "En proceso" |
| `components/dashboard/status_count_glass.html` | **Crear** | Sin cambios respecto al plan |
| `pages/dashboard/dashboard.html` | **Modificar** | + pill "Entradas hoy" en header; + banner pending_deliveries; usar lista compacta (no tabla) |

El plan original queda válido en todo lo demás. No hay cambios en rutas,
no hay cambios en el route de Python, no hay nuevas queries.
