# DataLab - Sistema de Gestión para Laboratorio ONIE

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask 3.0.0">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.35-FCA121?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0.35">
  <img src="https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL 14+">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT">
</p>

<p align="center">
  <b>LIMS (Laboratory Information Management System)</b> moderno para la <b>Oficina Nacional de Inspección Estatal (ONIE)</b> de Cuba.
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#arquitectura">Arquitectura</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#configuración">Configuración</a> •
  <a href="#uso">Uso</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## 📋 Descripción

**DataLab** es un sistema de gestión de laboratorio web moderno diseñado para reemplazar una base de datos Microsoft Access con más de **15 años de operación** (sistema RM2026). Gestiona aproximadamente **2,632 registros** distribuidos en **25 tablas** que cubren 4 áreas de laboratorio:

| Área | Descripción |
|------|-------------|
| 🔬 **FQ** | Físico-Químico |
| 🧫 **MB** | Microbiología |
| 👃 **ES** | Evaluación Sensorial |
| 📋 **OS** | Otros Servicios |

El sistema implementa una **arquitectura hexagonal (Ports & Adapters)** para garantizar mantenibilidad, escalabilidad y facilidad de testing.

---

## ✨ Características

### ✅ Implementadas

- [x] **Gestión de Clientes** - Clientes, fábricas y productos
- [x] **Catálogos de Ensayos** - Ensayos FQ y Evaluación Sensorial
- [x] **Órdenes de Trabajo** - Pedidos y gestión de solicitudes
- [x] **Sistema de Muestras** - Entradas y tracking de muestras
- [x] **Workflow de Estados** - Estados configurables para muestras
- [x] **Panel de Administración** - Con RBAC (Role-Based Access Control)
- [x] **Importación desde Access** - Migración de datos históricos
- [x] **Dashboard con Métricas** - Visualización interactiva con Plotly.js
- [x] **Búsqueda Global** - Búsqueda transversal en todas las entidades
- [x] **Sistema de Notificaciones** - Alertas y notificaciones en tiempo real
- [x] **i18n Completo** - Español (principal) e Inglés con GNU gettext

### 🔒 Seguridad

- Autenticación con **Flask-Login**
- Autorización **RBAC** (Admin, Manager, Técnico, Cliente)
- Protección **CSRF** en todos los formularios
- Hashing de contraseñas con **bcrypt**
- Gestión de sesiones segura
- **Audit logging** completo

---

## 🏗️ Arquitectura

### Patrón Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Routes     │  │  Templates   │  │  Static Assets   │  │
│  │   (Flask)    │  │   (Jinja2)   │  │  (Bootstrap 5)   │  │
│  └──────┬───────┘  └──────────────┘  └──────────────────┘  │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼ INBOUND PORTS
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              FEATURE MODULES (Bounded Contexts)        │ │
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌───────┐ ┌─────┐ │ │
│  │  │Clientes │ │Muestras │ │Ensayos │ │Órdenes│ │Repo-│ │ │
│  │  │ Feature │ │ Feature │ │Feature │ │Feature│ │rtes │ │ │
│  │  └────┬────┘ └────┬────┘ └───┬────┘ └───┬───┘ └──┬──┘ │ │
│  └───────┼───────────┼──────────┼──────────┼────────┼────┘ │
│          │           │          │          │        │      │
│  ┌───────┴───────────┴──────────┴──────────┴────────┴────┐ │
│  │              SHARED KERNEL (Core)                      │ │
│  │   ┌─────────────┐    ┌─────────────────────────────┐   │ │
│  │   │   Domain    │◄──►│    Infrastructure/Ports     │   │ │
│  │   │  (Entities) │    │   (Repository ABC, Adapters)│   │ │
│  │   └─────────────┘    └─────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
          ▼ OUTBOUND PORTS
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │    SQLite    │  │    Alembic       │  │
│  │  (Production)│  │ (Development)│  │  (Migrations)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Principios Arquitectónicos

| Principio | Implementación |
|-----------|----------------|
| **Separación de Concerns** | Features como bounded contexts independientes |
| **Dependency Inversion** | Puertos (interfaces) definen contratos, adaptadores implementan |
| **Single Responsibility** | Cada feature gestiona su propio dominio |
| **Open/Closed** | Extensible mediante nuevos features sin modificar existentes |

---

