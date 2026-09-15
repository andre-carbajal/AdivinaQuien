from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE / "motor.py").exists() else HERE.parent / "src"
sys.path.insert(0, str(SOURCE))

from motor import MotorClips, MotorLogic
from personajes import PERSONAJES


MOTORES = (MotorLogic, MotorClips)


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


if __name__ == "__main__":
    test_todos_los_personajes_en_ambos_motores()
    test_respuesta_contradictoria()
    test_sin_coincidencia()
    test_clips_retrae_candidatos_con_reglas()
    print("Los 12 personajes fueron identificados por LOGIC.py y CLIPS.")
