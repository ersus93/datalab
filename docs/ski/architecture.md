# DataLab Architecture Overview

This document describes the Hexagonal Architecture (Ports & Adapters) adopted for the DataLab application, including project structure, layer responsibilities, and design patterns.

---

## 1. Architecture Overview

### Hexagonal Architecture (Ports & Adapters)

Hexagonal Architecture, also known as Ports and Adapters or Clean Architecture, is an architectural pattern that structures the application so that:

- **Domain logic is isolated** in the center (core) of the application
- **Dependencies point inward** - outer layers depend on inner layers, never the reverse
- **External concerns are decoupled** from business logic through interfaces (Ports)
- **Adapters** implement these interfaces to connect to the outside world (databases, web frameworks, external APIs)

### Clean Architecture Principles

DataLab follows Clean Architecture principles:

1. **Independent of Frameworks** - The domain doesn't know about Flask or SQLAlchemy
2. **Testable** - Business rules can be tested without UI, database, or external services
3. **Independent of UI** - The interface can change without affecting business rules
4. **Independent of Database** - Business rules don't depend on database implementation
5. **Independent of External Services** - External dependencies are abstracted behind interfaces

### Why Hexagonal Architecture for DataLab?

- **Migration from Access**: Allows gradual migration from legacy Microsoft Access database
- **Maintainability**: Business rules are centralized and protected from framework churn
- **Testability**: Fast unit tests without database dependencies
- **Flexibility**: Can swap Flask for another framework or SQLite for PostgreSQL without touching domain logic

---

## 2. Layer Documentation

### Domain Layer (Core)

The Domain Layer contains the business logic and is completely independent of frameworks.

**Responsibilities:**
- Pure Python entities (no framework dependencies)
- Business rules and validations
- Repository interfaces (Ports)

**Rules:**
- No imports from Flask, SQLAlchemy, or any external framework
- All dependencies must be standard library or domain-specific
- Entities encapsulate all business invariants

**Locations:**
- `app/core/domain/` - Shared domain components
- `app/features/[feature]/domain/` - Feature-specific domain

**Example:**
```python
# app/features/clientes/domain/models.py
class Cliente:
    """Pure domain entity with business rules"""
    
    def __init__(self, id: Optional[int], codigo: str, nombre: str, 
                 email: Optional[str] = None, telefono: Optional[str] = None,
                 direccion: Optional[str] = None, activo: bool = True):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.activo = activo
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def validate(self) -> List[str]:
        """Business validation rules"""
        errors = []
        if not self.codigo or len(self.codigo) < 3:
            errors.append("El código debe tener al menos 3 caracteres")
        if not self.nombre or len(self.nombre) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        return errors
    
    def deactivate(self):
        """Business operation with domain rules"""
        self.activo = False
        self.updated_at = datetime.utcnow()
```

---

### Application Layer

The Application Layer orchestrates use cases by coordinating domain objects. It defines what the application can do.

**Responsibilities:**
- Use cases (Commands and Queries - CQRS pattern)
- DTOs (Data Transfer Objects) for input/output
- Orchestration logic
- Transaction boundaries

**Locations:**
- `app/features/[feature]/application/`

**Commands** - Write operations that change state:
```python
# app/features/clientes/application/commands.py
@dataclass
class CrearClienteCommand:
    codigo: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class CrearClienteHandler:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository
    
    def execute(self, command: CrearClienteCommand) -> Result[Cliente]:
        # 1. Create domain entity
        cliente = Cliente(
            id=None,
            codigo=command.codigo,
            nombre=command.nombre,
            email=command.email,
            telefono=command.telefono,
            direccion=command.direccion
        )
        
        # 2. Validate business rules
        errors = cliente.validate()
        if errors:
            return Result.failure(errors)
        
        # 3. Check uniqueness constraints
        if self.repository.exists_by_codigo(command.codigo):
            return Result.failure(["El código de cliente ya existe"])
        
        # 4. Persist
        self.repository.save(cliente)
        
        return Result.success(cliente)
```

