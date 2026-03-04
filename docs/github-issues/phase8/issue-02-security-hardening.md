# [Phase 8] Seguridad Avanzada & Hardening

**Labels:** `phase-8`, `security`, `backend`, `critical`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 5 días
**Depends on:** Phase 1 (Auth), Phase 2 (RBAC/Roles), Phase 6 (RBAC avanzado)

---

## Descripción

Implementar una capa de seguridad completa y endurecida para producción. Las fases anteriores implementaron autenticación básica y RBAC, pero un sistema LIMS con datos de trazabilidad legal (ISO 17025) requiere protecciones adicionales que van más allá de un login con contraseña.

Esta issue cubre: cabeceras de seguridad HTTP, protección contra ataques comunes, gestión segura de secretos, política de contraseñas robusta, 2FA opcional, y un sistema de detección de actividad sospechosa.

---

## Acceptance Criteria

### 1. Cabeceras HTTP de Seguridad

```python
# app/core/security/headers.py
from flask_talisman import Talisman

def configure_security_headers(app):
    Talisman(
        app,
        force_https=True,                           # Redirect HTTP → HTTPS
        strict_transport_security=True,
        strict_transport_security_max_age=31536000, # 1 año
        strict_transport_security_include_subdomains=True,
        content_security_policy={
            'default-src': "'self'",
            'script-src': [
                "'self'",
                'cdn.jsdelivr.net',                 # Bootstrap
                'cdn.plot.ly',                      # Plotly
                "'nonce-{nonce}'"                   # Inline scripts con nonce
            ],
            'style-src': [
                "'self'",
                'cdn.jsdelivr.net',
                "'unsafe-inline'"                   # Tailwind / Bootstrap inline
            ],
            'img-src': "'self' data:",
            'font-src': "'self' cdnjs.cloudflare.com",
            'frame-ancestors': "'none'",            # Anti-clickjacking
            'base-uri': "'self'",
            'form-action': "'self'"
        },
        referrer_policy='strict-origin-when-cross-origin',
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'"
        },
        x_content_type_options=True,    # nosniff
        x_xss_protection=True,
        x_frame_options='DENY'
    )
```

