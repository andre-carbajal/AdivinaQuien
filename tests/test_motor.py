from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE / "motor.py").exists() else HERE.parent / "src"
sys.path.insert(0, str(SOURCE))

from motor import MotorDemostracion
from personajes import PERSONAJES


def test_todos_los_personajes():
    for personaje in PERSONAJES:
        motor = MotorDemostracion()
        estado = motor.iniciar()
        while estado.estado == "preguntando":
            atributo, _ = estado.pregunta
            estado = motor.responder(atributo, personaje[atributo])
        assert estado.estado == "identificado"
        assert estado.identificado == personaje["nombre"]


if __name__ == "__main__":
    test_todos_los_personajes()
    print("Los 12 personajes fueron identificados correctamente.")