**Queries** - Read operations that return data:
```python
# app/features/clientes/application/queries.py
@dataclass
class ListarClientesQuery:
    activos_only: bool = True
    search_term: Optional[str] = None
    page: int = 1
    page_size: int = 50

class ListarClientesHandler:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository
    
    def execute(self, query: ListarClientesQuery) -> PaginatedResult[ClienteResponseDTO]:
        clientes = self.repository.list(
            activos_only=query.activos_only,
            search_term=query.search_term,
            page=query.page,
            page_size=query.page_size
        )
        total = self.repository.count(activos_only=query.activos_only)
        
        dtos = [ClienteResponseDTO.from_entity(c) for c in clientes]
        return PaginatedResult(dtos, total, query.page, query.page_size)
```

**DTOs** - Data Transfer Objects:
```python
# app/features/clientes/application/dtos.py
@dataclass
class ClienteCreateDTO:
    """Input DTO for creating a client"""
    codigo: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

@dataclass
class ClienteResponseDTO:
    """Output DTO for client responses"""
    id: int
    codigo: str
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    activo: bool
    created_at: str
    updated_at: str
    
    @staticmethod
    def from_entity(cliente: Cliente) -> 'ClienteResponseDTO':
        return ClienteResponseDTO(
            id=cliente.id,
            codigo=cliente.codigo,
            nombre=cliente.nombre,
            email=cliente.email,
            telefono=cliente.telefono,
            direccion=cliente.direccion,
            activo=cliente.activo,
            created_at=cliente.created_at.isoformat() if cliente.created_at else None,
            updated_at=cliente.updated_at.isoformat() if cliente.updated_at else None
        )
```

---

### Infrastructure Layer

The Infrastructure Layer contains framework-specific implementations of the interfaces defined in the Domain Layer.

**Responsibilities:**
- Database implementations of repositories (Adapters)
- Web framework route handlers (Web Adapters)
- External service integrations
- Framework-specific configurations

**Locations:**
- `app/features/[feature]/infrastructure/`

**SQLAlchemy Repository (Adapter):**
```python
# app/features/clientes/infrastructure/persistence/sql_repository.py
class SQLClienteRepository(ClienteRepository):
    """SQLAlchemy implementation of ClienteRepository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[Cliente]:
        orm_cliente = self.session.get(ClienteORM, id)
        return self._to_domain(orm_cliente) if orm_cliente else None
    
    def save(self, cliente: Cliente) -> Cliente:
        orm_cliente = self._to_orm(cliente)
        self.session.add(orm_cliente)
        self.session.flush()  # Get ID without committing
        cliente.id = orm_cliente.id
        return cliente
    
    def _to_domain(self, orm: ClienteORM) -> Cliente:
        return Cliente(
            id=orm.id,
            codigo=orm.codigo,
            nombre=orm.nombre,
            email=orm.email,
            telefono=orm.telefono,
            direccion=orm.direccion,
            activo=orm.activo
        )
```

**Flask Routes (Web Adapter):**
```python
# app/features/clientes/infrastructure/web/routes.py
clientes_bp = Blueprint('clientes', __name__, template_folder='templates')

@clientes_bp.route('/clientes')
def index():
    """List clients page"""
    query = ListarClientesQuery(
        activos_only=request.args.get('activos', '1') == '1',
        search_term=request.args.get('q'),
        page=int(request.args.get('page', 1))
    )
    
    # Dependency injection from application context
    repository = get_cliente_repository()
    handler = ListarClientesHandler(repository)
    result = handler.execute(query)
    
    return render_template('pages/clientes/index.html', 
                          clientes=result.items,
                          pagination=result)

@clientes_bp.route('/clientes', methods=['POST'])
def create():
    """Create client endpoint"""
    command = CrearClienteCommand(
        codigo=request.form['codigo'],
        nombre=request.form['nombre'],
        email=request.form.get('email'),
        telefono=request.form.get('telefono'),
        direccion=request.form.get('direccion')
    )
    
    repository = get_cliente_repository()
    handler = CrearClienteHandler(repository)
    result = handler.execute(command)
    
    if result.is_success:
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes.show', id=result.value.id))
    else:
        flash(f'Error: {", ".join(result.errors)}', 'danger')
        return render_template('pages/clientes/new.html'), 422
```

---

## 3. Shared Kernel

The Shared Kernel contains components used across all features.

