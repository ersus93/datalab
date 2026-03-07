# Billing Reports - Phase 5 Implementation Plan

> **For Claude:** Use subagent-driven-development to implement this plan task-by-task.

**Goal:** Implement complete billing and invoicing system for laboratory services with Excel export, report generation by client/period/assay type, and prevention of double billing.

**Architecture:** Extends existing BillingService with Excel export, report generation, and invoice validation. Uses openpyxl for Excel files.

**Tech Stack:** Python, Flask, SQLAlchemy, openpyxl

---

## Task 1: Extend Factura model with tipo_factura (A/B/C) ✅

**Status:** COMPLETED

- Added `TipoFactura` enum (A/B/C) to `app/database/models/utilizado.py`
- Added `tipo_factura` field to Factura model with default value B

## Task 2: Add openpyxl dependency ✅

**Status:** COMPLETED

- Added `openpyxl>=3.1.0` to requirements.txt

## Task 3: Create Excel export service ✅

**Status:** COMPLETED

- Created `app/services/excel_export_service.py` with:
  - `export_factura()` - Export single invoice to Excel
  - `export_reporte_cliente()` - Export usage report by client

## Task 4: Add double billing prevention ✅

**Status:** COMPLETED

- Added `verificar_disponible_para_facturacion()` method to BillingService
- Modified `generar_factura()` to use validation and accept tipo_factura parameter

## Task 5: Add report generation endpoints ✅

**Status:** COMPLETED

- Added `/api/billing/facturas/<id>/excel` - Download invoice as Excel
- Added `/api/billing/reportes/cliente/<id>/excel` - Download client usage report

---

## Summary of Changes

- **Model:** Added `tipo_factura` enum (A/B/C) to Factura model
- **Service:** Created `ExcelExportService` for Excel export functionality
- **Service:** Added `verificar_disponible_para_facturacion()` to prevent double billing
- **Routes:** Added `/api/billing/facturas/<id>/excel` and `/api/billing/reportes/cliente/<id>/excel` endpoints
- **Dependencies:** Added `openpyxl` to requirements.txt

## Notes

- Moneda: ARS (pesos argentinos)
- Prevention of double billing implemented through validation before invoice creation
- Excel export includes styling with brand colors (#003366)
- All existing billing functionality preserved and extended
