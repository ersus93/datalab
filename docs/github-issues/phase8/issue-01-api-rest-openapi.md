# [Phase 8] API REST Completa + Documentación OpenAPI

**Labels:** `phase-8`, `api`, `backend`, `documentation`, `high-priority`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 6 días
**Depends on:** Todas las fases anteriores (features implementadas)

---

## Descripción

Exponer toda la funcionalidad del sistema como una **API REST versionada** con documentación OpenAPI 3.0 automática. Esto permite:

1. **Integración futura** con sistemas externos (ERP, sistemas de facturación, equipos de laboratorio).
2. **Clientes móviles** — si en el futuro se construye una app nativa, tiene la API lista.
3. **Testing programático** — los tests de integración pueden hacer llamadas reales a la API.
4. **Transparencia** — el equipo puede explorar y probar endpoints desde Swagger UI.

La arquitectura hexagonal ya existente facilita esto enormemente: los Use Cases de la Application Layer se convierten directamente en endpoints REST sin tocar el Domain.

---

## Acceptance Criteria

### Estructura de la API

- [ ] API versionada bajo `/api/v1/`
- [ ] Swagger UI accesible en `/api/docs` (solo en entornos no-producción o con auth de admin)
- [ ] Esquema OpenAPI descargable en `/api/openapi.json`
- [ ] Autenticación JWT para todos los endpoints de la API (separado de la sesión web)
- [ ] Respuestas estandarizadas con envelope JSON

### Endpoints Requeridos

#### Autenticación
```
POST   /api/v1/auth/login          → JWT token + refresh token
POST   /api/v1/auth/refresh        → renovar token
POST   /api/v1/auth/logout         → invalidar token
GET    /api/v1/auth/me             → perfil del usuario actual
```

#### Clientes
```
GET    /api/v1/clientes            → lista paginada (filtros: nombre, codigo, activo)
POST   /api/v1/clientes            → crear cliente
GET    /api/v1/clientes/{id}       → detalle
PUT    /api/v1/clientes/{id}       → actualizar
DELETE /api/v1/clientes/{id}       → eliminar (soft delete)
GET    /api/v1/clientes/{id}/fabricas   → fábricas del cliente
GET    /api/v1/clientes/{id}/entradas   → entradas del cliente
```

#### Entradas (Muestras)
```
GET    /api/v1/entradas            → lista paginada (filtros: estado, area, fecha, cliente)
POST   /api/v1/entradas            → crear entrada
GET    /api/v1/entradas/{id}       → detalle completo con ensayos
PUT    /api/v1/entradas/{id}       → actualizar
PATCH  /api/v1/entradas/{id}/status → cambiar estado
GET    /api/v1/entradas/{id}/ensayos → ensayos asignados
```

#### Ensayos
```
GET    /api/v1/ensayos                    → catálogo
GET    /api/v1/detalles-ensayos           → asignaciones (filtros: estado, area, tecnico)
POST   /api/v1/detalles-ensayos           → asignar ensayo a entrada
PATCH  /api/v1/detalles-ensayos/{id}/resultado → registrar resultado
PATCH  /api/v1/detalles-ensayos/{id}/status    → cambiar estado
```

#### Informes
```
GET    /api/v1/informes            → lista de informes
POST   /api/v1/informes            → generar informe
GET    /api/v1/informes/{id}       → detalle
GET    /api/v1/informes/{id}/pdf   → descargar PDF (stream)
PATCH  /api/v1/informes/{id}/status → cambiar estado (borrador/final)
```

#### Dashboard / Analytics
```
GET    /api/v1/dashboard/kpis      → métricas principales (pendientes por área, etc.)
GET    /api/v1/dashboard/trends    → tendencias temporales
GET    /api/v1/dashboard/areas     → resumen por área de laboratorio
```

### Formato de Respuesta Estándar

```python
# Éxito con datos
{
    "success": true,
    "data": { ... },
    "meta": {
        "page": 1,
        "per_page": 25,
        "total": 156,
        "pages": 7
    }
}

# Éxito sin datos (creación/actualización)
{
    "success": true,
    "data": { ... },
    "message": "Cliente creado exitosamente"
}

# Error
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "El campo 'nombre' es requerido",
        "details": {
            "nombre": ["Este campo no puede estar vacío"]
        }
    }
}
```