### Location
`app/core/`

### Base Classes

**Entity Base Class:**
```python
# app/core/domain/entity.py
from abc import ABC, abstractmethod
from typing import Any, Optional

class Entity(ABC):
    """Base class for all domain entities"""
    
    def __init__(self, id: Optional[int] = None):
        self._id = id
    
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @id.setter
    def id(self, value: int):
        self._id = value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id is not None and self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id) if self.id else hash(id(self))
```

**Repository Interface (Port):**
```python
# app/core/domain/repository.py
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Base repository interface (Port)"""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity (create or update)"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID"""
        pass
```

**Audit Mixin:**
```python
# app/core/domain/audit.py
from datetime import datetime
from typing import Optional

class Auditable:
    """Mixin for auditable entities"""
    
    def __init__(self):
        self._created_at: Optional[datetime] = None
        self._updated_at: Optional[datetime] = None
    
    @property
    def created_at(self) -> Optional[datetime]:
        return self._created_at
    
    @property
    def updated_at(self) -> Optional[datetime]:
        return self._updated_at
    
    def mark_created(self):
        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at
    
    def mark_updated(self):
        self._updated_at = datetime.utcnow()
```

**Result Pattern:**
```python
# app/core/domain/result.py
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Result pattern for handling success/failure"""
    
    is_success: bool
    value: Optional[T] = None
    errors: List[str] = None
    
    @staticmethod
    def success(value: T) -> 'Result[T]':
        return Result(is_success=True, value=value, errors=[])
    
    @staticmethod
    def failure(errors: List[str]) -> 'Result[T]':
        return Result(is_success=False, value=None, errors=errors)
```

---

## 4. Feature Structure

Each feature follows a consistent structure. Here's the complete structure using **Clientes** as the example:

```
app/features/clientes/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── models.py              # Cliente entity with validation
│   └── repositories.py        # ClienteRepository interface (Port)
├── application/
│   ├── __init__.py
│   ├── dtos.py                # ClienteCreateDTO, ClienteResponseDTO
│   ├── commands.py            # CrearClienteHandler, ActualizarClienteHandler
│   └── queries.py             # ListarClientesHandler, ObtenerClienteHandler
└── infrastructure/
    ├── __init__.py
    ├── persistence/
    │   ├── __init__.py
    │   ├── models.py          # SQLAlchemy ORM model
    │   └── sql_repository.py  # SQLClienteRepository (Adapter)
    └── web/
        ├── __init__.py
        ├── routes.py          # Flask Blueprint
        └── templates/         # Feature-specific templates
            └── pages/
                └── clientes/
                    ├── index.html
                    ├── new.html
                    ├── edit.html
                    └── show.html
```

### Domain Layer Files

**models.py**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.core.domain.entity import Entity
from app.core.domain.audit import Auditable

