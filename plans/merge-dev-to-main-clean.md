# Plan: Merge Clean dev → main

## Descripción
Este documento define qué archivos excluir al hacer merge de la rama `dev` a `main` para mantener un proyecto limpio y profesional.

## Archivos/Directorios a **EXCLUIR** del merge

| Archivo/Directorio | Razón |
|---|---|
| `check_*.py` | Scripts de verificación de desarrollo |
| `crear_admin.py` | Script de administración |
| `fix_encoding.py` | Script de utilities |
| `import_*.py` | Scripts de importación de datos |
| `seed_*.py` | Scripts de seeding |
| `test_import.py` | Script de test |
| `config/` | Configuración local |
| `data/` | Datos de desarrollo |
| `docs/` | Documentación extensa |
| `locales/` | Traducciones locales |
| `plans/` | Planes de desarrollo |
| `tests/` | Tests |

## Archivos/Directorios a **INCLUIR** en main

| Archivo/Directorio | Razón |
|---|---|
| `.env.example` | Ejemplo de configuración |
| `.gitignore` | Configuración de git |
| `AGENTS.md` | Configuración de agentes |
| `app.py` | Archivo principal de la app |
| `README.md` | Documentación principal |
| `requirements.txt` | Dependencias Python |
| `tailwind.config.js` | Configuración de Tailwind |
| `app/` | Código de la aplicación |
| `.github/` | Configuración de CI/CD |
| `migrations/` | Migraciones de base de datos |

## Comandos para ejecutar

```bash
# 1. Asegurarse estar en main y tener los últimos cambios
git checkout main
git pull origin main

# 2. Hacer merge de dev
git merge dev

# 3. Eliminar archivos de desarrollo (si el merge los trae)
rm -rf check_*.py crear_admin.py fix_encoding.py
rm -rf import_*.py seed_*.py test_import.py
rm -rf config/ data/ docs/ locales/ plans/ tests/

# 4. Commit de la limpieza
git add -A
git commit -m "Clean: remove development files from main"

# 5. Push a main
git push origin main
```

## Fecha de creación
2026-03-17
