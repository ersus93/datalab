/**
 * Dashboard JavaScript - DataLab
 * Maneja la inicialización de widgets, gráficos y actualización de datos
 * Issue #45 - Dashboard Widgets
 */

// Configuración global del dashboard
const DashboardConfig = {
    refreshInterval: 5 * 60 * 1000, // 5 minutos
    apiEndpoint: '/api/dashboard/full',
    chartColors: {
        RECIBIDO: '#6c757d',    // secondary/gray
        EN_PROCESO: '#0d6efd',  // primary/blue
        COMPLETADO: '#198754',  // success/green
        ENTREGADO: '#0dcaf0',   // info/cyan
        ANULADO: '#dc3545'      // danger/red
    },
    chartLabels: {
        RECIBIDO: 'Recibido',
        EN_PROCESO: 'En Proceso',
        COMPLETADO: 'Completado',
        ENTREGADO: 'Entregado',
        ANULADO: 'Anulado'
    }
};

// Estado global del dashboard
let dashboardState = {
    statusChart: null,
    lastUpdate: null,
    refreshTimer: null,
    currentPeriod: 30
};

/**
 * Inicializa el dashboard cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Inicializa todos los componentes del dashboard
 */
function initializeDashboard() {
    console.log('[Dashboard] Inicializando...');

    // Inicializar gráfico de tendencias
    initializeStatusChart();

    // Cargar datos iniciales
    loadDashboardData();

    // Configurar auto-refresh
    startAutoRefresh();

    // Configurar manejadores de eventos
    setupEventHandlers();

    console.log('[Dashboard] Inicialización completa');
}

/**
 * Inicializa el gráfico de tendencias de estados
 */
function initializeStatusChart() {
    const ctx = document.getElementById('statusTrendChart');
    if (!ctx) {
        console.warn('[Dashboard] Canvas no encontrado: statusTrendChart');
        return;
    }

    const statuses = ['RECIBIDO', 'EN_PROCESO', 'COMPLETADO', 'ENTREGADO', 'ANULADO'];
    const datasets = statuses.map(status => ({
        label: DashboardConfig.chartLabels[status],
        data: [],
        borderColor: DashboardConfig.chartColors[status],
        backgroundColor: DashboardConfig.chartColors[status] + '20',
        borderWidth: 2,
        tension: 0.4,
        fill: false,
        pointRadius: 3,
        pointHoverRadius: 6
    }));

    dashboardState.statusChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false // Usamos legend personalizado en HTML
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: { size: 13 },
                    bodyFont: { size: 12 },
                    padding: 10,
                    cornerRadius: 4,
                    callbacks: {
                        title: function(context) {
                            return 'Fecha: ' + context[0].label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: { size: 11 },
                        maxRotation: 45
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: { size: 11 },
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });

    console.log('[Dashboard] Gráfico de tendencias inicializado');
}

/**
 * Carga los datos del dashboard desde la API
 */
async function loadDashboardData() {
    try {
        showLoadingState();

        const response = await fetch(DashboardConfig.apiEndpoint);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.success) {
            updateDashboardWidgets(data.data);
            dashboardState.lastUpdate = new Date();
            console.log('[Dashboard] Datos actualizados:', dashboardState.lastUpdate);
        } else {
            throw new Error(data.error || 'Error desconocido del servidor');
        }
    } catch (error) {
        console.error('[Dashboard] Error cargando datos:', error);
        showErrorState(error.message);
    } finally {
        hideLoadingState();
    }
}

/**
 * Actualiza todos los widgets del dashboard con los datos recibidos
 */
function updateDashboardWidgets(data) {
    // Actualizar conteos de estados
    if (data.status_counts) {
        updateStatusCounts(data.status_counts);
    }

    // Actualizar gráfico de tendencias
    if (data.trends) {
        updateStatusChart(data.trends);
    }

    // Actualizar métricas principales si están disponibles
    if (data.metrics) {
        updateMetrics(data.metrics);
    }
}

/**
 * Actualiza las tarjetas de conteo de estados
 */
function updateStatusCounts(statusCounts) {
    const statuses = ['RECIBIDO', 'EN_PROCESO', 'COMPLETADO', 'ENTREGADO', 'ANULADO'];
    let total = 0;

    // Calcular total
    statuses.forEach(status => {
        total += statusCounts[status] || 0;
    });

    // Actualizar cada tarjeta
    statuses.forEach(status => {
        const count = statusCounts[status] || 0;
        const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : 0;

        // Actualizar conteo
        const countElement = document.querySelector(`.status-count[data-status="${status}"]`);
        if (countElement) {
            animateNumber(countElement, parseInt(countElement.textContent) || 0, count);
        }

        // Actualizar porcentaje
        const percentElement = document.querySelector(`.status-percent[data-status="${status}"]`);
        if (percentElement) {
            percentElement.textContent = `${percentage}%`;
        }

        // Actualizar barra de progreso
        const progressBar = document.querySelector(`.progress-bar[data-status="${status}"]`);
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
    });

    console.log('[Dashboard] Conteos de estado actualizados');
}

