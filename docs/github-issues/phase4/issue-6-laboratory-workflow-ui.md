# [Phase 4] Laboratory Workflow UI

## Description
Create a comprehensive user interface for laboratory technicians to manage their daily work, execute tests, and track their performance. This is the primary interface for day-to-day laboratory operations.

## User Personas

### Primary: Laboratory Technician
- Executes tests assigned to them
- Records results in the system
- Manages their work queue
- Views their performance metrics

### Secondary: Laboratory Supervisor
- Assigns tests to technicians
- Reviews completed work
- Monitors team performance
- Manages workload distribution

## Interface Components

### 1. Technician Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  [Logo]  DataLab                    [User] [Notifications ▼] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RESUMEN DE TRABAJO - [Área: FQ]                           │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  PENDIENTES │  │ EN PROCESO  │  │ COMPLETADOS │         │
│  │     12      │  │      5      │  │    127      │         │
│  │  Esta semana│  │  Hoy        │  │  Este mes   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ACCIONES RÁPIDAS:                                          │
│  [+ Iniciar Ensayo]  [📋 Ver Cola]  [📊 Mis Estadísticas]   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Pending Tests View
```
┌─────────────────────────────────────────────────────────────┐
│  ENSAYOS PENDIENTES - Físico-Química                       │
├─────────────────────────────────────────────────────────────┤
│  [Filtrar ▼] [Buscar...]              [Vista: Lista ▼]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ☑ │ Muestra    │ Ensayo          │ Prioridad │ Vence     │
│  ──┼────────────┼─────────────────┼───────────┼────────── │
│  ☐ │ ENT-1234   │ pH              │ Alta      │ Hoy       │
│  ☐ │ ENT-1235   │ Densidad        │ Media     │ Mañana    │
│  ☐ │ ENT-1236   │ Humedad         │ Baja      │ 3 días    │
│  ☑ │ ENT-1237   │ Viscosidad      │ Alta      │ Hoy       │
│                                                             │
│  [Iniciar Seleccionados]    [Asignarme]    [Ver Detalle]   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Sortable columns
- Priority indicators (color-coded)
- Due date alerts
- Batch selection
- Quick actions

### 3. Test Execution Form
```
┌─────────────────────────────────────────────────────────────┐
│  EJECUTAR ENSAYO - Muestra ENT-1234                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INFORMACIÓN DE LA MUESTRA:                                 │
│  Cliente: [Nombre del Cliente]                              │
│  Producto: [Nombre del Producto]                            │
│  Fecha recepción: 2024-01-10                                │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ENSAYO: pH                                                 │
│  Método: [Método asociado]                                  │
│  Especificación: 6.0 - 8.0                                  │
│                                                             │
│  RESULTADO:                                                 │
│  ┌────────────────────────────────────────┐                 │
│  │  Valor: [_______] [pH units ▼]        │                 │
│  │                                        │                 │
│  │  Observaciones:                        │                 │
│  │  ┌────────────────────────────────┐   │                 │
│  │  │                                │   │                 │
│  │  └────────────────────────────────┘   │                 │
│  └────────────────────────────────────────┘                 │
│                                                             │
│  [Cancelar]              [Guardar Borrador]  [Completar ✓] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Client & product info display
- Specification ranges
- Multiple result types (numeric, text, boolean)
- Save draft capability
- Complete and submit

### 4. Result Entry Interface
```
┌─────────────────────────────────────────────────────────────┐
│  REGISTRO DE RESULTADOS                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tipo de entrada: [Numérico ▼]                              │
│                                                             │
│  Para ensayos numéricos:                                    │
│  Valor: [________]  Unidad: [________]                     │
│  Incertidumbre: ± [________]                               │
│                                                             │
│  Para ensayos de recuento (MB):                            │
│  UFC/g: [________]  [<10 | 10-100 | 100-1000 | >1000]      │
│                                                             │
│  Para ensayos sensoriales (ES):                            │
│  Atributo: [Olor ▼]                                         │
│  Puntuación: [1-5 scale]                                    │
│  Descripción: [________]                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5. Work Queue Management
```
┌─────────────────────────────────────────────────────────────┐
│  MI COLA DE TRABAJO                                         │
├─────────────────────────────────────────────────────────────┤
│  [En Proceso] [Pendientes] [Completados] [Todos]           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  #   │ Muestra  │ Ensayo      │ Inicio    │ Estado        │
│  ────┼──────────┼─────────────┼───────────┼───────────────│
│  1   │ ENT-1234 │ pH          │ 10:30     │ ● En Proceso  │
│  2   │ ENT-1235 │ Densidad    │ 11:00     │ ⏸ Pausado     │
│  3   │ ENT-1236 │ Humedad     │ --        │ ○ Pendiente   │
│                                                             │
│  Acciones: [Continuar] [Pausar] [Completar] [Reasignar]    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6. Performance Metrics
```
┌─────────────────────────────────────────────────────────────┐
│  MIS ESTADÍSTICAS                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ESTE MES:                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Ensayos         │  │ Eficiencia      │                  │
│  │ Completados     │  │                 │                  │
│  │                 │  │  ████████░░ 87% │                  │
│  │      127        │  │                 │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                             │
│  ┌────────────────────────────────────────┐                 │
│  │  ENSAYOS POR TIPO                      │                 │
│  │                                        │                 │
│  │  pH          ████████████████████ 45   │                 │
│  │  Densidad    ██████████████ 32         │                 │
│  │  Humedad     ██████████ 25             │                 │
│  │  Viscosidad  ████████ 20               │                 │
│  │  Otros       ██████ 15                 │                 │
│  └────────────────────────────────────────┘                 │
│                                                             │
│  TENDENCIA SEMANAL:                                         │
│  [Line chart showing completed tests per week]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Technician Dashboard
- Work summary cards
- Quick action buttons
- Recent activity feed
- Notifications/alerts

### Pending Tests
- Filter by area, priority, due date
- Search by sample or client
- Bulk operations
- Priority indicators

### Test Execution
- Guided result entry
- Specification validation
- Photo attachment
- Save draft capability

### Work Queue
- Drag-drop prioritization
- Status updates
- Pause/resume tests
- Reassign capability

### Performance Metrics
- Tests completed (daily/weekly/monthly)
- Efficiency rate
- Tests by type chart
- Trend analysis

## Acceptance Criteria
- [ ] Technician dashboard implemented
- [ ] Pending tests view with filtering
- [ ] Test execution form with validation
- [ ] Result entry for all test types (FQ, MB, ES)
- [ ] Work queue management interface
- [ ] Performance metrics dashboard
- [ ] Mobile-responsive design
- [ ] Real-time updates (optional)
- [ ] Role-based access control
- [ ] Keyboard navigation support

## Technical Notes
- Use HTMX for dynamic updates
- Responsive grid layout
- Offline form saving
- Keyboard shortcuts
- Print-friendly result forms
- Integration with equipment APIs

## Labels
`phase-4`, `testing`, `laboratory`, `ui/ux`, `frontend`

## Estimated Effort
**Story Points**: 13
**Time Estimate**: 5-6 days
