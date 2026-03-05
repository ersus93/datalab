/**
 * DataLab Notifications Module
 * Maneja el centro de notificaciones, polling y actualizaciones en tiempo real
 * Issue #45 - Notification Center
 */

const NotificationSystem = {
    // Configuración
    config: {
        pollInterval: 30000, // 30 segundos
        maxRetries: 3,
        retryDelay: 5000,
        pageSize: 10
    },

    // Estado
    state: {
        unreadCount: 0,
        notifications: [],
        currentFilter: 'all',
        currentPage: 1,
        totalPages: 1,
        selectedIds: new Set(),
        pollTimer: null,
        isPolling: false
    },

    // Iconos por tipo de notificación
    icons: {
        status_change: { icon: 'fa-exchange-alt', color: 'bg-blue-100 text-blue-600' },
        delivery: { icon: 'fa-truck', color: 'bg-green-100 text-green-600' },
        alert: { icon: 'fa-exclamation-triangle', color: 'bg-yellow-100 text-yellow-600' },
        info: { icon: 'fa-info-circle', color: 'bg-gray-100 text-gray-600' },
        success: { icon: 'fa-check-circle', color: 'bg-green-100 text-green-600' },
        warning: { icon: 'fa-exclamation-circle', color: 'bg-orange-100 text-orange-600' },
        error: { icon: 'fa-times-circle', color: 'bg-red-100 text-red-600' },
        entrada: { icon: 'fa-file-alt', color: 'bg-purple-100 text-purple-600' },
        pedido: { icon: 'fa-shopping-cart', color: 'bg-indigo-100 text-indigo-600' },
        default: { icon: 'fa-bell', color: 'bg-gray-100 text-gray-600' }
    },

    /**
     * Inicializa el sistema de notificaciones
     */
    init() {
        this.initDropdown();
        this.initCenter();
        this.startPolling();
        this.setupEventListeners();
        console.log('NotificationSystem initialized');
    },

    /**
     * Inicializa el dropdown de notificaciones
     */
    initDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (!dropdown) return;

        // Cargar notificaciones iniciales
        this.loadDropdownNotifications();
    },

    /**
     * Inicializa el centro de notificaciones (página completa)
     */
    initCenter() {
        const container = document.getElementById('notifications-container');
        if (!container) return;

        this.loadCenterNotifications();
    },

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Dropdown: Marcar todo como leído
        const markAllReadBtn = document.getElementById('mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.markAllAsRead();
            });
        }

        // Centro: Tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.dataset.filter;
                this.switchTab(filter);
            });
        });

        // Centro: Seleccionar todo
        const selectAllCheckbox = document.getElementById('select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Centro: Acciones masivas
        const bulkMarkRead = document.getElementById('bulk-mark-read');
        const bulkDelete = document.getElementById('bulk-delete');

        if (bulkMarkRead) {
            bulkMarkRead.addEventListener('click', () => this.bulkMarkAsRead());
        }
        if (bulkDelete) {
            bulkDelete.addEventListener('click', () => this.bulkDelete());
        }

        // Centro: Paginación
        const prevPage = document.getElementById('prev-page');
        const nextPage = document.getElementById('next-page');

        if (prevPage) {
            prevPage.addEventListener('click', () => this.changePage(this.state.currentPage - 1));
        }
        if (nextPage) {
            nextPage.addEventListener('click', () => this.changePage(this.state.currentPage + 1));
        }
    },

    /**
     * Inicia el polling para nuevas notificaciones
     */
    startPolling() {
        if (this.state.isPolling) return;
        
        this.state.isPolling = true;
        this.poll();
        
        this.state.pollTimer = setInterval(() => {
            this.poll();
        }, this.config.pollInterval);
    },

    /**
     * Detiene el polling
     */
    stopPolling() {
        if (this.state.pollTimer) {
            clearInterval(this.state.pollTimer);
            this.state.pollTimer = null;
        }
        this.state.isPolling = false;
    },

    /**
     * Realiza una petición de polling
     */
    async poll() {
        try {
            const response = await fetch('/api/notifications/unread-count');
            if (!response.ok) throw new Error('Poll failed');
            
            const data = await response.json();
            this.updateBadge(data.count);
            
            // Si hay nuevas notificaciones, recargar el dropdown
            if (data.count > this.state.unreadCount) {
                this.loadDropdownNotifications();
            }
            
            this.state.unreadCount = data.count;
        } catch (error) {
            console.error('Polling error:', error);
        }
    },

    /**
     * Carga las notificaciones para el dropdown
     */
    async loadDropdownNotifications() {
        const loadingEl = document.getElementById('notification-loading');
        const emptyEl = document.getElementById('notification-empty');
        const itemsEl = document.getElementById('notification-items');

        if (loadingEl) loadingEl.classList.remove('hidden');
        if (emptyEl) emptyEl.classList.add('hidden');
        if (itemsEl) itemsEl.classList.add('hidden');

        try {
            const response = await fetch('/api/notifications?limit=5');
            if (!response.ok) throw new Error('Failed to load notifications');

            const data = await response.json();

            if (loadingEl) loadingEl.classList.add('hidden');

            if (data.notifications.length === 0) {
                if (emptyEl) emptyEl.classList.remove('hidden');
            } else {
                if (itemsEl) {
                    itemsEl.innerHTML = data.notifications.map(n => this.renderDropdownItem(n)).join('');
                    itemsEl.classList.remove('hidden');
                }
            }

            this.updateBadge(data.unread_count);
        } catch (error) {
            console.error('Error loading dropdown notifications:', error);
            if (loadingEl) loadingEl.classList.add('hidden');
            if (emptyEl) {
                emptyEl.querySelector('p').textContent = 'Error al cargar notificaciones';
                emptyEl.classList.remove('hidden');
            }
        }
    },

    /**
     * Renderiza un item para el dropdown
     */
    renderDropdownItem(notification) {
        const style = this.icons[notification.type] || this.icons.default;
        const timeAgo = this.formatTimeAgo(notification.created_at);
        const unreadClass = notification.is_read ? '' : 'bg-blue-50';

        return `
            <a href="${notification.link || '#'}" 
               class="block px-4 py-3 hover:bg-gray-100 border-b border-gray-100 last:border-0 ${unreadClass}"
               data-notification-id="${notification.id}"
               onclick="NotificationSystem.markAsRead(${notification.id}, event)">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full ${style.color} flex items-center justify-center">
                        <i class="fas ${style.icon} text-sm"></i>
                    </div>
                    <div class="flex-grow min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">${this.escapeHtml(notification.title)}</p>
                        <p class="text-xs text-gray-600 line-clamp-1">${this.escapeHtml(notification.message)}</p>
                        <p class="text-xs text-gray-400 mt-1">${timeAgo}</p>
                    </div>
                    ${!notification.is_read ? '<span class="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></span>' : ''}
                </div>
            </a>
        `;
    },

    /**
     * Carga las notificaciones para el centro
     */
    async loadCenterNotifications() {
        const loadingEl = document.getElementById('center-loading');
        const itemsEl = document.getElementById('notification-list-items');

        if (loadingEl) loadingEl.classList.remove('hidden');
        if (itemsEl) itemsEl.classList.add('hidden');

        // Ocultar estados vacíos
        document.getElementById('empty-all')?.classList.add('hidden');
        document.getElementById('empty-unread')?.classList.add('hidden');
        document.getElementById('empty-read')?.classList.add('hidden');

        try {
            const params = new URLSearchParams({
                page: this.state.currentPage,
                per_page: this.config.pageSize,
                filter: this.state.currentFilter
            });

            const response = await fetch(`/api/notifications?${params}`);
            if (!response.ok) throw new Error('Failed to load notifications');

            const data = await response.json();
            this.state.notifications = data.notifications;
            this.state.totalPages = data.total_pages || 1;

            if (loadingEl) loadingEl.classList.add('hidden');

            if (data.notifications.length === 0) {
                // Mostrar estado vacío según el filtro
                const emptyId = `empty-${this.state.currentFilter}`;
                const emptyEl = document.getElementById(emptyId);
                if (emptyEl) emptyEl.classList.remove('hidden');
            } else {
                if (itemsEl) {
                    itemsEl.innerHTML = data.notifications.map(n => this.renderCenterItem(n)).join('');
                    itemsEl.classList.remove('hidden');
                    this.attachItemListeners();
                }
            }

            this.updatePagination(data);
            this.updateCounts(data.counts);
        } catch (error) {
            console.error('Error loading center notifications:', error);
            if (loadingEl) loadingEl.classList.add('hidden');
        }
    },

    /**
     * Renderiza un item para el centro de notificaciones
     */
    renderCenterItem(notification) {
        const template = document.getElementById('notification-item-template');
        if (!template) return '';

        const clone = template.content.cloneNode(true);
        const item = clone.querySelector('.notification-item');
        const style = this.icons[notification.type] || this.icons.default;

        item.dataset.notificationId = notification.id;
        item.querySelector('.notification-checkbox').value = notification.id;
        item.querySelector('.notification-checkbox').checked = this.state.selectedIds.has(notification.id);

        const iconContainer = item.querySelector('.notification-icon');
        iconContainer.classList.add(...style.color.split(' '));
        iconContainer.querySelector('i').classList.add(style.icon);

        item.querySelector('.notification-title').textContent = notification.title;
        item.querySelector('.notification-message').textContent = notification.message;
        item.querySelector('.notification-time').textContent = this.formatTimeAgo(notification.created_at);

        const link = item.querySelector('.notification-link');
        if (notification.link) {
            link.href = notification.link;
        } else {
            link.classList.add('hidden');
        }

        // Mostrar/ocultar indicadores según estado
        if (!notification.is_read) {
            item.querySelector('.notification-unread-indicator').classList.remove('hidden');
            item.querySelector('.notification-mark-read').classList.remove('hidden');
            item.querySelector('.notification-mark-unread').classList.add('hidden');
        } else {
            item.querySelector('.notification-unread-indicator').classList.add('hidden');
            item.querySelector('.notification-mark-read').classList.add('hidden');
            item.querySelector('.notification-mark-unread').classList.remove('hidden');
        }

        const wrapper = document.createElement('div');
        wrapper.appendChild(item);
        return wrapper.innerHTML;
    },

    /**
     * Adjunta listeners a los items renderizados
     */
    attachItemListeners() {
        // Checkboxes
        document.querySelectorAll('.notification-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const id = parseInt(e.target.value);
                if (e.target.checked) {
                    this.state.selectedIds.add(id);
                } else {
                    this.state.selectedIds.delete(id);
                }
                this.updateBulkActions();
            });
        });

        // Botones de marcar como leída
        document.querySelectorAll('.notification-mark-read').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.closest('.notification-item').dataset.notificationId);
                this.markAsRead(id);
            });
        });

        // Botones de marcar como no leída
        document.querySelectorAll('.notification-mark-unread').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.closest('.notification-item').dataset.notificationId);
                this.markAsUnread(id);
            });
        });

        // Botones de eliminar
        document.querySelectorAll('.notification-delete').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.closest('.notification-item').dataset.notificationId);
                this.deleteNotification(id);
            });
        });
    },

    /**
     * Marca una notificación como leída
     */
    async markAsRead(id, event = null) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        try {
            const response = await fetch(`/api/notifications/${id}/mark-read`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to mark as read');

            // Actualizar UI
            this.loadDropdownNotifications();
            this.loadCenterNotifications();

            // Si hay evento, navegar al link
            if (event) {
                const link = event.currentTarget.href;
                if (link && link !== '#') {
                    window.location.href = link;
                }
            }
        } catch (error) {
            console.error('Error marking as read:', error);
            this.showToast('Error al marcar como leída', 'error');
        }
    },

    /**
     * Marca una notificación como no leída
     */
    async markAsUnread(id) {
        try {
            const response = await fetch(`/api/notifications/${id}/mark-unread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to mark as unread');

            this.loadDropdownNotifications();
            this.loadCenterNotifications();
        } catch (error) {
            console.error('Error marking as unread:', error);
            this.showToast('Error al marcar como no leída', 'error');
        }
    },

    /**
     * Marca todas las notificaciones como leídas
     */
    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to mark all as read');

            this.loadDropdownNotifications();
            this.loadCenterNotifications();
            this.showToast('Todas las notificaciones marcadas como leídas', 'success');
        } catch (error) {
            console.error('Error marking all as read:', error);
            this.showToast('Error al marcar todas como leídas', 'error');
        }
    },

    /**
     * Elimina una notificación
     */
    async deleteNotification(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar esta notificación?')) {
            return;
        }

        try {
            const response = await fetch(`/api/notifications/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete notification');

            this.loadDropdownNotifications();
            this.loadCenterNotifications();
            this.showToast('Notificación eliminada', 'success');
        } catch (error) {
            console.error('Error deleting notification:', error);
            this.showToast('Error al eliminar la notificación', 'error');
        }
    },

    /**
     * Marca seleccionadas como leídas
     */
    async bulkMarkAsRead() {
        const ids = Array.from(this.state.selectedIds);
        if (ids.length === 0) return;

        try {
            const response = await fetch('/api/notifications/bulk-mark-read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids })
            });

            if (!response.ok) throw new Error('Failed to bulk mark as read');

            this.state.selectedIds.clear();
            this.loadDropdownNotifications();
            this.loadCenterNotifications();
            this.showToast(`${ids.length} notificaciones marcadas como leídas`, 'success');
        } catch (error) {
            console.error('Error in bulk mark as read:', error);
            this.showToast('Error al marcar notificaciones', 'error');
        }
    },

    /**
     * Elimina notificaciones seleccionadas
     */
    async bulkDelete() {
        const ids = Array.from(this.state.selectedIds);
        if (ids.length === 0) return;

        if (!confirm(`¿Estás seguro de que deseas eliminar ${ids.length} notificaciones?`)) {
            return;
        }

        try {
            const response = await fetch('/api/notifications/bulk-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids })
            });

            if (!response.ok) throw new Error('Failed to bulk delete');

            this.state.selectedIds.clear();
            this.loadDropdownNotifications();
            this.loadCenterNotifications();
            this.showToast(`${ids.length} notificaciones eliminadas`, 'success');
        } catch (error) {
            console.error('Error in bulk delete:', error);
            this.showToast('Error al eliminar notificaciones', 'error');
        }
    },

    /**
     * Cambia el tab activo
     */
    switchTab(filter) {
        this.state.currentFilter = filter;
        this.state.currentPage = 1;
        this.state.selectedIds.clear();

        // Actualizar tabs UI
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.dataset.filter === filter) {
                btn.classList.remove('border-transparent', 'text-gray-500');
                btn.classList.add('border-blue-500', 'text-blue-600');
            } else {
                btn.classList.add('border-transparent', 'text-gray-500');
                btn.classList.remove('border-blue-500', 'text-blue-600');
            }
        });

        this.loadCenterNotifications();
    },

    /**
     * Cambia de página
     */
    changePage(page) {
        if (page < 1 || page > this.state.totalPages) return;
        this.state.currentPage = page;
        this.loadCenterNotifications();
    },

    /**
     * Selecciona/deselecciona todas las notificaciones
     */
    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.notification-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            const id = parseInt(checkbox.value);
            if (checked) {
                this.state.selectedIds.add(id);
            } else {
                this.state.selectedIds.delete(id);
            }
        });
        this.updateBulkActions();
    },

    /**
     * Actualiza los botones de acciones masivas
     */
    updateBulkActions() {
        const hasSelection = this.state.selectedIds.size > 0;
        const bulkMarkRead = document.getElementById('bulk-mark-read');
        const bulkDelete = document.getElementById('bulk-delete');

        if (bulkMarkRead) bulkMarkRead.disabled = !hasSelection;
        if (bulkDelete) bulkDelete.disabled = !hasSelection;

        // Actualizar checkbox "seleccionar todo"
        const selectAll = document.getElementById('select-all');
        if (selectAll) {
            const checkboxes = document.querySelectorAll('.notification-checkbox');
            const checkedBoxes = document.querySelectorAll('.notification-checkbox:checked');
            selectAll.checked = checkboxes.length > 0 && checkboxes.length === checkedBoxes.length;
            selectAll.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < checkboxes.length;
        }
    },

    /**
     * Actualiza el badge de notificaciones
     */
    updateBadge(count) {
        const badges = document.querySelectorAll('#notification-badge, .notification-badge');
        badges.forEach(badge => {
            if (count > 0) {
                badge.classList.remove('hidden');
                badge.classList.add('notification-badge--pulse');
                badge.textContent = count > 99 ? '99+' : count;
                badge.dataset.count = count;
            } else {
                badge.classList.add('hidden');
                badge.classList.remove('notification-badge--pulse');
                badge.dataset.count = 0;
            }
        });
    },

    /**
     * Actualiza la paginación
     */
    updatePagination(data) {
        const container = document.getElementById('pagination-container');
        const start = document.getElementById('pagination-start');
        const end = document.getElementById('pagination-end');
        const total = document.getElementById('pagination-total');
        const current = document.getElementById('current-page');
        const pages = document.getElementById('total-pages');
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');

        if (!container || !data.total) {
            if (container) container.classList.add('hidden');
            return;
        }

        container.classList.remove('hidden');
        
        const startNum = ((this.state.currentPage - 1) * this.config.pageSize) + 1;
        const endNum = Math.min(this.state.currentPage * this.config.pageSize, data.total);

        if (start) start.textContent = startNum;
        if (end) end.textContent = endNum;
        if (total) total.textContent = data.total;
        if (current) current.textContent = this.state.currentPage;
        if (pages) pages.textContent = this.state.totalPages;

        if (prevBtn) prevBtn.disabled = this.state.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.state.currentPage >= this.state.totalPages;
    },

    /**
     * Actualiza los contadores de los tabs
     */
    updateCounts(counts) {
        if (counts) {
            const allCount = document.getElementById('count-all');
            const unreadCount = document.getElementById('count-unread');
            const readCount = document.getElementById('count-read');

            if (allCount) allCount.textContent = counts.all || 0;
            if (unreadCount) unreadCount.textContent = counts.unread || 0;
            if (readCount) readCount.textContent = counts.read || 0;
        }
    },

    /**
     * Formatea tiempo relativo
     */
    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'hace un momento';
        if (seconds < 3600) return `hace ${Math.floor(seconds / 60)} min`;
        if (seconds < 86400) return `hace ${Math.floor(seconds / 3600)} h`;
        if (seconds < 604800) return `hace ${Math.floor(seconds / 86400)} d`;
        
        return date.toLocaleDateString('es-ES');
    },

    /**
     * Escapa HTML para prevenir XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Muestra un toast notification
     */
    showToast(message, type = 'info') {
        if (window.DataLab && window.DataLab.showToast) {
            window.DataLab.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
};

/**
 * NotificationCenter - Wrapper para la página completa
 */
const NotificationCenter = {
    init() {
        NotificationSystem.initCenter();
    }
};

// Exportar al scope global
window.NotificationSystem = NotificationSystem;
window.NotificationCenter = NotificationCenter;

// Auto-inicializar si estamos en el dropdown
if (document.getElementById('notification-dropdown')) {
    document.addEventListener('DOMContentLoaded', () => {
        NotificationSystem.init();
    });
}

/*
 * =====================================================
 * WEBSOCKET SUPPORT (Comentado - Listo para implementar)
 * =====================================================
 * 
 * Para habilitar WebSocket en lugar de polling:
 * 
 * 1. Descomentar el siguiente código
 * 2. Configurar el servidor WebSocket (Socket.io, ws, etc.)
 * 3. Ajustar la URL de conexión
 * 
 * =====================================================
 */

/*
const WebSocketNotifications = {
    socket: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    reconnectDelay: 3000,

    connect() {
        const wsUrl = window.location.protocol === 'https:' 
            ? `wss://${window.location.host}/ws/notifications`
            : `ws://${window.location.host}/ws/notifications`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            
            // Autenticar
            this.socket.send(JSON.stringify({
                type: 'auth',
                token: this.getAuthToken()
            }));
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            this.attemptReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    },
    
    handleMessage(data) {
        switch(data.type) {
            case 'new_notification':
                NotificationSystem.updateBadge(data.unread_count);
                NotificationSystem.loadDropdownNotifications();
                NotificationSystem.showToast(data.notification.title, 'info');
                break;
                
            case 'notification_read':
                NotificationSystem.updateBadge(data.unread_count);
                break;
                
            case 'notification_count':
                NotificationSystem.updateBadge(data.count);
                break;
        }
    },
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), this.reconnectDelay);
        }
    },
    
    getAuthToken() {
        // Obtener token de autenticación (cookie, localStorage, etc.)
        return document.querySelector('meta[name="csrf-token"]')?.content || '';
    },
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
};

// Para usar WebSocket en lugar de polling:
// 1. Comentar NotificationSystem.startPolling()
// 2. Descomentar: WebSocketNotifications.connect();
*/