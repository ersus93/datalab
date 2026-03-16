# [Phase 8] Observabilidad: Logging Estructurado, Métricas & Alertas

**Labels:** `phase-8`, `devops`, `monitoring`, `backend`, `high-priority`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 5 días
**Depends on:** Todas las fases anteriores

---

## Descripción

En producción, cuando algo falla, la pregunta es: **¿cuándo ocurrió, qué estaba haciendo el usuario, y por qué falló?** Sin observabilidad adecuada, esa pregunta no tiene respuesta.

Esta issue implementa tres pilares de observabilidad para DataLab:

1. **Logging estructurado** — Logs en JSON con contexto rico (usuario, request ID, duración, etc.)
2. **Métricas de aplicación** — Contadores y tiempos de respuesta por endpoint, alertas cuando algo se degrada
3. **Health checks** — Endpoints que informan el estado real del sistema (BD, disco, servicios externos)

---

## Acceptance Criteria

### 1. Logging Estructurado (JSON)

```python
# app/core/logging/config.py
import structlog
import logging

def configure_logging(app):
    """
    En desarrollo: logs legibles por humanos (coloridos)
    En producción: logs JSON para ingestión por ELK/Datadog/CloudWatch
    """
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if app.config['ENV'] == 'production':
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Uso en cualquier módulo:
import structlog
log = structlog.get_logger()

# Con contexto rico:
log.info("entrada_creada", 
    entrada_id=123, 
    cliente_id=45, 
    user_id=current_user.id,
    duration_ms=45.2
)
```

#### Request Logging Middleware

```python
# app/core/logging/middleware.py
import time
import uuid
import structlog
from flask import request, g

log = structlog.get_logger()

def setup_request_logging(app):
    
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        # Bind request context para todos los logs de esta request
        structlog.contextvars.bind_contextvars(
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            user_id=getattr(current_user, 'id', None),
            ip=request.remote_addr
        )
        
        log.debug("request_started")
    
    @app.after_request
    def after_request(response):
        duration_ms = (time.time() - g.start_time) * 1000
        
        log.info("request_completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            content_length=response.content_length
        )
        
        # Agregar request ID a la respuesta (útil para soporte)
        response.headers['X-Request-ID'] = g.request_id
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        log.error("unhandled_exception",
            error_type=type(error).__name__,
            error_message=str(error),
            exc_info=True
        )
        # No exponer detalles internos al cliente
        return jsonify({"error": "Error interno del servidor"}), 500
```

- [ ] Configurar `structlog` con JSON en producción, consola colorida en desarrollo
- [ ] Middleware de request logging (duración, status code, user, request ID)
- [ ] Logs de eventos de negocio: creación de entradas, generación de informes, cambios de estado
- [ ] Logs de seguridad: login, logout, accesos denegados (integrado con issue-02)
- [ ] Rotación de archivos de log (máximo 50MB por archivo, 30 días de retención)
- [ ] Formato que pueda ser ingerido por ELK Stack o similar

### 2. Métricas con Flask-Metrics (Prometheus)

```python
# app/core/metrics/setup.py
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge

metrics = PrometheusMetrics.for_app_factory()

# Métricas de negocio custom
entradas_creadas = Counter(
    'datalab_entradas_created_total',
    'Total de entradas de muestras creadas',
    ['area', 'cliente_tipo']
)

ensayos_completados = Counter(
    'datalab_ensayos_completed_total',
    'Ensayos completados',
    ['area', 'resultado']  # resultado: conforme/no_conforme/pendiente
)

pdf_generation_duration = Histogram(
    'datalab_pdf_generation_seconds',
    'Tiempo de generación de PDF',
    ['report_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

pending_ensayos = Gauge(
    'datalab_pending_ensayos',
    'Ensayos pendientes en cola',
    ['area']
)

# Uso:
with pdf_generation_duration.labels(report_type='certificado').time():
    pdf_bytes = generate_pdf(informe)
```

#### Dashboard de Métricas (Grafana-ready)

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
```

- [ ] Instalar y configurar `prometheus-flask-exporter`
- [ ] Definir métricas custom de negocio (entradas, ensayos, PDFs)
- [ ] Exponer endpoint `/metrics` (protegido, solo acceso interno/admin)
- [ ] Archivo `docker-compose.monitoring.yml` con Prometheus + Grafana
- [ ] Dashboard de Grafana pre-configurado (exportar como JSON)
- [ ] Alertas básicas: tiempo de respuesta > 2s, errores 5xx > 1% de requests

### 3. Health Check Endpoints

```python
# app/core/health/routes.py
from flask import Blueprint, jsonify
import psutil
import time

