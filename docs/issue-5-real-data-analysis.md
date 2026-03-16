# DataLab — Análisis de Datos Reales del Access
## Hallazgos Críticos para la Migración Phase 4

**Generado:** 2026-03-06  
**Fuentes:** `RM2026_be.accdb` (extracción directa)

---

## ⚠️ HALLAZGO CRÍTICO: `Utilizado R` ≠ Lo que describe el issue

El issue-5 describe `Utilizado R` como una tabla de uso por ensayo con campos `IdEns`, `Precio`, `Importe`.  
**La tabla real tiene una estructura completamente diferente:**

### Estructura real de `Utilizado R` (632 filas)

| Campo | Tipo | Descripción real |
|-------|------|-----------------|
| `IdEnt` | INTEGER | ID de entrada (FK a `Entradas`) — pero con IDs 1978–2628, NO los 9391–9501 actuales |
| `Mes` | INTEGER | Número de mes (1–4 en los datos: ene, feb, mar, abr) |
| `IdUM` | INTEGER | Unidad de medida (1=Kg, 2=L, 3=unidades aprox.) |
| `CantEnt` | FLOAT | Cantidad total de muestra entregada |
| `CantCont` | FLOAT | Cantidad para control |
| `CantFQ` | FLOAT | Cantidad consumida en área Físico-Química |
| `CantMB` | FLOAT | Cantidad consumida en área Microbiología |
| `CantES` | FLOAT | Cantidad consumida en área Evaluación Sensorial |
| `ValeNo` | VARCHAR | Número de vale/referencia (ej: "001", "019", "") |

**Lo que NO tiene la tabla real:** `IdEns` (no hay FK a ensayo individual), `Precio`, `Importe`, `FechReal`, `Hora`, `Anno`.

### Interpretación correcta
`Utilizado R` es una tabla de **consumo de muestra por entrada**, desglosado por área de laboratorio. NO es una tabla de "uso por ensayo específico con precio". Es más un registro de logística de muestras/materiales que de facturación por ensayo.

---

## Estructura real de `Detalles de ensayos` (563 filas)

### Columnas reales

| Campo | Tipo | Valores de muestra |
|-------|------|--------------------|
| `IdEnt` | INTEGER | 9391–9501 (IDs legacy de las 109 entradas actuales) |
| `IdEns` | INTEGER | 1–144 (IDs de ensayos del catálogo FQ) |
| `Cantidad` | INTEGER | Siempre 1 en los datos observados |
| `FechReal` | DATETIME | **Vacío en todos los registros** ("") |

**Observaciones críticas:**
- `FechReal` está vacío en todas las filas — no hay fechas de realización en el Access
- Solo hay ensayos FQ (`IdEns` 1–144) — los ensayos ES (29-34 por ID numérico) no aparecen
- Los IDs `IdEnt` coinciden exactamente con los `IdEnt` de la tabla `Entradas` actual
- Hay ~5–8 ensayos por entrada típicamente

---

## Estructura real de `Entradas` (109 filas)

Tiene muchos más campos que los registrados en el issue:

| Campo real | Descripción |
|-----------|-------------|
| `IdEnt` | ID legacy (9391–9501) |
| `RE` | Código de registro (ej: "1-0001") |
| `IdPed` | FK a Pedido |
| `IdPro` | FK a Producto |
| `FechaProd` | Fecha de producción |
| `CondMue` | Condición de muestra |
| `IdentMue` | Identificación del lote/muestra (texto) |
| `CantMue` | Cantidad de muestra (texto, ej: "1.6Kg") |
| `NoMue` | Número de muestras |
| `NoFQ`, `NoMB`, `NoES`, `NoEN`, `NoMC` | Cantidad de ensayos por área |
| `IdDest` | FK a Destino |
| `IdTipoES` | FK a Tipo ES |
| `IdUM` | FK a UM |
| `CantEnt`, `CantCont`, `CantFQ`, `CantMB`, `CantES` | Cantidades procesadas |
| `ValeNo` | Número de vale |

---

## Comparación: Esquema del Issue vs. Datos Reales

| Aspecto | Descripción en Issue-5 | Realidad en Access |
|---------|----------------------|-------------------|
| `Utilizado R` tiene `IdEns` | ✓ (asumido) | ✗ NO existe |
| `Utilizado R` tiene `Precio` | ✓ (asumido) | ✗ NO existe |
| `Utilizado R` tiene `Importe` | ✓ (asumido) | ✗ NO existe |
| `Utilizado R` vincula entradas | ✓ | ✓ pero con IDs históricos distintos |
| `Utilizado R` es archivo de uso | Uso por ensayo | Consumo de muestra por área |
| `Detalles de ensayos` tiene fechas | ✓ (FechReal) | ✗ Vacío en todos los registros |
| Los IDs `IdEnt` coinciden | Asumido 1:1 | Solo para `Detalles` (9391–9501); `Utilizado R` tiene IDs 1978–2628 |