### Implementación Técnica

```python
# app/features/clientes/infrastructure/api/routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.features.clientes.application.use_cases import ListarClientesUseCase
from app.core.api.decorators import permission_required, paginate

clientes_api_bp = Blueprint('clientes_api', __name__, url_prefix='/api/v1/clientes')

@clientes_api_bp.get('/')
@jwt_required()
@permission_required('view_clientes')
@paginate
def list_clientes(pagination):
    use_case = ListarClientesUseCase()
    filters = {
        'nombre': request.args.get('nombre'),
        'activo': request.args.get('activo', type=bool)
    }
    result = use_case.execute(filters=filters, **pagination)
    return jsonify({
        "success": True,
        "data": [c.to_dict() for c in result.items],
        "meta": result.pagination_meta()
    })
```

### Paginación y Filtros

```python
# app/core/api/pagination.py
class PaginationParams:
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 25
    MAX_PER_PAGE = 100
    
    def __init__(self, request):
        self.page = request.args.get('page', self.DEFAULT_PAGE, type=int)
        self.per_page = min(
            request.args.get('per_page', self.DEFAULT_PER_PAGE, type=int),
            self.MAX_PER_PAGE
        )
        self.sort_by = request.args.get('sort_by', 'id')
        self.sort_dir = request.args.get('sort_dir', 'asc')
```

### JWT Configuration

```python
# config/auth.py
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']          # Rotado periódicamente
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
JWT_ALGORITHM = 'HS256'
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# En endpoints sensibles:
@clientes_api_bp.post('/')
@limiter.limit("10 per minute")
@jwt_required()
def create_cliente():
    ...
```

### Documentación OpenAPI (Flasgger / Flask-OpenAPI3)

```python
# Usar decoradores para auto-generar documentación
from flask_openapi3 import OpenAPI, Tag

app = OpenAPI(__name__, info=info)

class ClienteQuery(BaseModel):
    nombre: Optional[str] = Field(None, description="Filtrar por nombre")
    activo: Optional[bool] = Field(None, description="Solo clientes activos")
    page: int = Field(1, ge=1)
    per_page: int = Field(25, ge=1, le=100)

@app.get('/api/v1/clientes', tags=[clientes_tag], responses={200: ClienteListResponse})
def list_clientes(query: ClienteQuery):
    """Lista todos los clientes con filtros y paginación"""
    ...
```

---

## Tareas

- [ ] Instalar y configurar `flask-jwt-extended` y `flask-openapi3` (o Flasgger)
- [ ] Crear módulo `app/core/api/` con decoradores, paginación y respuestas estándar
- [ ] Implementar endpoint de autenticación JWT
- [ ] Exponer endpoints de Clientes, Fabricas, Productos
- [ ] Exponer endpoints de Entradas y Detalles de Ensayos
- [ ] Exponer endpoints de Informes (incluyendo streaming de PDF)
- [ ] Exponer endpoints de Dashboard/KPIs
- [ ] Documentar todos los endpoints con schemas OpenAPI
- [ ] Implementar rate limiting en endpoints críticos
- [ ] Tests de integración para cada endpoint (al menos happy path + error cases)
- [ ] Configurar Swagger UI (deshabilitado en producción por defecto)

---

## Tests

```python
# tests/api/test_clientes_api.py
def test_list_clientes_requires_auth(client):
    response = client.get('/api/v1/clientes')
    assert response.status_code == 401

def test_list_clientes_with_valid_token(client, auth_token):
    response = client.get('/api/v1/clientes', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'data' in response.json
    assert 'meta' in response.json

def test_create_cliente_validates_required_fields(client, admin_token):
    response = client.post('/api/v1/clientes', 
        json={},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400
    assert response.json['error']['code'] == 'VALIDATION_ERROR'
```

---

## Librerías

```txt
# requirements additions
flask-jwt-extended==4.6.0
flask-openapi3==3.1.0
flask-limiter==3.5.0
```

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 6 días

## Related Issues
- Phase 6 #04 - RBAC (permisos usados en decoradores de la API)
- Phase 5 #03 - Analytics Dashboard (datos expuestos en `/api/v1/dashboard`)
- Phase 2 #04 - User Auth (usuarios + roles para JWT)
