# Plan de Implementación Detallado: Dashboard Redesign

**Fecha:** 2026-03-16
**Estado:** Listo para ejecución
**Basado en:** `plans/dashboard_redesign_plan.md` + `plans/2026-03-16-dashboard-redesign-fixes.md`

---

## Resumen del Plan

Este plan implementa el rediseño del dashboard principal de DataLab, migrando de estilos Bootstrap a Glass Design System. Se incorporan **2 bugs corregidos** y **3 mejoras** del documento de correcciones.

### Archivos a Crear/Modificar

| # | Archivo | Acción | Descripción |
|---|---------|--------|-------------|
| 1 | `app/templates/components/dashboard/status_count_glass.html` | **CREAR** | Widget de estados con estilo glass |
| 2 | `app/templates/components/dashboard/actions_panel.html` | **CREAR** | Panel de acciones rápidas y CRUD |
| 3 | `app/templates/pages/dashboard/dashboard.html` | **MODIFICAR** | Template principal del dashboard |

---

## Componente 1: `status_count_glass.html`

**Ubicación:** `app/templates/components/dashboard/status_count_glass.html`

**Descripción:** Widget de conteo por estado con estilo glass, mostrando 5 estados de entradas.

**Notas:**
- NO usa macros glass internamente (solo clases CSS directas) → no necesita imports
- Las 5 keys del dict coinciden con las constantes de `EntradaStatus`

```jinja2
{# app/templates/components/dashboard/status_count_glass.html #}
{# Widget de Estados de Entradas - Estilo Glass Design System #}

{% macro status_count_glass(status_counts) %}
<div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
    {# Recibido #}
    <div class="p-4 rounded-xl bg-glass-1 border border-glass-border hover:border-gray-500/30 transition-all cursor-pointer"
         onclick="window.location.href='{{ url_for('entradas.listar') }}?estado=RECIBIDO'">
        <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-gray-500/20 flex items-center justify-center">
                <i class="fas fa-inbox text-gray-400"></i>
            </div>
            <span class="text-xs text-text-muted uppercase">Recibido</span>
        </div>
        <div class="text-2xl font-bold text-text-primary font-mono">{{ status_counts.RECIBIDO|default(0) }}</div>
    </div>
    
    {# En Proceso #}
    <div class="p-4 rounded-xl bg-primary-50/20 border border-primary-500/30 hover:border-primary-400/50 transition-all cursor-pointer"
         onclick="window.location.href='{{ url_for('entradas.listar') }}?estado=EN_PROCESO'">
        <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                <i class="fas fa-spinner text-primary-400"></i>
            </div>
            <span class="text-xs text-text-muted uppercase">En Proceso</span>
        </div>
        <div class="text-2xl font-bold text-text-primary font-mono">{{ status_counts.EN_PROCESO|default(0) }}</div>
    </div>
    
    {# Completado #}
    <div class="p-4 rounded-xl bg-success-50/20 border border-success-500/30 hover:border-success-400/50 transition-all cursor-pointer"
         onclick="window.location.href='{{ url_for('entradas.listar') }}?estado=COMPLETADO'">
        <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-success-500/20 flex items-center justify-center">
                <i class="fas fa-check-circle text-success-400"></i>
            </div>
            <span class="text-xs text-text-muted uppercase">Completado</span>
        </div>
        <div class="text-2xl font-bold text-text-primary font-mono">{{ status_counts.COMPLETADO|default(0) }}</div>
    </div>
    
    {# Entregado #}
    <div class="p-4 rounded-xl bg-info-50/20 border border-info-500/30 hover:border-info-400/50 transition-all cursor-pointer"
         onclick="window.location.href='{{ url_for('entradas.listar') }}?estado=ENTREGADO'">
        <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-info-500/20 flex items-center justify-center">
                <i class="fas fa-truck text-info-400"></i>
            </div>
            <span class="text-xs text-text-muted uppercase">Entregado</span>
        </div>
        <div class="text-2xl font-bold text-text-primary font-mono">{{ status_counts.ENTREGADO|default(0) }}</div>
    </div>
    
    {# Anulado #}
    <div class="p-4 rounded-xl bg-error-50/20 border border-error-500/30 hover:border-error-400/50 transition-all cursor-pointer"
         onclick="window.location.href='{{ url_for('entradas.listar') }}?estado=ANULADO'">
        <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-error-500/20 flex items-center justify-center">
                <i class="fas fa-times-circle text-error-400"></i>
            </div>
            <span class="text-xs text-text-muted uppercase">Anulado</span>
        </div>
        <div class="text-2xl font-bold text-text-primary font-mono">{{ status_counts.ANULADO|default(0) }}</div>
    </div>
</div>
{% endmacro %}
```

