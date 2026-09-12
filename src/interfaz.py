"""Interfaz moderna Tú vs. Computadora para Adivina quién."""
from pathlib import Path
import random
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "ctk_vendor"))

import customtkinter as ctk
from PIL import Image, ImageDraw

from motor import MotorDemostracion
from personajes import ATRIBUTOS, PERSONAJES

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR = {
    "bg": "#07172F", "surface": "#0D2344", "surface2": "#132E55",
    "card": "#173963", "line": "#285487", "white": "#F8FBFF",
    "muted": "#AFC4DF", "blue": "#2F8CFF", "blue2": "#166DDD",
    "yellow": "#FFD54A", "green": "#2ED18A", "red": "#FF5C6C",
    "purple": "#8775FF",
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
        self.motor_nombre = "LOGIC.py"
        self.personaje = self.motor = self.estado = None
        self.personaje_cpu = self.motor_usuario = self.estado_usuario = None
        self.turno = "usuario"
        self.ganador = self.mensaje_resultado = None
        self.ultima_respuesta_cpu = ""
        self.imagenes = []
        self.inicio()

    def limpiar(self):
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
        self._jugador_card(versus, "TÚ", PERSONAJES[0], COLOR["blue"]).pack(side="left", padx=30)
        badge = ctk.CTkFrame(versus, width=72, height=72, corner_radius=36, fg_color=COLOR["yellow"])
        badge.pack(side="left", padx=6); badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="VS", text_color="#17213A", font=ctk.CTkFont("Segoe UI", 21, "bold")).place(relx=.5, rely=.5, anchor="center")
        self._cpu_card(versus).pack(side="left", padx=30)
        foot = ctk.CTkFrame(hero, fg_color="transparent")
        foot.pack(fill="x", padx=32, pady=(14, 28))
        self.texto(foot, "Motor de inferencia", 11, COLOR["muted"], True).pack(side="left", padx=(0, 10))
        selector = ctk.CTkSegmentedButton(foot, values=["LOGIC.py", "CLIPS"], selected_color=COLOR["blue"],
                                          selected_hover_color=COLOR["blue2"], unselected_color=COLOR["surface2"],
                                          corner_radius=13, command=lambda v: setattr(self, "motor_nombre", v))
        selector.set(self.motor_nombre); selector.pack(side="left")
        self.boton(foot, "Empezar partida  →", self.seleccion, COLOR["blue"], 210).pack(side="right")

    def _jugador_card(self, master, title, personaje, accent):
        card=ctk.CTkFrame(master,width=260,height=300,corner_radius=24,fg_color=COLOR["surface2"],border_width=2,border_color=accent); card.pack_propagate(False)
        img=avatar(personaje,180); self.imagenes.append(img); ctk.CTkLabel(card,text="",image=img).pack(pady=(24,8))
        self.texto(card,title,19,accent,True).pack(); self.texto(card,"Elige tu personaje",11,COLOR["muted"]).pack(pady=3); return card
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
                            font=ctk.CTkFont("Segoe UI",14,"bold"),command=lambda x=p:self.elegir(x))
            b.grid(row=i//6,column=i%6,padx=10,pady=12,sticky="nsew")

    def elegir(self, personaje):
        self.personaje = personaje
        self.personaje_cpu = random.choice(PERSONAJES)
        self.motor = MotorDemostracion(self.motor_nombre)
        self.estado = self.motor.iniciar()
        self.motor_usuario = MotorDemostracion(self.motor_nombre)
        self.estado_usuario = self.motor_usuario.iniciar()
        self.turno = "usuario"
        self.ganador = self.mensaje_resultado = None
        self.ultima_respuesta_cpu = ""
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
        attr,pregunta=self.estado.pregunta; n=len(self.estado.historial)+1
        top=ctk.CTkFrame(panel,fg_color="transparent"); top.pack(fill="x",padx=26,pady=(22,7))
        self.texto(top,"TURNO DE LA COMPUTADORA",13,COLOR["purple"],True).pack(side="left")
        self.texto(top,"RESPONDE SÍ O NO",10,COLOR["muted"],True).pack(side="right")
        ficha=ctk.CTkFrame(panel,corner_radius=17,fg_color=COLOR["surface2"]); ficha.pack(fill="x",padx=26,pady=(0,13))
        img=avatar(self.personaje,92); self.imagenes.append(img); ctk.CTkLabel(ficha,text="",image=img).pack(side="left",padx=15,pady=10)
        info=ctk.CTkFrame(ficha,fg_color="transparent"); info.pack(side="left",fill="y",pady=17)
        self.texto(info,"Tu personaje",10,COLOR["muted"]).pack(anchor="w"); self.texto(info,self.personaje["nombre"],22,bold=True).pack(anchor="w"); self.texto(info,f"Pregunta {n} · {len(self.estado.candidatos)} candidatos",10,COLOR["muted"]).pack(anchor="w",pady=3)
        if self.ultima_respuesta_cpu:
            aviso=ctk.CTkFrame(panel,corner_radius=13,fg_color=COLOR["card"]); aviso.pack(fill="x",padx=26,pady=(0,10))
            self.texto(aviso,self.ultima_respuesta_cpu,10,COLOR["yellow"],True,wraplength=900,justify="left").pack(anchor="w",padx=16,pady=10)
        bubble=ctk.CTkFrame(panel,corner_radius=18,fg_color=COLOR["card"]); bubble.pack(fill="x",padx=26,pady=5)
        self.texto(bubble,pregunta,25,bold=True,wraplength=900,justify="left").pack(anchor="w",padx=22,pady=25)
        self.texto(panel,"Responde según el personaje que elegiste",11,COLOR["muted"]).pack(anchor="w",padx=28,pady=(13,10))
        actions=ctk.CTkFrame(panel,fg_color="transparent"); actions.pack(anchor="w",padx=26)
        si=self.boton(actions,"✓  Sí",lambda:self.responder_computadora(attr,True),COLOR["green"],145); si.pack(side="left",padx=(0,9))
        no=self.boton(actions,"✕  No",lambda:self.responder_computadora(attr,False),COLOR["red"],145); no.pack(side="left")
        if self.estado.historial:
            last=self.estado.historial[-1]; self.texto(panel,f"Anterior: {'Sí' if last['valor'] else 'No'} · {last['pregunta']}",9,COLOR["muted"],wraplength=480,justify="left").pack(anchor="w",padx=28,pady=16)

    def responder_computadora(self, atributo, valor):
        self.estado = self.motor.responder(atributo, valor)
        if self.estado.estado == "identificado":
            self.ganador = "computadora"
            self.mensaje_resultado = f"La computadora dedujo que elegiste a {self.estado.identificado}."
        elif self.estado.estado != "preguntando":
            self.ganador = "usuario"
            self.mensaje_resultado = "Tus respuestas dejaron a la computadora sin una conclusión válida."
        else:
            self.turno = "usuario"
        self.actualizar()

    def turno_usuario(self, panel):
        """Permite al jugador preguntar o acusar a un personaje."""
        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.pack(fill="x", padx=38, pady=(25, 6))
        self.texto(top, "TU TURNO", 13, COLOR["blue"], True).pack(side="left")
        self.texto(top, "ELIGE UNA ACCIÓN", 10, COLOR["green"],True).pack(side="right")
        self.texto(panel, "Pregunta o intenta adivinar", 23, bold=True).pack(anchor="w", padx=38, pady=(4, 2))
        estado_texto=self.ultima_respuesta_cpu or f"La computadora guarda un personaje secreto · {len(self.estado_usuario.candidatos)} candidatos"
        aviso=ctk.CTkFrame(panel,corner_radius=13,fg_color=COLOR["card"]); aviso.pack(fill="x",padx=38,pady=(8,10))
        self.texto(aviso,estado_texto,10,COLOR["yellow"] if self.ultima_respuesta_cpu else COLOR["muted"],True,wraplength=500,justify="left").pack(anchor="w",padx=14,pady=10)

        preguntas = ctk.CTkFrame(panel, corner_radius=16, fg_color=COLOR["surface2"])
        preguntas.pack(fill="x", padx=38, pady=(0, 14))
        disponibles = [item for item in ATRIBUTOS if item[0] not in self.motor_usuario.respuestas]
        for i, (atributo, pregunta) in enumerate(disponibles):
            b = ctk.CTkButton(
                preguntas, text=pregunta, height=35, corner_radius=11,
                fg_color=COLOR["card"], hover_color=COLOR["blue2"], anchor="w",
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                command=lambda a=atributo: self.preguntar_computadora(a),
            )
            b.grid(row=i//2, column=i%2, padx=7, pady=6, sticky="ew")
        preguntas.grid_columnconfigure((0, 1), weight=1)

        self.texto(panel, "Haz clic en un candidato para adivinar:", 10, COLOR["yellow"], True).pack(anchor="w", padx=40, pady=(0, 5))
        tablero = ctk.CTkScrollableFrame(panel, height=220, fg_color="transparent")
        tablero.pack(fill="both", expand=True, padx=31, pady=(0, 20))
        candidatos = [p for p in PERSONAJES if p["nombre"] in self.estado_usuario.candidatos]
        for col in range(6): tablero.grid_columnconfigure(col, weight=1)
        for i, p in enumerate(candidatos):
            img = avatar(p, 78); self.imagenes.append(img)
            candidato=ctk.CTkButton(
                tablero, text=p["nombre"], image=img, compound="top", width=130, height=128,
                corner_radius=15, fg_color=COLOR["card"], hover_color=COLOR["blue2"],
                border_width=1, border_color=COLOR["line"],
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                command=lambda x=p: self.adivinar(x),
            )
            candidato.grid(row=i//6, column=i%6, padx=6, pady=6, sticky="nsew")

    def preguntar_computadora(self, atributo):
        valor = bool(self.personaje_cpu[atributo])
        pregunta = dict(ATRIBUTOS)[atributo]
        self.estado_usuario = self.motor_usuario.responder(atributo, valor)
        respuesta = "Sí" if valor else "No"
        self.ultima_respuesta_cpu = f"La computadora respondió {respuesta}: {pregunta}"
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
