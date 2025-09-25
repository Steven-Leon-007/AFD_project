# ui/editor.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import math

class GraphEditor(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#141130", **kwargs)

        # Almacenar nodos y aristas
        self.nodes = {}
        self.edges = []  # cada elemento: {from, to, line, label_id, symbol}
        self.node_colors = {}

        # NUEVO: Estados especiales
        self.initial_state = None      # string: id del estado inicial
        self.final_states = set()      # set: ids de estados finales

        self.node_count = 0
        self.selected_node = None
        self.dragging_node = None
        self.mode = "select"
        self.selected_edge = None
        self.item_to_edge = {}  # map canvas item -> edge dict

        # Eventos del mouse
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        # NUEVO: Click derecho para menú contextual
        self.bind("<Button-3>", self.on_right_click)

    # -------------------------
    # Crear un nuevo nodo (MODIFICADO)
    # -------------------------
    def add_node(self, x, y):
        r = 25
        node_id = f"q{self.node_count}"
        color = self._random_color()
        circle = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="white", width=2)
        text = self.create_text(x, y, text=node_id)
        
        # NUEVA estructura para incluir círculo exterior y flecha
        self.nodes[node_id] = {
            'x': x, 'y': y,
            'circle': circle,
            'text': text,
            'outer_circle': None,    # para estados finales
            'initial_arrow': None    # para estado inicial
        }
        
        self.node_colors[node_id] = color
        self.node_count += 1
        
        # Si es el primer nodo, hacerlo inicial automáticamente
        if len(self.nodes) == 1:
            self.set_initial_state(node_id)
            
        return node_id

    # NUEVO: Marcar estado inicial
    def set_initial_state(self, node_id):
        if node_id not in self.nodes:
            return
            
        # Quitar marca anterior
        if self.initial_state:
            old_arrow = self.nodes[self.initial_state]['initial_arrow']
            if old_arrow:
                self.delete(old_arrow)
                self.nodes[self.initial_state]['initial_arrow'] = None
        
        # Marcar nuevo inicial
        self.initial_state = node_id
        self._draw_initial_arrow(node_id)

    def _draw_initial_arrow(self, node_id):
        node = self.nodes[node_id]
        x, y = node['x'], node['y']
        r = 25
        
        # Flecha entrante desde la izquierda
        start_x = x - r - 30
        end_x = x - r - 2
        arrow = self.create_line(start_x, y, end_x, y, 
                                arrow=tk.LAST, width=3, fill="lime", 
                                arrowshape=(10, 12, 4))
        node['initial_arrow'] = arrow

    # NUEVO: Marcar/desmarcar estado final
    def toggle_final_state(self, node_id):
        if node_id not in self.nodes:
            return
            
        if node_id in self.final_states:
            # Quitar de finales
            self.final_states.remove(node_id)
            outer = self.nodes[node_id]['outer_circle']
            if outer:
                self.delete(outer)
                self.nodes[node_id]['outer_circle'] = None
        else:
            # Añadir a finales
            self.final_states.add(node_id)
            self._draw_outer_circle(node_id)

    def _draw_outer_circle(self, node_id):
        node = self.nodes[node_id]
        x, y = node['x'], node['y']
        r = 25
        outer_r = r + 5
        
        outer_circle = self.create_oval(x-outer_r, y-outer_r, x+outer_r, y+outer_r, 
                                       fill="", outline="lime", width=2)
        node['outer_circle'] = outer_circle

    # NUEVO: Menú contextual
    def on_right_click(self, event):
        clicked_node = self._get_node_at(event.x, event.y)
        if not clicked_node:
            return
            
        menu = tk.Menu(self, tearoff=0)
        
        # Estado inicial
        if clicked_node == self.initial_state:
            menu.add_command(label="✓ Estado inicial", state="disabled")
        else:
            menu.add_command(label="Marcar como inicial", 
                           command=lambda: self.set_initial_state(clicked_node))
        
        # Estado final
        if clicked_node in self.final_states:
            menu.add_command(label="✓ Estado final", state="disabled")
            menu.add_command(label="Quitar estado final", 
                           command=lambda: self.toggle_final_state(clicked_node))
        else:
            menu.add_command(label="Marcar como final", 
                           command=lambda: self.toggle_final_state(clicked_node))
        
        menu.tk_popup(event.x_root, event.y_root)

    # NUEVO: Métodos para obtener datos del AFD
    def get_afd_data(self):
        """Devuelve los datos necesarios para crear un AFD"""
        return {
            'states': set(self.nodes.keys()),
            'initial_state': self.initial_state,
            'final_states': self.final_states.copy(),
            'edges': self.edges.copy()
        }

    def has_valid_structure(self):
        """Verifica si tiene estructura mínima para AFD"""
        return (len(self.nodes) > 0 and 
                self.initial_state is not None and 
                len(self.edges) > 0)

    # -------------------------
    # Crear una conexión (arista) 
    # -------------------------
    def add_edge(self, from_node, to_node, symbols):
        """Crea una arista (o actualiza si ya existe) con lista de símbolos."""
        # Normalizar símbolos a lista única preservando orden
        if isinstance(symbols, str):
            symbols = self._parse_symbols(symbols)
        else:
            # limpiar cada símbolo
            clean = []
            for s in symbols:
                s = s.strip()
                if s and s not in clean:
                    clean.append(s)
            symbols = clean

        # Buscar si ya existe la arista (mismo origen y destino)
        for edge in self.edges:
            if edge["from"] == from_node and edge["to"] == to_node:
                # Fusionar símbolos
                existing_list = edge["symbols"]
                for s in symbols:
                    if s not in existing_list:
                        existing_list.append(s)
                # Actualizar texto
                self.itemconfig(edge["label_id"], text=",".join(existing_list))
                edge["symbol"] = ",".join(existing_list)
                return edge
        # Crear nueva arista
        x1, y1 = self.nodes[from_node]['x'], self.nodes[from_node]['y']
        x2, y2 = self.nodes[to_node]['x'], self.nodes[to_node]['y']

        is_loop = from_node == to_node
        if is_loop:
            r = 25
            loop_h = r * 2.0  # altura del lazo
            pts = self._compute_loop_points(x1, y1, r, loop_h)
            line = self.create_line(*pts, smooth=True, arrow=tk.LAST, width=2, fill="white")
            # Etiqueta encima del lazo
            mx, my = x1, y1 - r - loop_h - 15
        else:
            # Línea normal con flecha
            line = self.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2, fill="white")
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 15
            
        label_text = ",".join(symbols)
        label_id = self.create_text(mx, my, text=label_text, fill="white", font=("Arial", 11, "bold"))
        edge = {
            "from": from_node,
            "to": to_node,
            "line": line,
            "label_id": label_id,
            "symbol": label_text,
            "symbols": symbols,
            "is_loop": is_loop,
            "loop_h": loop_h if is_loop else None,
            "bidirectional": False,
            "direction_sign": 0,
            "offset_mag": 24,
        }
        self.edges.append(edge)
        # Mapear ítems a la arista (para selección)
        self.item_to_edge[line] = edge
        self.item_to_edge[label_id] = edge
        
        if not is_loop:
            reverse = None
            for e in self.edges:
                if e is not edge and e["from"] == to_node and e["to"] == from_node:
                    reverse = e
                    break
            if reverse:
                # Marcar ambos con desplazos opuestos
                edge["bidirectional"] = True
                reverse["bidirectional"] = True
                edge["direction_sign"] = 1
                reverse["direction_sign"] = -1

        # Recalcular inmediatamente para aplicar offsets si procede
        self._update_edges()
        self._notify_selection_change()
        return edge

    # -------------------------
    # Eventos del mouse
    # -------------------------
    def on_click(self, event):
        clicked_node = self._get_node_at(event.x, event.y)
        current_item = self.find_withtag("current")
        
        if self.mode == "select":
            if clicked_node:
                self._select_node(clicked_node)
                self.dragging_node = clicked_node
            else:
                # ¿Click sobre arista?
                edge = None
                if current_item:
                    edge = self.item_to_edge.get(current_item[0])
                if edge:
                    self._select_edge(edge)
                else:
                    # click vacío: limpiar selección y crear nodo
                    self.clear_selection()
                    self.add_node(event.x, event.y)
                    self._notify_selection_change()

        elif self.mode == "connect":
            if clicked_node:
                if not self.selected_node:
                    self.selected_node = clicked_node
                    # CORREGIDO: usar nueva estructura
                    self.itemconfig(self.nodes[clicked_node]['circle'], fill="orange")
                else:
                    # Pedir símbolo de transición
                    symbol = simpledialog.askstring(
                        "Transición",
                        f"Símbolo para {self.selected_node} -> {clicked_node}",
                        parent=self
                    )
                    if symbol is None or symbol.strip() == "":
                        # Restaurar color original
                        original = self.node_colors.get(self.selected_node, "lightblue")
                        self.itemconfig(self.nodes[self.selected_node]['circle'], fill=original)
                        self.selected_node = None
                        return
                    symbol = symbol.strip()
                    # Crear arista
                    self.add_edge(self.selected_node, clicked_node, symbol)
                    original = self.node_colors.get(self.selected_node, "lightblue")
                    self.itemconfig(self.nodes[self.selected_node]['circle'], fill=original)
                    self.selected_node = None

    def on_drag(self, event):
        if self.dragging_node:
            node_id = self.dragging_node
            node = self.nodes[node_id]
            r = 25
            
            # Mover círculo principal y texto
            self.coords(node['circle'], event.x-r, event.y-r, event.x+r, event.y+r)
            self.coords(node['text'], event.x, event.y)
            
            # Mover círculo exterior si existe
            if node['outer_circle']:
                outer_r = r + 5
                self.coords(node['outer_circle'], event.x-outer_r, event.y-outer_r, 
                           event.x+outer_r, event.y+outer_r)
            
            # Mover flecha inicial si existe
            if node['initial_arrow']:
                self.delete(node['initial_arrow'])
                node['initial_arrow'] = None
                # Actualizar posición primero
                node['x'] = event.x
                node['y'] = event.y
                self._draw_initial_arrow(node_id)
            else:
                # Actualizar posición
                node['x'] = event.x
                node['y'] = event.y
            
            # Actualizar aristas conectadas
            self._update_edges()

    def on_release(self, event):
        self.dragging_node = None

    # -------------------------
    # Helpers 
    # -------------------------
    def _get_node_at(self, x, y):
        """Devuelve el id del nodo si se hace clic dentro de uno."""
        for node_id, node in self.nodes.items():
            nx, ny = node['x'], node['y']
            r = 25
            if (nx-r <= x <= nx+r) and (ny-r <= y <= ny+r):
                return node_id
        return None

    def _update_edges(self):
        """Redibuja las aristas al mover nodos."""
        for edge in self.edges:
            from_node = edge["from"]
            to_node = edge["to"]
            line = edge["line"]
            label_id = edge["label_id"]
            # CORREGIDO: usar nueva estructura
            x1, y1 = self.nodes[from_node]['x'], self.nodes[from_node]['y']
            x2, y2 = self.nodes[to_node]['x'], self.nodes[to_node]['y']
            
            if edge.get("is_loop"):
                # Recalcular lazo con flecha
                r = 25
                loop_h = edge.get("loop_h") or r * 2.0
                pts = self._compute_loop_points(x1, y1, r, loop_h)
                self.coords(line, *pts)
                mx, my = x1, y1 - r - loop_h - 15
                self.coords(label_id, mx, my)
            else:
                # Arista normal o bidireccional
                if edge.get("bidirectional"):
                    sx, sy, ex, ey, (mx, my) = self._compute_line_with_offset(
                        x1, y1, x2, y2,
                        r=25,
                        offset_sign=edge["direction_sign"],
                        offset_mag=edge.get("offset_mag", 24)
                    )
                    self.coords(line, sx, sy, ex, ey)
                    # Etiqueta en el centro de su propia línea
                    self.coords(label_id, mx, my + 15)
                else:
                    # Arista simple
                    sx, sy, ex, ey, (mx, my) = self._compute_line_with_offset(
                        x1, y1, x2, y2, r=25, offset_sign=0, offset_mag=0
                    )
                    self.coords(line, sx, sy, ex, ey)
                    self.coords(label_id, mx, my - 15)

    # -------------------------
    # Cambiar modos
    # -------------------------
    def set_mode(self, mode: str):
        if mode not in ("select", "connect"):
            raise ValueError("Modo inválido. Use 'select' o 'connect'.")
        # Resetear selección si cambio de modo
        if self.selected_node:
            original = self.node_colors.get(self.selected_node, "lightblue")
            # CORREGIDO: usar nueva estructura
            self.itemconfig(self.nodes[self.selected_node]['circle'], fill=original)
            self.selected_node = None
        self.mode = mode

    # -------------------------
    # Parseo de símbolos
    # -------------------------
    def _parse_symbols(self, raw: str):
        parts = [p.strip() for p in raw.split(",")]
        result = []
        for p in parts:
            if p and p not in result:
                result.append(p)
        return result

    # -------------------------
    # Generación de colores
    # -------------------------
    def _random_color(self):
        """Devuelve un color hex aleatorio con buena visibilidad sobre fondo oscuro."""
        palette = [
            "#4FC3F7", "#81C784", "#FFB74D", "#E57373", "#BA68C8",
            "#FFD54F", "#4DB6AC", "#F06292", "#9575CD", "#64B5F6",
            "#AED581", "#FF8A65", "#A1887F", "#90A4AE", "#DCE775"
        ]
        return random.choice(palette)

    # -------------------------
    # Cálculo de puntos para lazo con flecha
    # -------------------------
    def _compute_loop_points(self, x: int, y: int, r: int, loop_h: float):
        """Genera una lista de puntos para un lazo suave con flecha hacia el nodo."""
        top = y - r - loop_h
        mid_upper = y - r - loop_h * 0.65
        mid_lower = y - r - loop_h * 0.25
        near_top = y - r - 2

        w1 = r * 0.55
        w2 = r * 0.85

        pts = [
            x, mid_lower,
            x + w1, mid_lower - (loop_h * 0.15),
            x + w2, mid_upper,
            x, top,
            x - w2, mid_upper,
            x - w1, mid_lower - (loop_h * 0.15),
            x, mid_lower,
            x, near_top
        ]
        return pts

    def _compute_line_with_offset(self, x1, y1, x2, y2, r=25, offset_sign=0, offset_mag=24):
        """Calcula coordenadas de línea desde borde a borde con posible desplazamiento perpendicular."""
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return x1, y1, x2, y2, ((x1 + x2) / 2, (y1 + y2) / 2)

        # Vector unitario
        ux = dx / dist
        uy = dy / dist

        # Base determinista para perpendicular
        bdx, bdy = dx, dy
        if bdx < 0 or (bdx == 0 and bdy < 0):
            bdx = -bdx
            bdy = -bdy
        bdist = math.hypot(bdx, bdy)
        bx = bdx / bdist
        by = bdy / bdist

        # Perpendicular consistente
        px = -by
        py = bx

        # Recortar para que no entren al círculo
        sx = x1 + ux * r
        sy = y1 + uy * r
        ex = x2 - ux * r
        ey = y2 - uy * r

        if offset_sign != 0:
            ox = px * offset_mag * offset_sign
            oy = py * offset_mag * offset_sign
            sx += ox; sy += oy
            ex += ox; ey += oy

        mx = (sx + ex) / 2
        my = (sy + ey) / 2
        return sx, sy, ex, ey, (mx, my)
    
    # -------------------------
    # Selección y edición
    # -------------------------
    def clear_selection(self):
        # Restaurar nodo
        if self.selected_node:
            original = self.node_colors.get(self.selected_node, "lightblue")
            # CORREGIDO: usar nueva estructura
            circle = self.nodes[self.selected_node]['circle']
            self.itemconfig(circle, outline="white", width=2, fill=original)
            self.selected_node = None
        # Restaurar arista
        if self.selected_edge:
            line = self.selected_edge["line"]
            label = self.selected_edge["label_id"]
            self.itemconfig(line, fill="white", width=2)
            self.itemconfig(label, fill="white")
            self.selected_edge = None

    def _select_node(self, node_id):
        if self.selected_node == node_id:
            return
        self.clear_selection()
        self.selected_node = node_id
        # CORREGIDO: usar nueva estructura
        circle = self.nodes[node_id]['circle']
        self.itemconfig(circle, outline="yellow", width=3)
        self._notify_selection_change()

    def _select_edge(self, edge):
        if self.selected_edge is edge:
            return
        self.clear_selection()
        self.selected_edge = edge
        self.itemconfig(edge["line"], fill="#FFEB3B", width=3)
        self.itemconfig(edge["label_id"], fill="#FFEB3B")
        self._notify_selection_change()

    def get_selection_kind(self):
        if self.selected_node:
            return "node"
        if self.selected_edge:
            return "edge"
        return None

    def edit_selected(self):
        if self.selected_node:
            old_id = self.selected_node
            new_id = simpledialog.askstring("Editar nodo", "Nuevo nombre del estado:", initialvalue=old_id, parent=self)
            if not new_id or new_id == old_id:
                return
            new_id = new_id.strip()
            if new_id in self.nodes:
                messagebox.showerror("Error", "Ya existe un nodo con ese nombre.")
                return
            # CORREGIDO: actualizar con nueva estructura
            node = self.nodes.pop(old_id)
            self.node_colors[new_id] = self.node_colors.pop(old_id)
            self.nodes[new_id] = node
            self.itemconfig(node['text'], text=new_id)
            
            # Actualizar estados especiales
            if self.initial_state == old_id:
                self.initial_state = new_id
            if old_id in self.final_states:
                self.final_states.remove(old_id)
                self.final_states.add(new_id)
                
            # Actualizar aristas
            for edge in self.edges:
                if edge["from"] == old_id:
                    edge["from"] = new_id
                if edge["to"] == old_id:
                    edge["to"] = new_id
            self.selected_node = new_id
        elif self.selected_edge:
            edge = self.selected_edge
            current = ",".join(edge["symbols"])
            new_syms = simpledialog.askstring("Editar transición", "Símbolos (separados por coma):", initialvalue=current, parent=self)
            if new_syms is None:
                return
            symbols = self._parse_symbols(new_syms)
            if not symbols:
                messagebox.showerror("Error", "Debe ingresar al menos un símbolo.")
                return
            edge["symbols"] = symbols
            edge["symbol"] = ",".join(symbols)
            self.itemconfig(edge["label_id"], text=edge["symbol"])
        self._update_edges()
        self._notify_selection_change()

    def delete_selected(self):
        if self.selected_edge:
            edge = self.selected_edge
            self.delete(edge["line"])
            self.delete(edge["label_id"])
            self.edges.remove(edge)
            self.item_to_edge.pop(edge["line"], None)
            self.item_to_edge.pop(edge["label_id"], None)
            self.selected_edge = None
        elif self.selected_node:
            node_id = self.selected_node
            node = self.nodes[node_id]
            
            # Eliminar aristas incidentes
            for edge in self.edges[:]:
                if edge["from"] == node_id or edge["to"] == node_id:
                    self.delete(edge["line"])
                    self.delete(edge["label_id"])
                    self.item_to_edge.pop(edge["line"], None)
                    self.item_to_edge.pop(edge["label_id"], None)
                    self.edges.remove(edge)
            
            # CORREGIDO: eliminar elementos con nueva estructura
            self.delete(node['circle'])
            self.delete(node['text'])
            if node['outer_circle']:
                self.delete(node['outer_circle'])
            if node['initial_arrow']:
                self.delete(node['initial_arrow'])
                
            # Actualizar estados especiales
            if self.initial_state == node_id:
                self.initial_state = None
            if node_id in self.final_states:
                self.final_states.remove(node_id)
                
            # Eliminar del diccionario
            self.nodes.pop(node_id, None)
            self.node_colors.pop(node_id, None)
            self.selected_node = None
            
        self.clear_selection()
        self._update_edges()
        self._notify_selection_change()

    def _notify_selection_change(self):
        # Evento virtual para que la app habilite/deshabilite botones
        self.event_generate("<<SelectionChanged>>", when="tail")

    # -------------------------
    # Métodos públicos para la interfaz
    # -------------------------
    def get_selected_node(self):
        """Devuelve el ID del nodo seleccionado o None"""
        return self.selected_node
        
    def is_initial_state(self, node_id):
        """Verifica si un nodo es el estado inicial"""
        return self.initial_state == node_id
        
    def is_final_state(self, node_id):
        """Verifica si un nodo es un estado final"""
        return node_id in self.final_states
        
    def get_automaton_info(self):
        """Devuelve información del autómata para exportar/guardar"""
        return {
            'nodes': list(self.nodes.keys()),
            'initial_state': self.initial_state,
            'final_states': list(self.final_states),
            'edges': [(e['from'], e['to'], e['symbols']) for e in self.edges]
        }
    
    # -------------------------
    # NUEVO: Conversión Canvas → AFD
    # -------------------------
    def to_afd(self):
        """Convierte el estado actual del canvas a una instancia AFD."""
        from afd_core.afd import AFD
        
        if not self.has_valid_structure():
            raise ValueError("El autómata no tiene estructura válida (necesita estados, inicial y transiciones)")
        
        # Extraer alfabeto de las aristas
        alphabet = set()
        for edge in self.edges:
            for symbol in edge["symbols"]:
                alphabet.add(symbol)
        
        if not alphabet:
            raise ValueError("No se ha definido ningún símbolo en las transiciones")
        
        # Construir función de transición
        transitions = {}
        states = list(self.nodes.keys())
        
        # Inicializar tabla de transiciones
        for state in states:
            transitions[state] = {}
            for symbol in alphabet:
                transitions[state][symbol] = None  # Marcamos como no definida
        
        # Llenar transiciones desde las aristas
        for edge in self.edges:
            from_state = edge["from"]
            to_state = edge["to"]
            for symbol in edge["symbols"]:
                if transitions[from_state][symbol] is not None:
                    raise ValueError(f"Transición duplicada: {from_state} con símbolo '{symbol}'")
                transitions[from_state][symbol] = to_state
        
        # Verificar completitud
        for state in states:
            for symbol in alphabet:
                if transitions[state][symbol] is None:
                    raise ValueError(f"Falta transición: estado '{state}' con símbolo '{symbol}'")
        
        return AFD(
            states=states,
            alphabet=list(alphabet),
            initial=self.initial_state,
            finals=list(self.final_states),
            transitions=transitions
        )
    
    # -------------------------
    # NUEVO: Conversión AFD → Canvas
    # -------------------------
    def from_afd(self, afd):
        """Carga un AFD en el canvas."""
        from afd_core.afd import AFD
        
        if not isinstance(afd, AFD):
            raise ValueError("Se esperaba una instancia de AFD")
        
        # Limpiar canvas actual
        self.clear_canvas()
        
        # Crear nodos en posiciones automáticas
        import math
        num_states = len(afd.states)
        center_x, center_y = 400, 250  # Centro del canvas
        radius = max(100, num_states * 30)  # Radio del círculo
        
        for i, state in enumerate(afd.states):
            angle = 2 * math.pi * i / num_states
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Crear nodo
            node_id = state
            color = self._random_color()
            r = 25
            circle = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="white", width=2)
            text = self.create_text(x, y, text=node_id)
            
            self.nodes[node_id] = {
                'x': x, 'y': y,
                'circle': circle,
                'text': text,
                'outer_circle': None,
                'initial_arrow': None
            }
            self.node_colors[node_id] = color
        
        # Marcar estado inicial
        if afd.initial:
            self.set_initial_state(afd.initial)
        
        # Marcar estados finales
        for final_state in afd.finals:
            if final_state in self.nodes:
                self.final_states.add(final_state)
                self._draw_outer_circle(final_state)
        
        # Crear aristas agrupadas por (from, to)
        edge_groups = {}  # (from, to) -> [symbols]
        
        for from_state in afd.transitions:
            for symbol, to_state in afd.transitions[from_state].items():
                key = (from_state, to_state)
                if key not in edge_groups:
                    edge_groups[key] = []
                edge_groups[key].append(symbol)
        
        # Crear aristas en el canvas
        for (from_state, to_state), symbols in edge_groups.items():
            self.add_edge(from_state, to_state, symbols)
        
        # Actualizar contador de nodos
        self.node_count = len(self.nodes)
    
    def clear_canvas(self):
        """Limpia completamente el canvas."""
        self.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.node_colors.clear()
        self.item_to_edge.clear()
        self.initial_state = None
        self.final_states.clear()
        self.selected_node = None
        self.selected_edge = None
        self.dragging_node = None
        self.node_count = 0