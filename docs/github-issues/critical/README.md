# Critical Issues - DataLab

Este directorio contiene issues críticos que bloquean el desarrollo y deben resolverse con máxima prioridad.

## Issues Activos

| Issue | Título | Prioridad | Estado | GitHub |
|-------|--------|-----------|--------|--------|
| #36 | Fix missing clientes feature module | CRITICAL | 🔴 Pendiente | [Ver](https://github.com/ersus93/datalab/issues/36) |
| #38 | Create missing database migrations | CRITICAL | 🔴 Pendiente | [Ver](https://github.com/ersus93/datalab/issues/38) |
| #40 | Execute reference data seeding | HIGH | 🟡 Bloqueado | [Ver](https://github.com/ersus93/datalab/issues/40) |

## Dependencias

```
Issue #36 (Fix clientes module)
    ↓
Issue #38 (Create migrations)
    ↓
Issue #40 (Seed reference data)
```

## Resumen de Problemas

### Issue #36 - ImportError
La aplicación no inicia porque falta el módulo `app.features.clientes.infrastructure.web.routes`

**Solución rápida:** Usar rutas legacy temporalmente

### Issue #38 - Migraciones faltantes
Solo existe 1 migración para 22 tablas necesarias.

**Impacto:** Las relaciones de clave foránea fallarán.

### Issue #40 - Datos de referencia
El script de seed existe pero no se ha ejecutado.

**Prerequisito:** Las tablas deben existir (Issue #38).

## Próximos Pasos

1. Resolver Issue #36 para que la app inicie
2. Generar migraciones con `flask db migrate`
3. Aplicar migraciones con `flask db upgrade`
4. Ejecutar seed con `flask seed-reference`
5. Verificar con tests

## Created
2026-03-04