@dataclass
class Cliente(Entity, Auditable):
    """Cliente domain entity"""
    codigo: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True
    
    def validate(self) -> List[str]:
        """Business validation rules"""
        errors = []
        if not self.codigo or len(self.codigo.strip()) < 3:
            errors.append("El código debe tener al menos 3 caracteres")
        if not self.nombre or len(self.nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        if self.email and '@' not in self.email:
            errors.append("El email no es válido")
        return errors
```

**repositories.py**
```python
from abc import abstractmethod
from typing import List, Optional

from app.core.domain.repository import Repository
from app.features.clientes.domain.models import Cliente

class ClienteRepository(Repository[Cliente]):
    """Repository interface for Cliente (Port)"""
    
    @abstractmethod
    def exists_by_codigo(self, codigo: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a client with given code exists"""
        pass
    
    @abstractmethod
    def list(self, activos_only: bool = True, search_term: Optional[str] = None,
             page: int = 1, page_size: int = 50) -> List[Cliente]:
        """List clients with filtering and pagination"""
        pass
    
    @abstractmethod
    def count(self, activos_only: bool = True) -> int:
        """Count total clients matching criteria"""
        pass
```

### Application Layer Files

**dtos.py**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClienteCreateDTO:
    codigo: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

@dataclass
class ClienteUpdateDTO:
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

@dataclass
class ClienteResponseDTO:
    id: int
    codigo: str
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    activo: bool
    created_at: Optional[str]
    updated_at: Optional[str]
```

**commands.py**
```python
from dataclasses import dataclass
from typing import Optional

from app.core.domain.result import Result
from app.features.clientes.domain.models import Cliente
from app.features.clientes.domain.repositories import ClienteRepository

@dataclass
class CrearClienteCommand:
    codigo: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class CrearClienteHandler:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository
    
    def execute(self, command: CrearClienteCommand) -> Result[Cliente]:
        # Create domain entity
        cliente = Cliente(
            id=None,
            codigo=command.codigo,
            nombre=command.nombre,
            email=command.email,
            telefono=command.telefono,
            direccion=command.direccion
        )
        
        # Validate
        errors = cliente.validate()
        if errors:
            return Result.failure(errors)
        
        # Check duplicates
        if self.repository.exists_by_codigo(command.codigo):
            return Result.failure(["El código de cliente ya existe"])
        
        # Save
        self.repository.save(cliente)
        return Result.success(cliente)
```

**queries.py**
```python
from dataclasses import dataclass
from typing import List, Optional

from app.core.domain.result import PaginatedResult
from app.features.clientes.application.dtos import ClienteResponseDTO
from app.features.clientes.domain.repositories import ClienteRepository

@dataclass
class ListarClientesQuery:
    activos_only: bool = True
    search_term: Optional[str] = None
    page: int = 1
    page_size: int = 50

class ListarClientesHandler:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository
    
    def execute(self, query: ListarClientesQuery) -> PaginatedResult[ClienteResponseDTO]:
        clientes = self.repository.list(
            activos_only=query.activos_only,
            search_term=query.search_term,
            page=query.page,
            page_size=query.page_size
        )
        total = self.repository.count(activos_only=query.activos_only)
        
        dtos = [ClienteResponseDTO.from_entity(c) for c in clientes]
        return PaginatedResult(dtos, total, query.page, query.page_size)
```

### Infrastructure Layer Files

**persistence/models.py**
```python
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database.base import Base

class ClienteORM(Base):
    """SQLAlchemy ORM model for Cliente"""
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(120), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(300), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**persistence/sql_repository.py**
```python
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.features.clientes.domain.models import Cliente
from app.features.clientes.domain.repositories import ClienteRepository
from app.features.clientes.infrastructure.persistence.models import ClienteORM

class SQLClienteRepository(ClienteRepository):
    """SQLAlchemy implementation of ClienteRepository (Adapter)"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[Cliente]:
        orm = self.session.get(ClienteORM, id)
        return self._to_domain(orm) if orm else None
    
    def save(self, cliente: Cliente) -> Cliente:
        if cliente.id:
            orm = self.session.get(ClienteORM, cliente.id)
            if orm:
                self._update_orm(orm, cliente)
            else:
                orm = self._to_orm(cliente)
                self.session.add(orm)
        else:
            orm = self._to_orm(cliente)
            self.session.add(orm)
        
        self.session.flush()
        cliente.id = orm.id
        return cliente
    
    def delete(self, id: int) -> bool:
        orm = self.session.get(ClienteORM, id)
        if orm:
            self.session.delete(orm)
            return True
        return False
    
    def exists_by_codigo(self, codigo: str, exclude_id: Optional[int] = None) -> bool:
        query = self.session.query(ClienteORM).filter_by(codigo=codigo)
        if exclude_id:
            query = query.filter(ClienteORM.id != exclude_id)
        return query.first() is not None
    
    def list(self, activos_only: bool = True, search_term: Optional[str] = None,
             page: int = 1, page_size: int = 50) -> List[Cliente]:
        query = self.session.query(ClienteORM)
        
        if activos_only:
            query = query.filter_by(activo=True)
        
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    ClienteORM.nombre.ilike(search),
                    ClienteORM.codigo.ilike(search)
                )
            )
        
        query = query.order_by(ClienteORM.nombre)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        return [self._to_domain(orm) for orm in query.all()]
    
    def count(self, activos_only: bool = True) -> int:
        query = self.session.query(ClienteORM)
        if activos_only:
            query = query.filter_by(activo=True)
        return query.count()
    
    def _to_domain(self, orm: ClienteORM) -> Cliente:
        return Cliente(
            id=orm.id,
            codigo=orm.codigo,
            nombre=orm.nombre,
            email=orm.email,
            telefono=orm.telefono,
            direccion=orm.direccion,
            activo=orm.activo
        )
    
    def _to_orm(self, cliente: Cliente) -> ClienteORM:
        return ClienteORM(
            id=cliente.id,
            codigo=cliente.codigo,
            nombre=cliente.nombre,
            email=cliente.email,
            telefono=cliente.telefono,
            direccion=cliente.direccion,
            activo=cliente.activo
        )
    
    def _update_orm(self, orm: ClienteORM, cliente: Cliente):
        orm.codigo = cliente.codigo
        orm.nombre = cliente.nombre
        orm.email = cliente.email
        orm.telefono = cliente.telefono
        orm.direccion = cliente.direccion
        orm.activo = cliente.activo
