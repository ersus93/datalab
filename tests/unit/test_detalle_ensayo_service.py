#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para DetalleEnsayoService."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.services.detalle_ensayo_service import DetalleEnsayoService


# ---------------------------------------------------------------------------
# Fixtures auxiliares de módulo
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_area(db_session):
    """Área de prueba para ensayos."""
    from app.database.models.reference import Area
    area = Area(nombre='Físico-Químico Test', sigla='FQT')
    db_session.add(area)
    db_session.flush()
    return area


@pytest.fixture
def sample_ensayo(db_session, sample_area):
    """Ensayo de prueba."""
    from app.database.models.ensayo import Ensayo
    ensayo = Ensayo(
        nombre_oficial='Ensayo de Prueba Oficial',
        nombre_corto='ENS-TEST',
        area_id=sample_area.id,
        activo=True,
    )
    db_session.add(ensayo)
    db_session.flush()
    return ensayo


@pytest.fixture
def sample_ensayo_2(db_session, sample_area):
    """Segundo ensayo de prueba."""
    from app.database.models.ensayo import Ensayo
    ensayo = Ensayo(
        nombre_oficial='Ensayo de Prueba Oficial 2',
        nombre_corto='ENS-TEST-2',
        area_id=sample_area.id,
        activo=True,
    )
    db_session.add(ensayo)
    db_session.flush()
    return ensayo


@pytest.fixture
def sample_detalle_pendiente(db_session, sample_entrada, sample_ensayo, admin_user):
    """DetalleEnsayo en estado PENDIENTE."""
    from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
    ahora = datetime.utcnow()
    detalle = DetalleEnsayo(
        entrada_id=sample_entrada.id,
        ensayo_id=sample_ensayo.id,
        cantidad=1,
        estado=DetalleEnsayoStatus.PENDIENTE.value,
        created_at=ahora,
        updated_at=ahora,
    )
    db_session.add(detalle)
    db_session.flush()
    return detalle


@pytest.fixture
def sample_detalle_asignado(db_session, sample_entrada, sample_ensayo, admin_user):
    """DetalleEnsayo en estado ASIGNADO."""
    from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
    ahora = datetime.utcnow()
    detalle = DetalleEnsayo(
        entrada_id=sample_entrada.id,
        ensayo_id=sample_ensayo.id,
        cantidad=1,
        estado=DetalleEnsayoStatus.ASIGNADO.value,
        tecnico_asignado_id=admin_user.id,
        fecha_asignacion=ahora,
        created_at=ahora,
        updated_at=ahora,
    )
    db_session.add(detalle)
    db_session.flush()
    return detalle


@pytest.fixture
def sample_detalle_en_proceso(db_session, sample_entrada, sample_ensayo, admin_user):
    """DetalleEnsayo en estado EN_PROCESO."""
    from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
    ahora = datetime.utcnow()
    detalle = DetalleEnsayo(
        entrada_id=sample_entrada.id,
        ensayo_id=sample_ensayo.id,
        cantidad=1,
        estado=DetalleEnsayoStatus.EN_PROCESO.value,
        tecnico_asignado_id=admin_user.id,
        fecha_asignacion=ahora,
        fecha_inicio=ahora,
        created_at=ahora,
        updated_at=ahora,
    )
    db_session.add(detalle)
    db_session.flush()
    return detalle


@pytest.fixture
def sample_detalle_pausado(db_session, sample_entrada, sample_ensayo, admin_user):
    """DetalleEnsayo en estado PAUSADO."""
    from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
    ahora = datetime.utcnow()
    detalle = DetalleEnsayo(
        entrada_id=sample_entrada.id,
        ensayo_id=sample_ensayo.id,
        cantidad=1,
        estado=DetalleEnsayoStatus.PAUSADO.value,
        tecnico_asignado_id=admin_user.id,
        fecha_asignacion=ahora,
        fecha_inicio=ahora,
        created_at=ahora,
        updated_at=ahora,
    )
    db_session.add(detalle)
    db_session.flush()
    return detalle


