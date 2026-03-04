# [Phase 8] Caché Inteligente & Optimización de Rendimiento

**Labels:** `phase-8`, `performance`, `backend`, `database`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 5 días
**Depends on:** Phase 5 (Dashboard/Reporting), Phase 4 (Test Management)

---

## Descripción

El sistema DataLab maneja consultas complejas sobre datos de laboratorio que se ejecutan repetidamente: el dashboard se recarga constantemente, las listas de entradas/ensayos se paginan y filtran, y los informes se generan en PDF con queries pesadas.

Sin optimización, al escalar a 50+ usuarios simultáneos el sistema se volverá lento. Esta issue implementa estrategias de caché, optimización de queries y gestión de tareas pesadas en background para garantizar tiempos de respuesta < 500ms en P95.

---

## Acceptance Criteria

### 1. Caché con Redis (Flask-Caching)

```python
# app/core/cache/setup.py
from flask_caching import Cache

cache = Cache()

def configure_cache(app):
    cache.init_app(app, config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': app.config['REDIS_URL'],
        'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutos por defecto
        'CACHE_KEY_PREFIX': 'datalab:'
    })
```

#### Estrategia de Caché por Tipo de Dato

```python
# app/features/dashboard/application/use_cases.py
from app.core.cache.setup import cache

class ObtenerKPIsDashboardUseCase:
    """
    KPIs del dashboard: caché de 5 minutos.
    Son datos agregados costosos de calcular pero toleran 5 min de desfase.
    """
    
    @cache.cached(timeout=300, key_prefix=lambda: f"dashboard_kpis_{current_user.id}")
    def execute(self) -> DashboardKPIsDTO:
        return DashboardKPIsDTO(
            pendientes_fq=self._count_pendientes('FQ'),
            pendientes_mb=self._count_pendientes('MB'),
            pendientes_es=self._count_pendientes('ES'),
            entradas_hoy=self._count_entradas_hoy(),
            informes_mes=self._count_informes_mes()
        )

class ListarEnsayosUseCase:
    """
    Catálogo de ensayos: caché de 1 hora.
    Datos muy estables, raramente cambian.
    """
    
    @cache.cached(timeout=3600, key_prefix='catalogo_ensayos')
    def execute(self) -> list[EnsayoDTO]:
        return [EnsayoDTO.from_model(e) for e in Ensayo.query.filter_by(activo=True).all()]


# Invalidación de caché cuando los datos cambian:
class CrearEntradaUseCase:
    def execute(self, cmd: CrearEntradaCommand) -> EntradaDTO:
        entrada = self._create_entrada(cmd)
        
        # Invalidar caché del dashboard (los KPIs han cambiado)
        cache.delete_memoized(ObtenerKPIsDashboardUseCase.execute)
        cache.delete(f"dashboard_kpis_{cmd.user_id}")
        
        return EntradaDTO.from_model(entrada)
```

- [ ] Instalar y configurar `flask-caching` con Redis
- [ ] Caché de KPIs del dashboard (5 minutos, por usuario para respetar RBAC)
- [ ] Caché de catálogos estáticos: áreas, ensayos, ramas, provincias (1 hora)
- [ ] Caché de lista de clientes para dropdowns/autocomplete (10 minutos)
- [ ] Invalidación correcta: cuando se modifica un dato, invalidar su caché
- [ ] Fallback graceful si Redis no está disponible (sin caché, sin crash)

### 2. Optimización de Queries con SQLAlchemy

```python
# Problema típico: N+1 queries
# ❌ MAL — genera 1 query por cada entrada para cargar el cliente:
entradas = Entrada.query.all()
for e in entradas:
    print(e.cliente.nombre)  # Query por cada iteración

# ✅ BIEN — joinedload trae todo en 1-2 queries:
entradas = Entrada.query\
    .options(
        joinedload(Entrada.cliente),
        joinedload(Entrada.producto),
        joinedload(Entrada.detalles_ensayos).joinedload(DetalleEnsayo.ensayo)
    )\
    .filter(Entrada.status == 'EN_PROCESO')\
    .all()

# Para listas grandes, usar selectinload (más eficiente que joinedload en colecciones):
entradas = Entrada.query\
    .options(
        selectinload(Entrada.detalles_ensayos)
    )\
    .paginate(page=page, per_page=25)
```

#### Índices de Base de Datos

```python
# En los modelos SQLAlchemy, agregar índices en campos frecuentemente filtrados:
class Entrada(Base):
    __tablename__ = 'entradas'
    __table_args__ = (
        Index('ix_entradas_status', 'status'),
        Index('ix_entradas_cliente_fecha', 'cliente_id', 'fech_entrada'),
        Index('ix_entradas_lote', 'lote'),  # Búsquedas por número de lote
    )
    
class DetalleEnsayo(Base):
    __tablename__ = 'detalles_ensayos'
    __table_args__ = (
        Index('ix_detalles_area_status', 'area', 'status'),
        Index('ix_detalles_entrada', 'entrada_id'),
        Index('ix_detalles_tecnico_status', 'tecnico_id', 'status'),
    )
```

#### Query Profiling

```python
# app/core/database/profiling.py
from sqlalchemy import event
import time

class QueryProfiler:
    """En desarrollo: loguea queries lentas"""
    
    SLOW_QUERY_THRESHOLD_MS = 100
    
    def __init__(self, engine):
        self.queries = []
        
        @event.listens_for(engine, "before_cursor_execute")
        def before_execute(conn, cursor, statement, params, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_execute(conn, cursor, statement, params, context, executemany):
            duration_ms = (time.time() - conn.info['query_start_time'].pop()) * 1000
            
            if duration_ms > self.SLOW_QUERY_THRESHOLD_MS:
                log.warning("slow_query_detected",
                    duration_ms=round(duration_ms, 2),
                    statement=statement[:200]  # Primeros 200 chars
                )
```

