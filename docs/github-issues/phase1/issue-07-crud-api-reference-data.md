# [Phase 1] CRUD API for Reference Data

**Labels:** `phase-1`, `api`, `backend`, `crud`, `rest`, `high-priority`
**Milestone:** Phase 1: Foundation & Schema (Weeks 1-2)
**Estimated Effort:** 3 days
**Depends on:** 
- Issue #1 ([Phase 1] Create Reference Data Models)
- Issue #5 ([Phase 1] Implement Authentication System)
- Issue #6 ([Phase 1] Create Base Templates for CRUD)

---

## Description

Create a complete CRUD (Create, Read, Update, Delete) REST API and web interface for all 9 reference data tables. This enables administrators to manage the foundational lookup data required by the entire system.

### Scope

| Entity | Records | Priority | Operations |
|--------|---------|----------|------------|
| Areas | 4 | High | List, View, Create, Edit, Delete |
| Organismos | 12 | High | List, View, Create, Edit, Delete |
| Provincias | 4 | Medium | List, View, Create, Edit, Delete |
| Destinos | 7 | High | List, View, Create, Edit, Delete |
| Ramas | 13 | High | List, View, Create, Edit, Delete |
| Meses | 12 | Medium | List, View, Create, Edit, Delete |
| Annos | 10 | Low | List, View, Create, Edit, Delete |
| TipoES | 4 | High | List, View, Create, Edit, Delete |
| UM (Unidades de Medida) | 3 | Medium | List, View, Create, Edit, Delete |

### API Design Principles

1. **RESTful URLs**: `/api/reference/<entity>` and `/reference/<entity>` for web views
2. **Consistent Response Format**: JSON with standardized error handling
3. **Validation**: Server-side validation with clear error messages
4. **Pagination**: All list endpoints support pagination
5. **Filtering**: Search and filter capabilities
6. **Authentication**: All endpoints require authentication
7. **Authorization**: Only admins and laboratory managers can modify reference data

---

## Acceptance Criteria

### API Endpoints (REST)

For each of the 9 reference entities, create:

#### List Endpoint
- [ ] `GET /api/reference/<entities>` - List all records
  - [ ] Support pagination (`?page=1&per_page=25`)
  - [ ] Support search (`?q=search_term`)
  - [ ] Support sorting (`?sort=nombre&order=asc`)
  - [ ] Return JSON: `{ "items": [...], "total": 50, "pages": 2, "page": 1 }`

#### Detail Endpoint
- [ ] `GET /api/reference/<entity>/<id>` - Get single record
  - [ ] Return 404 if not found
  - [ ] Return JSON with full record data

#### Create Endpoint
- [ ] `POST /api/reference/<entity>` - Create new record
  - [ ] Accept JSON body with required fields
  - [ ] Validate all required fields present
  - [ ] Validate no duplicates (unique constraints)
  - [ ] Return 201 Created with new record
  - [ ] Return 400 with validation errors if invalid

#### Update Endpoint
- [ ] `PUT /api/reference/<entity>/<id>` - Update record
  - [ ] Accept JSON body with fields to update
  - [ ] Validate data
  - [ ] Return 200 with updated record
  - [ ] Return 404 if not found

