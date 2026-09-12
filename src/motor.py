"""Contrato del motor y motor local para probar la interfaz.

Los adaptadores LOGIC.py y CLIPS deberán exponer estas mismas operaciones.
"""

from dataclasses import dataclass, field
from typing import Optional

from personajes import ATRIBUTOS, PERSONAJES


@dataclass
class EstadoJuego:
    estado: str
    candidatos: list[str]
    pregunta: Optional[tuple[str, str]] = None
    identificado: Optional[str] = None
    historial: list[dict] = field(default_factory=list)
    explicacion: str = ""


class MotorConocimiento:
    """Interfaz que deberán cumplir MotorLogic y MotorClips."""

    def iniciar(self) -> EstadoJuego:
        raise NotImplementedError

    def responder(self, atributo: str, valor: bool) -> EstadoJuego:
        raise NotImplementedError

    def reiniciar(self) -> EstadoJuego:
        return self.iniciar()


class MotorDemostracion(MotorConocimiento):
    """Filtrado determinista usado para desarrollar y probar la interfaz."""

    def __init__(self, tecnologia: str = "LOGIC.py"):
        self.tecnologia = tecnologia
        self.personajes = {p["nombre"]: p for p in PERSONAJES}
        self.preguntas = dict(ATRIBUTOS)
        self.respuestas: dict[str, bool] = {}
        self.historial: list[dict] = []

    def iniciar(self) -> EstadoJuego:
        self.respuestas = {}
        self.historial = []
        return self._estado()

    def responder(self, atributo: str, valor: bool) -> EstadoJuego:
        if atributo in self.respuestas and self.respuestas[atributo] != valor:
            return EstadoJuego(
                estado="contradiccion",
                candidatos=self._candidatos(),
                historial=list(self.historial),
                explicacion="El atributo ya tenía una respuesta diferente.",
            )
        self.respuestas[atributo] = valor
        candidatos = self._candidatos()
        descartados = [
            p["nombre"] for p in PERSONAJES
            if p["nombre"] not in candidatos
            and all(p[a] == v for a, v in list(self.respuestas.items())[:-1])
        ]
        self.historial.append({
            "atributo": atributo,
            "pregunta": self.preguntas[atributo],
            "valor": valor,
            "candidatos": list(candidatos),
            "descartados": descartados,
        })
        return self._estado()

    def _candidatos(self) -> list[str]:
        return [
            p["nombre"] for p in PERSONAJES
            if all(p[a] == v for a, v in self.respuestas.items())
        ]

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

    def _estado(self) -> EstadoJuego:
        candidatos = self._candidatos()
        if not candidatos:
            return EstadoJuego(
                estado="sin_coincidencia", candidatos=[], historial=list(self.historial),
                explicacion="Ningún personaje coincide con todas las respuestas.",
            )
        if len(candidatos) == 1:
            nombre = candidatos[0]
            return EstadoJuego(
                estado="identificado", candidatos=candidatos, identificado=nombre,
                historial=list(self.historial),
                explicacion=f"{nombre} es el único personaje compatible con los hechos registrados.",
            )
        pregunta = self._mejor_pregunta(candidatos)
        if pregunta is None:
            return EstadoJuego(
                estado="indistinguible", candidatos=candidatos, historial=list(self.historial),
                explicacion="La base no contiene otro atributo capaz de separar los candidatos.",
            )
        return EstadoJuego(
            estado="preguntando", candidatos=candidatos, pregunta=pregunta,
            historial=list(self.historial),
            explicacion=f"Quedan {len(candidatos)} candidatos compatibles.",
        )