---

## Componente 2: `actions_panel.html`

**Ubicación:** `app/templates/components/dashboard/actions_panel.html`

**Descripción:** Panel consolidado de acciones rápidas y accesos directos CRUD.

**CRÍTICO - Bugs corregidos en este archivo:**

| Bug | Descripción | Solución |
|-----|-------------|----------|
| **Bug 1** | Macro usa `glass_card` internamente sin imports | ✅ Agregar imports al inicio del archivo |
| **Bug 2** | Botón "Nueva Fábrica" sin guard de permisos | ✅ Agregar `{% if current_user.is_admin() or current_user.is_laboratory_manager() %}` |

**CRÍTICO - Mejoras aplicadas en este archivo:**

| Mejora | Descripción |
|--------|-------------|
| **Mejora B** | Agregar botón "En proceso" con filtro `?estado=EN_PROCESO` |

```jinja2
{# app/templates/components/dashboard/actions_panel.html #}
{# Panel de Acciones Rápidas y CRUD - Glass Design System #}

{# BUG 1 CORREGIDO: Importar macros necesarios #}
{% from 'components/glass_card.html' import glass_card, glass_card_header, glass_card_body %}

{% macro actions_panel() %}
{% call glass_card(variant='lg') %}
{% call glass_card_header() %}
<h3 class="text-lg font-semibold text-text-primary">
    <i class="fas fa-bolt mr-2 text-warning-500"></i>
    Acciones Rápidas
</h3>
{% endcall %}
{% call glass_card_body() %}

{# Primera fila: Crear nuevos registros #}
<div class="mb-6">
    <h4 class="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wide">
        <i class="fas fa-plus-circle mr-1"></i> Nuevo Registro
    </h4>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <a href="{{ url_for('entradas.nueva') }}" class="p-3 rounded-lg bg-primary-50/20 border border-primary-500/30 hover:bg-primary-50/30 transition-all text-center">
            <i class="fas fa-vial text-primary-400 mb-1"></i>
            <span class="text-sm text-text-primary block">Nueva Entrada</span>
        </a>
        <a href="{{ url_for('pedidos.nuevo') }}" class="p-3 rounded-lg bg-success-50/20 border border-success-500/30 hover:bg-success-50/30 transition-all text-center">
            <i class="fas fa-clipboard-list text-success-400 mb-1"></i>
            <span class="text-sm text-text-primary block">Nuevo Pedido</span>
        </a>
        <a href="{{ url_for('clientes.nuevo') }}" class="p-3 rounded-lg bg-secondary-50/20 border border-secondary-500/30 hover:bg-secondary-50/30 transition-all text-center">
            <i class="fas fa-user-plus text-secondary-400 mb-1"></i>
            <span class="text-sm text-text-primary block">Nuevo Cliente</span>
        </a>
        
        {# BUG 2 CORREGIDO: Guard de permisos para Nueva Fábrica #}
        {% if current_user.is_admin() or current_user.is_laboratory_manager() %}
        <a href="{{ url_for('fabricas.nueva') }}" class="p-3 rounded-lg bg-warning-50/20 border border-warning-500/30 hover:bg-warning-50/30 transition-all text-center">
            <i class="fas fa-industry text-warning-500 mb-1"></i>
            <span class="text-sm text-text-primary block">Nueva Fábrica</span>
        </a>
        {% else %}
        <a href="{{ url_for('ordenes_trabajo.nueva') }}" class="p-3 rounded-lg bg-info-50/20 border border-info-500/30 hover:bg-info-50/30 transition-all text-center">
            <i class="fas fa-clipboard-check text-info-400 mb-1"></i>
            <span class="text-sm text-text-primary block">Nueva Orden</span>
        </a>
        {% endif %}
    </div>
</div>

{# Segunda fila: Gestionar registros #}
<div class="mb-6">
    <h4 class="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wide">
        <i class="fas fa-cogs mr-1"></i> Gestionar
    </h4>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <a href="{{ url_for('clientes.listar') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-users text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Clientes</span>
        </a>
        <a href="{{ url_for('fabricas.listar') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-building text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Fábricas</span>
        </a>
        <a href="{{ url_for('productos.listar') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-box text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Productos</span>
        </a>
        <a href="{{ url_for('ordenes_trabajo.listar') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-tasks text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Órdenes</span>
        </a>
    </div>
</div>

{# Tercera fila: Ver listados #}
<div>
    <h4 class="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wide">
        <i class="fas fa-list mr-1"></i> Ver Listados
    </h4>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <a href="{{ url_for('entradas.listar') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-vials text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Todas las entradas</span>
        </a>
        
        {# MEJORA B: Botón "En proceso" con filtro #}
        <a href="{{ url_for('entradas.listar') }}?estado=EN_PROCESO"
           class="p-3 rounded-lg bg-warning-50/10 border border-warning-500/20
                  hover:bg-warning-50/20 transition-all text-center">
            <i class="fas fa-clock text-warning-500 mb-1"></i>
            <span class="text-sm text-warning-400 block">En proceso</span>
        </a>
        
        <a href="{{ url_for('informes.listar') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-file-alt text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Informes</span>
        </a>
        <a href="{{ url_for('lab.index') }}" class="p-3 rounded-lg bg-glass-1 border border-glass-border hover:bg-glass-2 transition-all text-center">
            <i class="fas fa-flask text-text-secondary mb-1"></i>
            <span class="text-sm text-text-secondary block">Laboratorio</span>
        </a>
    </div>
</div>

{% endcall %}
{% endcall %}
{% endmacro %}
```