#### Delete Endpoint
- [ ] `DELETE /api/reference/<entity>/<id>` - Delete record
  - [ ] Check for foreign key constraints (don't allow delete if referenced)
  - [ ] Return 204 No Content on success
  - [ ] Return 404 if not found
  - [ ] Return 409 Conflict if FK constraint prevents delete

### Web Views (HTML)

For each of the 9 reference entities, create:

#### List View
- [ ] `GET /reference/<entities>` - HTML list page
  - [ ] Use `base_list.html` template
  - [ ] Display paginated table
  - [ ] Include search/filter form
  - [ ] Show record count
  - [ ] Action buttons (view, edit, delete)

#### Detail View
- [ ] `GET /reference/<entity>/<id>` - HTML detail page
  - [ ] Use `base_detail.html` template
  - [ ] Display all fields
  - [ ] Show related entities (if any)
  - [ ] Edit and delete buttons

#### Create/Edit View
- [ ] `GET /reference/<entity>/new` - Create form
- [ ] `GET /reference/<entity>/<id>/edit` - Edit form
  - [ ] Use `base_form.html` template
  - [ ] Pre-populate fields for edit
  - [ ] Client-side validation
  - [ ] Server-side validation
  - [ ] Success/error flash messages

### Validation & Error Handling

- [ ] Implement `ReferenceDataForm` (Flask-WTF) for each entity
- [ ] Required field validation
- [ ] Unique constraint validation (e.g., no duplicate area siglas)
- [ ] Length validation (match database constraints)
- [ ] Return 400 Bad Request with detailed error messages
- [ ] Return 422 Unprocessable Entity for semantic errors
- [ ] Log all validation failures

### Forms (Flask-WTF)

Create forms for each entity:

```python
class AreaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(),
        Length(max=100)
    ])
    sigla = StringField('Sigla', validators=[
        DataRequired(),
        Length(max=10),
        Regexp('^[A-Z]{2,10}$', message='Sigla must be 2-10 uppercase letters')
    ])
    submit = SubmitField('Guardar')
    
    def validate_sigla(self, field):
        # Check uniqueness (exclude current record on edit)
        existing = Area.query.filter_by(sigla=field.data).first()
        if existing and existing.id != request.view_args.get('id'):
            raise ValidationError('Esta sigla ya existe')

# Similar forms for other entities...
```

### Access Control

- [ ] All endpoints require `@login_required`
- [ ] Modification endpoints require `@admin_required` or `@laboratory_manager_required`
- [ ] Return 403 Forbidden for unauthorized access attempts
- [ ] Hide edit/delete buttons in UI for unauthorized users

### API Documentation

- [ ] Create `docs/API_REFERENCE.md` documenting all endpoints
- [ ] Include request/response examples
- [ ] Document error codes and messages
- [ ] Document authentication requirements

---

## Technical Notes

### Blueprint Structure

```
app/
├── routes/
│   ├── __init__.py
│   ├── dashboard.py       # (existing)
│   ├── pedidos.py         # (existing)
│   ├── auth.py            # (from Issue #5)
│   └── reference/         # <-- NEW directory
│       ├── __init__.py    # Blueprint registration
│       ├── areas.py       # Area CRUD
│       ├── organismos.py  # Organismo CRUD
│       ├── provincias.py  # Provincia CRUD
│       ├── destinos.py    # Destino CRUD
│       ├── ramas.py       # Rama CRUD
│       ├── meses.py       # Mes CRUD
│       ├── annos.py       # Anno CRUD
│       ├── tipos_es.py    # TipoES CRUD
│       └── unidades.py    # UnidadMedida CRUD
```

### Generic CRUD Blueprint Factory

```python
# app/routes/reference/__init__.py

from flask import Blueprint
from .areas import areas_bp
from .organismos import organismos_bp
# ... import other blueprints

def register_reference_blueprints(app):
    """Register all reference data blueprints"""
    app.register_blueprint(areas_bp, url_prefix='/reference')
    app.register_blueprint(organismos_bp, url_prefix='/reference')
    # ... register others
```

### Base CRUD Mixin/Utility

```python
# app/utils/crud.py

from functools import wraps
from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

class CRUDMixin:
    """Mixin providing standard CRUD operations"""
    
    model = None
    form_class = None
    template_dir = 'reference'
    
    def list(self):
        """List all records with pagination"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        search = request.args.get('q', '')
        
        query = self.model.query
        
        if search:
            # Override in subclass for specific search fields
            query = query.filter(self.model.nombre.ilike(f'%{search}%'))
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        if request.is_json:
            return jsonify({
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'page': pagination.page
            })
        
        return render_template(
            f'{self.template_dir}/list.html',
            items=pagination,
            search_term=search
        )
    
    def detail(self, id):
        """Get single record"""
        item = self.model.query.get_or_404(id)
        
        if request.is_json:
            return jsonify(item.to_dict())
        
        return render_template(
            f'{self.template_dir}/detail.html',
            item=item
        )
    
    def create(self):
        """Create new record"""
        form = self.form_class()
        
        if form.validate_on_submit():
            item = self.model()
            form.populate_obj(item)
            db.session.add(item)
            db.session.commit()
            
            flash(f'{self.model.__name__} creado exitosamente', 'success')
            
            if request.is_json:
                return jsonify(item.to_dict()), 201
            return redirect(url_for(f'.detail', id=item.id))
        
        if request.is_json:
            return jsonify({'errors': form.errors}), 400
        
        return render_template(
            f'{self.template_dir}/form.html',
            form=form,
            action='create'
        )
    
    def update(self, id):
        """Update existing record"""
        item = self.model.query.get_or_404(id)
        form = self.form_class(obj=item)
        
        if form.validate_on_submit():
            form.populate_obj(item)
            db.session.commit()
            
            flash(f'{self.model.__name__} actualizado exitosamente', 'success')
            
            if request.is_json:
                return jsonify(item.to_dict())
            return redirect(url_for(f'.detail', id=item.id))
        
        if request.is_json:
            return jsonify({'errors': form.errors}), 400
        
        return render_template(
            f'{self.template_dir}/form.html',
            form=form,
            item=item,
            action='edit'
        )
    
    def delete(self, id):
        """Delete record"""
        item = self.model.query.get_or_404(id)
        
        try:
            db.session.delete(item)
            db.session.commit()
            flash(f'{self.model.__name__} eliminado exitosamente', 'success')
        except IntegrityError:
            db.session.rollback()
            flash(f'No se puede eliminar: está en uso', 'error')
            if request.is_json:
                return jsonify({'error': 'Foreign key constraint'}), 409
            return redirect(url_for(f'.detail', id=id))
        
        if request.is_json:
            return '', 204
        return redirect(url_for(f'.list'))


def crud_routes(bp, model, form_class, name):
    """Register CRUD routes for a model"""
    handler = type(f'{name}Handler', (CRUDMixin,), {
        'model': model,
        'form_class': form_class
    })()
    
    bp.route(f'/{name.lower()}s', methods=['GET'])(login_required(handler.list))
    bp.route(f'/{name.lower()}s/<int:id>', methods=['GET'])(login_required(handler.detail))
    bp.route(f'/{name.lower()}s/new', methods=['GET', 'POST'])(admin_required(handler.create))
    bp.route(f'/{name.lower()}s/<int:id>/edit', methods=['GET', 'POST'])(admin_required(handler.update))
    bp.route(f'/{name.lower()}s/<int:id>/delete', methods=['POST'])(admin_required(handler.delete))
```

### Area Blueprint Example

```python
# app/routes/reference/areas.py

from flask import Blueprint
from app.database.models import Area
from app.forms.reference import AreaForm
from app.utils.crud import crud_routes

areas_bp = Blueprint('areas', __name__)
crud_routes(areas_bp, Area, AreaForm, 'area')
```

### Model to_dict() Method

Add to all reference models:

```python
class Area(db.Model):
    # ... existing fields ...
    
    def to_dict(self):
        """Serialize to dictionary for API responses"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
```

### URL Structure

| Action | URL | Method |
|--------|-----|--------|
| List | `/reference/areas` | GET |
| API List | `/api/reference/areas` | GET |
| Detail | `/reference/areas/1` | GET |
| API Detail | `/api/reference/areas/1` | GET |
| Create Form | `/reference/areas/new` | GET |
| Create | `/reference/areas/new` | POST |
| API Create | `/api/reference/areas` | POST |
| Edit Form | `/reference/areas/1/edit` | GET |
| Update | `/reference/areas/1/edit` | POST |
| API Update | `/api/reference/areas/1` | PUT |
| Delete | `/reference/areas/1/delete` | POST |
| API Delete | `/api/reference/areas/1` | DELETE |

---

## Dependencies

**Blocked by:**
- Issue #1: [Phase 1] Create Reference Data Models (need models to CRUD)
- Issue #5: [Phase 1] Implement Authentication System (need auth for security)
- Issue #6: [Phase 1] Create Base Templates for CRUD (need templates for UI)

**Blocks:**
- Issue #8: [Phase 1] Import Access Data - Reference & Master (can verify data via API)
- All Phase 2 CRUD features (uses this pattern)

---

## API Documentation Template

```markdown
# DataLab API Reference

## Reference Data Endpoints

### Areas

#### List Areas
```http
GET /api/reference/areas?page=1&per_page=25&q=fisico
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Físico-Químico",
      "sigla": "FQ",
      "creado_en": "2026-03-02T10:00:00"
    }
  ],
  "total": 1,
  "pages": 1,
  "page": 1
}
```

#### Create Area
```http
POST /api/reference/areas
Content-Type: application/json

{
  "nombre": "Microbiología",
  "sigla": "MB"
}
```

**Response (201):**
```json
{
  "id": 2,
  "nombre": "Microbiología",
  "sigla": "MB",
  "creado_en": "2026-03-02T14:30:00"
}
```

**Error Response (400):**
```json
{
  "errors": {
    "sigla": ["Esta sigla ya existe"]
  }
}
```

(Similar documentation for other entities...)
```

---

## Testing Requirements

- [ ] Test all CRUD operations for each of 9 entities
- [ ] Test pagination works correctly
- [ ] Test search/filter functionality
- [ ] Test validation errors return proper JSON
- [ ] Test unauthorized access returns 403
- [ ] Test unauthenticated access redirects to login
- [ ] Test foreign key constraint errors return 409
- [ ] Test API content negotiation (Accept: application/json)

---

## Definition of Done

- [ ] All 9 entities have complete CRUD API
- [ ] All 9 entities have complete web UI
- [ ] API documentation written
- [ ] All endpoints have authentication
- [ ] All modification endpoints have proper authorization
- [ ] Validation working on all forms
- [ ] Pagination working on all list views
- [ ] Code review completed
- [ ] All tests passing
