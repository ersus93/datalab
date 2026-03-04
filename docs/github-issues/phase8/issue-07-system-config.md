# [Phase 8] Módulo de Configuración Avanzada del Sistema

**Labels:** `phase-8`, `backend`, `frontend`, `admin`, `configuration`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 5 días
**Depends on:** Phase 2 (Auth/Users), Phase 6 (RBAC)

---

## Descripción

Actualmente la configuración del sistema (parámetros operativos, plantillas de informes, umbrales de alertas, preferencias de usuario) está hardcodeada en el código o en archivos `.env`. Para una app de producción, el administrador del laboratorio debe poder ajustar el comportamiento del sistema sin tocar el código o reiniciar el servidor.

Esta issue implementa un **módulo de configuración completo** con:
1. Panel de administración para configuración del sistema
2. Preferencias por usuario (timezone, idioma, notificaciones)
3. Plantillas personalizables para informes oficiales
4. Gestión de copias de seguridad desde el panel

---

## Acceptance Criteria

### 1. Configuración Global del Sistema (Admin)

```python
# app/features/configuracion/domain/models.py
from enum import Enum

class ConfigDataType(Enum):
    STRING = 'string'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    JSON = 'json'
    TEXT = 'text'  # Para templates HTML/texto largo

class SystemConfig(db.Model):
    """
    Configuración del sistema almacenada en BD.
    Permite cambios en caliente sin reiniciar la aplicación.
    """
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.Enum(ConfigDataType), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50))  # 'laboratory', 'email', 'reports', 'security'
    is_sensitive = db.Column(db.Boolean, default=False)  # Ocultar en UI si es True
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def get_typed_value(self):
        """Retorna el valor con el tipo de dato correcto"""
        if self.data_type == ConfigDataType.BOOLEAN:
            return self.value.lower() == 'true'
        elif self.data_type == ConfigDataType.INTEGER:
            return int(self.value)
        elif self.data_type == ConfigDataType.JSON:
            return json.loads(self.value)
        return self.value
```

#### Configuraciones del Laboratorio

```python
# migrations/seed_system_config.py
LABORATORY_CONFIGS = [
    # Identidad
    {
        "key": "lab.nombre",
        "value": "Laboratorio de Química de Alimentos - ONIE",
        "data_type": "string",
        "description": "Nombre oficial del laboratorio (aparece en informes y reportes)",
        "category": "laboratory"
    },
    {
        "key": "lab.codigo",
        "value": "ONIE-LQA-001",
        "data_type": "string",
        "description": "Código identificador del laboratorio para informes oficiales",
        "category": "laboratory"
    },
    {
        "key": "lab.director",
        "value": "",
        "data_type": "string",
        "description": "Nombre del Director/Jefe del Laboratorio (firma en informes)",
        "category": "laboratory"
    },
    {
        "key": "lab.acreditacion",
        "value": "",
        "data_type": "string",
        "description": "Número de acreditación ISO 17025",
        "category": "laboratory"
    },
    
    # Operación
    {
        "key": "lab.dias_alerta_vencimiento",
        "value": "3",
        "data_type": "integer",
        "description": "Días de antelación para alertar sobre ensayos próximos a vencer",
        "category": "laboratory"
    },
    {
        "key": "lab.max_ensayos_por_tecnico",
        "value": "20",
        "data_type": "integer",
        "description": "Máximo de ensayos simultáneos asignables a un técnico",
        "category": "laboratory"
    },
    {
        "key": "lab.formato_lote",
        "value": "^[A-Z]-\\d{4}$",
        "data_type": "string",
        "description": "Expresión regular para validar formato de número de lote",
        "category": "laboratory"
    },
    
    # Sesiones y seguridad
    {
        "key": "security.session_timeout_minutes",
        "value": "60",
        "data_type": "integer",
        "description": "Minutos de inactividad antes de cerrar sesión automáticamente",
        "category": "security"
    },
    {
        "key": "security.max_login_attempts",
        "value": "5",
        "data_type": "integer",
        "description": "Intentos de login fallidos antes de bloquear la cuenta",
        "category": "security"
    },
    {
        "key": "security.require_2fa_for_admin",
        "value": "true",
        "data_type": "boolean",
        "description": "Requerir autenticación de dos factores para el rol Administrador",
        "category": "security"
    },
    
    # Email
    {
        "key": "email.from_address",
        "value": "noreply@laboratorio.cu",
        "data_type": "string",
        "description": "Dirección de correo origen para notificaciones del sistema",
        "category": "email"
    },
    {
        "key": "email.notify_overdue_enabled",
        "value": "true",
        "data_type": "boolean",
        "description": "Enviar notificaciones de ensayos vencidos",
        "category": "email"
    },
]
```

#### Config Manager (Cache en Memoria)