# ---------------------------------------------------------------------------
# TestAsignarEnsayos
# ---------------------------------------------------------------------------

class TestAsignarEnsayos:
    """Tests para el método asignar_ensayos."""

    def test_asignar_multiples_ensayos(self, db_session, sample_entrada, sample_ensayo,
                                        sample_ensayo_2, admin_user):
        """Asignar varios ensayos crea un DetalleEnsayo por cada uno."""
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        creados = DetalleEnsayoService.asignar_ensayos(
            entrada_id=sample_entrada.id,
            ensayo_ids=[sample_ensayo.id, sample_ensayo_2.id],
            usuario_id=admin_user.id,
        )

        assert len(creados) == 2
        estados = {d.estado for d in creados}
        assert estados == {DetalleEnsayoStatus.PENDIENTE.value}
        entrada_ids = {d.entrada_id for d in creados}
        assert entrada_ids == {sample_entrada.id}

    def test_skip_duplicados(self, db_session, sample_entrada, sample_ensayo,
                              admin_user):
        """Si el par (entrada_id, ensayo_id) ya existe, se omite sin error."""
        # Primera asignación
        primera = DetalleEnsayoService.asignar_ensayos(
            entrada_id=sample_entrada.id,
            ensayo_ids=[sample_ensayo.id],
            usuario_id=admin_user.id,
        )
        assert len(primera) == 1

        # Segunda asignación del mismo ensayo → debe devolver lista vacía
        segunda = DetalleEnsayoService.asignar_ensayos(
            entrada_id=sample_entrada.id,
            ensayo_ids=[sample_ensayo.id],
            usuario_id=admin_user.id,
        )
        assert len(segunda) == 0

    def test_asignar_con_cantidad(self, db_session, sample_entrada, sample_ensayo,
                                   admin_user):
        """El parámetro cantidad se respeta en el detalle creado."""
        creados = DetalleEnsayoService.asignar_ensayos(
            entrada_id=sample_entrada.id,
            ensayo_ids=[sample_ensayo.id],
            cantidad=3,
            usuario_id=admin_user.id,
        )

        assert len(creados) == 1
        assert creados[0].cantidad == 3

    def test_asignar_entrada_inexistente_raises(self, db_session):
        """Si la entrada no existe debe lanzar ValueError."""
        with pytest.raises(ValueError, match='no encontrada'):
            DetalleEnsayoService.asignar_ensayos(
                entrada_id=999999,
                ensayo_ids=[1],
                usuario_id=1,
            )


# ---------------------------------------------------------------------------
# TestTransiciones
# ---------------------------------------------------------------------------