---

## Template 3: `dashboard.html` (Modificación)

**Ubicación:** `app/templates/pages/dashboard/dashboard.html`

**Cambios principales:**
1. Cambiar `extends "base/base.html"` a `extends "base.html"`
2. Eliminar referencia a Bootstrap CSS
3. Importar macros glass
4. Nuevo layout con grid glass
5. **Mejora A:** Pill "Entradas hoy" en el header
6. **Mejora C:** Banner de pendientes de entrega

```jinja2
{% extends "base.html" %}

{% block title %}Dashboard - DataLab{% endblock %}
{% block description %}Panel de control principal con métricas y análisis en tiempo real{% endblock %}
{% block keywords %}dashboard, métricas, análisis, estadísticas, tiempo real{% endblock %}

{# Importar macros de componentes glass #}
{% from 'components/glass_card.html' import glass_card, glass_card_header, glass_card_body, glass_card_footer %}
{% from 'components/dashboard/status_count_glass.html' import status_count_glass %}
{% from 'components/dashboard/actions_panel.html' import actions_panel %}

{% block extra_css %}
{# Eliminar Bootstrap CSS - no longer needed #}
{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto">
    
    {# Header del Dashboard #}
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
            
            {# MEJORA A: Pill "Entradas hoy" - dato ya disponible sin costo extra #}
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

    {# Widget de Conteo por Estado - Nuevo estilo glass #}
    {{ status_count_glass(status_counts|default({})) }}

    {# Métricas Principales #}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <a href="{{ url_for('clientes.listar') }}" class="block group">
            {% call glass_card(variant='md', class='bg-primary-50/50 border-primary-500/30 hover:border-primary-400/50') %}
                <h5 class="text-sm font-medium text-primary-400 mb-2">Total Clientes</h5>
                <h2 class="text-3xl font-bold text-text-primary font-mono">{{ stats.total_clientes }}</h2>
            {% endcall %}
        </a>
        
        <a href="{{ url_for('pedidos.listar') }}" class="block group">
            {% call glass_card(variant='md', class='bg-success-50/50 border-success-500/30 hover:border-success-400/50') %}
                <h5 class="text-sm font-medium text-success-500 mb-2">Total Pedidos</h5>
                <h2 class="text-3xl font-bold text-text-primary font-mono">{{ total_pedidos }}</h2>
            {% endcall %}
        </a>
        
        <a href="{{ url_for('tecnico.metricas') }}" class="block group">
            {% call glass_card(variant='md', class='bg-warning-50/50 border-warning-500/30 hover:border-warning-400/50') %}
                <h5 class="text-sm font-medium text-warning-500 mb-2">Total Ensayos</h5>
                <h2 class="text-3xl font-bold text-text-primary font-mono">{{ total_ensayos }}</h2>
            {% endcall %}
        </a>
        
        <a href="{{ url_for('ordenes_trabajo.listar') }}" class="block group">
            {% call glass_card(variant='md', class='bg-info-50/50 border-info-500/30 hover:border-info-400/50') %}
                <h5 class="text-sm font-medium text-info-500 mb-2">Órdenes de Trabajo</h5>
                <h2 class="text-3xl font-bold text-text-primary font-mono">{{ total_ordenes }}</h2>
            {% endcall %}
        </a>
    </div>

    {# MEJORA C: Banner de pendientes de entrega - dato ya disponible del DashboardService #}
    {% if pending_deliveries %}
    <div class="flex items-center gap-3 px-4 py-3 rounded-xl
                bg-warning-50/20 border border-warning-500/30 mb-8">
        <i class="fas fa-exclamation-triangle text-warning-500"></i>
        <span class="text-sm text-warning-400">
            <strong class="font-mono">{{ pending_deliveries|length }}</strong>
            muestras completadas pendientes de entrega al cliente
        </span>
        <a href="{{ url_for('entradas.listar') }}?estado=COMPLETADO"
           class="ml-auto text-xs text-warning-400 hover:text-warning-300 underline">
            Ver todas →
        </a>
    </div>
    {% endif %}

    {# Acciones Rápidas y Actividad Reciente #}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div class="lg:col-span-2">
            {{ actions_panel() }}
        </div>
        
        <div>
            {# Actividad Reciente - Lista compacta tipo feed (Fase 6, NO tabla de Fase 5) #}
            {% call glass_card(variant='md') %}
            {% call glass_card_header() %}
            <h3 class="text-lg font-semibold text-text-primary">
                <i class="fas fa-clock mr-2 text-info-500"></i>
                Entradas Recientes
            </h3>
            {% endcall %}
            {% call glass_card_body() %}
            <div class="space-y-3">
                {% for entrada in entradas_recientes[:5] %}
                <a href="{{ url_for('entradas.ver', id=entrada.id) }}" class="block p-3 rounded-lg bg-glass-1 hover:bg-glass-2 border border-glass-border transition-all">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <p class="text-sm font-medium text-text-primary">{{ entrada.codigo }}</p>
                            <p class="text-xs text-text-muted">{{ entrada.producto.nombre[:30] if entrada.producto else '-' }}</p>
                        </div>
                        <span class="text-xs px-2 py-1 rounded-full 
                            {{ 'bg-success-50 text-success-400' if entrada.status.value == 'COMPLETADO' else '' }}
                            {{ 'bg-primary-50 text-primary-400' if entrada.status.value == 'EN_PROCESO' else '' }}
                            {{ 'bg-gray-500/20 text-gray-400' if entrada.status.value == 'RECIBIDO' else '' }}">
                            {{ entrada.status.value }}
                        </span>
                    </div>
                </a>
                {% else %}
                <p class="text-sm text-text-muted text-center py-4">No hay entradas recientes</p>
                {% endfor %}
            </div>
            <a href="{{ url_for('entradas.listar') }}" class="block mt-4 text-center text-sm text-primary-400 hover:text-primary-300">
                Ver todas las entradas →
            </a>
            {% endcall %}
            {% endcall %}
        </div>
    </div>

</div>
{% endblock %}

{% block extra_js %}
{# Eliminar Bootstrap JS - no longer needed #}
{# Eliminar Chart.js y dashboard.js si no se usan #}
{% endblock %}
```

