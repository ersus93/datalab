# [Phase 8] CI/CD Pipeline & Automatización de Despliegue

**Labels:** `phase-8`, `devops`, `ci-cd`, `automation`, `high-priority`
**Milestone:** Phase 8: Production Hardening & Professional Excellence
**Estimated Effort:** 5 días
**Depends on:** Phase 1 (base de tests), Phase 7 (tests completos)

---

## Descripción

Actualmente el despliegue al VPS es manual: hacer SSH, hacer `git pull`, reiniciar Gunicorn. Esto es lento, propenso a errores, y no ejecuta los tests antes de desplegar — lo que significa que un bug puede llegar a producción sin detectarse.

Esta issue implementa un pipeline de CI/CD completo usando GitHub Actions que:
1. Ejecuta todos los tests en cada Pull Request
2. Verifica calidad de código (linting, type checking)
3. Construye y valida la aplicación
4. Despliega automáticamente a producción cuando se hace merge a `main`
5. Hace rollback automático si el despliegue falla

---

## Acceptance Criteria

### 1. Pipeline CI (Continuous Integration) — en cada PR

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [dev, main]
  pull_request:
    branches: [dev, main]

jobs:
  test:
    name: Tests & Quality
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: datalab_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      
      # 1. Formato de código
      - name: Check code formatting (Black)
        run: black --check app/ tests/
      
      # 2. Linting
      - name: Lint with Ruff
        run: ruff check app/ tests/
      
      # 3. Type checking
      - name: Type check with mypy
        run: mypy app/ --ignore-missing-imports
      
      # 4. Security check
      - name: Security scan with Bandit
        run: bandit -r app/ -ll  # Solo severidad media/alta
      
      # 5. Tests unitarios
      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/datalab_test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-not-for-production
          TESTING: 'true'
        run: |
          pytest tests/unit/ -v \
            --cov=app \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=70
      
      # 6. Tests de integración
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/datalab_test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-not-for-production
        run: |
          flask db upgrade  # Aplicar migraciones a la BD de test
          pytest tests/integration/ -v
      
      # 7. Coverage report
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
      
      # 8. Accesibilidad (no bloquea, solo reporta)
      - name: Start app for accessibility tests
        run: |
          flask run &
          sleep 5
      - name: Run pa11y accessibility check
        run: |
          npx pa11y http://localhost:5000/login --standard WCAG2AA --reporter json > pa11y-report.json || true
      - name: Upload pa11y report
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: pa11y-report.json

  docker-build:
    name: Docker Build Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t datalab:test .
      - name: Verify container starts
        run: |
          docker run -d --name test-container \
            -e SECRET_KEY=test \
            -e DATABASE_URL=sqlite:///test.db \
            datalab:test
          sleep 5
          docker exec test-container curl -f http://localhost:5000/health
          docker stop test-container
```

### 2. Pipeline CD (Continuous Deployment) — en merge a main

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy to VPS
    runs-on: ubuntu-latest
    environment: production  # Requiere aprobación manual en GitHub
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_PORT }}
          script: |
            set -e  # Salir si cualquier comando falla
            
            cd /var/www/datalab
            
            # Guardar commit actual para rollback
            PREVIOUS_COMMIT=$(git rev-parse HEAD)
            echo $PREVIOUS_COMMIT > /tmp/previous_commit
            
            # Actualizar código
            git fetch origin main
            git checkout main
            git pull origin main
            
            # Instalar/actualizar dependencias
            pip install -r requirements.txt --quiet
            
            # Aplicar migraciones de BD
            flask db upgrade
            
            # Recargar aplicación (zero-downtime con Gunicorn)
            kill -HUP $(cat /var/run/gunicorn.pid)
            
            # Verificar que la aplicación levantó correctamente
            sleep 5
            curl -f http://localhost:5000/health || {
                echo "❌ Health check falló. Ejecutando rollback..."
                git checkout $PREVIOUS_COMMIT
                pip install -r requirements.txt --quiet
                kill -HUP $(cat /var/run/gunicorn.pid)
                exit 1
            }
            
            echo "✅ Despliegue exitoso: $(git rev-parse --short HEAD)"
      
      - name: Notify Slack on success
        if: success()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "✅ DataLab desplegado exitosamente\nCommit: ${{ github.sha }}\nAutor: ${{ github.actor }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "❌ Fallo en despliegue de DataLab\nCommit: ${{ github.sha }}\nVer: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 3. Dockerfile para Producción

```dockerfile
# Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Dependencias del sistema (WeasyPrint necesita estas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Stage de dependencias (separado para cache)
FROM base AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage final
FROM base AS production
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY . .

# Usuario no-root para seguridad
RUN useradd -m -r datalab && chown -R datalab:datalab /app
USER datalab

EXPOSE 5000

# Health check integrado
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", \
     "--worker-class", "gthread", "--threads", "2", \
     "--timeout", "120", "--access-logfile", "-", \
     "run:app"]
```

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    image: datalab:${VERSION:-latest}
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    
  postgres:
    image: postgres:14
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      retries: 5
  
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
      - static_files:/app/static

volumes:
  postgres_data:
  static_files:
```

### 4. Pre-commit Hooks (Calidad Local)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
  
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit/ -x -q
        language: system
        pass_filenames: false
        stages: [commit]
```

```bash
# Instalación:
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg  # Para conventional commits
```

### 5. Environments de GitHub

```
main branch    → production environment (requiere aprobación)
dev branch     → staging environment (auto-deploy)
feature/*      → solo CI (no deploy)
```

**GitHub Secrets necesarios:**
```
VPS_HOST          → IP o dominio del servidor
VPS_USER          → usuario SSH
VPS_SSH_KEY       → clave privada SSH (sin passphrase)
VPS_PORT          → puerto SSH (default 22)
SECRET_KEY        → Flask secret key de producción
DATABASE_URL      → PostgreSQL de producción
SLACK_WEBHOOK_URL → para notificaciones (opcional)
```

---

## Tareas

- [ ] Crear `.github/workflows/ci.yml` con tests, linting, type checking
- [ ] Crear `.github/workflows/deploy.yml` con deploy al VPS y rollback automático
- [ ] Crear `Dockerfile` multi-stage optimizado para producción
- [ ] Crear `docker-compose.prod.yml`
- [ ] Configurar pre-commit hooks (ruff, black, detect-secrets)
- [ ] Agregar `requirements-dev.txt` con herramientas de desarrollo
- [ ] Configurar GitHub Secrets para producción
- [ ] Configurar environments de GitHub (staging, production)
- [ ] Verificar que el pipeline completo pasa en un PR de prueba
- [ ] Documentar proceso de despliegue en `docs/DEPLOYMENT.md`

---

## Archivos a crear

```
.github/
├── workflows/
│   ├── ci.yml
│   └── deploy.yml
├── PULL_REQUEST_TEMPLATE.md
└── CODEOWNERS
Dockerfile
docker-compose.prod.yml
docker-compose.monitoring.yml
.pre-commit-config.yaml
nginx/
└── nginx.conf
docs/
└── DEPLOYMENT.md
```

## Estimated Effort
**Story Points:** 13
**Estimated Time:** 5 días

## Related Issues
- Phase 7 #01-05 - Testing (los tests que el pipeline ejecuta)
- Phase 8 #03 - Observability (health check usado en deploy)
- Phase 8 #02 - Security (detect-secrets en pre-commit)