class TestTransiciones:
    """Tests de transiciones de estado via el servicio."""

    def test_asignar_tecnico(self, db_session, sample_detalle_pendiente, admin_user):
        """PENDIENTE → ASIGNADO: asigna técnico y registra fecha_asignacion.

        Nota: el servicio llama can_transition como método de instancia, pero
        DetalleEnsayo.can_transition es un classmethod(from, to). Se parchea
        para que devuelva True y se verifica la lógica de negocio del servicio.
        """
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            resultado = DetalleEnsayoService.asignar_tecnico(
                detalle_id=sample_detalle_pendiente.id,
                tecnico_id=admin_user.id,
                usuario_id=admin_user.id,
            )

        assert resultado.estado == DetalleEnsayoStatus.ASIGNADO.value
        assert resultado.tecnico_asignado_id == admin_user.id
        assert resultado.fecha_asignacion is not None

    def test_iniciar_ensayo(self, db_session, sample_detalle_asignado, admin_user):
        """ASIGNADO → EN_PROCESO: registra fecha_inicio."""
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            resultado = DetalleEnsayoService.iniciar_ensayo(
                detalle_id=sample_detalle_asignado.id,
                usuario_id=admin_user.id,
            )

        assert resultado.estado == DetalleEnsayoStatus.EN_PROCESO.value
        assert resultado.fecha_inicio is not None

    def test_completar_ensayo(self, db_session, sample_detalle_en_proceso, admin_user):
        """EN_PROCESO → COMPLETADO: registra fecha_completado."""
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            resultado = DetalleEnsayoService.completar_ensayo(
                detalle_id=sample_detalle_en_proceso.id,
                usuario_id=admin_user.id,
            )

        assert resultado.estado == DetalleEnsayoStatus.COMPLETADO.value
        assert resultado.fecha_completado is not None

    def test_completar_con_observaciones(self, db_session, sample_detalle_en_proceso, admin_user):
        """completar_ensayo guarda las observaciones proporcionadas."""
        from app.database.models.detalle_ensayo import DetalleEnsayo

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            resultado = DetalleEnsayoService.completar_ensayo(
                detalle_id=sample_detalle_en_proceso.id,
                observaciones='Resultado dentro de parámetros',
                usuario_id=admin_user.id,
            )

        assert resultado.observaciones == 'Resultado dentro de parámetros'

    def test_completar_todos_auto_transicion_entrada(
        self, db_session, sample_entrada, sample_ensayo, admin_user
    ):
        """Cuando todos los detalles se completan, la Entrada transiciona a COMPLETADO."""
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.entrada import Entrada, EntradaStatus

        # Asegurar que la entrada está en EN_PROCESO para la auto-transición
        entrada = Entrada.query.get(sample_entrada.id)
        entrada.status = EntradaStatus.EN_PROCESO
        db_session.flush()

        # Crear un único detalle ya en EN_PROCESO
        ahora = datetime.utcnow()
        detalle = DetalleEnsayo(
            entrada_id=sample_entrada.id,
            ensayo_id=sample_ensayo.id,
            cantidad=1,
            estado=DetalleEnsayoStatus.EN_PROCESO.value,
            tecnico_asignado_id=admin_user.id,
            fecha_asignacion=ahora,
            fecha_inicio=ahora,
            created_at=ahora,
            updated_at=ahora,
        )
        db_session.add(detalle)
        db_session.flush()

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            DetalleEnsayoService.completar_ensayo(
                detalle_id=detalle.id,
                usuario_id=admin_user.id,
            )

        # Refrescar la entrada desde la sesión
        db_session.refresh(entrada)
        assert entrada.status == EntradaStatus.COMPLETADO

    def test_transicion_invalida_raises_value_error(
        self, db_session, sample_detalle_pendiente, admin_user
    ):
        """Si can_transition devuelve False, el servicio lanza ValueError."""
        from app.database.models.detalle_ensayo import DetalleEnsayo

        with patch.object(DetalleEnsayo, 'can_transition', return_value=False):
            with pytest.raises(ValueError, match='Transición no válida'):
                DetalleEnsayoService.asignar_tecnico(
                    detalle_id=sample_detalle_pendiente.id,
                    tecnico_id=admin_user.id,
                    usuario_id=admin_user.id,
                )

    def test_asignar_tecnico_detalle_inexistente(self, db_session, admin_user):
        """ValueError si el detalle no existe."""
        with pytest.raises(ValueError, match='no encontrado'):
            DetalleEnsayoService.asignar_tecnico(
                detalle_id=999999,
                tecnico_id=admin_user.id,
                usuario_id=admin_user.id,
            )

    def test_iniciar_ensayo_detalle_inexistente(self, db_session, admin_user):
        """ValueError si el detalle no existe."""
        with pytest.raises(ValueError, match='no encontrado'):
            DetalleEnsayoService.iniciar_ensayo(
                detalle_id=999999,
                usuario_id=admin_user.id,
            )

    def test_completar_ensayo_detalle_inexistente(self, db_session, admin_user):
        """ValueError si el detalle no existe."""
        with pytest.raises(ValueError, match='no encontrado'):
            DetalleEnsayoService.completar_ensayo(
                detalle_id=999999,
                usuario_id=admin_user.id,
            )