```python
# app/core/config/manager.py
class ConfigManager:
    """
    Caché en memoria de configuración del sistema.
    Se recarga automáticamente si la BD cambia.
    """
    _cache: dict = {}
    _last_loaded: datetime = None
    CACHE_TTL_SECONDS = 60
    
    @classmethod
    def get(cls, key: str, default=None):
        cls._maybe_reload()
        return cls._cache.get(key, default)
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        value = cls.get(key)
        if value is None:
            return default
        return str(value).lower() == 'true'
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        value = cls.get(key, default)
        return int(value)
    
    @classmethod
    def set(cls, key: str, value, data_type: str = 'string'):
        """Actualiza en BD e invalida caché"""
        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            config.value = str(value)
            config.updated_at = datetime.utcnow()
            config.updated_by_id = current_user.id
            db.session.commit()
            cls._last_loaded = None  # Forzar recarga del caché
    
    @classmethod
    def _maybe_reload(cls):
        if (cls._last_loaded is None or 
            (datetime.utcnow() - cls._last_loaded).seconds > cls.CACHE_TTL_SECONDS):
            cls._reload()
    
    @classmethod
    def _reload(cls):
        configs = SystemConfig.query.all()
        cls._cache = {c.key: c.get_typed_value() for c in configs}
        cls._last_loaded = datetime.utcnow()

# Uso en cualquier parte de la app:
from app.core.config.manager import ConfigManager

dias_alerta = ConfigManager.get_int('lab.dias_alerta_vencimiento', default=3)
require_2fa = ConfigManager.get_bool('security.require_2fa_for_admin', default=True)
```

### 2. Panel de Administración de Configuración (UI)

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️  Configuración del Sistema                  [Buscar config...] │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                   │
│ Categorías:  │  🔬 Laboratorio                                  │
│              │                                                   │
│ 🔬 Laboratorio│  Nombre del laboratorio                          │
│ 📧 Email     │  [Laboratorio de Química de Alimentos - ONIE    ] │
│ 🔒 Seguridad │  Nombre oficial para informes y reportes          │
│ 📊 Informes  │  ─────────────────────────────────────────────── │
│ 🔔 Alertas   │                                                   │
│              │  Código de laboratorio                            │
│              │  [ONIE-LQA-001                                  ] │
│              │  Aparece en el encabezado de informes oficiales   │
│              │  ─────────────────────────────────────────────── │
│              │                                                   │
│              │  Días de alerta por vencimiento                   │
│              │  [3                                             ] │
│              │  Días antes del vencimiento para alertar técnicos │
│              │                                                   │
│              │                           [Cancelar] [Guardar ✓] │
└──────────────┴──────────────────────────────────────────────────┘
```

- [ ] Panel con categorías en sidebar izquierdo
- [ ] Formulario dinámico según tipo de dato: text input, toggle switch, number input
- [ ] Campos sensibles (`is_sensitive=True`) muestran `••••••` con botón de revelar
- [ ] Historial de cambios: quién cambió qué y cuándo
- [ ] Botón "Restaurar valores por defecto" por categoría
- [ ] Búsqueda de configuraciones

### 3. Preferencias por Usuario

```python
# app/features/users/domain/preferences.py
class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # UI
    theme = db.Column(db.String(10), default='light')        # 'light' | 'dark' | 'auto'
    locale = db.Column(db.String(10), default='es')          # 'es' | 'es_CU' | 'en'
    timezone = db.Column(db.String(50), default='America/Havana')
    items_per_page = db.Column(db.Integer, default=25)       # 10 | 25 | 50 | 100
    
    # Notificaciones
    notify_overdue_ensayos = db.Column(db.Boolean, default=True)
    notify_new_assignment = db.Column(db.Boolean, default=True)
    notify_informe_approved = db.Column(db.Boolean, default=True)
    notify_by_email = db.Column(db.Boolean, default=True)
    notify_in_app = db.Column(db.Boolean, default=True)
    
    # Dashboard
    dashboard_default_period = db.Column(db.String(10), default='month')  # 'week' | 'month' | 'year'
    dashboard_default_area = db.Column(db.String(10))  # Filtrar por área (FQ, MB, ES, None=todas)
