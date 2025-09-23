# ui/app.py
import tkinter as tk
from ui.editor import GraphEditor
from tkinter import ttk, filedialog, messagebox


class AutomataApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AFD simulator - By Nata, Steven and Mileth")

        # Menú principal
        self._create_menu()

        # Marco principal con layout
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Panel de herramientas (debajo del canvas o arriba)
        tool_frame = ttk.Frame(self.main_frame, padding=5)
        tool_frame.pack(fill="x")
        # Inicializar estilos para botones de modo
        self._init_styles()
        self.mode_buttons = {}
        self.mode_buttons['select'] = ttk.Button(tool_frame, text="Modo Selección (S)", style="Mode.TButton", command=lambda: self._set_mode('select'))
        self.mode_buttons['select'].pack(side="left")
        self.mode_buttons['connect'] = ttk.Button(tool_frame, text="Modo Conexión (C)", style="Mode.TButton", command=lambda: self._set_mode('connect'))
        self.mode_buttons['connect'].pack(side="left")

        # Botones de acción (editar / eliminar)
        action_frame = ttk.Frame(tool_frame)
        action_frame.pack(side="left", padx=10)
        self.btn_edit = ttk.Button(action_frame, text="Editar (E)", command=self._edit_selected, state="disabled")
        self.btn_edit.pack(side="left")
        self.btn_delete = ttk.Button(action_frame, text="Eliminar (Supr)", command=self._delete_selected, state="disabled")
        self.btn_delete.pack(side="left", padx=5)

        # Canvas central (donde irá el editor gráfico)
        self.canvas = GraphEditor(self.main_frame, width=800, height=500)
        self.canvas.pack(fill="both", expand=True)

        # Estado inicial de resaltado
        self._update_mode_buttons(active='select')
        
        self._bind_shortcuts()
        self.canvas.bind("<<SelectionChanged>>", lambda e: self._update_action_buttons())

        # Panel inferior (entrada + resultados)
        self._create_bottom_panel()

    def _create_menu(self):
        menu_bar = tk.Menu(self.root)

        # Menú Archivo
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self._new_afd)
        file_menu.add_command(label="Cargar AFD", command=self._load_afd)
        file_menu.add_command(label="Guardar AFD", command=self._save_afd)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menu_bar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Simulación
        sim_menu = tk.Menu(menu_bar, tearoff=0)
        sim_menu.add_command(label="Ejecutar cadena", command=self._simulate_string)
        sim_menu.add_command(label="Paso a paso", command=self._simulate_step)
        menu_bar.add_cascade(label="Simulación", menu=sim_menu)

        # Menú Generación
        gen_menu = tk.Menu(menu_bar, tearoff=0)
        gen_menu.add_command(label="Mostrar primeras 10 cadenas", command=self._generate_strings)
        menu_bar.add_cascade(label="Generación", menu=gen_menu)

        self.root.config(menu=menu_bar)

    def _create_bottom_panel(self):
        bottom_frame = ttk.Frame(self.main_frame, padding=5)
        bottom_frame.pack(fill="x", side="bottom")

        # Entrada de cadena
        ttk.Label(bottom_frame, text="Cadena:").pack(side="left")
        self.entry_string = ttk.Entry(bottom_frame, width=30)
        self.entry_string.pack(side="left", padx=5)

        # Botón simular
        ttk.Button(bottom_frame, text="Simular", command=self._simulate_string).pack(side="left", padx=5)

        # Área de resultados
        self.result_label = ttk.Label(bottom_frame, text="Resultado: (pendiente)")
        self.result_label.pack(side="left", padx=10)
        
        
    def _bind_shortcuts(self):
        # s / S -> modo selección
        self.root.bind('<s>', lambda e: self._set_mode('select'))
        self.root.bind('<S>', lambda e: self._set_mode('select'))
        # c / C -> modo conexión
        self.root.bind('<c>', lambda e: self._set_mode('connect'))
        self.root.bind('<C>', lambda e: self._set_mode('connect'))
        # e / E -> editar
        self.root.bind('<e>', lambda e: self._edit_selected())
        self.root.bind('<E>', lambda e: self._edit_selected())
        # Supr / BackSpace -> eliminar
        self.root.bind('<Delete>', lambda e: self._delete_selected())
        self.root.bind('<BackSpace>', lambda e: self._delete_selected())

    # Métodos vacíos (se conectarán después con la lógica)
    def _new_afd(self):
        messagebox.showinfo("Nuevo", "Aquí se reiniciará el editor de AFD.")

    def _load_afd(self):
        filedialog.askopenfilename(title="Cargar AFD", filetypes=[("JSON Files", "*.json")])
        messagebox.showinfo("Cargar", "Aquí se cargará un AFD desde archivo.")

    def _save_afd(self):
        filedialog.asksaveasfilename(title="Guardar AFD", defaultextension=".json",
                                     filetypes=[("JSON Files", "*.json")])
        messagebox.showinfo("Guardar", "Aquí se guardará el AFD en archivo.")

    def _simulate_string(self):
        cadena = self.entry_string.get()
        self.result_label.config(text=f"Resultado: simulando '{cadena}' (sin lógica)")

    def _simulate_step(self):
        messagebox.showinfo("Paso a paso", "Aquí se mostrarán los pasos de simulación.")

    def _generate_strings(self):
        messagebox.showinfo("Generar", "Aquí se mostrarán las primeras 10 cadenas aceptadas.")

    # -------------------------
    # Estilos y modos visuales
    # -------------------------
    def _init_styles(self):
        style = ttk.Style()
        # Algunos temas no soportan ciertos campos; se usan valores seguros.
        base_bg = '#2d2b55'
        active_bg = '#4a487a'
        style.configure('Mode.TButton', padding=6)
        style.map('Mode.TButton', background=[('active', base_bg)])
        # Estilo para botón activo
        style.configure('ActiveMode.TButton', padding=6, background=active_bg, foreground='black')
        style.map('ActiveMode.TButton', background=[('active', active_bg)])

    def _set_mode(self, mode: str):
        # Delegar al canvas
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