- [ ] Auditar y resolver todos los N+1 queries (usar `flask-debugtoolbar` en desarrollo)
- [ ] Agregar índices en columnas de filtros frecuentes (status, area, cliente_id, fecha)
- [ ] Activar `QueryProfiler` en desarrollo para detectar queries lentas (>100ms)
- [ ] Implementar paginación server-side en TODAS las listas (nunca cargar todos los registros)
- [ ] Usar `selectinload` / `joinedload` apropiadamente para relaciones

### 3. Tareas Pesadas en Background (Celery)

```python
# app/core/tasks/setup.py
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['REDIS_URL'],
        broker=app.config['REDIS_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Tareas que NO deben bloquear el request:
@celery.task(bind=True, max_retries=3)
def generate_pdf_report_task(self, informe_id: int, user_id: int):
    """
    Generación de PDF en background.
    El usuario ve un spinner, recibe notificación cuando está listo.
    """
    try:
        informe = Informe.query.get(informe_id)
        pdf_bytes = PDFGenerator().generate(informe)
        
        # Guardar en storage
        filename = f"informe_{informe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        storage.save(filename, pdf_bytes)
        
        # Actualizar informe con URL del PDF
        informe.pdf_filename = filename
        informe.pdf_generated_at = datetime.utcnow()
        db.session.commit()
        
        # Notificar al usuario
        notify_user(user_id, f"Informe #{informe_id} listo para descargar", 
                   url=url_for('informes.download', id=informe_id))
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # Reintentar en 60s

@celery.task
def send_overdue_reminders():
    """Recordatorios de ensayos vencidos — ejecutar cada día a las 8am"""
    overdue = DetalleEnsayo.query.filter(
        DetalleEnsayo.fecha_limite < datetime.utcnow(),
        DetalleEnsayo.status.in_(['PENDIENTE', 'EN_PROCESO'])
    ).all()
    
    for ensayo in overdue:
        notify_technician(ensayo.tecnico_id, f"Ensayo #{ensayo.id} vencido")
```

```python
# Configuración de tareas periódicas:
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'send-overdue-reminders': {
        'task': 'app.core.tasks.send_overdue_reminders',
        'schedule': crontab(hour=8, minute=0)  # Cada día a las 8am
    },
    'cleanup-old-temp-files': {
        'task': 'app.core.tasks.cleanup_temp_files',
        'schedule': crontab(hour=2, minute=0, day_of_week=0)  # Domingos 2am
    },
    'refresh-dashboard-cache': {
        'task': 'app.core.tasks.refresh_dashboard_cache',
        'schedule': 300  # Cada 5 minutos
    }
}
```

- [ ] Configurar Celery con Redis como broker
- [ ] Mover generación de PDF a tarea background (`generate_pdf_report_task`)
- [ ] Mover envío de emails a tarea background
- [ ] Tarea periódica: recordatorios de ensayos vencidos (8am diario)
- [ ] Tarea periódica: limpieza de archivos temporales (domingos 2am)
- [ ] UI de estado de tareas: el usuario puede ver si su PDF está generándose
- [ ] Flower (UI de Celery) disponible para admin en `/admin/celery`

### 4. Compresión y Assets Optimizados

```python
# app/core/compression.py
from flask_compress import Compress

def configure_compression(app):
    Compress(app)
    # Comprimir respuestas > 500 bytes con gzip
    app.config['COMPRESS_MIN_SIZE'] = 500
    app.config['COMPRESS_LEVEL'] = 6  # Balance entre velocidad y compresión
```

```nginx
# Configuración Nginx para assets estáticos:
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip_static on;
}
```

- [ ] Activar `flask-compress` para respuestas HTTP
- [ ] Configurar Nginx con cache de assets estáticos (1 año + immutable)
- [ ] Minificar CSS y JS en el build de producción
- [ ] Lazy loading de imágenes y gráficos Plotly (cargar al hacer scroll)
- [ ] Implementar paginación virtual para tablas muy largas (>1000 filas)

---

## Métricas de Éxito

| Métrica | Antes | Objetivo |
|---------|-------|----------|
| Tiempo de carga dashboard | ~3s | <1s |
| Generación PDF (síncrona) | 5-15s (bloquea) | Background (respuesta inmediata) |
| Lista entradas (100 registros) | ~800ms | <200ms |
| Búsqueda global | ~1.5s | <300ms |
| P95 respuesta bajo 50 usuarios | N/A | <500ms |

---

## Tareas

- [ ] Instalar `flask-caching`, `celery`, `redis`, `flask-compress`
- [ ] Configurar Redis para caché y broker de Celery
- [ ] Implementar caché de KPIs y catálogos
- [ ] Auditar N+1 queries y resolverlos
- [ ] Agregar índices de BD en campos frecuentemente filtrados
- [ ] Mover PDF y emails a tareas Celery background
- [ ] Configurar tareas periódicas con Celery Beat
- [ ] Prueba de carga con `locust` o `k6` (50 usuarios simultáneos)
- [ ] Documentar arquitectura de caché en `docs/architecture/caching.md`

---

## Librerías

```txt
flask-caching==2.1.0
celery==5.3.6
redis==5.0.1
flask-compress==1.14
flower==2.0.1        # UI para monitorear Celery
```

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 5 días

## Related Issues
- Phase 5 #03 - Analytics Dashboard (caché de KPIs)
- Phase 5 #02 - PDF Generation (mover a Celery)
- Phase 6 #03 - Notifications (usar Celery para enviar notificaciones async)
- Phase 8 #03 - Observability (métricas de caché en Prometheus)
