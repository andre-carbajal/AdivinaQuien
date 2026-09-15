from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE / "interfaz.py").exists() else HERE.parent / "src"
sys.path.insert(0, str(SOURCE))

from interfaz import App
from personajes import PERSONAJES


def app_para_descartes_manuales():
    app = SimpleNamespace(
        fase_usuario="descartar",
        descartados_usuario=set(),
        tarjetas_usuario={},
        contador_descartes=None,
        estado_usuario=SimpleNamespace(candidatos=[]),
    )
    app._actualizar_descarte_visual = lambda _nombre: None
    return app


def test_el_tablero_usuario_no_hereda_descartes_del_motor():
    app = app_para_descartes_manuales()

    assert App._restantes_usuario(app) == len(PERSONAJES)
    assert not App._esta_descartado_usuario(app, "Ana")

    App.alternar_descarte(app, "Ana")

    assert app.descartados_usuario == {"Ana"}
    assert App._esta_descartado_usuario(app, "Ana")
    assert not App._esta_descartado_usuario(app, "Bruno")
    assert App._restantes_usuario(app) == len(PERSONAJES) - 1


def test_el_jugador_puede_marcar_un_personaje_que_el_motor_filtra():
    app = app_para_descartes_manuales()
    app.estado_usuario.candidatos = ["Bruno"]

    App.alternar_descarte(app, "Ana")

    assert app.descartados_usuario == {"Ana"}


if __name__ == "__main__":
    test_el_tablero_usuario_no_hereda_descartes_del_motor()
    test_el_jugador_puede_marcar_un_personaje_que_el_motor_filtra()
    print("Pruebas de descarte manual: OK")