health_bp = Blueprint('health', __name__)

@health_bp.get('/health')
def health_simple():
    """Endpoint simple para load balancer / uptime monitoring"""
    return jsonify({"status": "ok", "timestamp": time.time()})

@health_bp.get('/health/detailed')
@admin_required  # Solo administradores
def health_detailed():
    """Estado detallado de todos los subsistemas"""
    checks = {}
    overall_status = "healthy"
    
    # Base de datos
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "latency_ms": _db_latency()}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"
    
    # Disco
    disk = psutil.disk_usage('/')
    disk_pct = disk.percent
    checks["disk"] = {
        "status": "healthy" if disk_pct < 85 else "warning",
        "used_percent": disk_pct,
        "free_gb": round(disk.free / (1024**3), 2)
    }
    if disk_pct > 95:
        overall_status = "degraded"
    
    # Memoria
    mem = psutil.virtual_memory()
    checks["memory"] = {
        "status": "healthy" if mem.percent < 85 else "warning",
        "used_percent": mem.percent,
        "available_mb": round(mem.available / (1024**2))
    }
    
    # Email (si está configurado)
    checks["email"] = _check_email_service()
    
    return jsonify({
        "status": overall_status,
        "timestamp": time.time(),
        "version": app.config.get('APP_VERSION', 'unknown'),
        "checks": checks
    }), 200 if overall_status == "healthy" else 503
```

- [ ] Endpoint `/health` (simple, sin auth — para uptime monitoring)
- [ ] Endpoint `/health/detailed` (con auth admin — estado completo)
- [ ] Verificar: BD, disco, memoria, servicio de email
- [ ] Código HTTP 503 cuando el sistema está degradado (para alertas automáticas)
- [ ] Integrar con UptimeRobot o similar para notificaciones de caída

### 4. Alertas Configurables

```python
# app/core/alerting/alerts.py
class AlertRule:
    def __init__(self, name, condition_fn, severity, message_fn, cooldown_minutes=30):
        self.name = name
        self.condition_fn = condition_fn
        self.severity = severity  # 'warning' | 'critical'
        self.message_fn = message_fn
        self.cooldown_minutes = cooldown_minutes

ALERT_RULES = [
    AlertRule(
        name="high_response_time",
        condition_fn=lambda: get_p95_response_time() > 2000,  # ms
        severity="warning",
        message_fn=lambda: f"P95 respuesta: {get_p95_response_time()}ms (límite: 2000ms)"
    ),
    AlertRule(
        name="disk_space_critical",
        condition_fn=lambda: psutil.disk_usage('/').percent > 90,
        severity="critical",
        message_fn=lambda: f"Disco al {psutil.disk_usage('/').percent}%"
    ),
    AlertRule(
        name="ensayos_queue_backlog",
        condition_fn=lambda: get_pending_ensayos_count() > 200,
        severity="warning",
        message_fn=lambda: f"{get_pending_ensayos_count()} ensayos pendientes en cola"
    ),
]
```

- [ ] Sistema de alertas evaluado cada 5 minutos (APScheduler o Celery Beat)
- [ ] Canal de alerta: email al administrador
- [ ] Cooldown por alerta (no notificar la misma alerta más de 1 vez cada 30 min)
- [ ] Interfaz admin para ver alertas activas e historial

---

## Tareas

- [ ] Instalar `structlog`, `prometheus-flask-exporter`, `psutil`
- [ ] Configurar logging estructurado (desarrollo vs producción)
- [ ] Implementar middleware de request logging
- [ ] Definir y registrar métricas Prometheus custom
- [ ] Crear endpoints `/health` y `/health/detailed`
- [ ] Crear `docker-compose.monitoring.yml`
- [ ] Implementar sistema de alertas con APScheduler
- [ ] Documentar: cómo leer los logs, cómo interpretar las métricas

---

## Librerías

```txt
structlog==24.1.0
prometheus-flask-exporter==0.23.0
psutil==5.9.8
APScheduler==3.10.4
```

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 5 días

## Related Issues
- Phase 8 #02 - Security Hardening (eventos de seguridad en logs)
- Phase 8 #06 - CI/CD Pipeline (métricas usadas en deploy canary)
