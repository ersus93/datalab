/**
 * Analytics Dashboard JavaScript - DataLab
 * Maneja la carga de datos y renderizado de gráficos con Plotly.js
 */

const AnalyticsDashboard = (function() {
    'use strict';

    // Configuración
    const config = {
        apiEndpoint: '/api/analytics/full',
        cacheInvalidateEndpoint: '/api/analytics/invalidate-cache',
        refreshInterval: 5 * 60 * 1000, // 5 minutos
        charts: {}
    };

    // Estado
    let state = {
        lastUpdate: null,
        refreshTimer: null,
        data: null
    };

    // Colores
    const colors = {
        primary: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#06b6d4',
        purple: '#8b5cf6',
        gray: '#6b7280'
    };

    /**
     * Inicializa el dashboard
     */
    function init() {
        console.log('[Analytics] Inicializando dashboard...');
        loadData();
        startAutoRefresh();
        setupEventHandlers();
    }

    /**
     * Configura manejadores de eventos
     */
    function setupEventHandlers() {
        // Pausar refresh cuando la página no está visible
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                stopAutoRefresh();
            } else {
                startAutoRefresh();
                loadData();
            }
        });
    }

    /**
     * Inicia el auto-refresh
     */
    function startAutoRefresh() {
        if (state.refreshTimer) {
            clearInterval(state.refreshTimer);
        }
        state.refreshTimer = setInterval(loadData, config.refreshInterval);
    }

    /**
     * Detiene el auto-refresh
     */
    function stopAutoRefresh() {
        if (state.refreshTimer) {
            clearInterval(state.refreshTimer);
            state.refreshTimer = null;
        }
    }

    /**
     * Carga los datos del dashboard
     */
    async function loadData() {
        try {
            console.log('[Analytics] Cargando datos...');
            const response = await fetch(config.apiEndpoint);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                state.data = result.data;
                state.lastUpdate = new Date();
                updateUI();
                console.log('[Analytics] Datos cargados:', state.lastUpdate);
            } else {
                throw new Error(result.error?.message || 'Error desconocido');
            }
        } catch (error) {
            console.error('[Analytics] Error cargando datos:', error);
            showError('Error al cargar datos: ' + error.message);
        }
    }

    /**
     * Actualiza la UI con los datos recibidos
     */
    function updateUI() {
        if (!state.data) return;

        updateKPIs();
        updateChartTimeline();
        updateChartMuestreos();
        updateChartESPending();
        updateChartFQPending();
        updateChartMBPending();
        updateTableLotes();
        updateLastUpdateTime();
    }

    /**
     * Actualiza los KPIs
     */
    function updateKPIs() {
        const kpis = state.data.kpis;
        if (!kpis) return;

        animateValue('kpi-pending', kpis.ensayos_pendientes || 0);
        animateValue('kpi-completed', kpis.ensayos_completados || 0);
        animateValue('kpi-month', kpis.completados_mes || 0);
        animateValue('kpi-entries', kpis.entradas_pendientes || 0);

        document.getElementById('cache-info').textContent = 
            kpis.timestamp ? new Date(kpis.timestamp).toLocaleTimeString('es-ES') : 'Sin datos';
    }

    /**
     * Actualiza el gráfico de timeline
     */
    function updateChartTimeline() {
        const data = state.data.completed_timeline;
        if (!data || !data.length) {
            renderEmptyChart('chart-timeline', 'Sin datos de timeline');
            return;
        }

        const x = data.map(d => d.month);
        const y = data.map(d => d.count);

        const trace = {
            x: x,
            y: y,
            type: 'scatter',
            mode: 'lines+markers',
            fill: 'tozeroy',
            line: { color: colors.primary, width: 3 },
            marker: { size: 8, color: colors.primary }
        };

        const layout = {
            margin: { t: 20, r: 20, b: 40, l: 50 },
            xaxis: { title: 'Mes', tickangle: -45 },
            yaxis: { title: 'Ensayos completados', rangemode: 'tozero' },
            font: { family: 'system-ui, sans-serif' },
            showlegend: false
        };

        Plotly.newPlot('chart-timeline', [trace], layout, { responsive: true });
    }

    /**
     * Actualiza el gráfico de muestreos por tipo cliente
     */
    function updateChartMuestreos() {
        const data = state.data.muestreos_by_client_type;
        if (!data || !data.pie || !data.pie.length) {
            renderEmptyChart('chart-muestreos', 'Sin datos de muestreos');
            return;
        }

        const labels = data.pie.map(d => d.tipo_cliente || 'Sin tipo');
        const values = data.pie.map(d => d.count);

        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: [colors.primary, colors.success, colors.warning, colors.info, colors.purple]
            },
            textinfo: 'label+percent',
            textposition: 'outside'
        };

        const layout = {
            margin: { t: 20, r: 20, b: 20, l: 20 },
            font: { family: 'system-ui, sans-serif' },
            showlegend: true,
            legend: { orientation: 'h', y: -0.1 }
        };

        Plotly.newPlot('chart-muestreos', [trace], layout, { responsive: true });
    }

    /**
     * Actualiza el gráfico de ES pendientes
     */
    function updateChartESPending() {
        const data = state.data.es_pending;
        if (!data || !data.length) {
            renderEmptyChart('chart-es-pending', 'Sin ensayos sensoriales pendientes');
            return;
        }

        const y = data.map(d => d.area || d.sigla);
        const x = data.map(d => d.count);

        const trace = {
            x: x,
            y: y,
            type: 'bar',
            orientation: 'h',
            marker: { color: colors.warning }
        };

        const layout = {
            margin: { t: 20, r: 20, b: 40, l: 100 },
            xaxis: { title: 'Cantidad', rangemode: 'tozero' },
            font: { family: 'system-ui, sans-serif' },
            showlegend: false
        };

        Plotly.newPlot('chart-es-pending', [trace], layout, { responsive: true });
    }

    /**
     * Actualiza el gráfico de FQ pendientes
     */
    function updateChartFQPending() {
        const data = state.data.fq_pending;
        if (!data || !data.length) {
            renderEmptyChart('chart-fq-pending', 'Sin análisis FQ pendientes');
            return;
        }

        // Agrupar por área
        const areas = {};
        data.forEach(d => {
            const area = d.area || d.sigla;
            areas[area] = (areas[area] || 0) + d.count;
        });

        const labels = Object.keys(areas);
        const values = Object.values(areas);

        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: [colors.info, colors.primary, colors.success, colors.purple]
            },
            textinfo: 'label+percent'
        };

        const layout = {
            margin: { t: 20, r: 20, b: 20, l: 20 },
            font: { family: 'system-ui, sans-serif' },
            showlegend: true,
            legend: { orientation: 'h', y: -0.1 }
        };

        Plotly.newPlot('chart-fq-pending', [trace], layout, { responsive: true });
    }

    /**
     * Actualiza el gráfico de MB pendientes por técnico
     */
    function updateChartMBPending() {
        const data = state.data.mb_pending_by_tech;
        if (!data || !data.length) {
            renderEmptyChart('chart-mb-pending', 'Sin ensayos de microbiología pendientes');
            return;
        }

        const y = data.map(d => d.tecnico || 'Sin asignar');
        const x = data.map(d => d.count);

        const trace = {
            x: x,
            y: y,
            type: 'bar',
            orientation: 'h',
            marker: { color: colors.success }
        };

        const layout = {
            margin: { t: 20, r: 20, b: 40, l: 120 },
            xaxis: { title: 'Cantidad', rangemode: 'tozero' },
            font: { family: 'system-ui, sans-serif' },
            showlegend: false
        };

        Plotly.newPlot('chart-mb-pending', [trace], layout, { responsive: true });
    }

    /**
     * Actualiza la tabla de lotes
     */
    function updateTableLotes() {
        const data = state.data.lotes_by_type_client;
        const tbody = document.querySelector('#table-lotes tbody');
        
        if (!data || !data.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Sin datos disponibles</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(row => `
            <tr>
                <td>${row.tipo_muestra || 'Sin tipo'}</td>
                <td>${row.cliente || 'Sin cliente'}</td>
                <td class="text-end">${row.count}</td>
            </tr>
        `).join('');
    }

    /**
     * Renderiza un gráfico vacío
     */
    function renderEmptyChart(elementId, message) {
        const layout = {
            xaxis: { showgrid: false, showticklabels: false },
            yaxis: { showgrid: false, showticklabels: false },
            annotations: [{
                text: message,
                showarrow: false,
                font: { size: 14, color: '#9ca3af' }
            }],
            margin: { t: 40, r: 40, b: 40, l: 40 }
        };
        
        Plotly.newPlot(elementId, [], layout, { responsive: true });
    }

    /**
     * Actualiza el tiempo de última actualización
     */
    function updateLastUpdateTime() {
        const element = document.getElementById('last-update');
        if (element && state.lastUpdate) {
            element.textContent = state.lastUpdate.toLocaleString('es-ES');
        }
    }

    /**
     * Anima un valor numérico
     */
    function animateValue(elementId, end) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const start = parseInt(element.textContent) || 0;
        if (start === end) return;

        const duration = 500;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (end - start) * easeProgress);

            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }

    /**
     * Muestra un error
     */
    function showError(message) {
        // Usar el sistema de notificaciones si está disponible
        if (typeof DataLab !== 'undefined' && DataLab.showNotification) {
            DataLab.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }

    /**
     * Refresca los datos manualmente
     */
    function refresh() {
        loadData();
    }

    /**
     * Limpia la caché
     */
    async function clearCache() {
        if (!confirm('¿Está seguro de que desea limpiar la caché?')) {
            return;
        }

        try {
            const response = await fetch(config.cacheInvalidateEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();
            
            if (result.success) {
                showNotification('Caché limpiada correctamente');
                loadData(); // Recargar datos
            } else {
                throw new Error(result.error?.message || 'Error al limpiar caché');
            }
        } catch (error) {
            console.error('[Analytics] Error limpiando caché:', error);
            showError('Error al limpiar caché: ' + error.message);
        }
    }

    /**
     * Muestra una notificación
     */
    function showNotification(message) {
        if (typeof DataLab !== 'undefined' && DataLab.showNotification) {
            DataLab.showNotification(message, 'success');
        } else {
            console.log('[Analytics]', message);
        }
    }

    // API pública
    return {
        init: init,
        refresh: refresh,
        clearCache: clearCache
    };
})();