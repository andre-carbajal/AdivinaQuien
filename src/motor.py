"""Motores de inferencia LOGIC.py, CLIPS y TypeSafe para Adivina Quién."""

from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import Optional

import clips
from typesafe_sdk import Noul, TypeSafeClient

from logic import And, Not, Symbol, model_check
from personajes import ATRIBUTOS, PERSONAJES


@dataclass
class EstadoJuego:
    estado: str
    candidatos: list[str]
    pregunta: Optional[tuple[str, str]] = None
    identificado: Optional[str] = None
    historial: list[dict] = field(default_factory=list)
    explicacion: str = ""


def estadisticas_inferencia(tiempos_ms: list[float]):
    if not tiempos_ms:
        return None
    total_ms = sum(tiempos_ms)
    return {
        "cantidad": len(tiempos_ms),
        "total_ms": total_ms,
        "promedio_ms": total_ms / len(tiempos_ms),
        "minimo_ms": min(tiempos_ms),
        "maximo_ms": max(tiempos_ms),
    }


class MotorConocimiento:
    """Contrato común y comportamiento compartido de los motores."""

    def __init__(self, tecnologia: str):
        self.tecnologia = tecnologia
        self.personajes = {p["nombre"]: p for p in PERSONAJES}
        self.preguntas = dict(ATRIBUTOS)
        self.respuestas: dict[str, bool] = {}
        self.historial: list[dict] = []
        self.tiempos_inferencia_ms: list[float] = []

    def iniciar(self) -> EstadoJuego:
        self.respuestas = {}
        self.historial = []
        self.tiempos_inferencia_ms = []
        self._reiniciar_backend()
        return self._estado(self._candidatos())

    def responder(self, atributo: str, valor: bool) -> EstadoJuego:
        if atributo not in self.preguntas:
            raise ValueError(f"Atributo desconocido: {atributo}")

        valor = bool(valor)
        inicio_inferencia = time.perf_counter_ns()
        if self._respuesta_contradictoria(atributo, valor):
            candidatos = self._candidatos()
            self._registrar_inferencia(inicio_inferencia)
            return EstadoJuego(
                estado="contradiccion",
                candidatos=candidatos,
                historial=list(self.historial),
                explicacion="El atributo ya tenía una respuesta diferente.",
            )

        candidatos_anteriores = (
            self.historial[-1]["candidatos"]
            if self.historial
            else [p["nombre"] for p in PERSONAJES]
        )
        self.respuestas[atributo] = valor
        self._aplicar_respuesta(atributo, valor)
        candidatos = self._candidatos()
        self._registrar_inferencia(inicio_inferencia)
        self.historial.append({
            "atributo": atributo,
            "pregunta": self.preguntas[atributo],
            "valor": valor,
            "candidatos": list(candidatos),
            "descartados": [
                nombre for nombre in candidatos_anteriores
                if nombre not in candidatos
            ],
        })
        return self._estado(candidatos)

    def reiniciar(self) -> EstadoJuego:
        return self.iniciar()

    def _reiniciar_backend(self):
        raise NotImplementedError

    def _aplicar_respuesta(self, atributo: str, valor: bool):
        raise NotImplementedError

    def _candidatos(self) -> list[str]:
        raise NotImplementedError

    def _respuesta_contradictoria(self, atributo: str, valor: bool) -> bool:
        return atributo in self.respuestas and self.respuestas[atributo] != valor

    def _registrar_inferencia(self, inicio_ns: int):
        duracion_ms = (time.perf_counter_ns() - inicio_ns) / 1_000_000
        self.tiempos_inferencia_ms.append(duracion_ms)
        print(f"[INFERENCIA] {self.tecnologia}: {duracion_ms:.3f} ms")

    def _mejor_pregunta(self, candidatos: list[str]):
        pendientes = [a for a, _ in ATRIBUTOS if a not in self.respuestas]
        disponibles = []
        for orden, atributo in enumerate(pendientes):
            positivos = sum(self.personajes[n][atributo] for n in candidatos)
            negativos = len(candidatos) - positivos
            if positivos and negativos:
                disponibles.append((abs(positivos - negativos), orden, atributo))
        if not disponibles:
            return None
        atributo = min(disponibles)[2]
        return atributo, self.preguntas[atributo]

    def _estado(self, candidatos: list[str]) -> EstadoJuego:
        if not candidatos:
            return EstadoJuego(
                estado="sin_coincidencia",
                candidatos=[],
                historial=list(self.historial),
                explicacion="Ningún personaje coincide con todas las respuestas.",
            )
        if len(candidatos) == 1:
            nombre = candidatos[0]
            return EstadoJuego(
                estado="identificado",
                candidatos=candidatos,
                identificado=nombre,
                historial=list(self.historial),
                explicacion=f"{nombre} es el único personaje compatible con los hechos registrados.",
            )
        pregunta = self._mejor_pregunta(candidatos)
        if pregunta is None:
            return EstadoJuego(
                estado="indistinguible",
                candidatos=candidatos,
                historial=list(self.historial),
                explicacion="La base no contiene otro atributo capaz de separar los candidatos.",
            )
        return EstadoJuego(
            estado="preguntando",
            candidatos=candidatos,
            pregunta=pregunta,
            historial=list(self.historial),
            explicacion=f"Quedan {len(candidatos)} candidatos compatibles.",
        )