```

**web/routes.py**
```python
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.features.clientes.application.commands import CrearClienteCommand, CrearClienteHandler
from app.features.clientes.application.queries import ListarClientesQuery, ListarClientesHandler
from app.features.clientes.infrastructure.persistence.sql_repository import SQLClienteRepository
from app.database.database import get_session

clientes_bp = Blueprint('clientes', __name__, 
                        template_folder='templates',
                        url_prefix='/clientes')

def get_cliente_repository():
    """Factory for repository with current session"""
    return SQLClienteRepository(get_session())

@clientes_bp.route('/')
def index():
    """List clients page"""
    query = ListarClientesQuery(
        activos_only=request.args.get('activos', '1') == '1',
        search_term=request.args.get('q') or None,
        page=int(request.args.get('page', 1))
    )
    
    repository = get_cliente_repository()
    handler = ListarClientesHandler(repository)
    result = handler.execute(query)
    
    return render_template('pages/clientes/index.html',
                          clientes=result.items,
                          pagination=result,
                          search_term=request.args.get('q', ''))

@clientes_bp.route('/new', methods=['GET'])
def new():
    """New client form"""
    return render_template('pages/clientes/new.html')

@clientes_bp.route('/', methods=['POST'])
def create():
    """Create client"""
    command = CrearClienteCommand(
        codigo=request.form['codigo'],
        nombre=request.form['nombre'],
        email=request.form.get('email') or None,
        telefono=request.form.get('telefono') or None,
        direccion=request.form.get('direccion') or None
    )
    
    repository = get_cliente_repository()
    handler = CrearClienteHandler(repository)
    result = handler.execute(command)
    
    if result.is_success:
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes.show', id=result.value.id))
    else:
        for error in result.errors:
            flash(error, 'danger')
        return render_template('pages/clientes/new.html', 
                              data=request.form), 422
```

---

## 5. Dependency Rules

### Visual Dependency Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL LAYER                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Flask      │  │  SQLAlchemy  │  │   Other      │  │  External    │     │
│  │   Routes     │  │  Repository  │  │   Adapters   │  │   APIs       │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
│         │  depends on     │  implements     │  implements     │              │
│         │                 │                 │                 │              │
│         ▼                 ▼                 ▼                 ▼              │
├─────────────────────────────────────────────────────────────────────────────┤
│                        APPLICATION LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  Command Handlers  │  Query Handlers  │  DTOs  │  Orchestration  │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│         ▲                              │                                     │
│         │  uses                        │  uses                               │
│         │                              │                                     │
├─────────┼──────────────────────────────┼─────────────────────────────────────┤
│         │                              │                                     │
│         │        DOMAIN LAYER (Core)   │                                     │
│         │  ┌──────────────────────────────────────────────────────────┐     │
│         └──┤  Entities  │  Business Rules  │  Repository Interfaces   │     │
│            └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘

Dependency Rule: Dependencies point INWARD only
```

### Import Rules

| Layer | Can Import From | Cannot Import From |
|-------|-----------------|-------------------|
| **Domain** | Python stdlib, typing | Flask, SQLAlchemy, any framework |
| **Application** | Domain, Python stdlib | Flask, SQLAlchemy, infrastructure |
| **Infrastructure** | Domain, Application, Flask, SQLAlchemy | None (outermost layer) |