---

## Checklist de Implementación

### Paso 1 - Crear Componentes

- [ ] **Crear** `app/templates/components/dashboard/status_count_glass.html`
  - Verificar que NO usa macros glass internamente
  - Verificar las 5 keys del dict coinciden con `EntradaStatus`

- [ ] **Crear** `app/templates/components/dashboard/actions_panel.html`
  - [ ] ✅ **Bug 1:** Tiene `{% from 'components/glass_card.html' import glass_card, glass_card_header, glass_card_body %}` al inicio
  - [ ] ✅ **Bug 2:** Botón "Nueva Fábrica" tiene `{% if current_user.is_admin() or current_user.is_laboratory_manager() %}`
  - [ ] ✅ **Mejora B:** Sección "Ver Listados" incluye "En proceso" con filtro `?estado=EN_PROCESO`

### Paso 2 - Modificar Template Principal

- [ ] **Modificar** `app/templates/pages/dashboard/dashboard.html`
  - [ ] ✅ Cambiar `extends "base/base.html"` a `extends "base.html"`
  - [ ] ✅ Eliminar referencia a Bootstrap CSS
  - [ ] ✅ Importar macros glass necesarios
  - [ ] ✅ **Mejora A:** Header incluye pill "Entradas hoy" (`entrada_stats.hoy > 0`)
  - [ ] ✅ **Mejora C:** Banner de pending_deliveries si aplica
  - [ ] ✅ Usar lista compacta (Fase 6), NO tabla (Fase 5)