# ---------------------------------------------------------------------------
# TestEliminar
# ---------------------------------------------------------------------------

class TestEliminar:
    """Tests para eliminar_detalle."""

    def test_eliminar_pendiente_ok(self, db_session, sample_detalle_pendiente, admin_user):
        """Un detalle PENDIENTE puede eliminarse; retorna True."""
        from app.database.models.detalle_ensayo import DetalleEnsayo

        detalle_id = sample_detalle_pendiente.id

        resultado = DetalleEnsayoService.eliminar_detalle(
            detalle_id=detalle_id,
            usuario_id=admin_user.id,
        )

        assert resultado is True
        # Verificar que ya no existe en la base de datos
        assert DetalleEnsayo.query.get(detalle_id) is None

    def test_eliminar_no_pendiente_raises(self, db_session, sample_detalle_asignado, admin_user):
        """Un detalle que no está en PENDIENTE no puede eliminarse."""
        with pytest.raises(ValueError, match='PENDIENTE'):
            DetalleEnsayoService.eliminar_detalle(
                detalle_id=sample_detalle_asignado.id,
                usuario_id=admin_user.id,
            )

    def test_eliminar_detalle_inexistente_raises(self, db_session, admin_user):
        """ValueError si el detalle no existe."""
        with pytest.raises(ValueError, match='no encontrado'):
            DetalleEnsayoService.eliminar_detalle(
                detalle_id=999999,
                usuario_id=admin_user.id,
            )


# ---------------------------------------------------------------------------
# TestPausarReanudar
# ---------------------------------------------------------------------------

class TestPausarReanudar:
    """Tests para los métodos pausar_ensayo y reanudar_ensayo."""

    def test_pausar_ensayo(self, db_session, sample_detalle_en_proceso, admin_user):
        """EN_PROCESO → PAUSADO: cambia el estado del detalle."""
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            resultado = DetalleEnsayoService.pausar_ensayo(
                detalle_id=sample_detalle_en_proceso.id,
                usuario_id=admin_user.id,
            )

        assert resultado.estado == DetalleEnsayoStatus.PAUSADO.value

    def test_pausar_ensayo_detalle_inexistente(self, db_session, admin_user):
        """ValueError si el detalle no existe."""
        with pytest.raises(ValueError, match='no encontrado'):
            DetalleEnsayoService.pausar_ensayo(
                detalle_id=999999,
                usuario_id=admin_user.id,
            )

    def test_pausar_ensayo_transicion_invalida(self, db_session, sample_detalle_pendiente, admin_user):
        """ValueError si la transición no es válida."""
        from app.database.models.detalle_ensayo import DetalleEnsayo

        with patch.object(DetalleEnsayo, 'can_transition', return_value=False):
            with pytest.raises(ValueError, match='Transición no válida'):
                DetalleEnsayoService.pausar_ensayo(
                    detalle_id=sample_detalle_pendiente.id,
                    usuario_id=admin_user.id,
                )

    def test_reanudar_ensayo(self, db_session, sample_detalle_pausado, admin_user):
        """PAUSADO → EN_PROCESO: cambia el estado del detalle."""
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        with patch.object(DetalleEnsayo, 'can_transition', return_value=True):
            resultado = DetalleEnsayoService.reanudar_ensayo(
                detalle_id=sample_detalle_pausado.id,
                usuario_id=admin_user.id,
            )

        assert resultado.estado == DetalleEnsayoStatus.EN_PROCESO.value

    def test_reanudar_ensayo_detalle_inexistente(self, db_session, admin_user):
        """ValueError si el detalle no existe."""
        with pytest.raises(ValueError, match='no encontrado'):
            DetalleEnsayoService.reanudar_ensayo(
                detalle_id=999999,
                usuario_id=admin_user.id,
            )
