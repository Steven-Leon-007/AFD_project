import tkinter as tk
from tkinter import ttk, messagebox
from afd_core.afd import AFD


class BatchValidatorWindow:
    def __init__(self, parent, afd: AFD):
        self.parent = parent
        self.afd = afd
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Validador de Múltiples Cadenas")
        self.window.geometry("800x650")
        self.window.configure(bg="#f0f2f5")  # Fondo moderno
        
        # Configurar estilos
        self.setup_styles()
        
        self.create_widgets()
        self.center_window()
        
    def setup_styles(self):
        """Configura los estilos personalizados con paleta moderna."""
        self.style = ttk.Style()
        
        # Configurar tema claro
        self.style.theme_use('clam')
        
        # Colores principales (mismos del simulador)
        self.colors = {
            'bg_primary': '#f0f2f5',      # Fondo principal (gris muy claro)
            'bg_secondary': '#ffffff',     # Fondo secundario (blanco)
            'bg_card': '#ffffff',          # Fondo de tarjetas
            'border': '#e1e5e9',          # Bordes suaves
            'text_primary': '#1c1e21',    # Texto principal
            'text_secondary': '#65676b',   # Texto secundario
            'accent_blue': '#1877f2',      # Azul principal
            'accent_blue_light': '#42a5f5',# Azul claro
            'accent_green': '#42b883',     # Verde éxito
            'accent_orange': '#ff9800',    # Naranja advertencia
            'accent_red': '#f44336',       # Rojo error
            'accent_purple': '#9c27b0',    # Púrpura
            'hover': '#e4e6ea'             # Color hover
        }
        
        # Estilo para frame principal
        self.style.configure("Batch.TFrame", 
                           background=self.colors['bg_primary'],
                           relief='flat')
        
        # Estilo para LabelFrame
        self.style.configure("BatchCard.TLabelframe", 
                           background=self.colors['bg_card'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'])
        self.style.configure("BatchCard.TLabelframe.Label", 
                           background=self.colors['bg_card'],
                           foreground=self.colors['accent_blue'],
                           font=("Segoe UI", 11, "bold"))
        
        # Estilo para botones modernos
        self.style.configure("BatchNav.TButton",
                           background=self.colors['accent_blue'],
                           foreground='white',
                           font=("Segoe UI", 9, "bold"),
                           borderwidth=0,
                           focuscolor='none',
                           relief='flat',
                           padding=(12, 6))
        
        self.style.map("BatchNav.TButton",
                      background=[('active', self.colors['accent_blue_light']),
                                ('pressed', '#1565c0')])
        
        # Estilo para Treeview
        self.style.configure("BatchResults.Treeview",
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['bg_secondary'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure("BatchResults.Treeview.Heading",
                           background=self.colors['accent_blue'],
                           foreground='white',
                           font=("Segoe UI", 10, "bold"))
        
    def create_widgets(self):
        # Frame principal con estilo moderno
        main_frame = ttk.Frame(self.window, style="Batch.TFrame")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título moderno
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        title_frame.pack(fill="x", pady=(0, 15))
        
        title_label = tk.Label(title_frame, 
                              text="Validador de Múltiples Cadenas", 
                              font=("Segoe UI", 18, "bold"), 
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['text_primary'])
        title_label.pack()
        
        # Información del AFD
        info_frame = ttk.LabelFrame(main_frame, text="Información del AFD", style="BatchCard.TLabelframe")
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_container = tk.Frame(info_frame, bg=self.colors['bg_card'])
        info_container.pack(fill="x", padx=15, pady=10)
        
        info_text = f"Estados: {{{', '.join(sorted(self.afd.states))}}} | "
        info_text += f"Alfabeto: {{{', '.join(sorted(self.afd.alphabet))}}} | "
        info_text += f"Inicial: {self.afd.initial} | "
        info_text += f"Finales: {{{', '.join(sorted(self.afd.finals))}}}"
        
        tk.Label(info_container, text=info_text, 
                bg=self.colors['bg_card'], 
                fg=self.colors['text_secondary'], 
                font=("Segoe UI", 9),
                wraplength=750, justify="left").pack(anchor="w")
        
        # Frame de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Ingreso de Cadenas", style="BatchCard.TLabelframe")
        input_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        input_container = tk.Frame(input_frame, bg=self.colors['bg_card'])
        input_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Instrucciones
        instructions = tk.Label(input_container, 
                               text="Ingresa las cadenas que quieres validar (una por línea):",
                               bg=self.colors['bg_card'], 
                               fg=self.colors['text_primary'], 
                               font=("Segoe UI", 10, "bold"))
        instructions.pack(anchor="w", pady=(0, 8))
        
        # Área de texto para cadenas con scroll
        text_frame = tk.Frame(input_container, bg=self.colors['bg_card'])
        text_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.text_input = tk.Text(text_frame, height=8, width=70,
                                 bg=self.colors['bg_secondary'], 
                                 fg=self.colors['text_primary'], 
                                 font=("Segoe UI", 11),
                                 insertbackground=self.colors['text_primary'],
                                 relief='solid', bd=1)
        scrollbar_input = ttk.Scrollbar(text_frame, orient="vertical", 
                                       command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=scrollbar_input.set)
        
        self.text_input.pack(side="left", fill="both", expand=True)
        scrollbar_input.pack(side="right", fill="y")
        
        # Botones de acción modernos
        button_frame = tk.Frame(input_container, bg=self.colors['bg_card'])
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Validar Todas", 
                  style="BatchNav.TButton",
                  command=self.validate_all).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="Limpiar", 
                  style="BatchNav.TButton",
                  command=self.clear_input).pack(side="left", padx=8)
        
        # Frame de resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", style="BatchCard.TLabelframe")
        result_frame.pack(fill="both", expand=True)
        
        result_container = tk.Frame(result_frame, bg=self.colors['bg_card'])
        result_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Tabla de resultados con estilo moderno
        columns = ["#", "Cadena", "Resultado", "Estado Final"]
        self.result_tree = ttk.Treeview(result_container, columns=columns, 
                                       show="headings", height=8,
                                       style="BatchResults.Treeview")
        
        # Configurar columnas
        column_widths = [50, 250, 120, 150]
        for i, col in enumerate(columns):
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=column_widths[i], anchor="center")
        
        # Scrollbar para resultados
        scrollbar_result = ttk.Scrollbar(result_container, orient="vertical", 
                                        command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar_result.set)
        
        self.result_tree.pack(side="left", fill="both", expand=True)
        scrollbar_result.pack(side="right", fill="y")
        
    def validate_all(self):
        """Valida todas las cadenas ingresadas."""
        # Obtener cadenas del texto
        text_content = self.text_input.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showwarning("Advertencia", "No se han ingresado cadenas para validar.")
            return
        
        # Dividir por líneas y limpiar
        strings = []
        for line in text_content.split('\n'):
            line = line.strip()
            if line:  # Solo agregar líneas no vacías
                strings.append(line)
        
        if not strings:
            messagebox.showwarning("Advertencia", "No se encontraron cadenas válidas.")
            return
        
        # Limpiar resultados anteriores
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Validar cada cadena
        for i, cadena in enumerate(strings, 1):
            try:
                # Manejar cadena vacía
                test_string = cadena if cadena != "ε" else ""
                result = self.afd.simulate(test_string)
                
                # Determinar resultado
                if result.accepted:
                    resultado_text = "ACEPTADA"
                    resultado_color = "accepted"
                else:
                    resultado_text = "RECHAZADA"
                    resultado_color = "rejected"
                
                # Insertar en tabla
                item = self.result_tree.insert("", "end", values=[
                    str(i),
                    cadena if cadena else "ε",
                    resultado_text,
                    result.final_state
                ], tags=(resultado_color,))
                
            except Exception as e:
                # Error en la simulación
                self.result_tree.insert("", "end", values=[
                    str(i),
                    cadena,
                    f"ERROR: {str(e)[:20]}...",
                    "-"
                ], tags=("error",))
        
        # Configurar colores para las filas con estilo moderno
        self.result_tree.tag_configure("accepted", 
                                      background=self.colors['accent_green'], 
                                      foreground="white")
        self.result_tree.tag_configure("rejected", 
                                      background=self.colors['accent_red'], 
                                      foreground="white")
        self.result_tree.tag_configure("error", 
                                      background=self.colors['accent_orange'], 
                                      foreground="white")
    
    def clear_input(self):
        """Limpia el área de entrada y resultados."""
        self.text_input.delete(1.0, tk.END)
        # Limpiar resultados también
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")