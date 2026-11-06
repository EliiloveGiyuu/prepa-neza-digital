#!/usr/bin/env python3
"""
Cuestionario con pantalla de inicio (tkinter, no necesita instalar nada).

Uso:  python cuestionario.py

Carga tus preguntas desde un archivo .json o .csv (ver preguntas.json de ejemplo).
Si en la carpeta hay un "preguntas.json", se carga solo al abrir.
"""

import csv
import json
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ----------------------------- Colores y fuentes -----------------------------
BG = "#f4f6fb"
CARD = "#ffffff"
PRIMARY = "#4f46e5"
PRIMARY_DARK = "#3730a3"
TEXT = "#1f2937"
MUTED = "#6b7280"
BORDER = "#d1d5db"
OK_BG, OK_FG = "#dcfce7", "#166534"
BAD_BG, BAD_FG = "#fee2e2", "#991b1b"

F_TITLE = ("Segoe UI", 28, "bold")
F_H2 = ("Segoe UI", 18, "bold")
F_Q = ("Segoe UI", 16, "bold")
F_OPT = ("Segoe UI", 13)
F_TXT = ("Segoe UI", 12)
F_SMALL = ("Segoe UI", 10)

ARCHIVO_POR_DEFECTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preguntas.json")


# ------------------------------ Carga de archivos ----------------------------
def _normalizar(p, n):
    """Valida una pregunta y la devuelve en formato interno."""
    texto = str(p.get("pregunta", "")).strip()
    opciones = [str(o).strip() for o in p.get("opciones", []) if str(o).strip()]
    if not texto:
        raise ValueError(f"Pregunta #{n}: falta el texto de la pregunta.")
    if len(opciones) < 2:
        raise ValueError(f"Pregunta #{n}: necesita al menos 2 opciones.")

    c = p.get("correcta")
    if isinstance(c, str) and c.strip().isdigit():
        c = int(c.strip())
    if isinstance(c, int):                      # número 1-based
        if not 1 <= c <= len(opciones):
            raise ValueError(f"Pregunta #{n}: 'correcta' debe estar entre 1 y {len(opciones)}.")
        idx = c - 1
    elif isinstance(c, str) and c.strip() in opciones:   # texto exacto de la opción
        idx = opciones.index(c.strip())
    else:
        raise ValueError(f"Pregunta #{n}: 'correcta' no es válida (usa el número de la opción).")

    return {
        "pregunta": texto,
        "opciones": opciones,
        "correcta": idx,
        "explicacion": str(p.get("explicacion", "") or "").strip(),
        "imagen": str(p.get("imagen", "") or "").strip(),
    }


def cargar_preguntas(ruta):
    """Devuelve (titulo, lista_de_preguntas) desde un .json o .csv."""
    ext = os.path.splitext(ruta)[1].lower()
    crudas = []
    titulo = os.path.splitext(os.path.basename(ruta))[0]

    if ext == ".json":
        with open(ruta, encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, dict):
            titulo = data.get("titulo", titulo)
            crudas = data.get("preguntas", [])
        else:
            crudas = data
    elif ext == ".csv":
        with open(ruta, encoding="utf-8-sig", newline="") as f:
            muestra = f.read(2048)
            f.seek(0)
            try:
                dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t")
            except csv.Error:
                dialecto = csv.excel
            for fila in csv.DictReader(f, dialect=dialecto):
                fila = {(k or "").strip().lower(): (v or "").strip() for k, v in fila.items()}
                ops = [fila.get(f"opcion{i}", "") for i in range(1, 9)]
                crudas.append({
                    "pregunta": fila.get("pregunta", ""),
                    "opciones": [o for o in ops if o],
                    "correcta": fila.get("correcta", ""),
                    "explicacion": fila.get("explicacion", ""),
                    "imagen": fila.get("imagen", ""),
                })
    else:
        raise ValueError("Formato no soportado. Usa un archivo .json o .csv")

    preguntas = [_normalizar(p, i + 1) for i, p in enumerate(crudas)]
    if not preguntas:
        raise ValueError("El archivo no contiene preguntas.")
    return titulo, preguntas