### The Dependency Inversion Principle

**Before (Traditional):**
```
┌─────────────┐         ┌─────────────┐
│   Routes    │───────► │   Models    │
│             │         │  (SQLAlchemy)│
└─────────────┘         └─────────────┘
```
Routes directly depend on SQLAlchemy models - hard to test, tightly coupled.

**After (Hexagonal):**
```
┌───────────────┐         ┌──────────────────┐         ┌─────────────────┐
│     Routes    │───────► │ ClienteRepository│◄────────│ SQLClienteRepository│
│               │         │   (Interface)    │         │   (Implementation)  │
└───────────────┘         └──────────────────┘         └─────────────────┘
        │                                                    │
        │                                                    │
        └────────────────────────────────────────────────────┘
                    Depends on abstraction
```

Routes depend on the repository interface, not the SQLAlchemy implementation. We can:
- Swap SQLAlchemy for another ORM
- Use an in-memory repository for testing
- Mock repositories in unit tests

---

## 6. Testing Strategy

### Test Pyramid

```
    /\
   /  \
  / E2E\         <- Few tests (Selenium/Playwright)
 /______\
 /        \
/Integration\    <- Some tests (with real DB)
/____________\
/              \
/     Unit       \  <- Many tests (fast, no DB)
/__________________\
```

### Unit Tests - Domain + Application

Unit tests don't need a database. They test business rules in isolation.

```python
# tests/features/clientes/domain/test_models.py
import pytest

from app.features.clientes.domain.models import Cliente

class TestCliente:
    """Unit tests for Cliente domain entity"""
    
    def test_valid_cliente_passes_validation(self):
        cliente = Cliente(id=None, codigo="CLI001", nombre="Test Client")
        errors = cliente.validate()
        assert len(errors) == 0
    
    def test_short_codigo_fails_validation(self):
        cliente = Cliente(id=None, codigo="AB", nombre="Test Client")
        errors = cliente.validate()
        assert "al menos 3 caracteres" in errors[0]
    
    def test_empty_nombre_fails_validation(self):
        cliente = Cliente(id=None, codigo="CLI001", nombre="")
        errors = cliente.validate()
        assert "al menos 2 caracteres" in errors[0]
    
    def test_invalid_email_fails_validation(self):
        cliente = Cliente(id=None, codigo="CLI001", nombre="Test", email="invalid")
        errors = cliente.validate()
        assert "email no es válido" in errors[0]
```

```python
# tests/features/clientes/application/test_commands.py
import pytest
from unittest.mock import Mock

from app.features.clientes.application.commands import (
    CrearClienteCommand, CrearClienteHandler
)
from app.features.clientes.domain.models import Cliente

class TestCrearClienteHandler:
    """Unit tests for CrearCliente use case"""
    
    def setup_method(self):
        self.mock_repo = Mock()
        self.handler = CrearClienteHandler(self.mock_repo)
    
    def test_creates_cliente_successfully(self):
        self.mock_repo.exists_by_codigo.return_value = False
        
        command = CrearClienteCommand(
            codigo="CLI001",
            nombre="Test Client"
        )
        result = self.handler.execute(command)
        
        assert result.is_success
        assert result.value.codigo == "CLI001"
        self.mock_repo.save.assert_called_once()
    
    def test_fails_when_codigo_already_exists(self):
        self.mock_repo.exists_by_codigo.return_value = True
        
        command = CrearClienteCommand(
            codigo="CLI001",
            nombre="Test Client"
        )
        result = self.handler.execute(command)
        
        assert not result.is_success
        assert "ya existe" in result.errors[0]
        self.mock_repo.save.assert_not_called()
    
    def test_fails_when_validation_fails(self):
        command = CrearClienteCommand(codigo="AB", nombre="")  # Invalid
        result = self.handler.execute(command)
        
        assert not result.is_success
        assert len(result.errors) == 2  # codigo and nombre errors
```

### Integration Tests - Infrastructure

Integration tests verify the repository implementations work with a real database.

