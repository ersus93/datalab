"""Servicio de negocio para gestión de Informes."""

import logging
from datetime import datetime
from typing import Tuple

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.database.models import (
    Informe,
    InformeHistory,
    InformeStatus,
    TipoInforme,
)
from app.database.models.user import User, UserRole

logger = logging.getLogger(__name__)

TIPO_PREFIX = {
    TipoInforme.ANALISIS.value: "A",
    TipoInforme.CERTIFICADO.value: "C",
    TipoInforme.CONSULTA.value: "",
    TipoInforme.ESPECIAL.value: "E",
}


def puede_cambiar_estado(usuario: User, informe: Informe, nuevo_estado: InformeStatus) -> Tuple[bool, str]:
    """Valida si el usuario puede cambiar el estado de un informe.

    Args:
        usuario: Usuario que intenta realizar el cambio.
        informe: Instancia del informe a modificar.
        nuevo_estado: Nuevo estado según InformeStatus.

    Returns:
        Tuple[bool, str]: (True, "") si el cambio es válido, (False, mensaje_error) si no lo es.
    """
    if nuevo_estado == InformeStatus.ANULADO:
        if not (usuario.is_admin() or usuario.is_laboratory_manager()):
            return False, "Solo usuarios con rol ADMIN o LABORATORY_MANAGER pueden anular informes"

    if nuevo_estado == InformeStatus.EMITIDO:
        if not informe.emitido_por_id:
            return False, "No se puede emitir un informe sin emitido_por asignado"

    if nuevo_estado == InformeStatus.PENDIENTE_FIRMA:
        if not informe.resumen_resultados or not informe.resumen_resultados.strip():
            return False, "No se puede cambiar a PENDIENTE_FIRMA sin resumen_resultados"

    return True, ""


def generar_nro_oficial(tipo_informe: str) -> str:
    """Genera un número oficial único para un informe de forma atómica.

    Formato: INF-{tipo_prefix}-{YYYY}-{NNNN}
    Prefijos: ANALISIS='A', CERTIFICADO='C', CONSULTA='', ESPECIAL='E'

    Ejemplos:
        INF-A-2024-0001
        INF-C-2024-0001

    Args:
        tipo_informe: Tipo de informe según TipoInforme (valor de cadena).

    Returns:
        str: Número oficial único generado.

    Raises:
        ValueError: Si el tipo de informe no es válido.
        SQLAlchemyError: Si hay error de base de datos.
    """
    if tipo_informe not in TIPO_PREFIX:
        raise ValueError(f"Tipo de informe inválido: {tipo_informe}")

    prefix = TIPO_PREFIX[tipo_informe]
    current_year = datetime.utcnow().year
    year_str = str(current_year)

    try:
        last_informe = (
            db.session.query(Informe)
            .filter(Informe.nro_oficial.like(f"INF-{prefix}-{year_str}-%"))
            .order_by(Informe.nro_oficial.desc())
            .with_for_update(skip_locked=True)
            .first()
        )

        if last_informe:
            last_num = int(last_informe.nro_oficial.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        nuevo_nro = f"INF-{prefix}-{year_str}-{new_num:04d}"

        logger.info(f"Generado número de informe: {nuevo_nro} (tipo: {tipo_informe})")

        return nuevo_nro

    except SQLAlchemyError as e:
        logger.error(f"Error al generar número de informe: {e}")
        db.session.rollback()
        raise


def cambiar_estado(informe: Informe, nuevo_estado: InformeStatus, usuario, motivo: str = None) -> bool:
    """Cambia el estado de un informe con validación y registro de historial.

    Args:
        informe: Instancia del informe a modificar.
        nuevo_estado: Nuevo estado según InformeStatus.
        usuario: Usuario que realiza el cambio.
        motivo: Razón o motivo del cambio de estado.

    Returns:
        bool: True si el cambio fue exitoso, False si la transición es inválida o no tiene permisos.
    """
    from_estado = informe.estado.value if isinstance(informe.estado, InformeStatus) else informe.estado
    to_estado = nuevo_estado.value if isinstance(nuevo_estado, InformeStatus) else nuevo_estado

    if not Informe.can_transition(from_estado, to_estado):
        logger.warning(f"Transición inválida {from_estado} -> {to_estado} para informe {informe.id}")
        return False

    puede_cambiar, mensaje_error = puede_cambiar_estado(usuario, informe, nuevo_estado)
    if not puede_cambiar:
        logger.warning(f"Permiso denegado para cambio de estado en informe {informe.id}: {mensaje_error}")
        return False

    try:
        history_entry = InformeHistory(
            informe_id=informe.id,
            from_status=from_estado,
            to_status=to_estado,
            changed_by_id=usuario.id,
            changed_at=datetime.utcnow(),
            reason=motivo,
        )
        db.session.add(history_entry)

        informe.estado = nuevo_estado

        if nuevo_estado == InformeStatus.EMITIDO:
            informe.fecha_emision = datetime.utcnow()
            if not informe.nro_oficial:
                informe.nro_oficial = generar_nro_oficial(
                    informe.tipo_informe.value if isinstance(informe.tipo_informe, TipoInforme) else informe.tipo_informe
                )

        if nuevo_estado == InformeStatus.ANULADO:
            informe.anulado = True
            if motivo:
                informe.motivo_anulacion = motivo

        db.session.commit()
        logger.info(f"Estado de informe {informe.id} cambiado a {to_estado} por usuario {usuario.id}")
        return True

    except Exception as e:
        logger.error(f"Error al cambiar estado del informe {informe.id}: {e}")
        db.session.rollback()
        return False


def validar_ensayos_pertenecen_misma_entrada(informe: Informe, ensayos_ids: list) -> bool:
    """Verifica que todos los ensayos pertenezcan a la misma entrada.

    Además previene que un ensayo ya reportado en otro informe sea añadido.

    Args:
        informe: Instancia del informe.
        ensayos_ids: Lista de IDs de ensayos (DetalleEnsayo) a validar.

    Returns:
        bool: True si los ensayos son válidos, False en caso contrario.
    """
    if not ensayos_ids:
        return True

    from app.database.models import DetalleEnsayo

    ensayos = db.session.query(DetalleEnsayo).filter(DetalleEnsayo.id.in_(ensayos_ids)).all()

    if len(ensayos) != len(ensayos_ids):
        return False

    entrada_ids = set(e.entrada_id for e in ensayos)
    if len(entrada_ids) != 1:
        return False

    if informe.entrada_id and entrada_ids != {informe.entrada_id}:
        return False

    from app.database.models import InformeEnsayo
    for ensayo_id in ensayos_ids:
        existing = (
            db.session.query(InformeEnsayo)
            .filter(
                InformeEnsayo.detalle_ensayo_id == ensayo_id,
                InformeEnsayo.informe_id != informe.id,
            )
            .join(Informe)
            .filter(Informe.estado != InformeStatus.ANULADO)
            .first()
        )
        if existing:
            return False

    return True
