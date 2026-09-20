from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE / "motor.py").exists() else HERE.parent / "src"
sys.path.insert(0, str(SOURCE))

from motor import MotorClips, MotorLogic, MotorTypeSafe, estadisticas_inferencia
from personajes import PERSONAJES


MOTORES = (MotorLogic, MotorClips)


class FakeTypeSafeClient:
    calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def system_one(self, *, state, questions):
        self.calls.append((state, questions))
        return SimpleNamespace(
            nouls={
                nombre: SimpleNamespace(
                    noul=float(all(
                        datos[atributo] == valor
                        for atributo, valor in state["respuestas"].items()
                    ))
                )
                for nombre, datos in state["personajes"].items()
            }
        )


def resolver(motor_cls, personaje):
    motor = motor_cls()
    estado = motor.iniciar()
    while estado.estado == "preguntando":
        atributo, _ = estado.pregunta
        estado = motor.responder(atributo, personaje[atributo])
    return motor, estado


def test_todos_los_personajes_en_ambos_motores():
    for motor_cls in MOTORES:
        for personaje in PERSONAJES:
            _, estado = resolver(motor_cls, personaje)
            assert estado.estado == "identificado"
            assert estado.identificado == personaje["nombre"]


def test_respuesta_contradictoria():
    for motor_cls in MOTORES:
        motor = motor_cls()
        motor.iniciar()
        motor.responder("mujer", True)
        estado = motor.responder("mujer", False)
        assert estado.estado == "contradiccion"
        assert len(estado.historial) == 1


def test_sin_coincidencia():
    for motor_cls in MOTORES:
        motor = motor_cls()
        motor.iniciar()
        motor.responder("mujer", False)
        estado = motor.responder("cabello_largo", True)
        assert estado.estado == "sin_coincidencia"
        assert estado.candidatos == []


def test_clips_retrae_candidatos_con_reglas():
    motor = MotorClips()
    motor.iniciar()
    estado = motor.responder("mujer", True)
    esperados = {p["nombre"] for p in PERSONAJES if p["mujer"]}
    assert set(estado.candidatos) == esperados
    hechos = motor.environment.find_template("candidato").facts()
    assert {fact["nombre"] for fact in hechos} == esperados


def test_mide_inferencia_y_reinicia_las_mediciones():
    for motor_cls in MOTORES:
        motor = motor_cls()
        motor.iniciar()
        assert motor.tiempos_inferencia_ms == []

        motor.responder("mujer", True)

        assert len(motor.tiempos_inferencia_ms) == 1
        assert motor.tiempos_inferencia_ms[0] >= 0
        motor.iniciar()
        assert motor.tiempos_inferencia_ms == []


def test_calcula_estadisticas_de_inferencia():
    estadisticas = estadisticas_inferencia([0.1, 0.3, 0.2])

    assert estadisticas["cantidad"] == 3
    assert abs(estadisticas["total_ms"] - 0.6) < 1e-9
    assert abs(estadisticas["promedio_ms"] - 0.2) < 1e-9
    assert estadisticas["minimo_ms"] == 0.1
    assert estadisticas["maximo_ms"] == 0.3
    assert estadisticas_inferencia([]) is None


def test_typesafe_filtra_con_nouls_en_una_sola_llamada():
    FakeTypeSafeClient.calls.clear()

    with patch("motor.TypeSafeClient", FakeTypeSafeClient):
        motor = MotorTypeSafe()
        estado = motor.iniciar()
        assert set(estado.candidatos) == {p["nombre"] for p in PERSONAJES}

        estado = motor.responder("mujer", True)
        estado = motor.responder("lentes", True)

    esperados = {
        p["nombre"] for p in PERSONAJES
        if p["mujer"] and p["lentes"]
    }
    assert set(estado.candidatos) == esperados
    assert len(FakeTypeSafeClient.calls) == 2
    state, questions = FakeTypeSafeClient.calls[0]
    assert state["respuestas"] == {"mujer": True}
    assert set(questions) == {p["nombre"] for p in PERSONAJES}
    assert all(question.type == "noul" for question in questions.values())
    _, questions = FakeTypeSafeClient.calls[1]
    assert set(questions) == {
        p["nombre"] for p in PERSONAJES if p["mujer"]
    }


def test_typesafe_identifica_todos_los_personajes():
    with patch("motor.TypeSafeClient", FakeTypeSafeClient):
        for personaje in PERSONAJES:
            _, estado = resolver(MotorTypeSafe, personaje)
            assert estado.estado == "identificado"
            assert estado.identificado == personaje["nombre"]


def test_typesafe_maneja_contradiccion_y_reinicio():
    with patch("motor.TypeSafeClient", FakeTypeSafeClient):
        motor = MotorTypeSafe()
        motor.iniciar()
        motor.responder("mujer", True)
        estado = motor.responder("mujer", False)

        assert estado.estado == "contradiccion"
        assert len(estado.historial) == 1
        assert len(motor.tiempos_inferencia_ms) == 2

        motor.iniciar()
        assert motor.respuestas == {}
        assert motor.historial == []
        assert motor.tiempos_inferencia_ms == []


def test_typesafe_propaga_error_y_revierte_la_respuesta():
    motor = MotorTypeSafe()
    motor.iniciar()

    with patch("motor.TypeSafeClient", side_effect=RuntimeError("offline")):
        try:
            motor.responder("mujer", True)
        except RuntimeError as error:
            assert str(error) == "offline"
        else:
            raise AssertionError("El error de TypeSafe debía propagarse")

    assert motor.respuestas == {}
    assert motor.historial == []


if __name__ == "__main__":
    test_todos_los_personajes_en_ambos_motores()
    test_respuesta_contradictoria()
    test_sin_coincidencia()
    test_clips_retrae_candidatos_con_reglas()
    test_mide_inferencia_y_reinicia_las_mediciones()
    test_calcula_estadisticas_de_inferencia()
    test_typesafe_filtra_con_nouls_en_una_sola_llamada()
    test_typesafe_identifica_todos_los_personajes()
    test_typesafe_maneja_contradiccion_y_reinicio()
    test_typesafe_propaga_error_y_revierte_la_respuesta()
    print("Los 12 personajes fueron identificados por LOGIC.py, CLIPS y TypeSafe.")