```python
# tests/features/clientes/infrastructure/test_sql_repository.py
import pytest

from app.features.clientes.domain.models import Cliente
from app.features.clientes.infrastructure.persistence.sql_repository import (
    SQLClienteRepository
)

class TestSQLClienteRepository:
    """Integration tests for SQLClienteRepository"""
    
    def setup_method(self):
        # Using test database fixture
        self.session = get_test_session()
        self.repo = SQLClienteRepository(self.session)
    
    def teardown_method(self):
        self.session.rollback()
    
    def test_save_and_retrieve_cliente(self):
        cliente = Cliente(id=None, codigo="CLI001", nombre="Test")
        
        saved = self.repo.save(cliente)
        self.session.commit()
        
        retrieved = self.repo.get_by_id(saved.id)
        assert retrieved.codigo == "CLI001"
        assert retrieved.nombre == "Test"
    
    def test_exists_by_codigo(self):
        cliente = Cliente(id=None, codigo="CLI001", nombre="Test")
        self.repo.save(cliente)
        self.session.commit()
        
        assert self.repo.exists_by_codigo("CLI001")
        assert not self.repo.exists_by_codigo("NONEXISTENT")
    
    def test_list_with_pagination(self):
        # Create multiple clients
        for i in range(10):
            cliente = Cliente(id=None, codigo=f"CLI{i:03d}", nombre=f"Client {i}")
            self.repo.save(cliente)
        self.session.commit()
        
        page1 = self.repo.list(page=1, page_size=5)
        assert len(page1) == 5
        
        page2 = self.repo.list(page=2, page_size=5)
        assert len(page2) == 5
```

### E2E Tests

E2E tests verify the complete request-response cycle.

```python
# tests/e2e/test_clientes.py
import pytest

class TestClientesE2E:
    """End-to-end tests for clientes feature"""
    
    def test_create_cliente_flow(self, client):
        # GET new client form
        response = client.get('/clientes/new')
        assert response.status_code == 200
        
        # POST create cliente
        response = client.post('/clientes/', data={
            'codigo': 'CLI001',
            'nombre': 'Test Client',
            'email': 'test@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'creado exitosamente' in response.data
    
    def test_list_clientes(self, client):
        response = client.get('/clientes/')
        assert response.status_code == 200
```

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── unit/                          # Fast unit tests
│   ├── core/
│   │   └── test_result.py
│   └── features/
│       └── clientes/
│           ├── domain/
│           │   └── test_models.py
│           └── application/
│               └── test_commands.py
├── integration/                   # Tests with real DB
│   └── features/
│       └── clientes/
│           └── infrastructure/
│               └── test_sql_repository.py
└── e2e/                          # Full application tests
    └── test_clientes.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/features/clientes/domain/test_models.py -v
```

---

## 7. Migration from Access

### How Each Access Table Becomes a Feature

Microsoft Access tables are migrated to Hexagonal Architecture features:

| Access Table | Feature | Status |
|--------------|---------|--------|
| tblClientes | clientes | ✅ Completed |
| tblPedidos | pedidos | 🔄 Next |
| tblOrdenesTrabajo | ordenes_trabajo | ⏳ Pending |
| tblResultados | resultados | ⏳ Pending |
| tblParametros | parametros | ⏳ Pending |

### Migration Process

For each Access table:

1. **Analyze** - Understand table structure, relationships, business rules
2. **Design Domain** - Create pure Python entity with validation
3. **Define Repository** - Create repository interface (Port)
4. **Build Infrastructure** - Implement SQLAlchemy repository and Flask routes
5. **Write Tests** - Unit tests for domain, integration tests for repository
6. **Migrate Data** - Script to transfer data from Access to PostgreSQL

### Example Migration for tblClientes

```python
# migration_scripts/migrate_clientes.py
"""Script to migrate clients from Access to PostgreSQL"""

import pyodbc
from app import create_app
from app.database.database import db
from app.features.clientes.infrastructure.persistence.sql_repository import (
    SQLClienteRepository
)
from app.features.clientes.domain.models import Cliente