## 🛠️ Stack Tecnológico

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.11+ | Lenguaje principal |
| Flask | 3.0.0 | Framework web |
| SQLAlchemy | 2.0.35 | ORM y modelado de datos |
| Flask-SQLAlchemy | 3.1.1 | Integración Flask-SQLAlchemy |
| Flask-Login | 0.6.3 | Gestión de autenticación |
| Flask-WTF | 1.2.1 | Formularios y validación |
| Flask-Migrate | 4.0.7 | Migraciones de base de datos |
| Flask-Babel | 4.0.0 | Internacionalización (i18n) |
| Alembic | 1.13.2 | Migraciones de esquema |
| bcrypt | 4.2.0 | Hashing de contraseñas |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Bootstrap | 5.x | Framework CSS |
| Plotly.js | Última | Visualización de datos |
| DataTables | 1.13+ | Tablas interactivas |
| Jinja2 | 3.1.4 | Templating engine |

### Base de Datos

| Tecnología | Uso |
|------------|-----|
| PostgreSQL 14+ | Producción |
| SQLite | Desarrollo y testing |

### Testing

| Tecnología | Propósito |
|------------|-----------|
| pytest | Framework de testing |
| pytest-flask | Fixtures para Flask |
| pytest-cov | Cobertura de código |
| factory-boy | Generación de datos de test |

---

## 🚀 Instalación

### Prerrequisitos

- Python 3.11 o superior
- PostgreSQL 14+ (para producción)
- Git

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-organizacion/datalab.git
cd datalab
```

### Paso 2: Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones (ver sección [Configuración](#configuración)).

### Paso 5: Inicializar la base de datos

```bash
# Crear tablas
flask init_db

# O ejecutar migraciones
flask db upgrade
```

### Paso 6: Crear usuario administrador

```bash
flask create_admin
```

### Paso 7: Iniciar la aplicación

```bash
# Modo desarrollo
flask run

# O directamente
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

---

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta para sesiones | **REDACTED** |
| `DATABASE_URL` | URL de conexión a la base de datos | **REDACTED** |
| `FLASK_ENV` | Entorno de ejecución | `development` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `BABEL_DEFAULT_LOCALE` | Idioma por defecto | `es` |
| `BABEL_DEFAULT_TIMEZONE` | Zona horaria por defecto | `America/Havana` |

### Ejemplo de archivo `.env`

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=**REDACTED**

# Database
DATABASE_URL=**REDACTED**
# Para desarrollo con SQLite:
# DATABASE_URL=sqlite:///datalab.db

# Logging
LOG_LEVEL=INFO

# i18n
BABEL_DEFAULT_LOCALE=es
BABEL_DEFAULT_TIMEZONE=America/Havana
```

### Configuración de PostgreSQL (Producción)

```bash
# Formato de DATABASE_URL para PostgreSQL
postgresql://usuario:password@localhost:5432/datalab
```

---

## 📁 Estructura del Proyecto

```
datalab/
├── app/
│   ├── __init__.py              # Factory de aplicación Flask
│   ├── core/                    # Shared Kernel
│   │   ├── domain/              # Entidades y Repository ABC
│   │   │   ├── __init__.py
│   │   │   ├── base_entity.py   # Entidad base
│   │   │   └── repository.py    # Abstract Base Class para repos
│   │   └── infrastructure/      # Adaptadores de infraestructura
│   │       ├── __init__.py
│   │       └── database.py      # Configuración SQLAlchemy
│   ├── features/                # Módulos de negocio (Bounded Contexts)
│   │   ├── clientes/            # Feature: Gestión de Clientes
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   ├── muestras/            # Feature: Gestión de Muestras
│   │   ├── ensayos/             # Feature: Catálogo de Ensayos
│   │   ├── ordenes/             # Feature: Órdenes de Trabajo
│   │   └── reportes/            # Feature: Reportes y Dashboard
│   ├── database/                # Modelos legacy (en migración)
│   │   └── models/
│   ├── routes/                  # Rutas legacy (en migración)
│   ├── templates/               # Plantillas Jinja2
│   │   ├── base.html
│   │   ├── index.html
│   │   └── ...
│   ├── static/                  # Assets estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/                   # Utilidades compartidas
├── config/                      # Configuración de Flask
│   ├── __init__.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── docs/                        # Documentación
│   ├── PRD.md                   # Product Requirements Document
│   ├── analysis.md              # Análisis de sistema legacy
│   └── ...
├── locales/                     # Archivos de internacionalización
│   ├── messages.pot             # Template de traducciones
│   ├── es/                      # Español
│   │   └── LC_MESSAGES/
│   │       └── messages.po
│   └── en/                      # Inglés
│       └── LC_MESSAGES/
│           └── messages.po
├── migrations/                  # Migraciones Alembic
│   ├── versions/
│   └── env.py
├── ski/                         # Archivos de skill para agentes IA
├── tests/                       # Tests con pytest
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── requirements.txt             # Dependencias Python
├── requirements-dev.txt         # Dependencias de desarrollo
├── app.py                       # Punto de entrada
├── wsgi.py                      # Entry point para WSGI
├── .env.example                 # Ejemplo de variables de entorno
└── README.md                    # Este archivo
```

---

## 💻 Uso

### Comandos CLI

DataLab expone varios comandos personalizados a través de Flask CLI:

| Comando | Descripción |
|---------|-------------|
| `flask init_db` | Inicializar la base de datos |
| `flask create_admin` | Crear usuario administrador |
| `flask import_access` | Importar datos desde Access RM2026 |
| `flask export_data` | Exportar datos a CSV/Excel |
| `flask compile_translations` | Compilar archivos .po a .mo |
| `flask extract_messages` | Extraer cadenas para traducción |
| `flask update_translations` | Actualizar archivos de traducción |

### Gestión de Migraciones

```bash
# Crear una nueva migración
flask db migrate -m "Descripción de los cambios"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Ver historial
flask db history
```

### Internacionalización (i18n)

```bash
# Extraer cadenas traducibles
flask extract_messages

