"""
Tests unitarios: Feature Ensayos
Tests del workflow y reglas de negocio de laboratorio.
"""
import pytest
from datetime import date

from app.core.domain.base import ValidationError
from app.features.ensayos.domain.models import (
    Ensayo,
    EstadoEnsayo,
    ResultadoParametro,
    TipoEnsayo,
)


class TestWorkflowEnsayo:
    def _muestra_ensayo(self) -> Ensayo:
        return Ensayo(muestra_id=1, tipo=TipoEnsayo.FISICO_QUIMICO)

    def test_estado_inicial_es_pendiente(self):
        ensayo = self._muestra_ensayo()
        assert ensayo.estado == EstadoEnsayo.PENDIENTE

    def test_iniciar_ensayo_pendiente(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        assert ensayo.estado == EstadoEnsayo.EN_PROCESO
        assert ensayo.analist_responsable == "Dr. García"
        assert ensayo.fecha_inicio == date.today()

    def test_no_se_puede_iniciar_dos_veces(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        with pytest.raises(ValidationError):
            ensayo.iniciar("Dr. López")

    def test_registrar_resultado_en_proceso(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        resultado = ResultadoParametro(
            parametro="pH",
            valor_obtenido="7.2",
            unidad="",
            valor_referencia="6.5-8.5",
            conforme=True,
        )
        ensayo.registrar_resultado(resultado)
        assert len(ensayo.resultados) == 1

    def test_no_registrar_resultado_sin_iniciar(self):
        ensayo = self._muestra_ensayo()
        resultado = ResultadoParametro(
            parametro="pH", valor_obtenido="7.2",
            unidad="", valor_referencia=None, conforme=None
        )
        with pytest.raises(ValidationError):
            ensayo.registrar_resultado(resultado)

    def test_completar_con_resultados(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        ensayo.registrar_resultado(
            ResultadoParametro("pH", "7.0", "", "6-8", True)
        )
        ensayo.completar()
        assert ensayo.estado == EstadoEnsayo.COMPLETADO
        assert ensayo.fecha_fin == date.today()

    def test_no_completar_sin_resultados(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        with pytest.raises(ValidationError):
            ensayo.completar()

    def test_conformidad_ensayo(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        ensayo.registrar_resultado(ResultadoParametro("pH", "7.0", "", "6-8", True))
        ensayo.registrar_resultado(ResultadoParametro("Temp", "25", "°C", "20-30", True))
        assert ensayo.es_conforme is True

    def test_no_conforme_si_algun_resultado_falla(self):
        ensayo = self._muestra_ensayo()
        ensayo.iniciar("Dr. García")
        ensayo.registrar_resultado(ResultadoParametro("pH", "9.5", "", "6-8", False))
        ensayo.registrar_resultado(ResultadoParametro("Temp", "25", "°C", "20-30", True))
        assert ensayo.es_conforme is False
