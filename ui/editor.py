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

    # -------------------------
    # Crear un nuevo nodo
    # -------------------------
    def add_node(self, x, y):
        r = 25
        node_id = f"q{self.node_count}"
        color = self._random_color()
        circle = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="white", width=2)
        text = self.create_text(x, y, text=node_id)
        self.nodes[node_id] = (x, y, circle, text)
        self.node_colors[node_id] = color
        self.node_count += 1
        return node_id

    # -------------------------
    # Crear una conexión (arista)
    # -------------------------
    def add_edge(self, from_node, to_node, symbols):
        """Crea una arista (o actualiza si ya existe) con lista de símbolos.

        symbols puede ser str ("a,b") o lista de strings. Se normaliza y se
        fusiona con símbolos existentes si la arista ya estaba creada.
        Soporta bucles (from_node == to_node) dibujando un lazo encima del nodo.
        """
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
                edge["symbol"] = ",".join(existing_list)  # compat backwards
                return edge

        x1, y1, _, _ = self.nodes[from_node]
        x2, y2, _, _ = self.nodes[to_node]

        is_loop = from_node == to_node
        if is_loop:
            # --- Lazo con flecha ---
            # Usaremos una línea suavizada que forma una elipse sobre el nodo y
            # colocaremos la flecha (arrow=tk.LAST) apuntando hacia el nodo.
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
            # Nuevos campos para bidireccional
            "bidirectional": False,
            "direction_sign": 0,   # +1 o -1 cuando sea bidireccional
            "offset_mag": 24,      # magnitud del desplazamiento perpendicular
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
        # Prioridad: si hago click sobre nodo en modo select -> seleccionar nodo
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
                    self.itemconfig(self.nodes[clicked_node][2], fill="orange")
                else:
                    # Pedir símbolo de transición
                    symbol = simpledialog.askstring(
                        "Transición",
                        f"Símbolo para {self.selected_node} -> {clicked_node}",
                        parent=self
                    )
                    # Si se cancela o vacío, no crear arista
                    if symbol is None or symbol.strip() == "":
                        # Restaurar color original del nodo previamente seleccionado
                        original = self.node_colors.get(self.selected_node, "lightblue")
                        self.itemconfig(self.nodes[self.selected_node][2], fill=original)
                        self.selected_node = None
                        return
                    symbol = symbol.strip()
                    # Crear / actualizar arista con posibles múltiples símbolos
                    self.add_edge(self.selected_node, clicked_node, symbol)
                    original = self.node_colors.get(self.selected_node, "lightblue")
                    self.itemconfig(self.nodes[self.selected_node][2], fill=original)
                    self.selected_node = None

    def on_drag(self, event):
        if self.dragging_node:
            x, y, circle, text = self.nodes[self.dragging_node]
            r = 25
            # Mover círculo y texto
            self.coords(circle, event.x-r, event.y-r, event.x+r, event.y+r)
            self.coords(text, event.x, event.y)
            # Actualizar posición en el diccionario
            self.nodes[self.dragging_node] = (event.x, event.y, circle, text)
            # Actualizar aristas conectadas
            self._update_edges()

    def on_release(self, event):
        self.dragging_node = None

    # -------------------------
    # Helpers
    # -------------------------
    def _get_node_at(self, x, y):
        """Devuelve el id del nodo si se hace clic dentro de uno."""
        for node_id, (nx, ny, circle, _) in self.nodes.items():
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
            x1, y1, _, _ = self.nodes[from_node]
            x2, y2, _, _ = self.nodes[to_node]
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
                    # Arista simple (sin offset), con pequeño ajuste vertical para etiqueta
                    sx, sy, ex, ey, (mx, my) = self._compute_line_with_offset(
                        x1, y1, x2, y2, r=25, offset_sign=0, offset_mag=0
                    )
                    self.coords(line, sx, sy, ex, ey)
                    self.coords(label_id, mx, my - 15)

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
    # Cambiar modos
    # -------------------------
    def set_mode(self, mode: str):
        if mode not in ("select", "connect"):
            raise ValueError("Modo inválido. Use 'select' o 'connect'.")
        # Resetear selección si cambio de modo
        if self.selected_node:
            original = self.node_colors.get(self.selected_node, "lightblue")
            self.itemconfig(self.nodes[self.selected_node][2], fill=original)
            self.selected_node = None
        self.mode = mode

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
        """Genera una lista de puntos para un lazo suave con flecha hacia el nodo.

        El último tramo desciende hacia el nodo para que la flecha (arrow=tk.LAST)
        apunte visualmente hacia él.
        """
        # Alturas intermedias para dar forma de elipse
        top = y - r - loop_h
        mid_upper = y - r - loop_h * 0.65
        mid_lower = y - r - loop_h * 0.25
        near_top = y - r - 2  # punto final (flecha) justo encima del nodo

        # Anchuras laterales
        w1 = r * 0.55
        w2 = r * 0.85

        # Orden de puntos (cerrando el lazo) terminando en near_top para flecha
        pts = [
            x, mid_lower,          # inicio (no se nota el inicio con smooth)
            x + w1, mid_lower - (loop_h * 0.15),
            x + w2, mid_upper,     # lado derecho superior
            x, top,                # parte superior
            x - w2, mid_upper,     # lado izquierdo superior
            x - w1, mid_lower - (loop_h * 0.15),
            x, mid_lower,          # cierre virtual
            x, near_top            # tramo final descendente para flecha
        ]
        return pts

    def _compute_line_with_offset(self, x1, y1, x2, y2, r=25, offset_sign=0, offset_mag=24):
        """
        Calcula coordenadas de línea desde borde a borde con posible desplazamiento perpendicular.
        El perpendicular se define de forma determinista para el par (sin importar el sentido)
        de modo que las aristas opuestas realmente queden a lados opuestos.
        Devuelve (sx, sy, ex, ey, (mx, my)).
        """
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return x1, y1, x2, y2, ((x1 + x2) / 2, (y1 + y2) / 2)

        # Vector unitario en la dirección real (para recorte de extremos y flecha)
        ux = dx / dist
        uy = dy / dist

        # Base determinista para calcular el perpendicular (independiente del sentido)
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
    
    
    def clear_selection(self):
        # Restaurar nodo
        if self.selected_node:
            original = self.node_colors.get(self.selected_node, "lightblue")
            circle = self.nodes[self.selected_node][2]
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
        circle = self.nodes[node_id][2]
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
            # Actualizar diccionarios
            x, y, circle, text = self.nodes.pop(old_id)
            self.node_colors[new_id] = self.node_colors.pop(old_id)
            self.nodes[new_id] = (x, y, circle, text)
            self.itemconfig(text, text=new_id)
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
            x, y, circle, text = self.nodes[node_id]
            # Eliminar aristas incidentes
            for edge in self.edges[:]:
                if edge["from"] == node_id or edge["to"] == node_id:
                    self.delete(edge["line"])
                    self.delete(edge["label_id"])
                    self.item_to_edge.pop(edge["line"], None)
                    self.item_to_edge.pop(edge["label_id"], None)
                    self.edges.remove(edge)
            # Eliminar nodo
            self.delete(circle)
            self.delete(text)
            self.nodes.pop(node_id, None)
            self.node_colors.pop(node_id, None)
            self.selected_node = None
        self.clear_selection()
        self._update_edges()
        self._notify_selection_change()
    def _notify_selection_change(self):
        # Evento virtual para que la app habilite/deshabilite botones
        self.event_generate("<<SelectionChanged>>", when="tail")