# Actualizar archivos de traducción
flask update_translations

# Compilar traducciones (después de editar .po)
flask compile_translations
```

### Importación desde Access

```bash
# Importar todos los datos
flask import_access --file "ruta/a/RM2026.accdb"

# Importar tabla específica
flask import_access --file "RM2026.accdb" --table "Clientes"
```

---

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/
pytest tests/integration/

# Tests con verbose
pytest -v

# Tests por patrón
pytest -k "test_cliente"
```

### Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos
├── unit/                    # Tests unitarios
│   ├── core/
│   ├── features/
│   └── utils/
├── integration/             # Tests de integración
│   ├── test_routes.py
│   └── test_database.py
└── e2e/                     # Tests end-to-end
    └── test_workflows.py
```

### Cobertura

```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term

# Abrir reporte HTML
# En Windows:
start htmlcov/index.html
# En Linux/macOS:
open htmlcov/index.html
```

---

## 🔐 Seguridad

### Autenticación y Autorización

El sistema implementa **RBAC** con los siguientes roles:

| Rol | Permisos |
|-----|----------|
| **Admin** | Acceso total al sistema |
| **Manager** | Gestión de usuarios, reportes, configuración |
| **Técnico** | Operaciones diarias, ensayos, muestras |
| **Cliente** | Consulta de sus propios datos y reportes |

### Medidas de Seguridad Implementadas

- ✅ **CSRF Protection** - Todos los formularios incluyen tokens CSRF
- ✅ **Password Hashing** - bcrypt con salt automático
- ✅ **Session Security** - Sesiones seguras con expiración
- ✅ **Audit Logging** - Registro de todas las operaciones críticas
- ✅ **Input Validation** - Validación de formularios con WTForms
- ✅ **SQL Injection Prevention** - Uso de SQLAlchemy ORM
- ✅ **XSS Protection** - Escapado automático en Jinja2

### Variables Sensibles

**NUNCA** commitear el archivo `.env` o exponer las siguientes variables:

- `SECRET_KEY`
- `DATABASE_URL` (si contiene credenciales)
- Cualquier token o clave API

---

## 🌍 Internacionalización (i18n)

DataLab soporta múltiples idiomas mediante **GNU gettext** y **Flask-Babel**.

### Idiomas Soportados

| Idioma | Código | Estado |
|--------|--------|--------|
| Español | `es` | ✅ Principal |
| Inglés | `en` | ✅ Completo |

### Cambiar Idioma

Los usuarios pueden cambiar el idioma desde el selector en la barra de navegación o mediante el parámetro `?lang=en` en la URL.

### Agregar Nuevo Idioma

```bash
# 1. Inicializar traducción para nuevo idioma (ej: fr - Francés)
pybabel init -i locales/messages.pot -d locales -l fr

# 2. Traducir cadenas en locales/fr/LC_MESSAGES/messages.po

# 3. Compilar
flask compile_translations
```

---

## 🤝 Contribución

¡Agradecemos las contribuciones! Sigue estos pasos:

### Workflow de Git

```
main (producción)
  ↑
dev (desarrollo)
  ↑