---

## Impacto en el Plan de Migración

### `Detalles de ensayos` → `detalles_ensayo`

**VIABLE con ajustes menores:**

```python
# Mapeo de campos Access → Web App
mapeo = {
    "IdEnt": "entrada_id",    # Requiere lookup: IdEnt legacy → id nuevo
    "IdEns": "ensayo_id",     # Requiere lookup: IdEns legacy → id nuevo  
    "Cantidad": "cantidad",   # Directo
    "FechReal": None,         # Campo vacío — omitir, dejar NULL
}
# Estado default: "PENDIENTE"
```

**Desafío:** Los `IdEnt` en Access son 9391–9501 pero en la web app serán IDs secuenciales 1–109. Necesitas una tabla de mapeo legacy_id → new_id.

### `Utilizado R` → ??? 

**REQUIERE REDISEÑO DEL MODELO:**

La tabla real NO tiene `IdEns`, por lo que no puede mapearse directamente al modelo `Utilizado` actual que requiere `ensayo_id`. Las opciones son:

**Opción A:** Importar `Utilizado R` como tabla de consumo de muestra por área (no de facturación). Necesitaría un modelo nuevo o adaptar `Utilizado` para no requerir `ensayo_id`.

**Opción B:** Descontinuar la importación de `Utilizado R` al modelo actual `utilizados`. El modelo de facturación de la web app generará sus propios registros de `utilizados` a medida que los ensayos se completen.

**Opción C (recomendada):** Crear un modelo separado `ConsumoMuestra` o `UtilizadoHistorico` que refleje exactamente esta estructura del Access para preservar el historial, sin interferir con el modelo de facturación futuro.

---

## Resumen de Archivos Extraídos

### Directorio: `C:\Users\ernes\datalab\utiles\extracted\`

```
extracted/
├── full_extraction.json          # Toda la extracción (schemas + datos)
├── migration_report.md           # Reporte completo con checklist
├── backend/
│   ├── schema.json               # Esquemas de las 25 tablas
│   └── data/
│       ├── Annos.csv/.json              (10 filas)
│       ├── Areas.csv/.json              (4 filas)
│       ├── Clientes.csv/.json           (166 filas)
│       ├── Destinos.csv/.json           (7 filas)
│       ├── Detalles_de_ensayos.csv/.json (563 filas) ← PHASE 4
│       ├── Ensayos.csv/.json            (143 filas)
│       ├── EnsayosES.csv/.json          (29 filas)
│       ├── Entradas.csv/.json           (109 filas)
│       ├── Fabricas.csv/.json           (403 filas)
│       ├── Informes.csv/.json           (20 filas)
│       ├── Meses.csv/.json              (12 filas)
│       ├── Ordenes_de_trabajo.csv/.json (37 filas)
│       ├── Organismos.csv/.json         (12 filas)
│       ├── Pedidos.csv/.json            (49 filas)
│       ├── Productos.csv/.json          (160 filas)
│       ├── Provincias.csv/.json         (4 filas)
│       ├── Ramas.csv/.json              (13 filas)
│       ├── Tipo_ES.csv/.json            (4 filas)
│       ├── UM.csv/.json                 (3 filas)
│       └── Utilizado_R.csv/.json        (632 filas) ← REVISAR DISEÑO
└── frontend/
    ├── schema.json               # Sin tablas
    └── queries.sql               # 18 queries del frontend
```

### Directorio: `C:\Users\ernes\datalab\data\migrations\`
Archivos CSV listos para el servicio de importación:
- `detalles_ensayos.csv` — 563 filas, campos: `IdEnt, IdEns, Cantidad, FechReal`
- `utilizado_r.csv` — 632 filas, campos: `IdEnt, Mes, IdUM, CantEnt, CantCont, CantFQ, CantMB, CantES, ValeNo`
- `ensayos.csv`, `ensayos_es.csv`, `entradas.csv`, `clientes.csv`, `fabricas.csv`, `productos.csv`, `ordenes_trabajo.csv`, `pedidos.csv`

---

## Próximos Pasos Recomendados

1. **Antes de escribir `phase4_import_service.py`:** decidir qué hacer con `Utilizado R` (Opción A/B/C arriba)
2. **Construir tabla de mapeo ID legacy→new** para `Entradas` y `Ensayos` (ya que los IDs del Access no serán los mismos en la web app)
3. **Importar `Detalles de ensayos`** — viable con el mapeo de IDs
4. **Crear migración Alembic** para `utilizados` y `facturas` (pendiente crítico)
5. **Revisar si los 143 `Ensayos` del Access** ya fueron importados correctamente y verificar la correspondencia de IDs
