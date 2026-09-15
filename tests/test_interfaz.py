from pathlib import Path
import inspect
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE / "interfaz.py").exists() else HERE.parent / "src"
sys.path.insert(0, str(SOURCE))

from interfaz import AVATAR_CACHE, CPU_IMAGE_CACHE, App, avatar, cpu_image
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


class VistaFalsa:
    def __init__(self, gestor=""):
        self.gestor = gestor

    def winfo_exists(self):
        return True

    def winfo_manager(self):
        return self.gestor

    def pack_forget(self):
        self.gestor = ""

    def pack(self, **_kwargs):
        self.gestor = "pack"


def test_el_cambio_de_turno_reutiliza_las_vistas():
    app = SimpleNamespace(
        vista_usuario=VistaFalsa("pack"),
        vista_computadora=VistaFalsa(),
    )
    vista_usuario = app.vista_usuario
    vista_computadora = app.vista_computadora

    App._mostrar_vista(app, vista_computadora)

    assert app.vista_usuario is vista_usuario
    assert app.vista_computadora is vista_computadora
    assert vista_usuario.winfo_manager() == ""
    assert vista_computadora.winfo_manager() == "pack"


def test_actualizar_no_destruye_las_vistas():
    assert "destroy" not in inspect.getsource(App.actualizar)


def test_las_imagenes_se_reutilizan_por_tamano():
    AVATAR_CACHE.pop(("Ana", 86), None)
    CPU_IMAGE_CACHE.pop(138, None)

    avatar_original = avatar(PERSONAJES[0], 86)
    cpu_original = cpu_image(138)

    assert avatar(PERSONAJES[0], 86) is avatar_original
    assert cpu_image(138) is cpu_original


if __name__ == "__main__":
    test_el_tablero_usuario_no_hereda_descartes_del_motor()
    test_el_jugador_puede_marcar_un_personaje_que_el_motor_filtra()
    test_el_cambio_de_turno_reutiliza_las_vistas()
    test_actualizar_no_destruye_las_vistas()
    test_las_imagenes_se_reutilizan_por_tamano()
    print("Pruebas de interfaz: OK")