class MotorLogic(MotorConocimiento):
    """Motor proposicional basado en el logic.py adjunto."""

    def __init__(self):
        super().__init__("LOGIC.py")

    def _reiniciar_backend(self):
        pass

    def _aplicar_respuesta(self, atributo: str, valor: bool):
        pass

    @staticmethod
    def _literal(atributo: str, valor: bool):
        simbolo = Symbol(atributo)
        return simbolo if valor else Not(simbolo)

    def _formula_respuestas(self):
        return And(*(
            self._literal(atributo, valor)
            for atributo, valor in self.respuestas.items()
        ))

    def _respuesta_contradictoria(self, atributo: str, valor: bool) -> bool:
        if atributo not in self.respuestas:
            return False
        conocimiento = self._formula_respuestas()
        return model_check(conocimiento, Not(self._literal(atributo, valor)))

    def _candidatos(self) -> list[str]:
        conocimiento = self._formula_respuestas()
        return [
            personaje["nombre"]
            for personaje in PERSONAJES
            if conocimiento.evaluate({
                atributo: personaje[atributo]
                for atributo, _ in ATRIBUTOS
            })
        ]


class MotorClips(MotorConocimiento):
    """Motor basado en reglas CLIPS ejecutadas mediante clipspy."""

    REGLAS = Path(__file__).with_name("clips_rules.clp")

    def __init__(self):
        super().__init__("CLIPS")
        self.environment: Optional[clips.Environment] = None

    def _reiniciar_backend(self):
        self.environment = clips.Environment()
        self.environment.load(str(self.REGLAS))

        personaje = self.environment.find_template("personaje")
        candidato = self.environment.find_template("candidato")
        for datos in PERSONAJES:
            personaje.assert_fact(
                nombre=datos["nombre"],
                mujer=self._simbolo_booleano(datos["mujer"]),
                lentes=self._simbolo_booleano(datos["lentes"]),
                sombrero=self._simbolo_booleano(datos["sombrero"]),
                barba=self._simbolo_booleano(datos["barba"]),
                cabello_negro=self._simbolo_booleano(datos["cabello_negro"]),
                cabello_rubio=self._simbolo_booleano(datos["cabello_rubio"]),
                cabello_rojo=self._simbolo_booleano(datos["cabello_rojo"]),
                cabello_largo=self._simbolo_booleano(datos["cabello_largo"]),
            )
            candidato.assert_fact(nombre=datos["nombre"])

    def _aplicar_respuesta(self, atributo: str, valor: bool):
        if self.environment is None:
            raise RuntimeError("El motor CLIPS no ha sido iniciado.")
        respuesta = self.environment.find_template("respuesta")
        respuesta.assert_fact(
            atributo=clips.Symbol(atributo),
            valor=self._simbolo_booleano(valor),
        )
        self.environment.run()

    def _candidatos(self) -> list[str]:
        if self.environment is None:
            raise RuntimeError("El motor CLIPS no ha sido iniciado.")
        candidato = self.environment.find_template("candidato")
        return [fact["nombre"] for fact in candidato.facts()]

    @staticmethod
    def _simbolo_booleano(valor: bool) -> clips.Symbol:
        return clips.Symbol("TRUE" if valor else "FALSE")


class MotorTypeSafe(MotorConocimiento):
    """Motor remoto basado en preguntas Noul de TypeSafe AI."""

    UMBRAL_COMPATIBILIDAD = 0.5

    def __init__(self):
        super().__init__("TypeSafe")
        self._candidatos_actuales = []

    def responder(self, atributo: str, valor: bool) -> EstadoJuego:
        respuestas_anteriores = self.respuestas.copy()
        try:
            return super().responder(atributo, valor)
        except Exception:
            self.respuestas = respuestas_anteriores
            raise

    def _reiniciar_backend(self):
        self._candidatos_actuales = list(self.personajes)

    def _aplicar_respuesta(self, atributo: str, valor: bool):
        pass

    def _candidatos(self) -> list[str]:
        nombres = self._candidatos_actuales
        if not self.respuestas or not nombres:
            return list(nombres)

        state = {
            "personajes": {
                nombre: {
                    atributo: self.personajes[nombre][atributo]
                    for atributo, _ in ATRIBUTOS
                }
                for nombre in nombres
            },
            "respuestas": dict(self.respuestas),
        }
        questions = {
            nombre: Noul(
                instructions=(
                    f"¿El personaje en `personajes.{nombre}` coincide con todas "
                    "las respuestas conocidas en `respuestas`?"
                ),
                criteria={
                    "true": "Todos los atributos registrados coinciden exactamente.",
                    "false": "Al menos un atributo registrado no coincide.",
                },
            )
            for nombre in nombres
        }
        with TypeSafeClient() as client:
            response = client.system_one(state=state, questions=questions)

        self._candidatos_actuales = [
            nombre for nombre in nombres
            if response.nouls[nombre].noul >= self.UMBRAL_COMPATIBILIDAD
        ]
        return list(self._candidatos_actuales)