feat/nueva-funcionalidad
```

1. **Fork** el repositorio
2. Crea una **rama** desde `dev`: `git checkout -b feat/descripcion`
3. Realiza tus cambios siguiendo las [convenciones de commits](#convenciones-de-commits)
4. **Testea** tus cambios: `pytest`
5. **Push** a tu fork: `git push origin feat/descripcion`
6. Abre un **Pull Request** hacia la rama `dev`

### Convenciones de Commits

```
tipo(ámbito): descripción (#IssueID)

ejemplos:
feat(clientes): agregar búsqueda avanzada de clientes (#42)
fix(muestras): corregir validación de fechas (#38)
docs(readme): actualizar instrucciones de instalación
test(ordenes): agregar tests para workflow de estados
refactor(core): simplificar lógica de repositorios
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Estándares de Código

- Seguir **PEP 8** para código Python
- Usar **type hints** donde sea posible
- Documentar funciones y clases con **docstrings**
- Mantener cobertura de tests > 80%

---

## 🗺️ Roadmap

### Fase 1: Fundación ✅
- [x] Setup inicial del proyecto
- [x] Arquitectura hexagonal base
- [x] Autenticación y autorización
- [x] Panel de administración
- [x] Gestión de usuarios

### Fase 2: Core Features ✅
- [x] Gestión de clientes y fábricas
- [x] Catálogo de ensayos
- [x] Sistema de órdenes de trabajo
- [x] Workflow de muestras
- [x] Importación desde Access

### Fase 3: Reportes y Dashboards ✅
- [x] Dashboard principal con métricas
- [x] Reportes básicos
- [x] Visualizaciones con Plotly
- [x] Exportación a CSV/Excel

### Fase 4: Optimización y Escalabilidad 🚧
- [ ] Caché con Redis
- [ ] Optimización de queries
- [ ] Paginación en todas las tablas
- [ ] Búsqueda avanzada con Elasticsearch
- [ ] API REST completa

### Fase 5: Características Avanzadas 📋
- [ ] Workflows configurables
- [ ] Notificaciones por email
- [ ] Generación de certificados PDF
- [ ] Firma digital
- [ ] Integración con equipos de laboratorio (LIMS hardware)

### Fase 6: Producción 📋
- [ ] Deployment en servidor ONIE
- [ ] Backup automatizado
- [ ] Monitoreo y alerting
- [ ] Documentación de usuario final

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.

```
MIT License

Copyright (c) 2024 Oficina Nacional de Inspección Estatal (ONIE)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Créditos

Desarrollado con dedicación para la **Oficina Nacional de Inspección Estatal (ONIE)** de Cuba, institución cuyo rigor técnico y compromiso con la calidad alimentaria es la razón de ser de este proyecto.

---

### 🏛️ Legado: SistemaRM

DataLab no nace desde cero — es la evolución natural de un sistema que durante **más de 15 años** sostuvo las operaciones del laboratorio de química de alimentos de ONIE.

El **SistemaRM**, desarrollado en Microsoft Access, nació con un propósito concreto: la **Recepción de Muestras** de laboratorio. Con el tiempo, y gracias a la visión de su autor, fue creciendo orgánicamente hasta convertirse en una base de datos verdaderamente completa: gestión de clientes, fábricas, productos, ensayos por área (FQ, MB, ES), órdenes de trabajo, facturación y generación de informes oficiales. Lo que empezó como un registro de entradas se transformó en la memoria operativa del laboratorio.

Sus **25 tablas**, sus **consultas especializadas por área** y su lógica de negocio —acumulada y refinada a lo largo de más de una década— son la base conceptual sobre la que DataLab fue diseñado.

> *Toda migración exitosa comienza por entender y respetar profundamente lo que vino antes.*

Con el tiempo, las limitaciones inherentes a una solución de escritorio de archivo compartido —acceso monousuario, dependencia del sistema operativo, riesgo de corrupción de datos, ausencia de trazabilidad— hicieron necesaria esta transición hacia una plataforma web moderna. Pero esas limitaciones técnicas no deben opacar el mérito de lo logrado.

**Un reconocimiento especial a Rafael A. Ferro**, autor del SistemaRM, cuyo trabajo fue un pilar fundamental para la automatización y gestión de la información del laboratorio durante más de tres lustros. DataLab existe porque el SistemaRM funcionó — y funcionó bien.

---

### 🛠️ Tecnologías de Código Abierto

Este proyecto se construye sobre el trabajo de increíbles proyectos de código abierto:
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Plotly](https://plotly.com/javascript/) - Visualización de datos
- Y muchos más...

---

## 📞 Contacto

**Oficina Nacional de Inspección Estatal (ONIE)**
- 📧 Email: laboratorio@oniepr.alinet.cu
- 🌐 Web: https://www.minal.gob.cu

**Equipo de Desarrollo DataLab**
- 📧 Email: laboratorio@oniepr.alinet.cu
- 🐛 Issues: [GitHub Issues](https://github.com/datalabdev/datalab/issues)

---

<p align="center">
  <b>Desarrollado con ❤️ para la ciencia y la calidad</b>
</p>