```

```
┌─────────────────────────────────────────────────────────────────┐
│ 👤 Mis Preferencias                                              │
├─────────────────────────────────────────────────────────────────┤
│ Interfaz                                                         │
│   Tema:       ○ Claro  ○ Oscuro  ● Automático (sistema)        │
│   Idioma:     [Español (Cuba)           ▼]                      │
│   Zona horaria:[America/Havana          ▼]                      │
│   Filas/página:[25                      ▼]                      │
│                                                                  │
│ Notificaciones                                                   │
│   [✓] Ensayos próximos a vencer                                 │
│   [✓] Nuevas asignaciones                                        │
│   [ ] Informe aprobado                                           │
│   [✓] Notificar por email                                        │
│   [✓] Notificar en la aplicación                                 │
│                                                                  │
│ Dashboard por defecto                                            │
│   Período: ● Mes  ○ Semana  ○ Año                              │
│   Área:    [Todas                       ▼]                      │
│                                                                  │
│                                      [Guardar preferencias]     │
└─────────────────────────────────────────────────────────────────┘
```

- [ ] Modelo `UserPreferences` con valores por defecto
- [ ] Página de perfil con sección de preferencias
- [ ] Respetar `timezone` en todas las fechas mostradas al usuario
- [ ] Guardar `theme` en BD (además de localStorage para persistencia multi-dispositivo)

### 4. Gestión de Copias de Seguridad (Admin)

```python
# app/features/admin/backups/service.py
import subprocess
from datetime import datetime
import os

class BackupService:
    BACKUP_DIR = '/var/backups/datalab'
    RETENTION_DAYS = 30
    
    def create_database_backup(self) -> str:
        """Crea dump de PostgreSQL y retorna la ruta del archivo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"datalab_db_{timestamp}.sql.gz"
        filepath = os.path.join(self.BACKUP_DIR, filename)
        
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        
        result = subprocess.run([
            'pg_dump',
            '--dbname', current_app.config['DATABASE_URL'],
            '--compress=9',
            '--file', filepath
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Backup falló: {result.stderr}")
        
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        # Registrar en BD
        BackupRecord(
            filename=filename,
            size_mb=round(size_mb, 2),
            created_by_id=current_user.id,
            status='success'
        ).save()
        
        self._cleanup_old_backups()
        return filepath
    
    def list_backups(self) -> list[dict]:
        """Lista backups disponibles"""
        return BackupRecord.query\
            .order_by(BackupRecord.created_at.desc())\
            .limit(50).all()
    
    def _cleanup_old_backups(self):
        """Eliminar backups más antiguos de RETENTION_DAYS"""
        cutoff = datetime.now() - timedelta(days=self.RETENTION_DAYS)
        old_backups = BackupRecord.query.filter(BackupRecord.created_at < cutoff).all()
        for backup in old_backups:
            try:
                os.remove(os.path.join(self.BACKUP_DIR, backup.filename))
                db.session.delete(backup)
            except FileNotFoundError:
                db.session.delete(backup)
        db.session.commit()
```

```
┌─────────────────────────────────────────────────────────────────┐
│ 💾 Copias de Seguridad                    [+ Crear copia ahora] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Próxima copia automática: mañana a las 02:00                    │
│ Retención: 30 días                                               │
│                                                                  │
│ Fecha              Tamaño    Creado por     Estado   Acciones   │
│ 2026-03-03 02:00   12.4 MB   Sistema        ✅ OK    [⬇] [🗑]  │
│ 2026-03-02 02:00   12.3 MB   Sistema        ✅ OK    [⬇] [🗑]  │
│ 2026-03-01 15:42   12.1 MB   Admin          ✅ OK    [⬇] [🗑]  │
│ ...                                                              │
└─────────────────────────────────────────────────────────────────┘
```

- [ ] Servicio de backup de PostgreSQL con `pg_dump`
- [ ] Tarea Celery periódica: backup automático diario a las 2am
- [ ] Panel de admin: listar backups, descargar, eliminar, crear manual
- [ ] Retención automática: eliminar backups > 30 días
- [ ] Notificación al admin si el backup automático falla

### 5. Registro de Auditoría de Configuración

```python
# Cada cambio de configuración se registra:
class ConfigAuditLog(db.Model):
    __tablename__ = 'config_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    reason = db.Column(db.String(500))  # Motivo del cambio (opcional)
```

- [ ] Tabla `config_audit_log` con registro de todos los cambios
- [ ] Vista en panel admin de historial de configuración
- [ ] Campo opcional "Motivo del cambio" al editar configuración

---

## Tareas

- [ ] Crear modelos `SystemConfig`, `UserPreferences`, `BackupRecord`, `ConfigAuditLog`
- [ ] Crear migración con seed de configuraciones por defecto del laboratorio
- [ ] Implementar `ConfigManager` con caché en memoria
- [ ] Crear routes y templates del panel de configuración (admin only)
- [ ] Crear página de preferencias de usuario
- [ ] Integrar `timezone` de preferencias en display de fechas (Jinja2 filter)
- [ ] Implementar `BackupService` con backup automático via Celery
- [ ] Panel de backups con download/delete
- [ ] Tests unitarios para `ConfigManager` y `BackupService`

---

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 5 días

## Related Issues
- Phase 1 #05 - Authentication (usuarios y roles)
- Phase 6 #04 - RBAC (solo admin puede acceder a config del sistema)
- Phase 8 #03 - Observability (logs de cambios de configuración)
- Phase 8 #04 - Cache (ConfigManager usa caché)