### Paso 3 - Verificar en Navegador

Comprobar con distintos roles de usuario:
- [ ] Como **ADMIN**: ve botón "Nueva Fábrica" ✓
- [ ] Como **LABORATORY_MANAGER**: ve botón "Nueva Fábrica" ✓
- [ ] Como **TECHNICIAN**: ve botón alternativo (Nueva Orden) ✓
- [ ] Como **VIEWER**: ve botón alternativo (Nueva Orden) ✓
- [ ] Todos los estados del widget de estados muestran números (no ceros) ✓
- [ ] El pill "Entradas hoy" aparece solo cuando `entrada_stats.hoy > 0` ✓

---

## Dependencias Verificadas

Las siguientes rutas están verificadas y existen en el proyecto:

| Ruta | Nombre | Propósito |
|------|--------|-----------|
| `/entradas/nueva` | `entradas.nueva` | Crear entrada |
| `/pedidos/nuevo` | `pedidos.nuevo` | Crear pedido |
| `/clientes/nuevo` | `clientes.nuevo` | Crear cliente |
| `/clientes/listar` | `clientes.listar` | Listar clientes |
| `/fabricas/nueva` | `fabricas.nueva` | Crear fábrica (requiere `laboratory_manager_required`) |
| `/fabricas/listar` | `fabricas.listar` | Listar fábricas |
| `/productos/listar` | `productos.listar` | Listar productos |
| `/entradas/listar` | `entradas.listar` | Listar entradas |
| `/pedidos/listar` | `pedidos.listar` | Listar pedidos |
| `/informes/listar` | `informes.listar` | Listar informes |
| `/ordenes_trabajo/listar` | `ordenes_trabajo.listar` | Listar órdenes |
| `/ordenes_trabajo.nueva` | `ordenes_trabajo.nueva` | Nueva orden de trabajo |
| `/lab/` | `lab.index` | Vista laboratorio |
| `/tecnico/metricas` | `tecnico.metricas` | Métricas técnico |

---

## Datos Disponibles del Route

El template recibirá los siguientes datos (ya calculados en `dashboard.py`):

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `stats.total_clientes` | int | Total de clientes activos |
| `total_pedidos` | int | Total de pedidos |
| `total_ensayos` | int | Total de ensayos |
| `total_ordenes` | int | Total de órdenes de trabajo |
| `entrada_stats.hoy` | int | Entradas registradas hoy (**Mejora A**) |
| `status_counts` | dict | Conteo por estado |
| `pending_deliveries` | list | Entregas pendientes (**Mejora C**) |
| `entradas_recientes` | list | Últimas 5 entradas |

---

## Notas de Diseño

1. **Glass Design System**: El nuevo dashboard usa componentes del sistema de diseño glass existente en `components/glass_card.html`

2. **Responsive**: Grid adaptativo con `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`

3. **Interactividad**: Los widgets de estado tienen `onclick` para filtrar listas

4. **Fallback**: El código maneja casos donde los datos podrían estar vacíos usando `|default(0)` o `|default({})`

5. **Seguridad**: Los botones sensibles tienen guards de permisos basados en `current_user.is_admin()` y `current_user.is_laboratory_manager()`
