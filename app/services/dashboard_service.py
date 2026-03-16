"""Servicio de Dashboard - Métricas y widgets para el panel principal."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, desc, cast, Date

from app import db


class DashboardService:
    """
    Servicio para generar datos de dashboard.

    Proporciona métricas agregadas y tendencias para widgets
    del panel principal. Diseñado para consultas eficientes
    que evitan problemas N+1.
    """

    # TODO: Implementar caché con TTL de 5 minutos para datos del dashboard
    # CACHE_TTL = 300  # segundos

    @staticmethod
    def get_sample_status_counts() -> Dict[str, int]:
        """
        Obtener conteo de muestras por estado.

        Realiza una consulta agregada eficiente que cuenta
        entradas agrupadas por status.

        Returns:
            Dict[str, int]: Diccionario con conteos por estado:
                - RECIBIDO: Muestras recibidas pendientes
                - EN_PROCESO: En análisis
                - COMPLETADO: Análisis terminado, pendiente entrega
                - ENTREGADO: Entregadas al cliente
                - ANULADO: Anuladas/canceladas
        """
        from app.database.models.entrada import Entrada, EntradaStatus

        # Consulta agregada para evitar N+1
        results = db.session.query(
            Entrada.status,
            func.count(Entrada.id).label('count')
        ).group_by(Entrada.status).all()

        # Inicializar con ceros para todos los estados
        counts = {
            EntradaStatus.RECIBIDO: 0,
            EntradaStatus.EN_PROCESO: 0,
            EntradaStatus.COMPLETADO: 0,
            EntradaStatus.ENTREGADO: 0,
            EntradaStatus.ANULADO: 0
        }

        # Actualizar con resultados de la consulta
        for status, count in results:
            if status in counts:
                counts[status] = count

        return counts

    @staticmethod
    def get_status_trends(days: int = 30) -> List[Dict[str, Any]]:
        """
        Obtener tendencias de cambios de estado en el tiempo.

        Analiza el historial de estados para generar una serie
        temporal de muestras por estado por día.

        Args:
            days: Número de días hacia atrás a analizar (default: 30)

        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con formato:
                [
                    {
                        'date': '2026-03-01',
                        'RECIBIDO': 5,
                        'EN_PROCESO': 10,
                        'COMPLETADO': 3,
                        'ENTREGADO': 8,
                        'ANULADO': 0
                    },
                    ...
                ]
        """
        from app.database.models.entrada import EntradaStatus
        from app.database.models.status_history import StatusHistory

        # Calcular rango de fechas
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days - 1)

        # Consulta agregada por fecha y estado
        results = db.session.query(
            cast(StatusHistory.changed_at, Date).label('date'),
            StatusHistory.to_status,
            func.count(StatusHistory.id).label('count')
        ).filter(
            cast(StatusHistory.changed_at, Date) >= start_date,
            cast(StatusHistory.changed_at, Date) <= end_date
        ).group_by(
            cast(StatusHistory.changed_at, Date),
            StatusHistory.to_status
        ).order_by(
            cast(StatusHistory.changed_at, Date)
        ).all()

        # Organizar resultados por fecha
        trends_by_date: Dict[str, Dict[str, int]] = {}
        all_statuses = [
            EntradaStatus.RECIBIDO,
            EntradaStatus.EN_PROCESO,
            EntradaStatus.COMPLETADO,
            EntradaStatus.ENTREGADO,
            EntradaStatus.ANULADO
        ]

        # Inicializar todas las fechas del rango con ceros
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            trends_by_date[date_str] = {status: 0 for status in all_statuses}
            current_date += timedelta(days=1)

        # Poblar con datos reales
        for date_val, status, count in results:
            date_str = date_val.isoformat() if isinstance(date_val, datetime) else str(date_val)
            if date_str in trends_by_date and status in trends_by_date[date_str]:
                trends_by_date[date_str][status] = count

        # Convertir a lista ordenada por fecha
        trends_list = [
            {'date': date_str, **counts}
            for date_str, counts in sorted(trends_by_date.items())
        ]

        return trends_list

    @staticmethod
    def get_recent_activity(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener actividad reciente de cambios de estado.

        Recupera las últimas entradas del historial de estados
        con información relacionada.

        Args:
            limit: Cantidad máxima de registros a retornar (default: 10)

        Returns:
            List[Dict[str, Any]]: Lista de cambios de estado recientes
            con información serializable.
        """
        from app.database.models.status_history import StatusHistory

        # Consulta con join eficiente
        results = db.session.query(StatusHistory).options(
            db.joinedload(StatusHistory.entrada),
            db.joinedload(StatusHistory.changed_by)
        ).order_by(
            desc(StatusHistory.changed_at)
        ).limit(limit).all()

        # Convertir a diccionarios
        activity_list = []
        for history in results:
            activity_dict = history.to_dict()
            # Agregar información de la entrada relacionada
            if history.entrada:
                activity_dict['entrada'] = {
                    'id': history.entrada.id,
                    'codigo': history.entrada.codigo,
                    'producto': history.entrada.producto.nombre if history.entrada.producto else None,
                    'cliente': history.entrada.cliente.nombre if history.entrada.cliente else None
                }
            activity_list.append(activity_dict)

        return activity_list

    @staticmethod
    def get_pending_deliveries() -> List[Dict[str, Any]]:
        """
        Obtener muestras con saldo pendiente de entrega.

        Busca entradas que tienen estado COMPLETADO (análisis terminado)
        pero aún tienen saldo > 0 (pendiente de entregar al cliente).

        Returns:
            List[Dict[str, Any]]: Lista de entradas pendientes de entrega
            ordenadas por fecha de entrada (más antiguas primero).
        """
        from app.database.models.entrada import Entrada, EntradaStatus

        # Consulta eficiente con joins para evitar N+1
        results = db.session.query(Entrada).options(
            db.joinedload(Entrada.producto),
            db.joinedload(Entrada.cliente),
            db.joinedload(Entrada.fabrica)
        ).filter(
            Entrada.status == EntradaStatus.COMPLETADO,
            Entrada.saldo > 0,
            Entrada.anulado == False  # noqa: E712
        ).order_by(
            Entrada.fech_entrada.asc()
        ).all()

        # Convertir a diccionarios
        pending_list = []
        for entrada in results:
            pending_dict = entrada.to_dict()
            # Agregar información adicional útil para el dashboard
            pending_dict['dias_pendiente'] = (
                datetime.utcnow().date() - entrada.fech_entrada.date()
            ).days if entrada.fech_entrada else 0
            pending_list.append(pending_dict)

        return pending_list

    @staticmethod
    def get_full_dashboard_data() -> Dict[str, Any]:
        """
        Obtener todos los datos del dashboard en una sola llamada.

        Combina todas las métricas individuales en un único
        diccionario para el consumo del frontend.

        Returns:
            Dict[str, Any]: Diccionario completo con:
                - status_counts: Conteos por estado
                - status_trends: Tendencias últimos 30 días
                - recent_activity: Últimos 10 cambios
                - pending_deliveries: Muestras pendientes de entrega
                - timestamp: Fecha/hora de generación
        """
        return {
            'status_counts': DashboardService.get_sample_status_counts(),
            'status_trends': DashboardService.get_status_trends(days=30),
            'recent_activity': DashboardService.get_recent_activity(limit=10),
            'pending_deliveries': DashboardService.get_pending_deliveries(),
            'timestamp': datetime.utcnow().isoformat()
        }