# ------------------- Preguntas integradas (ya vienen en este archivo) -------------------
TITULO_INTEGRADO = "Historia de la UAEMéx"
PREGUNTAS_INTEGRADAS = [
    {"pregunta": "¿Qué representa el árbol de la mora dentro de la UAEMéx?",
     "opciones": ["Un símbolo de identidad universitaria", "Un edificio escolar", "Una materia académica"],
     "correcta": 1},
    {"pregunta": "¿Cómo se llama el museo universitario ubicado en el Edificio de Rectoría?",
     "opciones": ["Museo de Antropología", "Museo Universitario Leopoldo Flores",
                  "Museo Universitario José María Morelos y Pavón"],
     "correcta": 3},
    {"pregunta": "¿Qué personaje da nombre a la Preparatoria 2 de la UAEMéx?",
     "opciones": ["Miguel Hidalgo", "Nezahualcóyotl", "Benito Juárez"],
     "correcta": 2},
    {"pregunta": "¿Qué tipo de institución es la UAEMéx?",
     "opciones": ["Una universidad pública", "Una empresa privada", "Una escuela militar"],
     "correcta": 1},
    {"pregunta": "¿Qué colores se relacionan con la identidad institucional de la UAEMéx?",
     "opciones": ["Verde y oro", "Rojo y negro", "Morado y naranja"],
     "correcta": 1},
    {"pregunta": "¿Qué significa que la UAEMéx sea autónoma?",
     "opciones": ["Que no tiene estudiantes",
                  "Que cuenta con capacidad de autogobierno conforme a la ley",
                  "Que no necesita profesores"],
     "correcta": 2},
    {"pregunta": "¿Cuál es una de las principales funciones de la UAEMéx?",
     "opciones": ["Fabricar automóviles", "Administrar aeropuertos",
                  "Impartir educación y promover la investigación"],
     "correcta": 3},
    {"pregunta": "¿Por qué es importante conocer la historia de la UAEMéx?",
     "opciones": ["Para conocer sus orígenes y fortalecer la identidad universitaria",
                  "Para aprender a conducir",
                  "Para conocer la historia de otros países exclusivamente"],
     "correcta": 1},
]


