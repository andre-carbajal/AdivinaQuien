<div align="center">
  <h1>ADIVINA QUIÉN</h1>
  ## About
Adivina Quién es un juego de deducción desarrollado como sistema basado en conocimiento. Cada personaje se representa mediante hechos y atributos; las respuestas permiten aplicar inferencia, descartar candidatos y alcanzar una conclusión justificable.

<p><strong>Pregunta, descarta y descubre el personaje secreto antes que el sistema.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/CustomTkinter-5.2.2-1F6AA5?style=for-the-badge" alt="CustomTkinter 5.2.2">
    <img src="https://img.shields.io/badge/Estado-Jugable-2ED18A?style=for-the-badge" alt="Estado jugable">
  </p>
</div>

---

**Adivina Quién** es un juego de deducción desarrollado como sistema basado en conocimiento. Cada personaje se representa mediante hechos y atributos; las respuestas permiten aplicar inferencia, descartar candidatos y alcanzar una conclusión justificable.

El jugador y el sistema conservan personajes secretos y se alternan para formular preguntas de **Sí** o **No**. Gana quien identifique primero al personaje contrario.

## Características principales

- Interfaz gráfica moderna desarrollada con CustomTkinter.
- Doce personajes originales con retratos caricaturescos.
- Preguntas binarias basadas en atributos observables.
- Selección dinámica de preguntas para reducir el conjunto de candidatos.
- Registro de respuestas y candidatos compatibles.
- Turnos secuenciales dentro de una única ventana.
- Tablero interactivo para formular preguntas o identificar un personaje.
- Pantalla final con el resultado y la explicación de la conclusión.
- Arquitectura preparada para comparar LOGIC.py con una segunda tecnología.
- Pruebas automáticas para validar la identificación de los personajes.

## Cómo jugar

Al comenzar una partida, cada participante conserva un personaje secreto. El sistema administra dos procesos de deducción independientes: uno representa el razonamiento realizado a partir de las respuestas del jugador y otro conserva las respuestas obtenidas sobre el personaje secreto del sistema.

La partida sigue este ciclo:

1. El jugador selecciona un personaje de la base de conocimiento.
2. El sistema elige un personaje secreto.
3. El jugador formula una pregunta sobre un atributo o intenta identificar un candidato.
4. La respuesta obtenida descarta los personajes incompatibles.
5. El sistema formula su propia pregunta y el jugador responde **Sí** o **No**.
6. Los turnos continúan hasta que se identifica correctamente un personaje.

Una identificación correcta produce la victoria. Si el jugador selecciona un candidato incorrecto, la partida termina y se revela el personaje secreto.

## Base de conocimiento

Cada personaje está representado mediante proposiciones booleanas. La versión actual utiliza los siguientes atributos:

| Atributo | Pregunta asociada |
|---|---|
| `mujer` | ¿El personaje es mujer? |
| `lentes` | ¿El personaje usa lentes? |
| `sombrero` | ¿El personaje usa sombrero? |
| `barba` | ¿El personaje tiene barba? |
| `cabello_negro` | ¿Tiene el cabello negro? |
| `cabello_rubio` | ¿Tiene el cabello rubio? |
| `cabello_rojo` | ¿Tiene el cabello rojo? |
| `cabello_largo` | ¿Tiene el cabello largo? |

El motor conserva únicamente los personajes que satisfacen todas las respuestas registradas. La siguiente pregunta se selecciona buscando una división equilibrada entre los candidatos restantes, lo que reduce progresivamente el espacio de búsqueda.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10 o superior |
| Interfaz gráfica | CustomTkinter 5.2.2 |
| Procesamiento de imágenes | Pillow |
| Representación actual | Hechos booleanos y filtrado determinista |
| Primera alternativa académica | LOGIC.py |
| Segunda alternativa propuesta | CLIPS |

## Arquitectura del proyecto

```text
ADIVINAQUIEN/
├── docs/
│   ├── images/
│   │   └── interfaz-partida.png
│   └── informe_hasta_capitulo_viii.docx
├── src/
│   ├── assets/
│   │   └── personajes/
│   ├── interfaz.py
│   ├── main.py
│   ├── motor.py
│   └── personajes.py
├── tests/
│   └── test_motor.py
├── .gitignore
├── README.md
└── requirements.txt
```

### Responsabilidad de los módulos

- `main.py`: punto de entrada de la aplicación.
- `interfaz.py`: navegación, componentes visuales y gestión de turnos.
- `personajes.py`: personajes, atributos y preguntas de la base de conocimiento.
- `motor.py`: contrato del motor y estrategia de inferencia utilizada por la demostración.
- `assets/personajes/`: recursos gráficos de los personajes.
- `test_motor.py`: validación automática del proceso de identificación.

## Instalación

### Requisitos previos

- Python 3.10 o superior.
- `pip` disponible desde la terminal.

### Preparación del entorno

```powershell
git clone https://github.com/andre-carbajal/AdivinaQuien.git
cd ADIVINAQUIEN
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En Linux o macOS, la activación del entorno virtual se realiza con:

```bash
source .venv/bin/activate
```

## Ejecución

```powershell
python src\main.py
```

## Pruebas

```powershell
python tests\test_motor.py
```

La prueba recorre los doce personajes, responde cada pregunta según sus atributos y verifica que el motor alcance la identificación correcta.

## Estado del desarrollo

La interfaz, la base común de personajes, el flujo completo de la partida y el motor local de demostración se encuentran operativos. El selector visual incluye **LOGIC.py** y **CLIPS**, pero su integración académica definitiva debe realizarse mediante adaptadores que implementen el contrato `MotorConocimiento` definido en `src/motor.py`.

Esta separación permite conservar la misma interfaz y base conceptual al comparar ambas tecnologías.

## Próximas mejoras

- Integrar completamente los motores LOGIC.py y CLIPS.
- Incorporar la explicación detallada de las reglas activadas en cada inferencia.
- Ampliar la cantidad de personajes y atributos sin generar combinaciones indistinguibles.
- Guardar estadísticas de partidas, preguntas utilizadas y resultados.
- Añadir pruebas de interfaz y casos de contradicción.

---

<div align="center">
  <strong>¿Listo para descubrir quién es?</strong><br>
  Elige un personaje, formula la pregunta correcta y pon a prueba tu capacidad de deducción.
</div>
