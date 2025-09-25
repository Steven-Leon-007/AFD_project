# ui/app.py
import tkinter as tk
from ui.editor import GraphEditor
from tkinter import ttk, filedialog, messagebox
from afd_core.afd import AFD
from afd_core.generator import generate_strings
from afd_core.persistence import save_to_json, load_from_json
from ui.simulator import show_simulator
from ui.batch_validator import BatchValidatorWindow  # NUEVO IMPORT
from tkinter import messagebox



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
        sim_menu.add_separator()
        # NUEVO: Validación por lotes
        sim_menu.add_command(label="Validar múltiples cadenas", command=self._batch_validate)
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

    def _new_afd(self):
        """Reinicia el editor con un canvas limpio."""
        self.canvas.clear_canvas()
        self.result_label.config(text="Resultado: (nuevo AFD)")

    def _load_afd(self):
        """Carga un AFD desde archivo JSON."""
        filepath = filedialog.askopenfilename(
            title="Cargar AFD", 
            filetypes=[("JSON Files", "*.json")]
        )
        if not filepath:
            return
            
        try:
            afd = load_from_json(filepath)
            self.canvas.from_afd(afd)
            self.result_label.config(text="Resultado: AFD cargado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el AFD:\n{str(e)}")

    def _save_afd(self):
        """Guarda el AFD actual en archivo JSON."""
        try:
            afd = self.canvas.to_afd()
            filepath = filedialog.asksaveasfilename(
                title="Guardar AFD", 
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")]
            )
            if not filepath:
                return
                
            save_to_json(afd, filepath)
            self.result_label.config(text="Resultado: AFD guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el AFD:\n{str(e)}")

    def _simulate_string(self):
        """Simula la ejecución de una cadena en el AFD actual."""
        cadena = self.entry_string.get()
        
        try:
            afd = self.canvas.to_afd()
            result = afd.simulate(cadena)
            
            if result.accepted:
                self.result_label.config(
                    text=f"Resultado: '{cadena}' ACEPTADA (estado final: {result.final_state})",
                    foreground="green"
                )
            else:
                self.result_label.config(
                    text=f"Resultado: '{cadena}' RECHAZADA (estado final: {result.final_state})",
                    foreground="red"
                )
        except Exception as e:
            self.result_label.config(
                text=f"Error: {str(e)}",
                foreground="red"
            )
            messagebox.showerror("Error de simulación", str(e))

    def _simulate_step(self):
        """Muestra la simulación paso a paso con el nuevo simulador."""
        cadena = self.entry_string.get()
        
        try:
            afd = self.canvas.to_afd()
            # Usar el nuevo simulador avanzado
            from ui.simulator import show_simulator
            show_simulator(self.root, afd, cadena, self.canvas)
            
        except Exception as e:
            messagebox.showerror("Error de simulación", str(e))

    def _generate_strings(self):
        """Muestra las primeras 10 cadenas aceptadas por el AFD."""
        try:
            afd = self.canvas.to_afd()
            from afd_core.generator import generate_strings
            strings = generate_strings(afd, limit=10)
            
            # Crear ventana de resultados
            gen_window = tk.Toplevel(self.root)
            gen_window.title("Primeras 10 cadenas aceptadas")
            gen_window.geometry("400x300")
            
            frame = ttk.Frame(gen_window)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            if strings:
                ttk.Label(frame, text="Cadenas aceptadas (por orden de longitud):").pack(anchor="w")
                
                listbox = tk.Listbox(frame)
                listbox.pack(fill="both", expand=True, pady=5)
                
                for i, string in enumerate(strings, 1):
                    display_string = string if string else "ε (cadena vacía)"
                    listbox.insert(tk.END, f"{i:2d}. {display_string}")
            else:
                ttk.Label(frame, text="No se encontraron cadenas aceptadas.").pack(anchor="w")
                
        except Exception as e:
            messagebox.showerror("Error de generación", str(e))

    def _batch_validate(self):
        """Abre ventana para validar múltiples cadenas."""
        try:
            afd = self.canvas.to_afd()
            BatchValidatorWindow(self.root, afd)  # USAR LA CLASE IMPORTADA
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el validador:\n{str(e)}")

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