- [ ] Configurar `flask-talisman` con CSP estricta
- [ ] Verificar con [securityheaders.com](https://securityheaders.com) → mínimo grado "A"
- [ ] Agregar `X-Request-ID` header para trazabilidad de peticiones

### 2. Política de Contraseñas Robusta

```python
# app/core/security/password_policy.py
import re
from dataclasses import dataclass

@dataclass
class PasswordPolicy:
    min_length: int = 10
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    max_length: int = 128
    
    # Prevención de contraseñas comunes
    COMMON_PASSWORDS_FILE = 'app/core/security/common_passwords.txt'
    
    def validate(self, password: str) -> list[str]:
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Mínimo {self.min_length} caracteres")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Debe contener al menos una mayúscula")
        
        if self.require_digit and not re.search(r'\d', password):
            errors.append("Debe contener al menos un número")
        
        if self.require_special and not re.search(
            f'[{re.escape(self.special_chars)}]', password
        ):
            errors.append("Debe contener al menos un carácter especial")
        
        if self._is_common_password(password):
            errors.append("Esta contraseña es demasiado común. Elige otra")
        
        return errors
    
    def _is_common_password(self, password: str) -> bool:
        # Lista de top 10,000 contraseñas comunes
        try:
            with open(self.COMMON_PASSWORDS_FILE) as f:
                return password.lower() in f.read().splitlines()
        except FileNotFoundError:
            return False
```

- [ ] Implementar `PasswordPolicy` con validación completa
- [ ] Aplicar en formularios de creación y cambio de contraseña
- [ ] Mostrar indicador de fortaleza en tiempo real (JavaScript)
- [ ] Historial de contraseñas (no repetir las últimas 5)

### 3. Autenticación de Dos Factores (2FA) — Opcional por usuario

```python
# app/features/auth/domain/totp.py
import pyotp
import qrcode
from io import BytesIO
import base64

class TOTPService:
    APP_NAME = "DataLab ONIE"
    
    def generate_secret(self) -> str:
        return pyotp.random_base32()
    
    def get_qr_code(self, username: str, secret: str) -> str:
        """Retorna QR como base64 PNG para mostrar en UI"""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(username, issuer_name=self.APP_NAME)
        
        img = qrcode.make(uri)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify(self, secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # ±30 segundos
    
    def generate_backup_codes(self, count: int = 8) -> list[str]:
        """Códigos de respaldo de un solo uso"""
        import secrets
        return [secrets.token_hex(4).upper() for _ in range(count)]
```

- [ ] Campo `totp_secret` en modelo User (encriptado en BD)
- [ ] Campo `totp_enabled` (boolean)
- [ ] Campo `backup_codes` (JSON array, hasheados)
- [ ] Flujo de setup: activar 2FA → mostrar QR → verificar código → guardar
- [ ] Flujo de login: si 2FA activo, pedir código tras contraseña correcta
- [ ] Códigos de respaldo de emergencia (8 códigos de un solo uso)
- [ ] Forzar 2FA para rol `admin` (configurable)

### 4. Protección Anti-Fuerza Bruta

```python
# app/core/security/brute_force.py
from flask import request
from datetime import datetime, timedelta
from app.core.infrastructure.cache import cache

class BruteForceProtection:
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    
    def record_failed_attempt(self, identifier: str):
        """identifier puede ser username o IP"""
        key = f"failed_login:{identifier}"
        attempts = cache.get(key) or 0
        cache.set(key, attempts + 1, timeout=int(self.LOCKOUT_DURATION.total_seconds()))
    
    def is_locked(self, identifier: str) -> bool:
        key = f"failed_login:{identifier}"
        attempts = cache.get(key) or 0
        return attempts >= self.MAX_ATTEMPTS
    
    def get_lockout_remaining(self, identifier: str) -> int:
        """Segundos restantes del bloqueo"""
        key = f"failed_login:{identifier}"
        return cache.ttl(key) or 0
    
    def reset(self, identifier: str):
        cache.delete(f"failed_login:{identifier}")
```

- [ ] Bloqueo por IP y por username tras 5 intentos fallidos
- [ ] Lockout de 15 minutos con mensaje claro al usuario
- [ ] CAPTCHA (hCaptcha / simple math) tras 3 intentos fallidos
- [ ] Notificación por email al usuario cuando su cuenta es bloqueada
- [ ] Panel admin para desbloquear cuentas manualmente

### 5. Gestión Segura de Secretos

```python
# config/secrets.py
import os
from cryptography.fernet import Fernet

class SecretsManager:
    """
    En producción, usar HashiCorp Vault o AWS Secrets Manager.
    En desarrollo, variables de entorno con .env (nunca en git).
    """
    
    REQUIRED_SECRETS = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL',
        'MAIL_PASSWORD',
    ]
    
    @classmethod
    def validate_env(cls):
        missing = [s for s in cls.REQUIRED_SECRETS if not os.environ.get(s)]
        if missing:
            raise RuntimeError(
                f"Secretos requeridos no encontrados: {', '.join(missing)}\n"
                f"Copia .env.example a .env y configura los valores."
            )
    
    @classmethod
    def get_field_encryption_key(cls) -> bytes:
        """Clave para encriptar campos sensibles en BD (ej: totp_secret)"""
        key = os.environ.get('FIELD_ENCRYPTION_KEY')
        if not key:
            raise RuntimeError("FIELD_ENCRYPTION_KEY no configurada")
        return key.encode()

# Encriptación de campos sensibles en modelos
class EncryptedField:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
    
    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()
    
    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()
```

- [ ] Crear `.env.example` con todas las variables necesarias (sin valores reales)
- [ ] Validación en startup: la app no arranca si faltan secretos críticos
- [ ] Encriptar campos sensibles en BD (`totp_secret`, datos PII si aplica)
- [ ] Documentar proceso de rotación de claves
- [ ] Configurar pre-commit hook para evitar que secretos lleguen a git (`detect-secrets`)

### 6. SQL Injection & XSS — Auditoría y Hardening

```python
# Asegurar que TODOS los queries usan parámetros ORM, nunca f-strings:

# ❌ NUNCA hacer esto:
db.execute(f"SELECT * FROM clientes WHERE nombre = '{nombre}'")

# ✅ Siempre usar ORM o parámetros:
Cliente.query.filter(Cliente.nombre == nombre).all()
db.execute(text("SELECT * FROM clientes WHERE nombre = :nombre"), {"nombre": nombre})
```

- [ ] Auditoría de código: grep por concatenación de strings en queries
- [ ] Revisar todos los templates Jinja2: asegurar que variables pasan por `{{ var }}` (auto-escaped) y no `{{ var | safe }}` salvo casos justificados
- [ ] Configurar `flask-wtf` CSRF en TODOS los formularios (verificar que no hay excepciones no justificadas)
- [ ] Sanitizar inputs de texto libre (observaciones, notas) con `bleach`

### 7. Detección de Actividad Sospechosa

```python
# app/core/security/anomaly_detection.py
class SecurityEventLogger:
    """Registra eventos de seguridad para revisión humana"""
    
    SUSPICIOUS_EVENTS = [
        'multiple_failed_logins',
        'permission_denied_repeated',
        'unusual_download_volume',
        'login_from_new_ip',
        'bulk_delete_attempt',
        'admin_action_outside_hours',
    ]
    
    def log_event(self, event_type: str, user_id: int, details: dict):
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.session.add(event)
        db.session.commit()
        
        # Si es crítico, notificar al admin
        if event_type in ['bulk_delete_attempt', 'admin_action_outside_hours']:
            self._notify_admin(event)
```

- [ ] Modelo `SecurityEvent` en BD
- [ ] Detectar: múltiples logins fallidos, acceso desde nueva IP, descargas masivas inusuales
- [ ] Panel de eventos de seguridad para admin
- [ ] Email de alerta al admin para eventos críticos

---

## Tareas

- [ ] Instalar y configurar `flask-talisman` (cabeceras HTTP)
- [ ] Implementar `PasswordPolicy` y conectar a formularios
- [ ] Implementar 2FA con `pyotp` y `qrcode`
- [ ] Implementar protección anti-fuerza bruta con Flask-Cache + Redis
- [ ] Crear `SecretsManager` y validación de entorno en startup
- [ ] Auditar queries y templates para SQL Injection / XSS
- [ ] Implementar `SecurityEventLogger` y panel admin
- [ ] Configurar `detect-secrets` como pre-commit hook
- [ ] Ejecutar OWASP ZAP en entorno de staging y resolver hallazgos críticos/altos
- [ ] Documentar política de seguridad en `docs/SECURITY.md`

---

## Librerías

```txt
flask-talisman==1.1.0
pyotp==2.9.0
qrcode[pil]==7.4.2
bleach==6.1.0
detect-secrets==1.4.0
cryptography==42.0.0
```

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 5 días

## Related Issues
- Phase 1 #05 - Authentication System (base sobre la que construir)
- Phase 6 #04 - RBAC (permisos que esta issue protege)
- Phase 8 #03 - Observability (logs de seguridad integrados en sistema de logging)
