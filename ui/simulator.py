import tkinter as tk
from tkinter import ttk
import time
import math
from afd_core.afd import AFD, TraceResult

class SimulatorWindow:
    def __init__(self, parent, afd: AFD, cadena: str, canvas=None):
        self.parent = parent
        self.afd = afd
        self.cadena = cadena
        self.canvas = canvas  # Referencia al canvas original para sincronizar
        self.current_step = 0
        self.result = None
        self.original_colors = {}  # Para restaurar colores originales
        self.auto_playing = False  # Control para auto-play
        
        # Simular la cadena
        self.result = afd.simulate(cadena)
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title(f"Simulador AFD - Cadena: '{cadena if cadena else 'ε'}'")
        self.window.geometry("1200x800")
        self.window.configure(bg="#f0f2f5")  # Fondo claro moderno
        
        # Configurar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Inicializar visualización
        self.update_display()
        
        # Centrar ventana
        self.center_window()
        
    def setup_styles(self):
        """Configura los estilos personalizados con paleta moderna."""
        self.style = ttk.Style()
        
        # Configurar tema claro
        self.style.theme_use('clam')
        
        # Colores principales
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
        self.style.configure("Simulator.TFrame", 
                           background=self.colors['bg_primary'],
                           relief='flat')
        
        # Estilo para LabelFrame
        self.style.configure("Card.TLabelframe", 
                           background=self.colors['bg_card'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'])
        self.style.configure("Card.TLabelframe.Label", 
                           background=self.colors['bg_card'],
                           foreground=self.colors['accent_blue'],
                           font=("Segoe UI", 11, "bold"))
        
        # Estilo para labels de título
        self.style.configure("Title.TLabel", 
                           background=self.colors['bg_card'], 
                           foreground=self.colors['text_primary'],
                           font=("Segoe UI", 10, "bold"))
        
        # Estilo para labels de información
        self.style.configure("Info.TLabel", 
                           background=self.colors['bg_card'], 
                           foreground=self.colors['text_secondary'],
                           font=("Segoe UI", 9))
        
        # Estilo para botones modernos
        self.style.configure("Nav.TButton",
                           background=self.colors['accent_blue'],
                           foreground='white',
                           font=("Segoe UI", 9, "bold"),
                           borderwidth=0,
                           focuscolor='none',
                           relief='flat',
                           padding=(12, 6))
        
        self.style.map("Nav.TButton",
                      background=[('active', self.colors['accent_blue_light']),
                                ('pressed', '#1565c0')])
        
        # Estilo para Treeview
        self.style.configure("Modern.Treeview",
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['bg_secondary'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure("Modern.Treeview.Heading",
                           background=self.colors['accent_blue'],
                           foreground='white',
                           font=("Segoe UI", 9, "bold"))
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Frame principal con dos columnas
        main_frame = ttk.Frame(self.window, style="Simulator.TFrame")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Columna izquierda: Grafo visual
        left_frame = ttk.Frame(main_frame, style="Simulator.TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        # Columna derecha: Información y controles
        right_frame = ttk.Frame(main_frame, style="Simulator.TFrame")
        right_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))
        
        # Crear canvas visual del AFD
        self.create_visual_afd(left_frame)
        
        # Panel de información del AFD
        self.create_info_panel(right_frame)
        
        # Panel de simulación paso a paso
        self.create_simulation_panel(right_frame)
        
        # Panel de controles
        self.create_control_panel(right_frame)
        
    def create_visual_afd(self, parent):
        """Crea el canvas visual del AFD para la simulación."""
        visual_frame = ttk.LabelFrame(parent, text="Visualización del AFD", style="Card.TLabelframe")
        visual_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Canvas para el grafo con gradiente
        canvas_container = tk.Frame(visual_frame, bg=self.colors['bg_card'])
        canvas_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.visual_canvas = tk.Canvas(canvas_container, 
                                     bg="#fafbfc",  # Fondo muy claro
                                     width=500, height=400,
                                     highlightthickness=1,
                                     highlightbackground=self.colors['border'])
        self.visual_canvas.pack(fill="both", expand=True)
        
        # Dibujar el AFD
        self.draw_afd()
        
    def draw_afd(self):
        """Dibuja el AFD en el canvas visual con colores modernos."""
        self.visual_nodes = {}
        self.visual_edges = []
        
        # Posicionar nodos en círculo
        num_states = len(self.afd.states)
        center_x, center_y = 250, 200
        radius = max(120, num_states * 25)
        
        # Paleta de colores moderna para nodos
        node_colors = [
            "#1877f2",  # Azul principal
            "#42b883",  # Verde
            "#ff9800",  # Naranja
            "#e91e63",  # Rosa
            "#9c27b0",  # Púrpura
            "#00bcd4",  # Cian
            "#4caf50",  # Verde claro
            "#ff5722",  # Rojo naranja
            "#795548",  # Marrón
            "#607d8b"   # Azul gris
        ]
        
        for i, state in enumerate(sorted(self.afd.states)):
            angle = 2 * math.pi * i / num_states
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Color del nodo
            color = node_colors[i % len(node_colors)]
            
            # Dibujar sombra del círculo (efecto depth)
            shadow_offset = 2
            self.visual_canvas.create_oval(x-25+shadow_offset, y-25+shadow_offset, 
                                         x+25+shadow_offset, y+25+shadow_offset, 
                                         fill="#e0e0e0", outline="", width=0)
            
            # Dibujar círculo del estado
            r = 25
            circle = self.visual_canvas.create_oval(x-r, y-r, x+r, y+r, 
                                                   fill=color, outline="white", width=3)
            
            # Texto del estado
            text = self.visual_canvas.create_text(x, y, text=state, 
                                                 fill="white", font=("Segoe UI", 11, "bold"))
            
            # Círculo exterior para estados finales
            outer_circle = None
            if state in self.afd.finals:
                outer_r = r + 6
                outer_circle = self.visual_canvas.create_oval(x-outer_r, y-outer_r, x+outer_r, y+outer_r,
                                                            fill="", outline=self.colors['accent_green'], 
                                                            width=3)
            
            # Flecha inicial moderna
            initial_arrow = None
            if state == self.afd.initial:
                start_x = x - r - 35
                end_x = x - r - 3
                initial_arrow = self.visual_canvas.create_line(start_x, y, end_x, y,
                                                             arrow=tk.LAST, width=4, 
                                                             fill=self.colors['accent_green'], 
                                                             arrowshape=(12, 15, 5))
            
            self.visual_nodes[state] = {
                'x': x, 'y': y, 'color': color,
                'circle': circle, 'text': text,
                'outer_circle': outer_circle,
                'initial_arrow': initial_arrow
            }
        
        # Dibujar aristas
        self.draw_edges()
    
    def draw_edges(self):
        """Dibuja las aristas del AFD con estilo moderno."""
        # Agrupar transiciones por (from, to)
        edge_groups = {}
        for from_state in self.afd.transitions:
            for symbol, to_state in self.afd.transitions[from_state].items():
                key = (from_state, to_state)
                if key not in edge_groups:
                    edge_groups[key] = []
                edge_groups[key].append(symbol)
        
        # Dibujar aristas agrupadas
        for (from_state, to_state), symbols in edge_groups.items():
            from_node = self.visual_nodes[from_state]
            to_node = self.visual_nodes[to_state]
            
            x1, y1 = from_node['x'], from_node['y']
            x2, y2 = to_node['x'], to_node['y']
            
            is_loop = from_state == to_state
            
            if is_loop:
                # Auto-bucle con estilo moderno
                r = 25
                loop_h = r * 2.2
                pts = self._compute_loop_points(x1, y1, r, loop_h)
                line = self.visual_canvas.create_line(*pts, smooth=True, arrow=tk.LAST, 
                                                     width=3, fill=self.colors['text_secondary'],
                                                     arrowshape=(8, 10, 3))
                mx, my = x1, y1 - r - loop_h - 20
            else:
                # Línea normal con estilo moderno
                sx, sy, ex, ey = self._compute_edge_points(x1, y1, x2, y2, 25)
                line = self.visual_canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, 
                                                     width=3, fill=self.colors['text_secondary'],
                                                     arrowshape=(8, 10, 3))
                mx, my = (sx + ex) / 2, (sy + ey) / 2 - 18
            
            # Etiqueta con símbolos en una caja moderna
            label_text = ",".join(sorted(symbols))
            
            # Fondo de la etiqueta
            bbox = self.visual_canvas.create_text(mx, my, text=label_text, font=("Segoe UI", 9, "bold"))
            coords = self.visual_canvas.bbox(bbox)
            if coords:
                bg_rect = self.visual_canvas.create_rectangle(
                    coords[0]-4, coords[1]-2, coords[2]+4, coords[3]+2,
                    fill="white", outline=self.colors['border'], width=1)
                self.visual_canvas.tag_lower(bg_rect)
            
            label = self.visual_canvas.create_text(mx, my, text=label_text, 
                                                  fill=self.colors['text_primary'], 
                                                  font=("Segoe UI", 9, "bold"))
            
            self.visual_edges.append({
                'from': from_state, 'to': to_state,
                'line': line, 'label': label,
                'symbols': symbols, 'is_loop': is_loop
            })
    
    def _compute_loop_points(self, x, y, r, loop_h):
        """Calcula puntos para un auto-bucle."""
        top = y - r - loop_h
        mid_upper = y - r - loop_h * 0.65
        mid_lower = y - r - loop_h * 0.25
        near_top = y - r - 2
        
        w1 = r * 0.55
        w2 = r * 0.85
        
        return [
            x, mid_lower,
            x + w1, mid_lower - (loop_h * 0.15),
            x + w2, mid_upper,
            x, top,
            x - w2, mid_upper,
            x - w1, mid_lower - (loop_h * 0.15),
            x, mid_lower,
            x, near_top
        ]
    
    def _compute_edge_points(self, x1, y1, x2, y2, r):
        """Calcula puntos de inicio y fin de una arista normal."""
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        
        if dist == 0:
            return x1, y1, x2, y2
        
        ux = dx / dist
        uy = dy / dist
        
        sx = x1 + ux * r
        sy = y1 + uy * r
        ex = x2 - ux * r
        ey = y2 - uy * r
        
        return sx, sy, ex, ey
    
    def create_info_panel(self, parent):
        """Crea panel compacto de información del AFD."""
        info_frame = ttk.LabelFrame(parent, text="Información del AFD", style="Card.TLabelframe")
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_container = tk.Frame(info_frame, bg=self.colors['bg_card'])
        info_container.pack(fill="x", padx=15, pady=10)
        
        # Información básica del AFD
        basic_info = tk.Frame(info_container, bg=self.colors['bg_card'])
        basic_info.pack(fill="x", pady=(0, 8))
        
        # Estados como conjunto
        estados_text = f"Estados: {{{', '.join(sorted(self.afd.states))}}}"
        tk.Label(basic_info, text=estados_text, 
                bg=self.colors['bg_card'], 
                fg=self.colors['text_secondary'], 
                font=("Segoe UI", 9),
                wraplength=400, justify="left").pack(anchor="w")
        
        # Resto de información
        info_text = f"Alfabeto: {{{', '.join(sorted(self.afd.alphabet))}}} | "
        info_text += f"Inicial: {self.afd.initial} | "
        info_text += f"Finales: {{{', '.join(sorted(self.afd.finals))}}}"
        
        info_label = tk.Label(basic_info, text=info_text, 
                             bg=self.colors['bg_card'], 
                             fg=self.colors['text_secondary'], 
                             font=("Segoe UI", 9),
                             wraplength=400, justify="left")
        info_label.pack(anchor="w", pady=(3, 0))
        
        # Resultado de la simulación
        result_frame = tk.Frame(info_container, bg=self.colors['bg_card'])
        result_frame.pack(fill="x")
        
        result_text = "ACEPTADA" if self.result.accepted else "RECHAZADA"
        result_color = self.colors['accent_green'] if self.result.accepted else self.colors['accent_red']
        
        tk.Label(result_frame, text="Resultado:", 
                bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                font=("Segoe UI", 10, "bold")).pack(side="left")
        
        tk.Label(result_frame, text=result_text,
                bg=self.colors['bg_card'], fg=result_color,
                font=("Segoe UI", 10, "bold")).pack(side="left", padx=(5, 0))
        
        # Estado final
        final_state = self.result.steps[-1].to_state if self.result.steps else "N/A"
        final_info = f"Estado final: {final_state}"
        if self.result.accepted:
            final_info += " (Estado de aceptación)"
        else:
            final_info += " (Estado de rechazo)"
            
        tk.Label(result_frame, text=f" | {final_info}",
                bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                font=("Segoe UI", 9)).pack(side="left")
        
    def create_simulation_panel(self, parent):
        """Crea el panel de simulación paso a paso."""
        sim_frame = ttk.LabelFrame(parent, text="Simulación Paso a Paso", style="Card.TLabelframe")
        sim_frame.pack(fill="both", expand=True, pady=10)
        
        sim_container = tk.Frame(sim_frame, bg=self.colors['bg_card'])
        sim_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Visualización de cadena con resaltado y scroll
        string_frame = tk.Frame(sim_container, bg=self.colors['bg_card'])
        string_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(string_frame, text="Cadena:", 
                bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        # Frame contenedor para canvas y scrollbar
        canvas_frame = tk.Frame(string_frame, bg=self.colors['bg_card'])
        canvas_frame.pack(fill="x", pady=(5, 0))
        
        self.string_canvas = tk.Canvas(canvas_frame, height=50, 
                                     bg=self.colors['bg_secondary'],
                                     highlightthickness=1,
                                     highlightbackground=self.colors['border'])
        
        # Scrollbar horizontal para cadenas largas
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", 
                                   command=self.string_canvas.xview)
        self.string_canvas.configure(xscrollcommand=h_scrollbar.set)
        
        self.string_canvas.pack(side="top", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Estado actual
        status_frame = tk.Frame(sim_container, bg=self.colors['bg_card'])
        status_frame.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(status_frame, text="Estado actual: -", 
                                    bg=self.colors['bg_card'], 
                                    fg=self.colors['text_primary'], 
                                    font=("Segoe UI", 10, "bold"))
        self.status_label.pack(anchor="w")
        
        # Tabla compacta de pasos (sin columna "Paso")
        steps_frame = tk.Frame(sim_container, bg=self.colors['bg_card'])
        steps_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        step_columns = ["Estado Origen", "Símbolo", "Estado Destino"]
        self.steps_table = ttk.Treeview(steps_frame, columns=step_columns, 
                                       show="headings", height=6,
                                       style="Modern.Treeview")
        
        column_widths = [100, 80, 110]
        for i, col in enumerate(step_columns):
            self.steps_table.heading(col, text=col)
            self.steps_table.column(col, width=column_widths[i], anchor="center")
        
        scrollbar_steps = ttk.Scrollbar(steps_frame, orient="vertical", 
                                       command=self.steps_table.yview)
        self.steps_table.configure(yscrollcommand=scrollbar_steps.set)
        
        self.steps_table.pack(side="left", fill="both", expand=True)
        scrollbar_steps.pack(side="right", fill="y")
        
        # Llenar tabla
        self.populate_steps_table()
        
    def populate_steps_table(self):
        """Llena la tabla de pasos."""
        for i, step in enumerate(self.result.steps):
            if i == 0:
                values = ["Inicial", "-", step.to_state]
            else:
                values = [step.from_state, f"'{step.symbol}'", step.to_state]
            
            self.steps_table.insert("", "end", values=values)
        
    def create_control_panel(self, parent):
        """Crea el panel de controles."""
        control_frame = ttk.LabelFrame(parent, text="Controles", style="Card.TLabelframe")
        control_frame.pack(fill="x", pady=10)
        
        control_container = tk.Frame(control_frame, bg=self.colors['bg_card'])
        control_container.pack(fill="x", padx=15, pady=10)
        
        # Botones de navegación
        nav_frame = tk.Frame(control_container, bg=self.colors['bg_card'])
        nav_frame.pack(fill="x", pady=(0, 10))
        
        self.prev_btn = ttk.Button(nav_frame, text="< Anterior", 
                                  style="Nav.TButton",
                                  command=self.previous_step)
        self.prev_btn.pack(side="left", padx=(0, 5))
        
        self.next_btn = ttk.Button(nav_frame, text="Siguiente >", 
                                  style="Nav.TButton",
                                  command=self.next_step)
        self.next_btn.pack(side="left", padx=5)
        
        self.play_btn = ttk.Button(nav_frame, text="Auto Play", 
                                  style="Nav.TButton",
                                  command=self.auto_play)
        self.play_btn.pack(side="left", padx=5)
        
        self.reset_btn = ttk.Button(nav_frame, text="Reiniciar", 
                                   style="Nav.TButton",
                                   command=self.reset_simulation)
        self.reset_btn.pack(side="left", padx=5)
        
        # Información de paso
        info_frame = tk.Frame(control_container, bg=self.colors['bg_card'])
        info_frame.pack(fill="x")
        
        self.step_label = tk.Label(info_frame, 
                                  text=f"Paso: {self.current_step}/{len(self.result.steps)-1}",
                                  bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                                  font=("Segoe UI", 10, "bold"))
        self.step_label.pack(side="left")
        
    def update_display(self):
        """Actualiza toda la visualización."""
        # Actualizar indicador de paso
        self.step_label.config(text=f"Paso: {self.current_step}/{len(self.result.steps)-1}")
        
        # Actualizar botones
        self.prev_btn.config(state="normal" if self.current_step > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_step < len(self.result.steps)-1 else "disabled")
        
        # Actualizar visualización de cadena
        self.update_string_display()
        
        # Actualizar estado actual
        self.update_status_display()
        
        # Resaltar paso en tabla
        self.highlight_current_step()
        
        # Resaltar estado en el grafo visual
        self.highlight_visual_state()
        
        # Resaltar arista usada
        self.highlight_visual_edge()
        
        # Sincronizar con canvas original
        self.sync_with_original_canvas()
    
    def update_string_display(self):
        """Actualiza la visualización de la cadena con resaltado moderno y scroll."""
        self.string_canvas.delete("all")
        
        if not self.cadena:
            # Cadena vacía
            self.string_canvas.create_text(20, 25, text="ε (cadena vacía)", 
                                          fill=self.colors['text_secondary'], 
                                          font=("Segoe UI", 12, "italic"),
                                          anchor="w")
            # Actualizar scroll region
            self.string_canvas.configure(scrollregion=self.string_canvas.bbox("all"))
            return
        
        x_start = 25
        char_width = 30
        
        for i, char in enumerate(self.cadena):
            x = x_start + i * char_width
            
            # Color según el estado de procesamiento
            if i < self.current_step:
                # Ya procesado - Verde
                color = "white"
                bg_color = self.colors['accent_green']
                border_color = "#2e7d32"
            elif i == self.current_step and self.current_step > 0:
                # Actualmente procesando - Azul
                color = "white"
                bg_color = self.colors['accent_blue']
                border_color = "#1565c0"
            else:
                # Pendiente - Gris
                color = self.colors['text_secondary']
                bg_color = self.colors['bg_secondary']
                border_color = self.colors['border']
            
            # Dibujar fondo del carácter con bordes redondeados (simulado)
            if i < self.current_step or (i == self.current_step and self.current_step > 0):
                # Rectángulo con "bordes redondeados"
                self.string_canvas.create_rectangle(x-12, 12, x+12, 38, 
                                                   fill=bg_color, outline=border_color, width=2)
            else:
                self.string_canvas.create_rectangle(x-12, 12, x+12, 38, 
                                                   fill=bg_color, outline=border_color, width=1)
            
            # Dibujar carácter
            self.string_canvas.create_text(x, 25, text=char, fill=color, 
                                          font=("Segoe UI", 12, "bold"))
        
        # Flecha indicadora moderna
        if self.current_step > 0 and self.current_step <= len(self.cadena):
            arrow_x = x_start + (self.current_step - 1) * char_width
            # Crear flecha más elegante
            points = [arrow_x-8, 42, arrow_x+8, 42, arrow_x, 48]
            self.string_canvas.create_polygon(points, fill=self.colors['accent_blue'], 
                                            outline=self.colors['accent_blue'])
        
        # Actualizar scroll region para acomodar toda la cadena
        self.string_canvas.configure(scrollregion=self.string_canvas.bbox("all"))
        
        # Auto-scroll para mantener el carácter actual visible
        if self.current_step > 0 and self.current_step <= len(self.cadena):
            char_x = x_start + (self.current_step - 1) * char_width
            canvas_width = self.string_canvas.winfo_width()
            if canvas_width > 1:  # Asegurar que el canvas está inicializado
                scroll_region = self.string_canvas.bbox("all")
                if scroll_region:
                    total_width = scroll_region[2] - scroll_region[0]
                    fraction = char_x / total_width if total_width > 0 else 0
                    self.string_canvas.xview_moveto(max(0, fraction - 0.1))
    
    def update_status_display(self):
        """Actualiza el estado actual."""
        current_state = self.result.steps[self.current_step].to_state
        
        if self.current_step == 0:
            status = f"Estado actual: {current_state} (inicial)"
        else:
            step = self.result.steps[self.current_step]
            status = f"Estado: {current_state} | Símbolo procesado: '{step.symbol}'"
        
        self.status_label.config(text=status)
    
    def highlight_current_step(self):
        """Resalta el paso actual en la tabla."""
        for item in self.steps_table.selection():
            self.steps_table.selection_remove(item)
        
        if self.current_step < len(self.steps_table.get_children()):
            item = self.steps_table.get_children()[self.current_step]
            self.steps_table.selection_set(item)
            self.steps_table.see(item)
    
    def highlight_visual_state(self):
        """Resalta el estado actual en el grafo visual."""
        current_state = self.result.steps[self.current_step].to_state
        
        # Restaurar colores originales
        for state, node in self.visual_nodes.items():
            self.visual_canvas.itemconfig(node['circle'], 
                                         fill=node['color'], width=3,
                                         outline="white")
        
        # Resaltar estado actual con animación
        if current_state in self.visual_nodes:
            self.visual_canvas.itemconfig(self.visual_nodes[current_state]['circle'],
                                         fill=self.colors['accent_orange'], width=4,
                                         outline="#ff6f00")
    
    def highlight_visual_edge(self):
        """Resalta la arista utilizada en el paso actual."""
        # Restaurar colores originales de aristas
        for edge in self.visual_edges:
            self.visual_canvas.itemconfig(edge['line'], 
                                         fill=self.colors['text_secondary'], width=3)
            self.visual_canvas.itemconfig(edge['label'], 
                                         fill=self.colors['text_primary'])
        
        # Resaltar arista del paso actual
        if self.current_step > 0:
            step = self.result.steps[self.current_step]
            
            for edge in self.visual_edges:
                if (edge['from'] == step.from_state and 
                    edge['to'] == step.to_state and 
                    step.symbol in edge['symbols']):
                    
                    self.visual_canvas.itemconfig(edge['line'], 
                                                 fill=self.colors['accent_orange'], width=5)
                    self.visual_canvas.itemconfig(edge['label'], 
                                                 fill=self.colors['accent_orange'])
                    break
    
    def sync_with_original_canvas(self):
        """Sincroniza el resaltado con el canvas original."""
        if not self.canvas:
            return
        
        current_state = self.result.steps[self.current_step].to_state
        
        # Restaurar colores originales en canvas original
        for node_id, original_color in self.original_colors.items():
            if node_id in self.canvas.nodes:
                self.canvas.itemconfig(self.canvas.nodes[node_id]['circle'], 
                                     fill=original_color, width=2)
        
        # Guardar y resaltar estado actual
        if current_state not in self.original_colors and current_state in self.canvas.nodes:
            current_fill = self.canvas.itemcget(self.canvas.nodes[current_state]['circle'], 'fill')
            self.original_colors[current_state] = current_fill
        
        if current_state in self.canvas.nodes:
            self.canvas.itemconfig(self.canvas.nodes[current_state]['circle'], 
                                 fill=self.colors['accent_orange'], width=4)
    
    def previous_step(self):
        """Va al paso anterior."""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_display()
    
    def next_step(self):
        """Va al siguiente paso."""
        if self.current_step < len(self.result.steps) - 1:
            self.current_step += 1
            self.update_display()
    
    def auto_play(self):
        """Reproduce automáticamente la simulación."""
        if self.auto_playing:
            return
        
        self.auto_playing = True
        self.play_btn.config(text="Pausa", command=self.pause_auto_play)
        
        def play_step():
            if self.auto_playing and self.current_step < len(self.result.steps) - 1:
                self.next_step()
                self.window.after(1200, play_step)  # 1.2 segundos entre pasos
            else:
                self.auto_playing = False
                self.play_btn.config(text="Auto Play", command=self.auto_play)
        
        play_step()
    
    def pause_auto_play(self):
        """Pausa el auto-play."""
        self.auto_playing = False
        self.play_btn.config(text="Auto Play", command=self.auto_play)
    
    def reset_simulation(self):
        """Reinicia la simulación."""
        self.auto_playing = False
        self.play_btn.config(text="Auto Play", command=self.auto_play)
        self.current_step = 0
        self.update_display()
    
    def center_window(self):
        """Centra la ventana."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        """Maneja el cierre de la ventana."""
        # Restaurar colores originales en canvas principal
        if self.canvas:
            for node_id, original_color in self.original_colors.items():
                if node_id in self.canvas.nodes:
                    self.canvas.itemconfig(self.canvas.nodes[node_id]['circle'], 
                                         fill=original_color, width=2)
        
        self.auto_playing = False
        self.window.destroy()


def show_simulator(parent, afd: AFD, cadena: str, canvas=None):
    """Función auxiliar para mostrar el simulador."""
    return SimulatorWindow(parent, afd, cadena, canvas)