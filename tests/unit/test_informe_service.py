#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para InformeService."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.database.models.informe import InformeStatus, TipoInforme
from app.services.informe_service import puede_cambiar_estado, generar_nro_oficial


# ---------------------------------------------------------------------------
# Mocks auxiliares
# ---------------------------------------------------------------------------

def create_mock_user(role):
    """Crea un mock de User con el rol especificado."""
    user = MagicMock()
    user.id = 1
    user.role = role
    user.is_admin.return_value = role.value == "admin"
    user.is_laboratory_manager.return_value = role.value == "laboratory_manager"
    user.is_technician.return_value = role.value == "technician"
    return user


def create_mock_informe(
    estado=InformeStatus.BORRADOR,
    emitido_por_id=None,
    resumen_resultados=None,
):
    """Crea un mock de Informe con los atributos necesarios."""
    informe = MagicMock()
    informe.id = 1
    informe.estado = estado
    informe.emitido_por_id = emitido_por_id
    informe.resumen_resultados = resumen_resultados
    return informe


# ---------------------------------------------------------------------------
# Test puede_cambiar_estado - Tests de validación de permisos
# ---------------------------------------------------------------------------

class TestPuedeCambiarEstado:
    """Tests para la función puede_cambiar_estado."""

    def test_admin_puede_anular(self):
        """Admin puede cambiar el estado a ANULADO."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.ADMIN)
        informe = create_mock_informe(estado=InformeStatus.BORRADOR)

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.ANULADO)

        assert puede is True
        assert mensaje == ""

    def test_lab_manager_puede_anular(self):
        """Laboratory_manager puede cambiar el estado a ANULADO."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.LABORATORY_MANAGER)
        informe = create_mock_informe(estado=InformeStatus.BORRADOR)

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.ANULADO)

        assert puede is True
        assert mensaje == ""

    def test_tecnico_no_puede_anular(self):
        """Technician NO puede cambiar el estado a ANULADO."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.TECHNICIAN)
        informe = create_mock_informe(estado=InformeStatus.BORRADOR)

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.ANULADO)

        assert puede is False
        assert "ADMIN" in mensaje or " LABORATORY_MANAGER" in mensaje

    def test_emitido_sin_emitido_por_falla(self):
        """No se puede emitir un informe sin emitido_por_id."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.ADMIN)
        informe = create_mock_informe(
            estado=InformeStatus.PENDIENTE_FIRMA,
            emitido_por_id=None,
        )

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.EMITIDO)

        assert puede is False
        assert "emitido_por" in mensaje.lower() or "asignado" in mensaje.lower()

    def test_pendiente_firma_sin_resumen_falla(self):
        """No se puede cambiar a PENDIENTE_FIRMA sin resumen_resultados."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.ADMIN)
        informe = create_mock_informe(
            estado=InformeStatus.BORRADOR,
            resumen_resultados=None,
        )

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.PENDIENTE_FIRMA)

        assert puede is False
        assert "resumen_resultados" in mensaje.lower()

    def test_pendiente_firma_con_resumen_ok(self):
        """Se puede cambiar a PENDIENTE_FIRMA si existe resumen_resultados."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.ADMIN)
        informe = create_mock_informe(
            estado=InformeStatus.BORRADOR,
            resumen_resultados="Resultados dentro de parámetros normales",
        )

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.PENDIENTE_FIRMA)

        assert puede is True
        assert mensaje == ""

    def test_emitido_con_emitido_por_ok(self):
        """Se puede emitir un informe si tiene emitido_por_id."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.ADMIN)
        informe = create_mock_informe(
            estado=InformeStatus.PENDIENTE_FIRMA,
            emitido_por_id=1,
        )

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.EMITIDO)

        assert puede is True
        assert mensaje == ""

    def test_transicion_a_borrador_sin_restricciones(self):
        """Cambiar a BORRADOR no tiene restricciones especiales."""
        from app.database.models.user import UserRole

        usuario = create_mock_user(UserRole.TECHNICIAN)
        informe = create_mock_informe(estado=InformeStatus.EMITIDO)

        puede, mensaje = puede_cambiar_estado(usuario, informe, InformeStatus.BORRADOR)

        assert puede is True
        assert mensaje == ""


# ---------------------------------------------------------------------------
# Test generar_nro_oficial - Tests del generador
# ---------------------------------------------------------------------------

class TestGenerarNroOficial:
    """Tests para la función generar_nro_oficial."""

    @patch("app.services.informe_service.db")
    @patch("app.services.informe_service.datetime")
    def test_formato_informe_analisis(self, mock_datetime, mock_db):
        """Formato correcto para INF-A-2024-NNNN."""
        mock_datetime.utcnow.return_value = datetime(2024, 6, 15)
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        mock_filter.with_for_update.return_value = mock_filter
        mock_filter.first.return_value = None

        resultado = generar_nro_oficial(TipoInforme.ANALISIS.value)

        assert resultado.startswith("INF-A-2024-")
        assert resultado.endswith("-0001")

    @patch("app.services.informe_service.db")
    @patch("app.services.informe_service.datetime")
    def test_formato_informe_certificado(self, mock_datetime, mock_db):
        """Formato correcto para INF-C-2024-NNNN."""
        mock_datetime.utcnow.return_value = datetime(2024, 6, 15)
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        mock_filter.with_for_update.return_value = mock_filter
        mock_filter.first.return_value = None

        resultado = generar_nro_oficial(TipoInforme.CERTIFICADO.value)

        assert resultado.startswith("INF-C-2024-")
        assert resultado.endswith("-0001")

    @patch("app.services.informe_service.db")
    @patch("app.services.informe_service.datetime")
    def test_formato_informe_especial(self, mock_datetime, mock_db):
        """Formato correcto para INF-E-2024-NNNN."""
        mock_datetime.utcnow.return_value = datetime(2024, 6, 15)
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        mock_filter.with_for_update.return_value = mock_filter
        mock_filter.first.return_value = None

        resultado = generar_nro_oficial(TipoInforme.ESPECIAL.value)

        assert resultado.startswith("INF-E-2024-")
        assert resultado.endswith("-0001")

    @patch("app.services.informe_service.db")
    @patch("app.services.informe_service.datetime")
    def test_formato_informe_consulta(self, mock_datetime, mock_db):
        """Formato correcto para INF-2024-NNNN (sin prefijo, usa INF--)."""
        mock_datetime.utcnow.return_value = datetime(2024, 6, 15)
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        mock_filter.with_for_update.return_value = mock_filter
        mock_filter.first.return_value = None

        resultado = generar_nro_oficial(TipoInforme.CONSULTA.value)

        assert resultado.startswith("INF--2024-")
        assert resultado.endswith("-0001")
        assert "-A-" not in resultado
        assert "-C-" not in resultado
        assert "-E-" not in resultado

    @patch("app.services.informe_service.db")
    @patch("app.services.informe_service.datetime")
    def test_formato_informe_analisis_con_secuencia(self, mock_datetime, mock_db):
        """Incrementa la secuencia correctamente."""
        mock_datetime.utcnow.return_value = datetime(2024, 6, 15)
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        mock_filter.with_for_update.return_value = mock_filter

        mock_last = MagicMock()
        mock_last.nro_oficial = "INF-A-2024-0042"
        mock_filter.first.return_value = mock_last

        resultado = generar_nro_oficial(TipoInforme.ANALISIS.value)

        assert resultado == "INF-A-2024-0043"

    @patch("app.services.informe_service.db")
    @patch("app.services.informe_service.datetime")
    def test_formato_informe_consulta_con_secuencia(self, mock_datetime, mock_db):
        """Incrementa la secuencia correctamente para consulta (usa INF--)."""
        mock_datetime.utcnow.return_value = datetime(2024, 6, 15)
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        mock_filter.with_for_update.return_value = mock_filter

        mock_last = MagicMock()
        mock_last.nro_oficial = "INF--2024-0099"
        mock_filter.first.return_value = mock_last

        resultado = generar_nro_oficial(TipoInforme.CONSULTA.value)

        assert resultado == "INF--2024-0100"

    def test_tipo_invalido_lanza_error(self):
        """Tipo inexistente lanza ValueError."""
        with pytest.raises(ValueError, match="inválido"):
            generar_nro_oficial("TIPO_INEXISTENTE")

    def test_tipo_none_lanza_error(self):
        """Tipo None lanza ValueError."""
        with pytest.raises(ValueError, match="inválido"):
            generar_nro_oficial("")
