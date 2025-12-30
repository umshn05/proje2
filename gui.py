import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import math

from dinamik_agirlik import calculate_weight
from main import load_graph  # CSV varsa oradan, yoksa default graf
from dijkstra import dijkstra_shortest_path
from astar import astar_shortest_path
from components import connected_components
from centrality import top_k_degree_centrality
from welsh_powell import welsh_powell_coloring
from graph import Graph, Node, Edge


class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sosyal Ağ Analizi - GUI")
        self.geometry("1200x650")

        # Canvas için yardımcı yapılar
        self.node_positions = {}   # node_id -> (x, y)
        self.node_items = {}       # node_id -> canvas oval id
        self.edge_items = {}       # (a_id, b_id) -> line id

        # 1) Grafı backend'den yükle
        try:
            self.graph = load_graph()
        except Exception as e:
            messagebox.showerror("Hata", f"Graf yüklenirken hata oluştu:\n{e}")
            self.graph = None

        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Graf yüklenemedi veya düğüm yok.")
            return

        # 2) Düğüm listesi (id - name)
        self.node_ids = sorted(self.graph.nodes.keys())
        self.node_labels = [
            f"{nid} - {self.graph.nodes[nid].name}"
            for nid in self.node_ids
        ]

        # Arayüz elemanlarını oluştur
        self._create_widgets()
        self.draw_graph()

    # -------------------------------------------------
    # NODE SEÇİMİ / COMBOBOX GÜNCELLEME
    # -------------------------------------------------
    def refresh_node_options(self):
        """Başlangıç / hedef combobox'larının değerlerini günceller."""
        if not self.graph or not self.graph.nodes:
            return

        self.node_ids = sorted(self.graph.nodes.keys())
        self.node_labels = [
            f"{nid} - {self.graph.nodes[nid].name}"
            for nid in self.node_ids
        ]

        self.start_combo["values"] = self.node_labels
        self.goal_combo["values"] = self.node_labels

        if self.node_labels:
            try:
                self.start_combo.current(0)
                self.goal_combo.current(0)
            except tk.TclError:
                pass

    # -------------------------------------------------
    # WIDGET / LAYOUT
    # -------------------------------------------------
    def _create_widgets(self):
        # Üst frame: combobox'lar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Başlangıç düğümü
        ttk.Label(top_frame, text="Başlangıç düğümü:").grid(
            row=0, column=0, sticky="w"
        )
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(
            top_frame,
            textvariable=self.start_var,
            state="readonly",
            values=self.node_labels,
            width=25,
        )
        self.start_combo.grid(row=0, column=1, padx=5, pady=5)

        # Hedef düğüm
        ttk.Label(top_frame, text="Hedef düğüm:").grid(
            row=0, column=2, sticky="w", padx=(20, 0)
        )
        self.goal_var = tk.StringVar()
        self.goal_combo = ttk.Combobox(
            top_frame,
            textvariable=self.goal_var,
            state="readonly",
            values=self.node_labels,
            width=25,
        )
        self.goal_combo.grid(row=0, column=3, padx=5, pady=5)

        # Algoritma butonları
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.dijkstra_btn = ttk.Button(
            button_frame, text="Dijkstra", command=self.run_dijkstra
        )
        self.dijkstra_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.astar_btn = ttk.Button(
            button_frame, text="A* (A-star)", command=self.run_astar
        )
        self.astar_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.components_btn = ttk.Button(
            button_frame, text="Bağlı Bileşenler", command=self.show_components
        )
        self.components_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.centrality_btn = ttk.Button(
            button_frame, text="Degree Centrality (Top 5)", command=self.show_centrality
        )
        self.centrality_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.coloring_btn = ttk.Button(
            button_frame, text="Welsh-Powell Renkleme", command=self.show_coloring
        )
        self.coloring_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        self.clear_btn = ttk.Button(
            button_frame, text="Temizle", command=self.clear_output
        )
        self.clear_btn.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        # Node / Edge işlemleri
        node_frame = ttk.Frame(self)
        node_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.btn_add_node = ttk.Button(
            node_frame, text="Düğüm Ekle", command=self.add_node_dialog
        )
        self.btn_add_node.pack(side="left", padx=5)

        self.btn_delete_node = ttk.Button(
            node_frame, text="Düğüm Sil", command=self.delete_node_dialog
        )
        self.btn_delete_node.pack(side="left", padx=5)

        self.btn_update_node = ttk.Button(
            node_frame, text="Düğüm Güncelle", command=self.update_node_dialog
        )
        self.btn_update_node.pack(side="left", padx=5)

        self.btn_add_edge = ttk.Button(
            node_frame, text="Kenar Ekle", command=self.add_edge_dialog
        )
        self.btn_add_edge.pack(side="left", padx=5)

        self.btn_delete_edge = ttk.Button(
            node_frame, text="Kenar Sil", command=self.delete_edge_dialog
        )
        self.btn_delete_edge.pack(side="left", padx=5)

        # CSV Yükle / Kaydet
        csv_frame = ttk.Frame(self)
        csv_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.btn_load_csv = ttk.Button(
            csv_frame, text="CSV Yükle", command=self.load_csv
        )
        self.btn_load_csv.pack(side="left", padx=5)

        self.btn_save_csv = ttk.Button(
            csv_frame, text="CSV Kaydet", command=self.save_csv
        )
        self.btn_save_csv.pack(side="left", padx=5)

        # Ana görünüm: canvas solda, sonuçlar sağda
        main_pane = tk.PanedWindow(self, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, minsize=450)

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, minsize=300)

        self.canvas = tk.Canvas(left_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.output = tk.Text(right_frame, wrap="word")
        self.output.pack(fill="both", expand=True)

        # Başlangıçta graf bilgilerini yaz
        self.output.insert("end", "Graf yüklendi.\n\nDüğümler:\n")
        for nid in self.node_ids:
            node = self.graph.nodes[nid]
            self.output.insert(
                "end",
                f"- {nid}: {node.name} "
                f"(activity={node.activity}, "
                f"interaction={node.interaction}, "
                f"degree={node.degree})\n",
            )

        self.output.insert("end", "\nKomşuluk listesi:\n")
        adj = self.graph.adjacency_list()
        for nid in sorted(adj):
            self.output.insert("end", f"{nid}: {adj[nid]}\n")

    # -------------------------------------------------
    # ÇİZİM / HIGHLIGHT
    # -------------------------------------------------
    def refresh_degrees(self):
        """Adjacency list'e göre tüm düğümlerin degree değerlerini günceller."""
        if not self.graph or not self.graph.nodes:
            return

        for nid, node in self.graph.nodes.items():
            try:
                neighbors = self.graph.neighbors(nid)
                node.degree = len(neighbors)
            except Exception:
                if nid in self.graph.adj:
                    node.degree = len(self.graph.adj[nid])
                else:
                    node.degree = 0

    def draw_graph(self):
        """Grafı canvas üzerinde çizer."""
        self.canvas.delete("all")
        self.node_positions.clear()
        self.node_items.clear()
        self.edge_items.clear()

        if not self.graph or not self.graph.nodes:
            return

        try:
            self.refresh_degrees()
        except AttributeError:
            pass

        nodes = list(self.graph.nodes.values())
        n = len(nodes)
        if n == 0:
            return

        # Düğümleri grid düzeninde yerleştir
        cols = 6
        spacing_x = 120
        spacing_y = 90
        start_x = 80
        start_y = 80

        for idx, node in enumerate(nodes):
            row = idx // cols
            col = idx % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.node_positions[node.id] = (x, y)

        # Kenarları çiz
        try:
            adj = self.graph.adjacency_list()
        except Exception:
            adj = {}

        drawn_edges = set()
        for a_id, neighbors in adj.items():
            x1, y1 = self.node_positions.get(a_id, (0, 0))
            for b_id in neighbors:
                key = tuple(sorted((a_id, b_id)))
                if key in drawn_edges:
                    continue
                drawn_edges.add(key)

                x2, y2 = self.node_positions.get(b_id, (0, 0))
                line_id = self.canvas.create_line(
                    x1, y1, x2, y2, width=2, fill="gray"
                )
                self.edge_items[key] = line_id

        # Düğümleri (oval + id yazısı) çiz
        r = 20
        for node in nodes:
            x, y = self.node_positions[node.id]
            oval_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="#88c4ff", outline="black", width=2
            )
            text_id = self.canvas.create_text(x, y, text=str(node.id))

            self.node_items[node.id] = oval_id

            self.canvas.tag_bind(
                oval_id,
                "<Button-1>",
                lambda event, nid=node.id: self.on_node_click(nid)
            )
            self.canvas.tag_bind(
                text_id,
                "<Button-1>",
                lambda event, nid=node.id: self.on_node_click(nid)
            )

    def _reset_edge_styles(self):
        """Tüm kenarları varsayılan görünüme döndür."""
        for line_id in self.edge_items.values():
            self.canvas.itemconfig(line_id, fill="gray", width=2)

    def _highlight_path(self, path, color="red"):
        """Verilen path üzerindeki kenarları renklendir."""
        if not path or len(path) < 2:
            return

        self._reset_edge_styles()

        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            key = tuple(sorted((a, b)))
            line_id = self.edge_items.get(key)
            if line_id:
                self.canvas.itemconfig(line_id, fill=color, width=4)

    # -------------------------------------------------
    # DÜĞÜM / KENAR İŞLEMLERİ
    # -------------------------------------------------
    def add_node_dialog(self):
        """Kullanıcıdan yeni düğüm bilgilerini alıp grafa ekler."""
        if not self.graph:
            messagebox.showerror("Hata", "Graf yüklenmemiş.", parent=self)
            return

        id_str = simpledialog.askstring("Düğüm Ekle", "Düğüm id (tam sayı):", parent=self)
        if id_str is None:
            return
        try:
            node_id = int(id_str)
        except ValueError:
            messagebox.showerror("Hata", "Id tam sayı olmalı.", parent=self)
            return

        if node_id in self.graph.nodes:
            messagebox.showerror("Hata", f"{node_id} id'li düğüm zaten var.", parent=self)
            return

        name = simpledialog.askstring("Düğüm Ekle", "İsim:", parent=self)
        if not name:
            name = f"Node{node_id}"

        act_str = simpledialog.askstring(
            "Düğüm Ekle", "Aktiflik (0 ile 1 arası):", parent=self
        )
        if act_str is None:
            return
        try:
            activity = float(act_str)
            if not (0.0 <= activity <= 1.0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Aktiflik 0 ile 1 arasında bir sayı olmalı.", parent=self)
            return

        int_str = simpledialog.askstring(
            "Düğüm Ekle", "Etkileşim sayısı (tam sayı):", parent=self
        )
        if int_str is None:
            return
        try:
            interaction = int(int_str)
        except ValueError:
            messagebox.showerror("Hata", "Etkileşim tam sayı olmalı.", parent=self)
            return

        new_node = Node(id=node_id, name=name, activity=activity, interaction=interaction)
        try:
            self.graph.add_node(new_node)
        except Exception as e:
            messagebox.showerror("Hata", f"Düğüm eklenirken hata oluştu:\n{e}", parent=self)
            return

        self.refresh_node_options()
        self.draw_graph()

        self.output.insert("end", f"\n[Düğüm Ekle] id={node_id}, name={name} eklendi.\n")
        self.output.see("end")

    def delete_node_dialog(self):
        """Seçilen bir düğümü graflan siler."""
        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Silinecek düğüm yok.", parent=self)
            return

        mevcut_ids = ", ".join(str(nid) for nid in sorted(self.graph.nodes.keys()))
        id_str = simpledialog.askstring(
            "Düğüm Sil",
            f"Silinecek düğüm id'si (mevcutlar: {mevcut_ids}):",
            parent=self,
        )
        if id_str is None:
            return

        try:
            node_id = int(id_str)
        except ValueError:
            messagebox.showerror("Hata", "Id tam sayı olmalı.", parent=self)
            return

        if node_id not in self.graph.nodes:
            messagebox.showerror("Hata", f"{node_id} id'li düğüm bulunamadı.", parent=self)
            return

        if not messagebox.askyesno(
            "Onay", f"{node_id} id'li düğümü ve tüm bağlantılarını silmek istiyor musun?",
            parent=self
        ):
            return

        try:
            self.graph.remove_node(node_id)
        except AttributeError:
            for nid, edges in list(self.graph.adj.items()):
                self.graph.adj[nid] = [e for e in edges if e.to_id != node_id]
            if node_id in self.graph.adj:
                del self.graph.adj[node_id]
            del self.graph.nodes[node_id]

        self.refresh_node_options()
        self.draw_graph()

        self.output.insert("end", f"\n[Düğüm Sil] id={node_id} silindi.\n")
        self.output.see("end")

    def update_node_dialog(self):
        """Mevcut bir düğümün ad, aktiflik, etkileşim bilgilerini günceller."""
        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Güncellenecek düğüm yok.", parent=self)
            return

        mevcut_ids = ", ".join(str(nid) for nid in sorted(self.graph.nodes.keys()))
        id_str = simpledialog.askstring(
            "Düğüm Güncelle",
            f"Güncellenecek düğüm id'si (mevcutlar: {mevcut_ids}):",
            parent=self,
        )
        if id_str is None:
            return

        try:
            node_id = int(id_str)
        except ValueError:
            messagebox.showerror("Hata", "Id tam sayı olmalı.", parent=self)
            return

        if node_id not in self.graph.nodes:
            messagebox.showerror("Hata", f"{node_id} id'li düğüm bulunamadı.", parent=self)
            return

        node = self.graph.nodes[node_id]

        name = simpledialog.askstring(
            "Düğüm Güncelle",
            f"İsim (mevcut: {node.name}):",
            initialvalue=node.name,
            parent=self,
        )
        if not name:
            name = node.name

        act_str = simpledialog.askstring(
            "Düğüm Güncelle",
            f"Aktiflik (0-1, mevcut: {node.activity}):",
            initialvalue=str(node.activity),
            parent=self,
        )
        if act_str is None:
            return
        try:
            activity = float(act_str)
            if not (0.0 <= activity <= 1.0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Aktiflik 0 ile 1 arasında olmalı.", parent=self)
            return

        int_str = simpledialog.askstring(
            "Düğüm Güncelle",
            f"Etkileşim (mevcut: {node.interaction}):",
            initialvalue=str(node.interaction),
            parent=self,
        )
        if int_str is None:
            return
        try:
            interaction = int(int_str)
        except ValueError:
            messagebox.showerror("Hata", "Etkileşim tam sayı olmalı.", parent=self)
            return

        node.name = name
        node.activity = activity
        node.interaction = interaction

        self.refresh_node_options()
        self.draw_graph()

        self.output.insert(
            "end",
            f"\n[Düğüm Güncelle] id={node_id}, "
            f"name={name}, activity={activity}, interaction={interaction}\n"
        )
        self.output.see("end")

    def add_edge_dialog(self):
        """İki düğüm arasında kenar ekler."""
        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Graf yüklenmemiş.", parent=self)
            return

        mevcut_ids = ", ".join(str(nid) for nid in sorted(self.graph.nodes.keys()))

        from_str = simpledialog.askstring(
            "Kenar Ekle",
            f"Başlangıç düğüm id'si (mevcutlar: {mevcut_ids}):",
            parent=self,
        )
        if from_str is None:
            return

        to_str = simpledialog.askstring(
            "Kenar Ekle",
            f"Hedef düğüm id'si (mevcutlar: {mevcut_ids}):",
            parent=self,
        )
        if to_str is None:
            return

        try:
            from_id = int(from_str)
            to_id = int(to_str)
        except ValueError:
            messagebox.showerror("Hata", "Id'ler tam sayı olmalı.", parent=self)
            return

        if from_id not in self.graph.nodes or to_id not in self.graph.nodes:
            messagebox.showerror("Hata", "Girilen id'lerden biri graf içinde yok.", parent=self)
            return

        weight_str = simpledialog.askstring(
            "Kenar Ekle",
            "Ağırlık (boş bırakırsan 1.0 kabul edilir):",
            parent=self,
        )
        if not weight_str:
            weight = 1.0
        else:
            try:
                weight = float(weight_str)
            except ValueError:
                messagebox.showerror("Hata", "Ağırlık sayı olmalı.", parent=self)
                return

        if from_id not in self.graph.adj:
            self.graph.adj[from_id] = []
        if to_id not in self.graph.adj:
            self.graph.adj[to_id] = []

        for e in self.graph.adj[from_id]:
            if e.to_id == to_id:
                messagebox.showerror("Hata", f"{from_id} -> {to_id} kenarı zaten var.", parent=self)
                return

        edge1 = Edge(from_id=from_id, to_id=to_id, weight=weight)
        edge2 = Edge(from_id=to_id, to_id=from_id, weight=weight)

        self.graph.adj[from_id].append(edge1)
        self.graph.adj[to_id].append(edge2)

        if hasattr(self.graph, "edges"):
            self.graph.edges.append(edge1)
            self.graph.edges.append(edge2)

        self.draw_graph()

        self.output.insert(
            "end",
            f"\n[Kenar Ekle] {from_id} <-> {to_id} (weight={weight}) eklendi.\n"
        )
        self.output.see("end")

    def delete_edge_dialog(self):
        """İki düğüm arasındaki kenarı siler."""
        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Graf yüklenmemiş.", parent=self)
            return

        mevcut_ids = ", ".join(str(nid) for nid in sorted(self.graph.nodes.keys()))

        from_str = simpledialog.askstring(
            "Kenar Sil",
            f"Başlangıç düğüm id'si (mevcutlar: {mevcut_ids}):",
            parent=self,
        )
        if from_str is None:
            return

        to_str = simpledialog.askstring(
            "Kenar Sil",
            f"Hedef düğüm id'si (mevcutlar: {mevcut_ids}):",
            parent=self,
        )
        if to_str is None:
            return

        try:
            from_id = int(from_str)
            to_id = int(to_str)
        except ValueError:
            messagebox.showerror("Hata", "Id'ler tam sayı olmalı.", parent=self)
            return

        if from_id not in self.graph.nodes or to_id not in self.graph.nodes:
            messagebox.showerror("Hata", "Girilen id'lerden biri graf içinde yok.", parent=self)
            return

        silindi = False

        if from_id in self.graph.adj:
            eski_len = len(self.graph.adj[from_id])
            self.graph.adj[from_id] = [
                e for e in self.graph.adj[from_id] if e.to_id != to_id
            ]
            if len(self.graph.adj[from_id]) != eski_len:
                silindi = True

        if to_id in self.graph.adj:
            eski_len = len(self.graph.adj[to_id])
            self.graph.adj[to_id] = [
                e for e in self.graph.adj[to_id] if e.to_id != from_id
            ]
            if len(self.graph.adj[to_id]) != eski_len:
                silindi = True

        if hasattr(self.graph, "edges"):
            self.graph.edges = [
                e for e in self.graph.edges
                if not (
                    (e.from_id == from_id and e.to_id == to_id) or
                    (e.from_id == to_id and e.to_id == from_id)
                )
            ]

        if not silindi:
            messagebox.showinfo(
                "Bilgi", f"{from_id} ile {to_id} arasında silinecek kenar bulunamadı.",
                parent=self
            )
            return

        self.draw_graph()

        self.output.insert(
            "end",
            f"\n[Kenar Sil] {from_id} <-> {to_id} arasındaki kenar(lar) silindi.\n"
        )
        self.output.see("end")

    # -------------------------------------------------
    # NODE TIKLAMA / SEÇİM YARDIMCILAR
    # -------------------------------------------------
    def on_node_click(self, node_id: int):
        """Canvas üzerinde bir düğüme tıklanınca çalışır."""
        node = self.graph.nodes[node_id]
        neighbors = self.graph.neighbors(node_id)

        for nid, item_id in self.node_items.items():
            width = 3 if nid == node_id else 1
            self.canvas.itemconfig(item_id, width=width)

        self.output.insert("end", "\n--- Seçili düğüm ---\n")
        self.output.insert(
            "end",
            f"id={node.id}, name={getattr(node, 'name', f'Node{node.id}')}, "
            f"activity={node.activity}, interaction={node.interaction}, "
            f"degree={node.degree}\n"
        )
        self.output.insert("end", f"Komşuları: {neighbors}\n")
        self.output.see("end")

    def _get_selected_nodes(self):
        if not self.start_var.get() or not self.goal_var.get():
            messagebox.showwarning(
                "Uyarı", "Lütfen başlangıç ve hedef düğümlerini seçin."
            )
            return None, None

        try:
            start_id = int(self.start_var.get().split(" - ")[0])
            goal_id = int(self.goal_var.get().split(" - ")[0])
        except ValueError:
            messagebox.showerror("Hata", "Düğüm seçimleri okunamadı.")
            return None, None

        return start_id, goal_id

    def clear_output(self):
        self.output.delete("1.0", "end")

    # -------------------------------------------------
    # ALGORİTMA BUTONLARI
    # -------------------------------------------------
    def run_dijkstra(self):
        start, goal = self._get_selected_nodes()
        if start is None:
            return

        try:
            result = dijkstra_shortest_path(self.graph, start, goal)
        except Exception as e:
            messagebox.showerror("Hata", f"Dijkstra çalışırken hata oluştu:\n{e}")
            return

        self.output.insert("end", "\n\n[Dijkstra Sonucu]\n")
        self.output.insert("end", f"Başlangıç: {start}  Hedef: {goal}\n")
        self.output.insert("end", f"Mesafe: {result.distance}\n")
        self.output.insert("end", f"Yol: {result.path}\n")
        self.output.insert("end", f"Ziyaret sırası: {result.visited_order}\n")
        self.output.see("end")

        # Yol üzerindeki kenarları KIRMIZI ile vurgula
        self._highlight_path(result.path, color="red")

    def run_astar(self):
        start, goal = self._get_selected_nodes()
        if start is None:
            return

        try:
            result = astar_shortest_path(self.graph, start, goal)
        except Exception as e:
            messagebox.showerror("Hata", f"A* çalışırken hata oluştu:\n{e}")
            return

        self.output.insert("end", "\n\n[A* Sonucu]\n")
        self.output.insert("end", f"Başlangıç: {start}  Hedef: {goal}\n")
        self.output.insert("end", f"Mesafe: {result.distance}\n")
        self.output.insert("end", f"Yol: {result.path}\n")
        self.output.insert("end", f"Ziyaret sırası: {result.visited_order}\n")
        self.output.see("end")

        # Yol üzerindeki kenarları YEŞİL ile vurgula
        self._highlight_path(result.path, color="green")

    def show_components(self):
        try:
            comps = connected_components(self.graph)
        except Exception as e:
            messagebox.showerror("Hata", f"Bağlı bileşenler hesaplanırken hata:\n{e}")
            return

        self.output.insert("end", "\n\n[Bağlı Bileşenler]\n")
        for i, comp in enumerate(comps, start=1):
            names = [self.graph.nodes[n].name for n in comp]
            self.output.insert(
                "end", f"- Bileşen {i}: {comp} -> {names}\n"
            )
        self.output.see("end")

    def show_centrality(self):
        try:
            results = top_k_degree_centrality(self.graph, 5)
        except Exception as e:
            messagebox.showerror("Hata", f"Centrality hesaplanırken hata:\n{e}")
            return

        self.output.insert("end", "\n\n[Degree Centrality - Top 5]\n")
        for r in results:
            self.output.insert(
                "end",
                f"- {r.name} (id={r.node_id}) "
                f"degree={r.degree} "
                f"centrality={r.centrality:.3f}\n",
            )
        self.output.see("end")

    def show_coloring(self):
        try:
            color_map, table = welsh_powell_coloring(self.graph)
        except Exception as e:
            messagebox.showerror("Hata", f"Renkleme yapılırken hata:\n{e}")
            return

        self.output.insert("end", "\n\n[Welsh-Powell Renkleme]\n")
        self.output.insert("end", "Color map (node_id -> color):\n")
        for nid in sorted(color_map):
            self.output.insert("end", f"{nid} -> {color_map[nid]}\n")

        # Önce tüm düğümleri varsayılan renge döndür
        for nid, item_id in self.node_items.items():
            self.canvas.itemconfig(item_id, fill="#88c4ff")

        # Pastel renk paleti
        palette = [
            "#ffd966",
            "#9fc5f8",
            "#b6d7a8",
            "#d5a6bd",
            "#f4cccc",
            "#cfe2f3",
        ]

        self.output.insert("end", "\nTablo:\n")
        for r in table:
            self.output.insert(
                "end",
                f"- {r.name} (id={r.node_id}) degree={r.degree} -> color {r.color}\n",
            )

            item_id = self.node_items.get(r.node_id)
            if item_id:
                color_index = (r.color - 1) % len(palette)
                self.canvas.itemconfig(item_id, fill=palette[color_index])

        self.output.see("end")

    # -------------------------------------------------
    # CSV İÇE / DIŞA AKTARMA
    # -------------------------------------------------
    def load_csv(self):
        """CSV dosyasından graf yükle."""
        path = filedialog.askopenfilename(
            title="CSV Dosyası Seç",
            filetypes=[("CSV Files", "*.csv"), ("Tüm Dosyalar", "*.*")]
        )
        if not path:
            return

        try:
            self.graph = Graph.from_csv(path, calculate_weight)
        except Exception as e:
            messagebox.showerror("Hata", f"CSV yüklenirken hata oluştu:\n{e}", parent=self)
            return

        self.refresh_node_options()
        self.draw_graph()

        self.clear_output()
        self.output.insert("end", f"[CSV Yükle] {path} dosyasından graf yüklendi.\n\nDüğümler:\n")
        for nid in sorted(self.graph.nodes.keys()):
            node = self.graph.nodes[nid]
            self.output.insert(
                "end",
                f"- {nid}: {node.name} "
                f"(activity={node.activity}, interaction={node.interaction}, degree={node.degree})\n",
            )

        self.output.insert("end", "\nKomşuluk listesi:\n")
        adj = self.graph.adjacency_list()
        for nid in sorted(adj):
            self.output.insert("end", f"{nid}: {adj[nid]}\n")
        self.output.see("end")

    def save_csv(self):
        """Mevcut grafı CSV olarak kaydet."""
        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Kaydedilecek graf bulunamadı.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            title="CSV Kaydet",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Tüm Dosyalar", "*.*")]
        )
        if not path:
            return

        try:
            self.graph.to_csv(path)
        except Exception as e:
            messagebox.showerror("Hata", f"CSV kaydedilirken hata oluştu:\n{e}", parent=self)
            return

        self.output.insert("end", f"\n[CSV Kaydet] Graf {path} dosyasına kaydedildi.\n")
        self.output.see("end")
        messagebox.showinfo("Bilgi", f"Graf CSV olarak kaydedildi:\n{path}", parent=self)


if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
