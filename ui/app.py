# ui/app.py
import tkinter as tk
from ui.editor import GraphEditor
from tkinter import ttk, filedialog, messagebox
import json
from afd_core import AFD  # motor del autómata


class AutomataApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AFD simulator - By Nata, Steven and Mileth")

        self._create_menu()
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        tool_frame = ttk.Frame(self.main_frame, padding=5)
        tool_frame.pack(fill="x")
        self._init_styles()
        self.mode_buttons = {}
        self.mode_buttons['select'] = ttk.Button(tool_frame, text="Modo Selección (S)", style="Mode.TButton", command=lambda: self._set_mode('select'))
        self.mode_buttons['select'].pack(side="left")
        self.mode_buttons['connect'] = ttk.Button(tool_frame, text="Modo Conexión (C)", style="Mode.TButton", command=lambda: self._set_mode('connect'))
        self.mode_buttons['connect'].pack(side="left")

        action_frame = ttk.Frame(tool_frame)
        action_frame.pack(side="left", padx=10)
        self.btn_edit = ttk.Button(action_frame, text="Editar (E)", command=self._edit_selected, state="disabled")
        self.btn_edit.pack(side="left")
        self.btn_delete = ttk.Button(action_frame, text="Eliminar (Supr)", command=self._delete_selected, state="disabled")
        self.btn_delete.pack(side="left", padx=5)

        self.canvas = GraphEditor(self.main_frame, width=800, height=500)
        self.canvas.pack(fill="both", expand=True)

        self._update_mode_buttons(active='select')
        self._bind_shortcuts()
        self.canvas.bind("<<SelectionChanged>>", lambda e: self._update_action_buttons())

        self._create_bottom_panel()

    # ---------- Menús ----------
    def _create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self._new_afd)
        file_menu.add_command(label="Cargar AFD", command=self._load_afd)
        file_menu.add_command(label="Guardar AFD", command=self._save_afd)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menu_bar.add_cascade(label="Archivo", menu=file_menu)

        sim_menu = tk.Menu(menu_bar, tearoff=0)
        sim_menu.add_command(label="Ejecutar cadena", command=self._simulate_string)
        sim_menu.add_command(label="Paso a paso", command=self._simulate_step)
        menu_bar.add_cascade(label="Simulación", menu=sim_menu)

        gen_menu = tk.Menu(menu_bar, tearoff=0)
        gen_menu.add_command(label="Mostrar primeras 10 cadenas", command=self._generate_strings)
        menu_bar.add_cascade(label="Generación", menu=gen_menu)

        self.root.config(menu=menu_bar)

    def _create_bottom_panel(self):
        bottom_frame = ttk.Frame(self.main_frame, padding=5)
        bottom_frame.pack(fill="x", side="bottom")
        ttk.Label(bottom_frame, text="Cadena:").pack(side="left")
        self.entry_string = ttk.Entry(bottom_frame, width=30)
        self.entry_string.pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Simular", command=self._simulate_string).pack(side="left", padx=5)
        self.result_label = ttk.Label(bottom_frame, text="Resultado: (pendiente)")
        self.result_label.pack(side="left", padx=10)

    def _bind_shortcuts(self):
        self.root.bind('<s>', lambda e: self._set_mode('select'))
        self.root.bind('<S>', lambda e: self._set_mode('select'))
        self.root.bind('<c>', lambda e: self._set_mode('connect'))
        self.root.bind('<C>', lambda e: self._set_mode('connect'))
        self.root.bind('<e>', lambda e: self._edit_selected())
        self.root.bind('<E>', lambda e: self._edit_selected())
        self.root.bind('<Delete>', lambda e: self._delete_selected())
        self.root.bind('<BackSpace>', lambda e: self._delete_selected())

    # ---------- Conexión con lógica ----------
    def _new_afd(self):
        self.canvas.clear()
        self.result_label.config(text="Resultado: (pendiente)")

    def _load_afd(self):
        path = filedialog.askopenfilename(title="Cargar AFD", filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            afd = AFD(**data)
            afd.validate()
            self.canvas.load_from_afd(afd)
            messagebox.showinfo("Cargar", f"AFD cargado desde {path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el AFD:\n{e}")

    def _save_afd(self):
        path = filedialog.asksaveasfilename(title="Guardar AFD", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            # CORRECCIÓN: Ahora usa los estados finales del canvas
            afd = self.canvas.to_afd(initial="q0")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(afd.__dict__, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Guardar", f"AFD guardado en {path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el AFD:\n{e}")

    def _simulate_string(self):
        cadena = self.entry_string.get()
        try:
            # CORRECCIÓN: Ahora usa los estados finales del canvas
            afd = self.canvas.to_afd(initial="q0")
            result = afd.simulate(cadena)
            estado = "ACEPTADA ✅" if result.accepted else "RECHAZADA ❌"
            self.result_label.config(text=f"Resultado: {estado}")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo en simulación:\n{e}")

    def _simulate_step(self):
        try:
            afd = self.canvas.to_afd(initial="q0")
            cadena = self.entry_string.get()
            result = afd.simulate(cadena)

            pasos = []
            for step in result.steps:
                # CORRECCIÓN: Usar los atributos correctos del objeto TraceStep
                pasos.append(f"{step.from_state} --'{step.symbol}'--> {step.to_state}")
            pasos_txt = "\n".join(pasos) if pasos else "(sin pasos)"

            finales_txt = ", ".join(afd.finals) if afd.finals else "(ninguno)"
            final_txt = "ACEPTADA ✅" if result.accepted else "RECHAZADA"

            messagebox.showinfo(
                "Simulación paso a paso",
                f"Finales: {finales_txt}\n\nPasos:\n{pasos_txt}\n\nResultado: {final_txt}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Fallo en simulación:\n{e}")

    def _generate_strings(self):
        # AÚN NO IMPLEMENTADO: Placeholder para la futura lógica de generación de cadenas
        messagebox.showinfo("Generar", "Aquí se mostrarán las primeras 10 cadenas aceptadas.")

    # ---------- Estilos ----------
    def _init_styles(self):
        style = ttk.Style()
        base_bg = '#2d2b55'
        active_bg = '#4a487a'
        style.configure('Mode.TButton', padding=6)
        style.map('Mode.TButton', background=[('active', base_bg)])
        style.configure('ActiveMode.TButton', padding=6, background=active_bg, foreground='black')
        style.map('ActiveMode.TButton', background=[('active', active_bg)])

    def _set_mode(self, mode: str):
        self.canvas.set_mode(mode)
        self._update_mode_buttons(active=mode)

    def _update_mode_buttons(self, active: str):
        for name, btn in self.mode_buttons.items():
            if name == active:
                btn.configure(style='ActiveMode.TButton')
            else:
                btn.configure(style='Mode.TButton')

    def _edit_selected(self):
        self.canvas.edit_selected()

    def _delete_selected(self):
        self.canvas.delete_selected()

    def _update_action_buttons(self):
        kind = self.canvas.get_selection_kind()
        state = "normal" if kind in ("node", "edge") else "disabled"
        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)


def start_app():
    root = tk.Tk()
    app = AutomataApp(root)
    root.mainloop()