# ---------------------------------- App --------------------------------------
class CuestionarioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PEC de Cultura Digital")
        self.geometry("860x680")
        self.minsize(720, 600)
        self.configure(bg=BG)

        self.titulo = "Sin archivo cargado"
        self.banco = []          # todas las preguntas cargadas
        self.ruta = ""
        self.base_dir = ""

        self.ronda = []          # preguntas de la ronda actual
        self.i = 0
        self.puntos = 0
        self.fallos = []
        self.respondida = False
        self.img_ref = None

        self.var_cantidad = tk.IntVar(value=10)
        self.var_mezclar = tk.BooleanVar(value=False)

        self.contenedor = tk.Frame(self, bg=BG)
        self.contenedor.pack(fill="both", expand=True)

        # Carga las preguntas integradas (no hace falta ningún otro archivo)
        self.titulo = TITULO_INTEGRADO
        self.banco = [_normalizar(p, n + 1) for n, p in enumerate(PREGUNTAS_INTEGRADAS)]
        self.var_cantidad.set(len(self.banco))

        self.pantalla_inicio()

    # ------------------------------ utilidades -------------------------------
    def _limpiar(self):
        for w in self.contenedor.winfo_children():
            w.destroy()
        self.unbind("<Return>")
        for k in "1234567890":
            self.unbind(k)

    def _boton(self, padre, texto, comando, primario=True, **kw):
        bg = PRIMARY if primario else CARD
        fg = "white" if primario else TEXT
        b = tk.Label(padre, text=texto, bg=bg, fg=fg, font=("Segoe UI", 12, "bold"),
                     padx=22, pady=10, cursor="hand2",
                     highlightthickness=0 if primario else 1, highlightbackground=BORDER, **kw)
        hover = PRIMARY_DARK if primario else "#eef2ff"
        b.bind("<Enter>", lambda e: b.configure(bg=hover))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        b.bind("<Button-1>", lambda e: comando())
        return b

    def _cargar(self, ruta):
        titulo, preguntas = cargar_preguntas(ruta)
        self.titulo, self.banco, self.ruta = titulo, preguntas, ruta
        self.base_dir = os.path.dirname(os.path.abspath(ruta))
        self.var_cantidad.set(min(max(self.var_cantidad.get(), 1), len(preguntas)))

    # ----------------------------- Pantalla inicio ---------------------------
    def pantalla_inicio(self):
        self._limpiar()
        centro = tk.Frame(self.contenedor, bg=BG)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(centro, text="📝", bg=BG, font=("Segoe UI Emoji", 54)).pack()
        tk.Label(centro, text="PEC de Cultura Digital", bg=BG, fg=PRIMARY, font=F_TITLE,
                 wraplength=640).pack()
        tk.Label(centro, text="Pon a prueba lo que sabes", bg=BG, fg=MUTED, font=F_TXT).pack(pady=(0, 18))

        tarjeta = tk.Frame(centro, bg=CARD, padx=28, pady=22,
                           highlightthickness=1, highlightbackground=BORDER)
        tarjeta.pack(fill="x")

        if self.banco:
            tk.Label(tarjeta, text=self.titulo, bg=CARD, fg=TEXT, font=F_H2,
                     wraplength=420).pack()
            tk.Label(tarjeta, text=f"{len(self.banco)} preguntas disponibles",
                     bg=CARD, fg=MUTED, font=F_TXT).pack(pady=(2, 14))

            fila = tk.Frame(tarjeta, bg=CARD)
            fila.pack(pady=4)
            tk.Label(fila, text="Número de preguntas:", bg=CARD, fg=TEXT, font=F_TXT).pack(side="left", padx=(0, 8))
            tk.Spinbox(fila, from_=1, to=len(self.banco), width=5, textvariable=self.var_cantidad,
                       font=F_TXT, justify="center").pack(side="left")

            tk.Checkbutton(tarjeta, text="Mezclar el orden de preguntas y respuestas",
                           variable=self.var_mezclar, bg=CARD, activebackground=CARD,
                           fg=TEXT, font=F_TXT, selectcolor=CARD).pack(pady=(10, 0))
        else:
            tk.Label(tarjeta, text="Aún no has cargado preguntas", bg=CARD, fg=TEXT, font=F_H2).pack()
            tk.Label(tarjeta, text="Carga un archivo .json o .csv para empezar",
                     bg=CARD, fg=MUTED, font=F_TXT).pack(pady=(4, 0))

        botones = tk.Frame(centro, bg=BG)
        botones.pack(pady=22)
        if self.banco:
            self._boton(botones, "▶  Comenzar", self.comenzar).pack(side="left", padx=6)
        self._boton(botones, "📂  Cargar archivo", self.elegir_archivo, primario=not self.banco).pack(side="left", padx=6)
        self._boton(botones, "Salir", self.destroy, primario=False).pack(side="left", padx=6)

        if self.ruta:
            tk.Label(centro, text=f"Archivo: {os.path.basename(self.ruta)}",
                     bg=BG, fg=MUTED, font=F_SMALL).pack()

    def elegir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Elige tu archivo de preguntas",
            filetypes=[("Preguntas (JSON o CSV)", "*.json *.csv"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            self._cargar(ruta)
        except Exception as e:
            messagebox.showerror("No se pudo cargar el archivo", str(e))
            return
        self.pantalla_inicio()

    # --------------------------------- Quiz ----------------------------------
    def comenzar(self):
        try:
            n = int(self.var_cantidad.get())
        except (tk.TclError, ValueError):
            n = len(self.banco)
        n = max(1, min(n, len(self.banco)))
        preguntas = list(self.banco)
        if self.var_mezclar.get():
            random.shuffle(preguntas)
        self.iniciar_ronda(preguntas[:n])

    def iniciar_ronda(self, preguntas):
        self.ronda = preguntas
        self.i = 0
        self.puntos = 0
        self.fallos = []
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        self._limpiar()
        self.respondida = False
        q = self.ronda[self.i]

        # opciones (posiblemente mezcladas)
        opts = list(enumerate(q["opciones"]))
        if self.var_mezclar.get():
            random.shuffle(opts)
        self.opts = opts

        # barra superior
        top = tk.Frame(self.contenedor, bg=BG, padx=30, pady=18)
        top.pack(fill="x")
        tk.Label(top, text=self.titulo, bg=BG, fg=MUTED, font=F_SMALL).pack(side="left")
        self.lbl_puntos = tk.Label(top, text=f"Aciertos: {self.puntos}", bg=BG, fg=PRIMARY,
                                   font=("Segoe UI", 11, "bold"))
        self.lbl_puntos.pack(side="right")

        prog = tk.Frame(self.contenedor, bg=BG, padx=30)
        prog.pack(fill="x")
        tk.Label(prog, text=f"Pregunta {self.i + 1} de {len(self.ronda)}", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Progressbar(prog, maximum=len(self.ronda), value=self.i).pack(fill="x", pady=(4, 14))

        # tarjeta de la pregunta
        cuerpo = tk.Frame(self.contenedor, bg=CARD, padx=26, pady=20,
                          highlightthickness=1, highlightbackground=BORDER)
        cuerpo.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        tk.Label(cuerpo, text=q["pregunta"], bg=CARD, fg=TEXT, font=F_Q, justify="left",
                 anchor="w", wraplength=700).pack(fill="x", pady=(0, 12))

        self._mostrar_imagen(cuerpo, q["imagen"])

        self.cajas = []
        for pos, (orig, texto) in enumerate(opts):
            lbl = tk.Label(cuerpo, text=f"{pos + 1}.  {texto}", bg="#f9fafb", fg=TEXT, font=F_OPT,
                           anchor="w", justify="left", wraplength=680, padx=14, pady=10,
                           cursor="hand2", highlightthickness=1, highlightbackground=BORDER)
            lbl.pack(fill="x", pady=4)
            lbl.bind("<Button-1>", lambda e, p=pos: self.responder(p))
            self.cajas.append(lbl)
            if pos < 9:
                self.bind(str(pos + 1), lambda e, p=pos: self.responder(p))

        self.lbl_feedback = tk.Label(cuerpo, text="", bg=CARD, font=F_TXT, justify="left",
                                     anchor="w", wraplength=700)
        self.lbl_feedback.pack(fill="x", pady=(10, 0))

        pie = tk.Frame(self.contenedor, bg=BG, padx=30, pady=10)
        pie.pack(fill="x")
        self.btn_sig = self._boton(pie, "Siguiente  ➜", self.siguiente)
        # el botón aparece al responder

    def _mostrar_imagen(self, padre, nombre):
        self.img_ref = None
        if not nombre:
            return
        ruta = nombre if os.path.isabs(nombre) else os.path.join(self.base_dir, nombre)
        try:
            img = tk.PhotoImage(file=ruta)          # PNG / GIF
            while img.width() > 520 or img.height() > 220:
                img = img.subsample(2, 2)
            self.img_ref = img
            tk.Label(padre, image=img, bg=CARD).pack(pady=(0, 10))
        except Exception:
            tk.Label(padre, text=f"(no se pudo cargar la imagen: {nombre})",
                     bg=CARD, fg=MUTED, font=F_SMALL).pack()

    def responder(self, pos):
        if self.respondida:
            return
        self.respondida = True
        q = self.ronda[self.i]
        elegida_orig = self.opts[pos][0]
        acierto = elegida_orig == q["correcta"]

        for p, (orig, _) in enumerate(self.opts):
            if orig == q["correcta"]:
                self.cajas[p].configure(bg=OK_BG, fg=OK_FG, highlightbackground=OK_FG)
            elif p == pos:
                self.cajas[p].configure(bg=BAD_BG, fg=BAD_FG, highlightbackground=BAD_FG)
            self.cajas[p].configure(cursor="arrow")

        if acierto:
            self.puntos += 1
            msg, color = "✔ ¡Correcto!", OK_FG
        else:
            msg, color = "✘ Incorrecto", BAD_FG
            self.fallos.append((q, q["opciones"][elegida_orig]))
        if q["explicacion"]:
            msg += f"\n{q['explicacion']}"
        self.lbl_feedback.configure(text=msg, fg=color)
        self.lbl_puntos.configure(text=f"Aciertos: {self.puntos}")

        ultima = self.i == len(self.ronda) - 1
        self.btn_sig.configure(text="Ver resultados  ➜" if ultima else "Siguiente  ➜")
        self.btn_sig.pack(anchor="e")
        self.bind("<Return>", lambda e: self.siguiente())

    def siguiente(self):
        if not self.respondida:
            return
        self.i += 1
        if self.i >= len(self.ronda):
            self.pantalla_resultados()
        else:
            self.mostrar_pregunta()

    # ------------------------------- Resultados ------------------------------
    def pantalla_resultados(self):
        self._limpiar()
        total = len(self.ronda)
        pct = round(100 * self.puntos / total)
        if pct == 100:
            emoji, frase = "🏆", "¡Perfecto!"
        elif pct >= 80:
            emoji, frase = "🎉", "¡Excelente trabajo!"
        elif pct >= 60:
            emoji, frase = "👍", "¡Bien hecho!"
        else:
            emoji, frase = "💪", "Sigue practicando"

        centro = tk.Frame(self.contenedor, bg=BG, padx=30, pady=20)
        centro.pack(fill="both", expand=True)

        tk.Label(centro, text=emoji, bg=BG, font=("Segoe UI Emoji", 46)).pack()
        tk.Label(centro, text=frase, bg=BG, fg=PRIMARY, font=F_TITLE).pack()
        tk.Label(centro, text=f"{self.puntos} de {total} correctas  ({pct}%)",
                 bg=BG, fg=TEXT, font=F_H2).pack(pady=(4, 12))

        if self.fallos:
            tk.Label(centro, text="Preguntas que fallaste:", bg=BG, fg=TEXT,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w")
            marco = tk.Frame(centro, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
            marco.pack(fill="both", expand=True, pady=(4, 8))
            txt = tk.Text(marco, wrap="word", font=F_TXT, bg=CARD, relief="flat", padx=12, pady=8)
            sb = ttk.Scrollbar(marco, command=txt.yview)
            txt.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            txt.pack(fill="both", expand=True)
            txt.tag_configure("q", font=("Segoe UI", 12, "bold"))
            txt.tag_configure("mal", foreground=BAD_FG)
            txt.tag_configure("bien", foreground=OK_FG)
            for n, (q, elegida) in enumerate(self.fallos, 1):
                txt.insert("end", f"{n}. {q['pregunta']}\n", "q")
                txt.insert("end", f"   Tu respuesta: {elegida}\n", "mal")
                txt.insert("end", f"   Correcta: {q['opciones'][q['correcta']]}\n", "bien")
                if q["explicacion"]:
                    txt.insert("end", f"   {q['explicacion']}\n")
                txt.insert("end", "\n")
            txt.configure(state="disabled")
        else:
            tk.Label(centro, text="¡No fallaste ninguna pregunta!", bg=BG, fg=OK_FG,
                     font=F_H2).pack(pady=20)

        botones = tk.Frame(centro, bg=BG)
        botones.pack(pady=6)
        self._boton(botones, "🔁  Repetir", self.comenzar).pack(side="left", padx=5)
        if self.fallos:
            self._boton(botones, "🎯  Repasar falladas",
                        lambda: self.iniciar_ronda([q for q, _ in self.fallos]),
                        primario=False).pack(side="left", padx=5)
        self._boton(botones, "🏠  Inicio", self.pantalla_inicio, primario=False).pack(side="left", padx=5)


if __name__ == "__main__":
    CuestionarioApp().mainloop()
