"""Servicio de negocio para gestión de Informes."""

from datetime import datetime

from app import db
from app.database.models import (
    Informe,
    InformeHistory,
    InformeStatus,
    TipoInforme,
)


TIPO_PREFIX = {
    TipoInforme.ANALISIS.value: "A",
    TipoInforme.CERTIFICADO.value: "C",
    TipoInforme.CONSULTA.value: "",
    TipoInforme.ESPECIAL.value: "E",
}


def generar_nro_oficial(tipo_informe: str) -> str:
    """Genera un número oficial único para un informe.

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
    """
    if tipo_informe not in TIPO_PREFIX:
        raise ValueError(f"Tipo de informe inválido: {tipo_informe}")

    prefix = TIPO_PREFIX[tipo_informe]
    current_year = datetime.utcnow().year
    year_str = str(current_year)

    last_informe = (
        db.session.query(Informe)
        .filter(Informe.nro_oficial.like(f"INF-{prefix}-{year_str}-%"))
        .order_by(Informe.nro_oficial.desc())
        .first()
    )

    if last_informe:
        last_num = int(last_informe.nro_oficial.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"INF-{prefix}-{year_str}-{new_num:04d}"


def cambiar_estado(informe: Informe, nuevo_estado: InformeStatus, usuario, motivo: str = None) -> bool:
    """Cambia el estado de un informe con validación y registro de historial.

    Args:
        informe: Instancia del informe a modificar.
        nuevo_estado: Nuevo estado según InformeStatus.
        usuario: Usuario que realiza el cambio.
        motivo: Razón o motivo del cambio de estado.

    Returns:
        bool: True si el cambio fue exitoso, False si la transición es inválida.
    """
    from_estado = informe.estado.value if isinstance(informe.estado, InformeStatus) else informe.estado
    to_estado = nuevo_estado.value if isinstance(nuevo_estado, InformeStatus) else nuevo_estado

    if not Informe.can_transition(from_estado, to_estado):
        return False

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
    return True


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