def migrate_clientes():
    # Connect to Access database
    access_conn = pyodbc.connect(
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=C:\DataLab\Legacy\DataLab.mdb;'
    )
    cursor = access_conn.cursor()
    
    # Fetch all clients
    cursor.execute("SELECT Codigo, Nombre, Email, Telefono, Direccion FROM tblClientes")
    
    app = create_app()
    with app.app_context():
        repo = SQLClienteRepository(db.session)
        
        for row in cursor.fetchall():
            cliente = Cliente(
                id=None,
                codigo=row.Codigo,
                nombre=row.Nombre,
                email=row.Email,
                telefono=row.Telefono,
                direccion=row.Direccion,
                activo=True
            )
            
            # Validate before saving
            errors = cliente.validate()
            if errors:
                print(f"Skipping {row.Codigo}: {errors}")
                continue
            
            repo.save(cliente)
        
        db.session.commit()
        print("Migration complete!")

if __name__ == '__main__':
    migrate_clientes()
```

### Progressive Migration Strategy

1. **Phase 1: Feature Pilot (Clientes)** ✅
   - Implement full hexagonal architecture for one feature
   - Validate the pattern works for the team
   - Document lessons learned

2. **Phase 2: Core Features**
   - Pedidos (Orders)
   - Ordenes de Trabajo (Work Orders)
   - Establish patterns for related entities

3. **Phase 3: Supporting Features**
   - Resultados (Results)
   - Parametros (Parameters)
   - Configuracion (Configuration)

4. **Phase 4: Legacy Bridge**
   - Synchronization layer for phased cutover
   - Allow running Access and DataLab in parallel

### Feature Pilot: Clientes ✅

The **Clientes** feature has been completed as the architecture pilot:

- ✅ Domain entity with validation
- ✅ Repository interface and SQLAlchemy implementation
- ✅ Command and Query handlers
- ✅ Flask routes with forms
- ✅ Full CRUD operations
- ✅ Unit tests
- ✅ Integration tests
- ✅ Templates and UI

Lessons learned from the pilot:
- Repository pattern works well for testability
- DTOs add boilerplate but improve API clarity
- Result pattern is cleaner than exceptions for business errors
- Feature folders make the codebase easier to navigate

---

## 8. Architecture Decision Records (ADRs)

### ADR 5: Hexagonal Architecture
**Decision:** Adopt Hexagonal (Ports & Adapters) Architecture
**Rationale:**
- Clear separation of concerns
- Testability without database
- Easier migration from legacy Access database
- Framework independence
**Status:** ✅ Accepted - Pilot completed with Clientes feature

### ADR 6: CQRS for Application Layer
**Decision:** Use Command Query Responsibility Segregation
**Rationale:**
- Clear distinction between reads and writes
- Optimized query handlers for complex reads
- Commands can enforce business rules strictly
**Status:** ✅ Accepted

### ADR 7: Repository Pattern
**Decision:** Use Repository pattern with explicit interfaces
**Rationale:**
- Abstracts database details from domain
- Enables testing with mocks
- Can swap ORM without changing domain
**Status:** ✅ Accepted

### ADR 8: Feature-Based Organization
**Decision:** Organize code by feature, not by layer
**Rationale:**
- Easier to navigate and understand
- Feature changes are localized
- Clear boundaries between features
**Status:** ✅ Accepted

---

## 9. Quick Reference

### Adding a New Feature

1. Create feature structure:
```bash
mkdir -p app/features/{nombre}/domain
mkdir -p app/features/{nombre}/application
mkdir -p app/features/{nombre}/infrastructure/persistence
mkdir -p app/features/{nombre}/infrastructure/web/templates/pages/{nombre}
```

2. Implement in order:
   - `domain/models.py` - Entity with validation
   - `domain/repositories.py` - Repository interface
   - `application/dtos.py` - Input/output DTOs
   - `application/commands.py` - Write operations
   - `application/queries.py` - Read operations
   - `infrastructure/persistence/models.py` - SQLAlchemy ORM
   - `infrastructure/persistence/sql_repository.py` - Repository impl
   - `infrastructure/web/routes.py` - Flask routes

3. Register blueprint in `app/routes/__init__.py`

4. Write tests:
   - `tests/unit/features/{nombre}/domain/`
   - `tests/unit/features/{nombre}/application/`
   - `tests/integration/features/{nombre}/infrastructure/`

---

*Last Updated:* March 2026
