"""Servicio de Analytics para Dashboard de Análisis de Laboratorio."""
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, desc, cast, Date

from app import db
from app.utils.cache import cache, CACHE_TTL_DEFAULT


class AnalyticsService:
    """Servicio para generar datos de analytics del laboratorio.

    Proporciona métricas para los 6 reportes principales del dashboard:
    1. Análisis Sensorial Pendiente (ES)
    2. Análisis FQ Pendiente
    3. Microbiología Pendiente (MB)
    4. Determinaciones Realizadas (timeline)
    5. Lotes Analizados
    6. Muestreos por Tipo Cliente
    """

    CACHE_PREFIX = "analytics"

    @staticmethod
    def _get_cache_key(method_name: str, **kwargs) -> str:
        """Generar clave de caché."""
        params = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{AnalyticsService.CACHE_PREFIX}:{method_name}:{params}"

    @staticmethod
    def get_es_pending() -> List[Dict[str, Any]]:
        """Obtener ensayos sensoriales pendientes por área.

        Returns:
            Lista de áreas con conteo de ensayos ES pendientes.
        """
        from app.database.models.ensayo_es import EnsayoES
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.reference import Area

        cache_key = AnalyticsService._get_cache_key("es_pending")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        pendientes = [
            DetalleEnsayoStatus.PENDIENTE.value,
            DetalleEnsayoStatus.ASIGNADO.value,
            DetalleEnsayoStatus.EN_PROCESO.value,
        ]

        results = db.session.query(
            Area.nombre,
            Area.sigla,
            func.count(DetalleEnsayo.id).label('count')
        ).join(
            EnsayoES, EnsayoES.area_id == Area.id
        ).join(
            DetalleEnsayo, DetalleEnsayo.ensayo_id == EnsayoES.id
        ).filter(
            DetalleEnsayo.estado.in_(pendientes)
        ).group_by(
            Area.id, Area.nombre, Area.sigla
        ).all()

        data = [
            {"area": r.nombre, "sigla": r.sigla, "count": r.count}
            for r in results
        ]

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_fq_pending() -> List[Dict[str, Any]]:
        """Obtener ensayos físico-químicos pendientes.

        Returns:
            Lista de ensayos FQ con conteo de pendientes.
        """
        from app.database.models.ensayo import Ensayo
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.reference import Area

        cache_key = AnalyticsService._get_cache_key("fq_pending")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        pendientes = [
            DetalleEnsayoStatus.PENDIENTE.value,
            DetalleEnsayoStatus.ASIGNADO.value,
            DetalleEnsayoStatus.EN_PROCESO.value,
        ]

        results = db.session.query(
            Area.nombre,
            Area.sigla,
            Ensayo.nombre_corto,
            func.count(DetalleEnsayo.id).label('count')
        ).join(
            Ensayo, Ensayo.area_id == Area.id
        ).join(
            DetalleEnsayo, DetalleEnsayo.ensayo_id == Ensayo.id
        ).filter(
            DetalleEnsayo.estado.in_(pendientes)
        ).group_by(
            Area.id, Area.nombre, Area.sigla, Ensayo.id, Ensayo.nombre_corto
        ).all()

        data = [
            {"area": r.nombre, "sigla": r.sigla, "ensayo": r.nombre_corto, "count": r.count}
            for r in results
        ]

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_mb_pending_by_tech() -> List[Dict[str, Any]]:
        """Obtener ensayos de microbiología pendientes agrupados por técnico.

        Returns:
            Lista de técnicos con conteo de ensayos MB pendientes.
        """
        from app.database.models.ensayo import Ensayo
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.reference import Area
        from app.database.models.user import User

        cache_key = AnalyticsService._get_cache_key("mb_pending_by_tech")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        pendientes = [
            DetalleEnsayoStatus.PENDIENTE.value,
            DetalleEnsayoStatus.ASIGNADO.value,
            DetalleEnsayoStatus.EN_PROCESO.value,
        ]

        results = db.session.query(
            User.id,
            User.nombre_completo,
            func.count(DetalleEnsayo.id).label('count')
        ).join(
            DetalleEnsayo, DetalleEnsayo.tecnico_asignado_id == User.id
        ).join(
            Ensayo, DetalleEnsayo.ensayo_id == Ensayo.id
        ).join(
            Area, Ensayo.area_id == Area.id
        ).filter(
            Area.sigla == 'MB',
            DetalleEnsayo.estado.in_(pendientes)
        ).group_by(
            User.id, User.nombre_completo
        ).all()

        data = [
            {"tecnico_id": r.id, "tecnico": r.nombre_completo, "count": r.count}
            for r in results
        ]

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_completed_timeline(months: int = 12) -> List[Dict[str, Any]]:
        """Obtener timeline de determinaciones completadas por mes.

        Args:
            months: Número de meses hacia atrás a analizar (default: 12)

        Returns:
            Lista de meses con conteo de ensayos completados.
        """
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        cache_key = AnalyticsService._get_cache_key("completed_timeline", months=months)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)

        results = db.session.query(
            func.strftime('%Y-%m', DetalleEnsayo.fecha_completado).label('month'),
            func.count(DetalleEnsayo.id).label('count')
        ).filter(
            DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
            DetalleEnsayo.fecha_completado >= start_date
        ).group_by(
            func.strftime('%Y-%m', DetalleEnsayo.fecha_completado)
        ).order_by(
            func.strftime('%Y-%m', DetalleEnsayo.fecha_completado)
        ).all()

        data = [{"month": r.month, "count": r.count} for r in results]

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_lotes_by_type_client() -> List[Dict[str, Any]]:
        """Obtener lotes analizados agrupados por tipo de muestra y cliente.

        Returns:
            Lista de tipos de muestra con conteo por cliente.
        """
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.database.models.rama import Rama
        from app.database.models.cliente import Cliente

        cache_key = AnalyticsService._get_cache_key("lotes_by_type_client")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        results = db.session.query(
            Rama.nombre.label('tipo_muestra'),
            Cliente.nombre.label('cliente'),
            func.count(Entrada.id).label('count')
        ).outerjoin(
            Rama, Entrada.rama_id == Rama.id
        ).outerjoin(
            Cliente, Entrada.cliente_id == Cliente.id
        ).filter(
            Entrada.status.in_([
                EntradaStatus.COMPLETADO.value,
                EntradaStatus.ENTREGADO.value
            ]),
            Entrada.anulado == False
        ).group_by(
            Rama.nombre, Cliente.nombre
        ).order_by(
            desc('count')
        ).limit(50).all()

        data = [
            {
                "tipo_muestra": r.tipo_muestra or "Sin tipo",
                "cliente": r.cliente or "Sin cliente",
                "count": r.count
            }
            for r in results
        ]

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_muestreos_by_client_type() -> Dict[str, List[Dict[str, Any]]]:
        """Obtener muestreos agrupados por tipo de cliente.

        Returns:
            Diccionario con datos para area chart y pie chart.
        """
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.database.models.cliente import Cliente

        cache_key = AnalyticsService._get_cache_key("muestreos_by_client_type")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        results = db.session.query(
            Cliente.tipo.label('tipo_cliente'),
            func.count(Entrada.id).label('count')
        ).join(
            Cliente, Entrada.cliente_id == Cliente.id
        ).filter(
            Entrada.anulado == False
        ).group_by(
            Cliente.tipo
        ).all()

        pie_data = [
            {"tipo_cliente": r.tipo_cliente or "Sin tipo", "count": r.count}
            for r in results
        ]

        monthly_results = db.session.query(
            func.strftime('%Y-%m', Entrada.fech_entrada).label('month'),
            Cliente.tipo.label('tipo_cliente'),
            func.count(Entrada.id).label('count')
        ).join(
            Cliente, Entrada.cliente_id == Cliente.id
        ).filter(
            Entrada.anulado == False
        ).group_by(
            func.strftime('%Y-%m', Entrada.fech_entrada),
            Cliente.tipo
        ).order_by(
            func.strftime('%Y-%m', Entrada.fech_entrada)
        ).all()

        area_data = [
            {
                "month": r.month,
                "tipo_cliente": r.tipo_cliente or "Sin tipo",
                "count": r.count
            }
            for r in monthly_results
        ]

        data = {
            "pie": pie_data,
            "area": area_data
        }

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_analytics_kpis() -> Dict[str, Any]:
        """Obtener KPIs generales del laboratorio.

        Returns:
            Diccionario con contadores de KPIs.
        """
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.entrada import Entrada, EntradaStatus

        cache_key = AnalyticsService._get_cache_key("kpis")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        pendientes = [
            DetalleEnsayoStatus.PENDIENTE.value,
            DetalleEnsayoStatus.ASIGNADO.value,
            DetalleEnsayoStatus.EN_PROCESO.value,
        ]

        total_ensayos_pendientes = DetalleEnsayo.query.filter(
            DetalleEnsayo.estado.in_(pendientes)
        ).count()

        total_ensayos_completados = DetalleEnsayo.query.filter(
            DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value
        ).count()

        hoy = datetime.utcnow().date()
        inicio_mes = hoy.replace(day=1)

        completados_mes = DetalleEnsayo.query.filter(
            DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
            DetalleEnsayo.fecha_completado >= inicio_mes
        ).count()

        entradas_pendientes = Entrada.query.filter(
            Entrada.status.in_([
                EntradaStatus.RECIBIDO.value,
                EntradaStatus.EN_PROCESO.value
            ]),
            Entrada.anulado == False
        ).count()

        data = {
            "ensayos_pendientes": total_ensayos_pendientes,
            "ensayos_completados": total_ensayos_completados,
            "completados_mes": completados_mes,
            "entradas_pendientes": entradas_pendientes,
            "timestamp": datetime.utcnow().isoformat()
        }

        cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    @staticmethod
    def get_full_analytics(period_days: Optional[int] = None) -> Dict[str, Any]:
        """Obtener todos los datos de analytics en una llamada.

        Args:
            period_days: Período en días para los reportes (optional)

        Returns:
            Diccionario con todos los datos de analytics.
        """
        months = 12
        if period_days:
            months = max(1, period_days // 30)

        return {
            "es_pending": AnalyticsService.get_es_pending(),
            "fq_pending": AnalyticsService.get_fq_pending(),
            "mb_pending_by_tech": AnalyticsService.get_mb_pending_by_tech(),
            "completed_timeline": AnalyticsService.get_completed_timeline(months),
            "lotes_by_type_client": AnalyticsService.get_lotes_by_type_client(),
            "muestreos_by_client_type": AnalyticsService.get_muestreos_by_client_type(),
            "kpis": AnalyticsService.get_analytics_kpis(),
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def invalidate_cache() -> int:
        """Invalidar toda la caché de analytics.

        Returns:
            Número de claves eliminadas.
        """
        return cache.clear_pattern(f"{AnalyticsService.CACHE_PREFIX}:*")