/**
 * Actualiza el gráfico de tendencias
 */
function updateStatusChart(trends) {
    if (!dashboardState.statusChart) {
        console.warn('[Dashboard] Gráfico no inicializado');
        return;
    }

    // Preparar datos
    const labels = trends.map(t => t.date || t.fecha);
    const statuses = ['RECIBIDO', 'EN_PROCESO', 'COMPLETADO', 'ENTREGADO', 'ANULADO'];

    dashboardState.statusChart.data.labels = labels;
    dashboardState.statusChart.data.datasets.forEach((dataset, index) => {
        const status = statuses[index];
        dataset.data = trends.map(t => t[status] || t[status.toLowerCase()] || 0);
    });

    dashboardState.statusChart.update('active');
    console.log('[Dashboard] Gráfico de tendencias actualizado');
}

/**
 * Actualiza las métricas principales
 */
function updateMetrics(metrics) {
    // Actualizar cada métrica si el elemento existe
    Object.keys(metrics).forEach(key => {
        const element = document.querySelector(`[data-metric="${key}"]`);
        if (element) {
            const value = metrics[key].value || metrics[key];
            element.textContent = formatNumber(value);
        }
    });
}

/**
 * Configura los manejadores de eventos
 */
function setupEventHandlers() {
    // Manejar visibilidad de página (pausar refresh cuando no visible)
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Configurar filtros de estado
    window.filterByStatus = function(status) {
        console.log('[Dashboard] Filtrando por estado:', status);
        // Redirigir a la lista con filtro
        window.location.href = `/entradas/listar?estado=${status}`;
    };

    // Configurar cambio de período
    window.updateTrendPeriod = function(period) {
        console.log('[Dashboard] Cambiando período a:', period);
        dashboardState.currentPeriod = period;

        // Actualizar botones activos
        document.querySelectorAll('[data-period]').forEach(btn => {
            btn.classList.remove('active');
            if (parseInt(btn.dataset.period) === period) {
                btn.classList.add('active');
            }
        });

        // Recargar datos con nuevo período
        loadDashboardData();
    };
}

/**
 * Maneja el cambio de visibilidad de la página
 */
function handleVisibilityChange() {
    if (document.hidden) {
        // Página oculta - pausar refresh
        stopAutoRefresh();
        console.log('[Dashboard] Auto-refresh pausado (página no visible)');
    } else {
        // Página visible - reanudar refresh
        startAutoRefresh();
        // Recargar datos si han pasado más de 2 minutos
        if (dashboardState.lastUpdate) {
            const elapsed = Date.now() - dashboardState.lastUpdate.getTime();
            if (elapsed > 2 * 60 * 1000) {
                loadDashboardData();
            }
        }
        console.log('[Dashboard] Auto-refresh reanudado');
    }
}

/**
 * Inicia el auto-refresh
 */
function startAutoRefresh() {
    if (dashboardState.refreshTimer) {
        clearInterval(dashboardState.refreshTimer);
    }
    dashboardState.refreshTimer = setInterval(loadDashboardData, DashboardConfig.refreshInterval);
}

/**
 * Detiene el auto-refresh
 */
function stopAutoRefresh() {
    if (dashboardState.refreshTimer) {
        clearInterval(dashboardState.refreshTimer);
        dashboardState.refreshTimer = null;
    }
}

/**
 * Muestra estado de carga
 */
function showLoadingState() {
    document.body.classList.add('dashboard-loading');
}

/**
 * Oculta estado de carga
 */
function hideLoadingState() {
    document.body.classList.remove('dashboard-loading');
}

/**
 * Muestra estado de error
 */
function showErrorState(message) {
    // Mostrar notificación de error (usando el sistema de notificaciones si existe)
    if (typeof DataLab !== 'undefined' && DataLab.showNotification) {
        DataLab.showNotification('Error al cargar datos del dashboard: ' + message, 'error');
    } else {
        console.error('[Dashboard] Error:', message);
    }

    // Marcar widgets como desactualizados
    document.querySelectorAll('.status-card').forEach(card => {
        card.classList.add('stale-data');
    });
}

/**
 * Anima un número de valor inicial a final
 */
function animateNumber(element, start, end, duration = 500) {
    const startTime = performance.now();
    const diff = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease-out cubic
        const current = Math.round(start + diff * easeProgress);

        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/**
 * Formatea un número con separadores de miles
 */
function formatNumber(value) {
    if (typeof value === 'number') {
        return value.toLocaleString();
    }
    return value;
}

// API pública del dashboard
window.DataLabDashboard = {
    refresh: loadDashboardData,
    getLastUpdate: () => dashboardState.lastUpdate,
    config: DashboardConfig
};
