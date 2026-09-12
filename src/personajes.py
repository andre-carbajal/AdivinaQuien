"""Base común de personajes y atributos para la interfaz."""

ATRIBUTOS = [
    ("mujer", "¿El personaje es mujer?"),
    ("lentes", "¿El personaje usa lentes?"),
    ("sombrero", "¿El personaje usa sombrero?"),
    ("barba", "¿El personaje tiene barba?"),
    ("cabello_negro", "¿Tiene el cabello negro?"),
    ("cabello_rubio", "¿Tiene el cabello rubio?"),
    ("cabello_rojo", "¿Tiene el cabello rojo?"),
    ("cabello_largo", "¿Tiene el cabello largo?"),
]


PERSONAJES = [
    {"nombre": "Ana", "mujer": True, "lentes": False, "sombrero": False, "barba": False,
     "cabello_negro": True, "cabello_rubio": False, "cabello_rojo": False, "cabello_largo": True},
    {"nombre": "Bruno", "mujer": False, "lentes": True, "sombrero": False, "barba": True,
     "cabello_negro": True, "cabello_rubio": False, "cabello_rojo": False, "cabello_largo": False},
    {"nombre": "Carla", "mujer": True, "lentes": True, "sombrero": True, "barba": False,
     "cabello_negro": False, "cabello_rubio": True, "cabello_rojo": False, "cabello_largo": True},
    {"nombre": "Diego", "mujer": False, "lentes": False, "sombrero": True, "barba": True,
     "cabello_negro": False, "cabello_rubio": False, "cabello_rojo": True, "cabello_largo": False},
    {"nombre": "Elena", "mujer": True, "lentes": True, "sombrero": False, "barba": False,
     "cabello_negro": False, "cabello_rubio": False, "cabello_rojo": True, "cabello_largo": True},
    {"nombre": "Fabio", "mujer": False, "lentes": False, "sombrero": False, "barba": True,
     "cabello_negro": False, "cabello_rubio": True, "cabello_rojo": False, "cabello_largo": False},
    {"nombre": "Gabriela", "mujer": True, "lentes": False, "sombrero": True, "barba": False,
     "cabello_negro": True, "cabello_rubio": False, "cabello_rojo": False, "cabello_largo": True},
    {"nombre": "Hugo", "mujer": False, "lentes": True, "sombrero": True, "barba": False,
     "cabello_negro": False, "cabello_rubio": True, "cabello_rojo": False, "cabello_largo": False},
    {"nombre": "Irene", "mujer": True, "lentes": True, "sombrero": False, "barba": False,
     "cabello_negro": True, "cabello_rubio": False, "cabello_rojo": False, "cabello_largo": False},
    {"nombre": "Javier", "mujer": False, "lentes": False, "sombrero": True, "barba": False,
     "cabello_negro": True, "cabello_rubio": False, "cabello_rojo": False, "cabello_largo": False},
    {"nombre": "Karen", "mujer": True, "lentes": False, "sombrero": False, "barba": False,
     "cabello_negro": False, "cabello_rubio": True, "cabello_rojo": False, "cabello_largo": True},
    {"nombre": "Luis", "mujer": False, "lentes": True, "sombrero": False, "barba": True,
     "cabello_negro": False, "cabello_rubio": False, "cabello_rojo": True, "cabello_largo": False},
]

