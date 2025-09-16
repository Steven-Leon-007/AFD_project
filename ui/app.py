# ui/app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class AutomataApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Simulador de AFD - By Nata, Steven and Mileth")

        # Menú principal
        self._create_menu()

        # Marco principal con layout
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Canvas central (donde irá el editor gráfico)
        self.canvas = tk.Canvas(self.main_frame, bg="white", width=600, height=400)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Dibujar algo de prueba
        self.canvas.create_oval(100, 100, 150, 150, outline="black", width=2)
        self.canvas.create_text(125, 125, text="q0")

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


def start_app():
    root = tk.Tk()
    app = AutomataApp(root)
    root.mainloop()
