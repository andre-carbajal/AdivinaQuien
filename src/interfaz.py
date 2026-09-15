"""Interfaz moderna Tú vs. Computadora para Adivina quién."""

from pathlib import Path
import secrets
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "ctk_vendor"))

import customtkinter as ctk
from PIL import Image, ImageDraw

from motor import MotorClips, MotorLogic

from personajes import ATRIBUTOS, PERSONAJES

MOTOR_LOGIC = "LOGIC.py"

MOTORES = {
    MOTOR_LOGIC: MotorLogic,
    "CLIPS": MotorClips,
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR = {
    "bg": "#171A1F", "surface": "#22262D", "surface2": "#2C313A",
    "card": "#343A44", "line": "#525B68", "white": "#F7F4EF",
    "muted": "#B9C0C8", "blue": "#397E72", "blue2": "#28695E",
    "yellow": "#F1CC82", "green": "#287A5B", "red": "#A94C55",
    "purple": "#BEA3D4", "discarded": "#362C32",
}
def avatar(personaje, size=220):
    """Genera un retrato nítido en memoria; no necesita archivos externos."""
    asset = BASE / "assets" / "personajes" / f"{personaje['nombre'].lower()}.png"
    if asset.exists():
        im = Image.open(asset).convert("RGBA")
        return ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = personaje
    pelo = "#20242B" if p["cabello_negro"] else "#E9B949" if p["cabello_rubio"] else "#BB533D"
    d.ellipse((10, 10, s-10, s-10), fill="#214A7A")
    d.ellipse((40, 40, s-40, s-40), fill="#2A5B91")
    if p["cabello_largo"]:
        d.ellipse((int(s*.22), int(s*.15), int(s*.78), int(s*.90)), fill=pelo)
    d.ellipse((int(s*.30), int(s*.20), int(s*.70), int(s*.78)), fill="#F2BE91")
    d.pieslice((int(s*.28), int(s*.10), int(s*.72), int(s*.48)), 180, 360, fill=pelo)
    if p["sombrero"]:
        d.rounded_rectangle((int(s*.22), int(s*.17), int(s*.78), int(s*.26)), radius=12, fill="#776CFF")
        d.rounded_rectangle((int(s*.34), int(s*.04), int(s*.66), int(s*.21)), radius=16, fill="#776CFF")
    eye = int(s*.025)
    for x in (.42, .58):
        d.ellipse((int(s*x-eye), int(s*.43-eye), int(s*x+eye), int(s*.43+eye)), fill="#152034")
    if p["lentes"]:
        w = max(4, int(s*.015))
        d.ellipse((int(s*.33), int(s*.34), int(s*.49), int(s*.51)), outline="#152034", width=w)
        d.ellipse((int(s*.51), int(s*.34), int(s*.67), int(s*.51)), outline="#152034", width=w)
        d.line((int(s*.49), int(s*.425), int(s*.51), int(s*.425)), fill="#152034", width=w)
    d.arc((int(s*.43), int(s*.52), int(s*.58), int(s*.67)), 20, 160, fill="#9D4D48", width=max(4, int(s*.014)))
    if p["barba"]:
        d.pieslice((int(s*.33), int(s*.46), int(s*.67), int(s*.79)), 0, 180, fill=pelo)
        d.arc((int(s*.43), int(s*.51), int(s*.58), int(s*.65)), 20, 160, fill="#F2BE91", width=max(4, int(s*.014)))
    return ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))


