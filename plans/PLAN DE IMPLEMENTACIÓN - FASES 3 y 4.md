📋 PLAN DE IMPLEMENTACIÓN - FASES 3 Y 4
Enfoque: Fase 3 → Fase 4  
Arquitectura: Mantener estructura actual (routes + Jinja2)  
Plazo: 1-2 semanas  
Testing: Máximo nivel
---
🎯 RESUMEN DE PENDIENTES
Fase	Componente
Fase 3	UI Entrada de Muestras
Fase 3	Workflow Estados UI
Fase 3	Pedidos UI
Fase 3	Import Datos Transaccional
Fase 4	Asignación de Ensayos UI
Fase 4	Tracking Ejecución
Fase 4	Dashboard Análisis
Fase 4	Billing/Facturación
---
📅 SEMANA 1: Completar Fase 3
Día 1: Auditoría y Validación de Existentes
#	Tarea
1.1	Revisar templates entradas/ existentes vs modelos
1.2	Probar endpoints API entradas_api.py con curl/Postman
1.3	Validar workflow de estados en modelo vs UI
1.4	Ejecutar tests unitarios existentes
Tiempo estimado: 4 horas
---
Día 2: Completar UI de Entradas
#	Tarea
2.1	Completar template entradas/form.html faltantes
2.2	Agregar validación de lote (X-XXXX) en JS
2.3	Completar widget de balance en entradas/ver.html
2.4	Agregar botones de transición de estado
Tiempo estimado: 4 horas
---
Día 3: Pedidos y Orders Workflow
#	Tarea
3.1	Revisar pedidos/form.html vs modelo
3.2	Agregar linking Entrada→Pedido en UI
3.3	Validar workflow OrdenTrabajo→Pedido→Entrada
3.4	Ejecutar tests de integración test_pedido_workflow.py
Tiempo estimado: 4 horas
---
Día 4: Validación y Fixes Fase 3
#	Tarea
4.1	Revisar y ejecutar phase3_import_service.py
4.2	Fix de bugs encontrados en testing
4.3	Tests de regresión completos
4.4	Code review de cambios
Tiempo estimado: 4 horas
---
📅 SEMANA 2: Completar Fase 4
Día 5: Sistema de Asignación de Ensayos
#	Tarea
5.1	Revisar template entradas/ensayos/asignacion.html
5.2	Completar multi-select de ensayos
5.3	Integrar con API detalle_ensayo_api.py
5.4	Validar state machine transitions en UI
Tiempo estimado: 4 horas
---
Día 6: Tracking de Ejecución
#	Tarea
6.1	Crear vista de ejecución por técnico
6.2	Agregar timeline de estados
6.3	Completar tecnico/ejecutar.html
6.4	Tests de integración test_orden_trabajo_workflow.py
Tiempo estimado: 4 horas
---
Día 7: Dashboard y Análisis
#	Tarea
7.1	Crear dashboard de laboratorio lab/area.html
7.2	Métricas de rendimiento por área
7.3	Completar tecnico/metricas.html
7.4	Tests de modelo test_detalle_ensayo_model.py
Tiempo estimado: 4 horas
---
Día 8: Facturación y Cierre
#	Tarea
8.1	Completar UI de billing billing/index.html
8.2	Integrar billing_api.py con UI
8.3	Tests finales de integración
8.4	Documentación de cambios
Tiempo estimado: 4 horas
---
🧪 ESTRATEGIA DE TESTING
Nivel	Alcance
Unitario	Modelos (Entrada, DetalleEnsayo, Pedido)
Integración	Workflows completos
Funcional	UI completa
E2E	Flujos críticos
---
⚠️ RIESGOS IDENTIFICADOS
Riesgo
Datos transaccionales no importan
Transiciones de estado fallan
UI no funciona con datos reales
Performance con 500+ ensayos
---
## ✅ CRITERIOS DE ÉXITO
- [ ] Todos los tests unitarios pasando (`pytest tests/unit/`)
- [ ] Todos los tests de integración pasando (`pytest tests/integration/`)
- [ ] Cobertura de código > 80% en modelos de Fase 3-4
- [ ] UI de entradas con workflow de estados funcionando
- [ ] UI de asignación de ensayos funcional
- [ ] Dashboard de laboratorio mostrando métricas
- [ ] Sistema de facturación creando facturas
---