def cpu_image(size=220):
    asset = BASE / "assets" / "personajes" / "computadora.png"
    if asset.exists():
        im = Image.open(asset).convert("RGBA")
        return ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((10, 10, s-10, s-10), fill="#332B78")
    d.rounded_rectangle((int(s*.23), int(s*.25), int(s*.77), int(s*.76)), radius=int(s*.10), fill="#8775FF")
    d.rounded_rectangle((int(s*.30), int(s*.34), int(s*.70), int(s*.62)), radius=int(s*.05), fill="#151C42")
    d.ellipse((int(s*.38), int(s*.43), int(s*.45), int(s*.50)), fill="#60E6FF")
    d.ellipse((int(s*.55), int(s*.43), int(s*.62), int(s*.50)), fill="#60E6FF")
    d.line((int(s*.43), int(s*.57), int(s*.57), int(s*.57)), fill="#60E6FF", width=max(5, int(s*.018)))
    d.line((s//2, int(s*.25), s//2, int(s*.15)), fill="#8775FF", width=max(7, int(s*.025)))
    d.ellipse((int(s*.47), int(s*.09), int(s*.53), int(s*.15)), fill="#FFD54A")
    return ctk.CTkImage(im, size=(size, size))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adivina quién")
        self.geometry("1240x790")
        self.minsize(1080, 720)
        self.configure(fg_color=COLOR["bg"])
        self.motor_nombre = MOTOR_LOGIC
        self.personaje = self.motor = self.estado = None
        self.personaje_cpu = self.motor_usuario = self.estado_usuario = None
        self.turno = "usuario"
        self.ganador = self.mensaje_resultado = None
        self.ultima_respuesta_cpu = ""
        self.descartados_usuario = set()
        self.fase_usuario = "preguntar"
        self.fase_computadora = "preguntar"
        self.tarjetas_usuario = {}
        self.contador_descartes = None
        self.preview_timer = None
        self.preview_index = 0
        self.imagenes = []
        self.inicio()

    def limpiar(self):
        if self.preview_timer is not None:
            self.after_cancel(self.preview_timer)
            self.preview_timer = None
        for w in self.winfo_children(): w.destroy()
        self.imagenes.clear()

    def texto(self, master, value, size=14, color=None, bold=False, **kw):
        return ctk.CTkLabel(master, text=value, text_color=color or COLOR["white"],
                            font=ctk.CTkFont("Segoe UI", size, "bold" if bold else "normal"), **kw)

    def header(self, paso=""):
        h = ctk.CTkFrame(self, fg_color="transparent", height=76)
        h.pack(fill="x", padx=42, pady=(20, 8))
        h.pack_propagate(False)
        self.texto(h, "ADIVINA QUIÉN", 30, COLOR["yellow"], True).place(relx=.5, rely=.5, anchor="center")
        if paso:
            self.texto(h, paso, 11, COLOR["muted"], True).place(relx=0, rely=.5, anchor="w")
        return h

    def boton(self, master, text, command, color, width=180):
        return ctk.CTkButton(master, text=text, command=command, width=width, height=48,
                             corner_radius=16, fg_color=color,
                             hover_color=COLOR["blue2"] if color == COLOR["blue"] else color,
                             text_color=COLOR["white"], text_color_disabled=COLOR["muted"],
                             font=ctk.CTkFont("Segoe UI", 14, "bold"))

    def inicio(self):
        self.limpiar(); self.header()
        hero = ctk.CTkFrame(self, fg_color=COLOR["surface"], corner_radius=28,
                            border_width=1, border_color=COLOR["line"])
        hero.pack(fill="both", expand=True, padx=42, pady=(8, 38))
        self.texto(hero, "SISTEMA BASADO EN CONOCIMIENTO", 11, COLOR["purple"], True).pack(pady=(31, 5))
        self.texto(hero, "Pregunta. Descarta. Adivina.", 35, bold=True).pack()
        self.texto(hero, "Cada jugador elige un personaje secreto. Formula preguntas de Sí o No y descubre al rival antes que la computadora.", 12, COLOR["muted"], wraplength=760, justify="center").pack(pady=(9, 18))
        versus = ctk.CTkFrame(hero, fg_color="transparent")
        versus.pack(expand=True)
        self._jugador_card(versus, "TÚ", COLOR["blue"]).pack(side="left", padx=30)
        badge = ctk.CTkFrame(versus, width=72, height=72, corner_radius=36, fg_color=COLOR["yellow"])
        badge.pack(side="left", padx=6); badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="VS", text_color="#221B2A", font=ctk.CTkFont("Segoe UI", 21, "bold")).place(relx=.5, rely=.5, anchor="center")
        self._cpu_card(versus).pack(side="left", padx=30)
        foot = ctk.CTkFrame(hero, fg_color="transparent")
        foot.pack(fill="x", padx=32, pady=(14, 28))
        self.texto(foot, "Motor de inferencia", 11, COLOR["muted"], True).pack(side="left", padx=(0, 10))
        selector = ctk.CTkSegmentedButton(foot, values=[MOTOR_LOGIC, "CLIPS"], selected_color=COLOR["blue"],
                                          selected_hover_color=COLOR["blue2"], unselected_color=COLOR["surface2"],
                                          unselected_hover_color=COLOR["card"], text_color=COLOR["white"],
                                          corner_radius=13, command=lambda v: setattr(self, "motor_nombre", v))
        selector.set(self.motor_nombre); selector.pack(side="left")
        self.boton(foot, "Empezar partida  →", self.seleccion, COLOR["blue"], 210).pack(side="right")

    def _jugador_card(self, master, title, accent):
        card=ctk.CTkFrame(master,width=260,height=300,corner_radius=24,fg_color=COLOR["surface2"],border_width=2,border_color=accent); card.pack_propagate(False)
        self.preview_imagenes = [avatar(personaje,180) for personaje in PERSONAJES]
        self.imagenes.extend(self.preview_imagenes)
        self.preview_index = 0
        self.preview_label=ctk.CTkLabel(card,text="",image=self.preview_imagenes[0])
        self.preview_label.pack(pady=(24,8))
        self.texto(card,title,19,accent,True).pack()
        self.texto(card,"12 personajes disponibles",11,COLOR["muted"]).pack(pady=3)
        self.preview_timer = self.after(2600,self.rotar_preview)
        return card

    def rotar_preview(self):
        """Cambia solo la imagen de ejemplo; nunca selecciona un personaje."""
        self.preview_timer = None
        if not self.preview_label.winfo_exists():
            return
        self.preview_index = (self.preview_index + 1) % len(self.preview_imagenes)
        self.preview_label.configure(image=self.preview_imagenes[self.preview_index])
        self.preview_timer = self.after(2600,self.rotar_preview)
    def _cpu_card(self, master):
        card=ctk.CTkFrame(master,width=260,height=300,corner_radius=24,fg_color=COLOR["surface2"],border_width=2,border_color=COLOR["purple"]); card.pack_propagate(False)
        img=cpu_image(180); self.imagenes.append(img); ctk.CTkLabel(card,text="",image=img).pack(pady=(24,8))
        self.texto(card,"COMPUTADORA",19,COLOR["purple"],True).pack(); self.texto(card,"Analiza tus respuestas",11,COLOR["muted"]).pack(pady=3); return card

    def seleccion(self):
        self.limpiar(); h=self.header("PASO 1 · ELIGE EN SECRETO")
        self.boton(h,"← Volver",self.inicio,COLOR["surface2"],110).pack(side="right",padx=(0,16))
        title=ctk.CTkFrame(self,fg_color="transparent"); title.pack(fill="x",padx=48,pady=(0,12))
        self.texto(title,"¿Quién será tu personaje?",28,bold=True).pack(anchor="w"); self.texto(title,"Haz clic en una tarjeta. La computadora no mirará… prometido.",12,COLOR["muted"]).pack(anchor="w",pady=4)
        board=ctk.CTkScrollableFrame(self,fg_color=COLOR["surface"],corner_radius=26,border_width=1,border_color=COLOR["line"])
        board.pack(fill="both",expand=True,padx=42,pady=(0,34))
        for col in range(6): board.grid_columnconfigure(col,weight=1)
        for i,p in enumerate(PERSONAJES):
            img=avatar(p,112); self.imagenes.append(img)
            b=ctk.CTkButton(board,text=p["nombre"],image=img,compound="top",width=155,height=205,
                            corner_radius=20,fg_color=COLOR["card"],hover_color=COLOR["blue2"],
                            border_width=2,border_color=COLOR["line"],
                            text_color=COLOR["white"],
                            font=ctk.CTkFont("Segoe UI",14,"bold"),command=lambda x=p:self.elegir(x))
            b.grid(row=i//6,column=i%6,padx=10,pady=12,sticky="nsew")

    def elegir(self, personaje):
        self.personaje = personaje
        opciones_cpu = [
            candidato for candidato in PERSONAJES
            if candidato["nombre"] != personaje["nombre"]
        ]
        self.personaje_cpu = secrets.choice(opciones_cpu)
        motor_cls = MOTORES[self.motor_nombre]
        self.motor = motor_cls()
        self.estado = self.motor.iniciar()
        self.motor_usuario = motor_cls()
        self.estado_usuario = self.motor_usuario.iniciar()
        self.turno = "usuario"
        self.ganador = self.mensaje_resultado = None
        self.ultima_respuesta_cpu = ""
        self.descartados_usuario = set()
        self.fase_usuario = "preguntar"
        self.fase_computadora = "preguntar"
        self.juego()

    def juego(self):
        self.limpiar(); h=self.header("PARTIDA EN CURSO")
        self.boton(h,"Cambiar personaje",self.seleccion,COLOR["surface2"],155).pack(side="right",padx=(0,16))
        self.panel=ctk.CTkFrame(self,corner_radius=26,fg_color=COLOR["surface"],border_width=2,border_color=COLOR["blue"])
        self.panel.pack(fill="both",expand=True,padx=42,pady=(8,34))
        self.actualizar()

    def actualizar(self):
        for w in self.panel.winfo_children(): w.destroy()
        if self.ganador:
            self.resultado()
            return
        if self.turno == "usuario":
            self.panel.configure(border_color=COLOR["blue"])
            self.turno_usuario(self.panel)
        else:
            self.panel.configure(border_color=COLOR["purple"])
            self.turno_computadora(self.panel)

    def turno_computadora(self, panel):
        """La computadora formula una pregunta sobre el personaje del jugador."""
        if self.estado.estado != "preguntando":
            self.ganador = "computadora"
            self.mensaje_resultado = f"La computadora dedujo que elegiste a {self.estado.identificado}."
            self.resultado()
            return
        attr,pregunta=self.estado.pregunta
        respuesta_anterior = None
        if self.fase_computadora == "revisar" and self.estado.historial:
            ultima = self.estado.historial[-1]
            attr, pregunta = ultima["atributo"], ultima["pregunta"]
            respuesta_anterior = ultima["valor"]
        top=ctk.CTkFrame(panel,fg_color="transparent"); top.pack(fill="x",padx=30,pady=(20,6))
        self.texto(top,"TURNO DE LA COMPUTADORA",13,COLOR["purple"],True).pack(side="left")
        self.texto(top,f"{len(self.estado.candidatos)} candidatos posibles",10,COLOR["muted"],True).pack(side="right")
        contenido=ctk.CTkFrame(panel,fg_color="transparent"); contenido.pack(fill="both",expand=True,padx=28,pady=(3,22))
        contenido.grid_columnconfigure(0,weight=0); contenido.grid_columnconfigure(1,weight=1); contenido.grid_rowconfigure(0,weight=1)

        lateral=ctk.CTkFrame(contenido,width=335,corner_radius=20,fg_color=COLOR["surface2"])
        lateral.grid(row=0,column=0,sticky="nsew",padx=(0,14)); lateral.grid_propagate(False)
        img=avatar(self.personaje,165); self.imagenes.append(img); ctk.CTkLabel(lateral,text="",image=img).pack(pady=(24,2))
        self.texto(lateral,"TU PERSONAJE",11,COLOR["muted"],True).pack(); self.texto(lateral,self.personaje["nombre"],22,bold=True).pack(pady=(0,15))
        bubble=ctk.CTkFrame(lateral,corner_radius=13,fg_color=COLOR["card"]); bubble.pack(fill="x",padx=16,pady=4)
        self.texto(bubble,pregunta,15,bold=True,wraplength=270,justify="center").pack(padx=12,pady=17)
        if respuesta_anterior is not None:
            self.texto(lateral,"Respuesta: Sí" if respuesta_anterior else "Respuesta: No",14,
                       COLOR["green"] if respuesta_anterior else COLOR["red"],True).pack(pady=(10,0))
        actions=ctk.CTkFrame(lateral,fg_color="transparent"); actions.pack(pady=16)
        si=self.boton(actions,"Sí",lambda:self.responder_computadora(attr,True),COLOR["green"],125); si.pack(side="left",padx=5)
        no=self.boton(actions,"No",lambda:self.responder_computadora(attr,False),COLOR["red"],125); no.pack(side="left",padx=5)
        if self.fase_computadora == "revisar":
            si.configure(state="disabled"); no.configure(state="disabled")
            self.texto(lateral,"La computadora actualizó sus descartes.",9,COLOR["yellow"],True).pack(pady=(0,8))

        derecha=ctk.CTkFrame(contenido,corner_radius=20,fg_color=COLOR["surface2"]); derecha.grid(row=0,column=1,sticky="nsew")
        cab=ctk.CTkFrame(derecha,fg_color="transparent"); cab.pack(fill="x",padx=20,pady=(14,6))
        self.texto(cab,"TABLERO DE LA COMPUTADORA",13,COLOR["purple"],True).pack(side="left")
        self.texto(cab,"Marco rojo: personaje descartado",9,COLOR["muted"]).pack(side="right")
        tablero=ctk.CTkScrollableFrame(derecha,fg_color="transparent"); tablero.pack(fill="both",expand=True,padx=10,pady=(0,8))
        posibles=set(self.estado.candidatos)
        for col in range(4): tablero.grid_columnconfigure(col,weight=1)
        for i,p in enumerate(PERSONAJES):
            self._tarjeta_cpu(tablero,p,p["nombre"] not in posibles).grid(row=i//4,column=i%4,padx=6,pady=6,sticky="nsew")
        if self.fase_computadora == "revisar":
            self.boton(derecha,"Siguiente turno",self.continuar_turno_usuario,COLOR["blue"],190).pack(pady=(0,12))

    def responder_computadora(self, atributo, valor):
        self.estado = self.motor.responder(atributo, valor)
        if self.estado.estado == "identificado":
            self.ganador = "computadora"
            self.mensaje_resultado = f"La computadora dedujo que elegiste a {self.estado.identificado}."
        elif self.estado.estado != "preguntando":
            self.ganador = "usuario"
            self.mensaje_resultado = "Tus respuestas dejaron a la computadora sin una conclusión válida."
        else:
            self.fase_computadora = "revisar"
        self.actualizar()

    def continuar_turno_usuario(self):
        self.fase_computadora = "preguntar"
        self.fase_usuario = "preguntar"
        self.turno = "usuario"
        self.actualizar()

    def turno_usuario(self, panel):
        """Permite al jugador preguntar o acusar a un personaje."""
        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.pack(fill="x", padx=30, pady=(20, 6))
        self.texto(top, "TU TURNO", 13, COLOR["blue"], True).pack(side="left")
        restantes = self._restantes_usuario()
        self.contador_descartes = self.texto(top, f"{restantes} personajes sin descartar", 10, COLOR["muted"], True)
        self.contador_descartes.pack(side="right")

        contenido = ctk.CTkFrame(panel, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=28, pady=(3, 22))
        contenido.grid_columnconfigure(0, weight=0)
        contenido.grid_columnconfigure(1, weight=1)
        contenido.grid_rowconfigure(0, weight=1)

        lateral = ctk.CTkFrame(contenido, width=335, corner_radius=20, fg_color=COLOR["surface2"])
        lateral.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        lateral.grid_propagate(False)
        img_cpu = cpu_image(138); self.imagenes.append(img_cpu)
        ctk.CTkLabel(lateral, text="", image=img_cpu).pack(pady=(13, 0))
        self.texto(lateral, "COMPUTADORA", 13, COLOR["purple"], True).pack(pady=(0, 5))
        estado_texto = self.ultima_respuesta_cpu or "Selecciona una pregunta"
        self.texto(lateral, estado_texto, 9, COLOR["yellow"] if self.ultima_respuesta_cpu else COLOR["muted"], True,
                   wraplength=285, justify="center").pack(padx=16, pady=(0, 9))

        preguntas = ctk.CTkFrame(lateral, fg_color="transparent")
        preguntas.pack(fill="x", padx=13, pady=(0, 12))
        for i, (atributo, pregunta) in enumerate(ATRIBUTOS):
            respondida = atributo in self.motor_usuario.respuestas
            valor = self.motor_usuario.respuestas.get(atributo)
            color = COLOR["green"] if respondida and valor else COLOR["red"] if respondida else COLOR["card"]
            prefijo = "Sí  ·  " if respondida and valor else "No  ·  " if respondida else ""
            b = ctk.CTkButton(
                preguntas, text=prefijo + pregunta, height=34, corner_radius=10,
                fg_color=color, hover_color=color if respondida else COLOR["blue2"], anchor="w",
                text_color=COLOR["white"], text_color_disabled=COLOR["white"] if respondida else COLOR["muted"],
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                command=lambda a=atributo: self.preguntar_computadora(a),
            )
            b.pack(fill="x", pady=3)
            if respondida or self.fase_usuario == "descartar":
                b.configure(state="disabled")

        derecha = ctk.CTkFrame(contenido, corner_radius=20, fg_color=COLOR["surface2"])
        derecha.grid(row=0, column=1, sticky="nsew")
        cab = ctk.CTkFrame(derecha, fg_color="transparent")
        cab.pack(fill="x", padx=20, pady=(14, 6))
        self.texto(cab, "TABLERO DE PERSONAJES", 13, COLOR["blue"], True).pack(side="left")
        self.texto(cab, "Pulsa una tarjeta para descartarla", 9, COLOR["muted"]).pack(side="right")
        tablero = ctk.CTkScrollableFrame(derecha, fg_color="transparent")
        tablero.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tarjetas_usuario = {}
        for col in range(4): tablero.grid_columnconfigure(col, weight=1)
        for i, personaje in enumerate(PERSONAJES):
            self._tarjeta_descartable(tablero, personaje).grid(
                row=i//4, column=i%4, padx=6, pady=6, sticky="nsew"
            )
        if self.fase_usuario == "descartar":
            self.boton(derecha,"Siguiente turno",self.continuar_turno_computadora,COLOR["blue"],190).pack(pady=(0,12))

    def _tarjeta_descartable(self, master, personaje):
        """Tarjeta que permite descartar manualmente sin convertir el clic en acusación."""
        nombre = personaje["nombre"]
        descartado = self._esta_descartado_usuario(nombre)
        card = ctk.CTkFrame(master, width=150, height=168, corner_radius=15,
                            fg_color=COLOR["discarded"] if descartado else COLOR["card"],
                            border_width=2, border_color=COLOR["red"] if descartado else COLOR["line"])
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        img = avatar(personaje, 86); self.imagenes.append(img)
        foto = ctk.CTkLabel(card, text="", image=img)
        foto.grid(row=0, column=0, pady=(7, 0))
        etiqueta = self.texto(card, nombre, 11, COLOR["muted"] if descartado else COLOR["white"], True)
        etiqueta.grid(row=1, column=0, pady=(0, 3))
        adivinar = ctk.CTkButton(card, text="Adivinar", height=25, corner_radius=8,
                                fg_color=COLOR["blue"], hover_color=COLOR["blue2"],
                                text_color=COLOR["white"], text_color_disabled=COLOR["muted"],
                                font=ctk.CTkFont("Segoe UI", 9, "bold"),
                                command=lambda p=personaje: self.adivinar(p))
        adivinar.grid(row=2, column=0, padx=18, pady=(0, 7), sticky="ew")
        if descartado:
            adivinar.configure(state="disabled")
        for widget in (card, foto, etiqueta):
            widget.bind("<Button-1>", lambda _e, n=nombre: self.alternar_descarte(n))
        self.tarjetas_usuario[nombre] = {
            "card": card,
            "etiqueta": etiqueta,
            "adivinar": adivinar,
        }
        return card

    def alternar_descarte(self, nombre):
        if self.fase_usuario != "descartar":
            return
        candidatos = set(self.estado_usuario.candidatos)
        if nombre not in candidatos:
            return
        if nombre in self.descartados_usuario:
            self.descartados_usuario.remove(nombre)
        else:
            self.descartados_usuario.add(nombre)
        self._actualizar_descarte_visual(nombre)

    def _esta_descartado_usuario(self, nombre):
        candidatos = set(self.estado_usuario.candidatos)
        return nombre not in candidatos or nombre in self.descartados_usuario

    def _restantes_usuario(self):
        candidatos = set(self.estado_usuario.candidatos)
        return len(candidatos - self.descartados_usuario)

    def _actualizar_descarte_visual(self, nombre):
        """Actualiza una tarjeta sin reconstruir el tablero ni perder el scroll."""
        widgets = self.tarjetas_usuario.get(nombre)
        if not widgets:
            return
        descartado = self._esta_descartado_usuario(nombre)
        widgets["card"].configure(
            fg_color=COLOR["discarded"] if descartado else COLOR["card"],
            border_width=3 if descartado else 2,
            border_color=COLOR["red"] if descartado else COLOR["line"],
        )
        widgets["etiqueta"].configure(
            text_color=COLOR["muted"] if descartado else COLOR["white"]
        )
        widgets["adivinar"].configure(state="disabled" if descartado else "normal")
        if self.contador_descartes is not None:
            restantes = self._restantes_usuario()
            self.contador_descartes.configure(text=f"{restantes} personajes sin descartar")

    def _tarjeta_cpu(self, master, personaje, descartado):
        card=ctk.CTkFrame(master,width=150,height=142,corner_radius=15,
                          fg_color=COLOR["discarded"] if descartado else COLOR["card"],
                          border_width=3 if descartado else 1,
                          border_color=COLOR["red"] if descartado else COLOR["line"])
        card.grid_propagate(False); card.grid_columnconfigure(0,weight=1)
        img=avatar(personaje,86); self.imagenes.append(img)
        ctk.CTkLabel(card,text="",image=img).grid(row=0,column=0,pady=(8,0))
        self.texto(card,personaje["nombre"],11,COLOR["muted"] if descartado else COLOR["white"],True).grid(row=1,column=0,pady=(0,8))
        return card

    def preguntar_computadora(self, atributo):
        valor = bool(self.personaje_cpu[atributo])
        pregunta = dict(ATRIBUTOS)[atributo]
        self.estado_usuario = self.motor_usuario.responder(atributo, valor)
        respuesta = "Sí" if valor else "No"
        self.ultima_respuesta_cpu = f"La computadora respondió {respuesta}: {pregunta}"
        self.fase_usuario = "descartar"
        self.actualizar()

    def continuar_turno_computadora(self):
        self.fase_usuario = "preguntar"
        self.fase_computadora = "preguntar"
        self.turno = "computadora"
        self.actualizar()

    def adivinar(self, personaje):
        if personaje["nombre"] == self.personaje_cpu["nombre"]:
            self.ganador = "usuario"
            self.mensaje_resultado = f"¡Adivinaste! La computadora había elegido a {personaje['nombre']}."
        else:
            self.ganador = "computadora"
            self.mensaje_resultado = f"Tu elección fue {personaje['nombre']}, pero el personaje secreto era {self.personaje_cpu['nombre']}."
        self.actualizar()

    def resultado(self):
        pop=ctk.CTkToplevel(self); pop.title("Resultado de la partida"); pop.geometry("540x650"); pop.resizable(False,False); pop.configure(fg_color=COLOR["bg"]); pop.transient(self); pop.grab_set(); pop.protocol("WM_DELETE_WINDOW",lambda:self.cerrar(pop,self.inicio))
        usuario_gana = self.ganador == "usuario"
        color = COLOR["green"] if usuario_gana else COLOR["yellow"]
        card=ctk.CTkFrame(pop,corner_radius=28,fg_color=COLOR["surface"],border_width=2,border_color=color); card.pack(fill="both",expand=True,padx=24,pady=24)
        self.texto(card,"¡GANASTE!" if usuario_gana else "GANÓ LA COMPUTADORA",13,color,True).pack(pady=(28,4)); self.texto(card,"Personaje secreto revelado",25,bold=True).pack()
        encontrado=self.personaje_cpu if usuario_gana else self.personaje
        if self.ganador == "computadora" and self.mensaje_resultado and "personaje secreto" in self.mensaje_resultado:
            encontrado = self.personaje_cpu
        img=avatar(encontrado,235); self.imagenes.append(img); ctk.CTkLabel(card,text="",image=img).pack(pady=(16,6)); self.texto(card,encontrado["nombre"],31,bold=True).pack(); self.texto(card,self.mensaje_resultado or "Partida terminada.",11,COLOR["muted"],wraplength=420,justify="center").pack(pady=(5,18)); self.texto(card,f"Motor {self.motor_nombre} · Turnos alternados",10,COLOR["muted"]).pack()
        actions=ctk.CTkFrame(card,fg_color="transparent"); actions.pack(pady=22); self.boton(actions,"Jugar otra vez",lambda:self.cerrar(pop,self.seleccion),COLOR["blue"],180).pack(side="left",padx=6); self.boton(actions,"Inicio",lambda:self.cerrar(pop,self.inicio),COLOR["surface2"],110).pack(side="left",padx=6)

    @staticmethod
    def cerrar(pop, accion):
        pop.grab_release(); pop.destroy(); accion()


def ejecutar():
    App().mainloop()
