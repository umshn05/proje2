import tkinter as tk
from tkinter import ttk, messagebox,simpledialog
import math

from main import load_graph  # CSV varsa oradan, yoksa default graf
from dijkstra import dijkstra_shortest_path
from astar import astar_shortest_path
from components import connected_components
from centrality import top_k_degree_centrality
from welsh_powell import welsh_powell_coloring


class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sosyal Ağ Analizi - GUI")
        self.geometry("900x600")
        # === Canvas için yardımcı yapılar ===
        self.node_positions = {}   # node_id -> (x, y)
        self.node_items = {}       # node_id -> canvas circle id
        self.edge_items = []       # çizilen kenarların idleri


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

    def refresh_node_options(self):
        """Başlangıç / hedef combobox'larının değerlerini günceller."""
        if not self.graph or not self.graph.nodes:
            return

        # id listesi
        self.node_ids = sorted(self.graph.nodes.keys())
        # Gösterilecek etiketler: '3 - Node3' gibi
        self.node_labels = [
            f"{nid} - {self.graph.nodes[nid].name}"
            for nid in self.node_ids
        ]

        # Combobox'ların isimleri sende farklıysa buna göre düzelt
        self.start_combo["values"] = self.node_labels
        self.goal_combo["values"] = self.node_labels

        # Varsayılan olarak ilkini seçelim (boşsa try/except)
        if self.node_labels:
            try:
                self.start_combo.current(0)
                self.goal_combo.current(0)
            except tk.TclError:
                pass


    def _create_widgets(self):
        # Üst frame: combobox'lar + butonlar
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

        # Butonlar satırı
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

        # === DÜĞÜM İŞLEMLERİ BUTONLARI ===
        node_frame = ttk.Frame(self)
        node_frame.pack(fill="x", padx=10, pady=(5, 0))
        #Ekleme
        self.btn_add_node = ttk.Button(
            node_frame, text="Düğüm Ekle", command=self.add_node_dialog
        )
        self.btn_add_node.pack(side="left", padx=5)
        #Silme
        self.btn_delete_node = ttk.Button(
            node_frame, text="Düğüm Sil", command=self.delete_node_dialog
        )
        self.btn_delete_node.pack(side="left", padx=5)
        #Güncelleme
        self.btn_update_node = ttk.Button(
            node_frame, text="Düğüm Güncelle", command=self.update_node_dialog
        )
        self.btn_update_node.pack(side="left", padx=5)




        # === GRAFİK ÇİZİM ALANI (Canvas) ===
        self.canvas = tk.Canvas(self, bg="white", height=300)
        self.canvas.pack(fill="x", padx=10, pady=(10, 5))


        # Alt kısım: sonuçların yazıldığı metin alanı
        self.output = tk.Text(self, wrap="word")
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

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
     
    def draw_graph(self):
        """self.graph içindeki node ve edge'leri canvas üzerinde çizer."""
        # Önce canvas'ı temizle
        self.canvas.delete("all")
        self.node_positions.clear()
        self.node_items.clear()
        self.edge_items.clear()

        # Graf hiç yoksa çık
        if not self.graph or not self.graph.nodes:
            return

        nodes = list(self.graph.nodes.values())
        n = len(nodes)
        if n == 0:
            return

        # Düğümleri daire şeklinde yerleştirelim
        cx, cy = 450, 150   # çemberin merkezi
        radius = 140        # çember yarıçapı
        r = 20              # düğüm dairesi yarıçapı

        # Node id -> (x, y) konumlarını hesapla
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.node_positions[node.id] = (x, y)

        # Önce kenarları çiz (aynı kenarı iki kere çizmemek için set kullanıyoruz)
        drawn_edges = set()
        for a_id, edges in self.graph.adj.items():
            x1, y1 = self.node_positions.get(a_id, (0, 0))
            for e in edges:
                key = tuple(sorted((e.from_id, e.to_id)))
                if key in drawn_edges:
                    continue
                drawn_edges.add(key)

                x2, y2 = self.node_positions.get(e.to_id, (0, 0))
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=2, fill="gray")
                self.edge_items.append(line_id)

        # Sonra düğümleri çiz (oval + id yazısı)
        for node in nodes:
            x, y = self.node_positions[node.id]
            oval_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="#88c4ff", outline="black", width=2
            )
            text_id = self.canvas.create_text(x, y, text=str(node.id))

            # Node id -> oval id kaydet
            self.node_items[node.id] = oval_id

            # Tıklama event'i bağla (oval ve text'e)
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
    def add_node_dialog(self):
        """Kullanıcıdan yeni düğüm bilgilerini alıp grafa ekler."""
        if not self.graph:
            messagebox.showerror("Hata", "Graf yüklenmemiş.", parent=self)
            return

        # 1) Id
        id_str = simpledialog.askstring("Düğüm Ekle", "Düğüm id (tam sayı):", parent=self)
        if id_str is None:  # İptal'e bastı
            return
        try:
            node_id = int(id_str)
        except ValueError:
            messagebox.showerror("Hata", "Id tam sayı olmalı.", parent=self)
            return

        if node_id in self.graph.nodes:
            messagebox.showerror("Hata", f"{node_id} id'li düğüm zaten var.", parent=self)
            return

        # 2) İsim
        name = simpledialog.askstring("Düğüm Ekle", "İsim:", parent=self)
        if not name:
            name = f"Node{node_id}"

        # 3) Aktiflik
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

        # 4) Etkileşim
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

        # 5) Node'u oluştur ve grafa ekle
        from graph import Node  # üstte import ettiysen gerekmez ama sorun değil

        new_node = Node(id=node_id, name=name, activity=activity, interaction=interaction)
        try:
            self.graph.add_node(new_node)
        except Exception as e:
            messagebox.showerror("Hata", f"Düğüm eklenirken hata oluştu:\n{e}", parent=self)
            return

        # 6) Combobox'ları ve çizimi güncelle
        self.refresh_node_options()
        self.draw_graph()

        # 7) Output alanına bilgi yaz
        self.output.insert("end", f"\n[Düğüm Ekle] id={node_id}, name={name} eklendi.\n")
        self.output.see("end")
    
    def delete_node_dialog(self):
        """Seçilen bir düğümü graflan siler."""
        if not self.graph or not self.graph.nodes:
            messagebox.showerror("Hata", "Silinecek düğüm yok.", parent=self)
            return

        # Var olan id'leri string olarak gösterelim
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

        # Emin mi diye sor
        if not messagebox.askyesno(
            "Onay", f"{node_id} id'li düğümü ve tüm bağlantılarını silmek istiyor musun?",
            parent=self
        ):
            return

        # --- Asıl silme işlemi (Graph sınıfına göre ayarla) ---
        try:
            # Eğer Graph içinde remove_node varsa:
            self.graph.remove_node(node_id)
        except AttributeError:
            # remove_node yoksa: bu basit versiyon: komşuları ve node'u elle sil
            # 1) Diğer düğümlerin adjacency listesinden çıkar
            for nid, edges in list(self.graph.adj.items()):
                self.graph.adj[nid] = [e for e in edges if e.to_id != node_id]
            # 2) Bu düğümün adjacency kaydını sil
            if node_id in self.graph.adj:
                del self.graph.adj[node_id]
            # 3) Node kaydını sil
            del self.graph.nodes[node_id]

        # Combobox ve çizimi güncelle
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

        # Mevcut değerleri göstererek güncelleme isteyelim
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

        # Güncelle
        node.name = name
        node.activity = activity
        node.interaction = interaction
        # degree'i algoritmaların kendisi zaten kullanıyor, elle değiştirmiyoruz

        # Combobox label'ları ve çizimi güncelle
        self.refresh_node_options()
        self.draw_graph()

        self.output.insert(
            "end",
            f"\n[Düğüm Güncelle] id={node_id}, "
            f"name={name}, activity={activity}, interaction={interaction}\n"
        )
        self.output.see("end")

         
    def on_node_click(self, node_id: int):
        """Canvas üzerinde bir düğüme tıklanınca çalışır."""
        node = self.graph.nodes[node_id]
        neighbors = self.graph.neighbors(node_id)

        # Seçili düğümü görsel olarak biraz vurgulayalım
        for nid, item_id in self.node_items.items():
            width = 3 if nid == node_id else 1
            self.canvas.itemconfig(item_id, width=width)

        # Bilgiyi output alanına yaz
        self.output.insert("end", "\n--- Seçili düğüm ---\n")
        self.output.insert(
            "end",
            f"id={node.id}, name={getattr(node, 'name', f'Node{node.id}')}, "
            f"activity={node.activity}, interaction={node.interaction}, "
            f"degree={node.degree}\n"
        )
        self.output.insert("end", f"Komşuları: {neighbors}\n")
        self.output.see("end")

    # Yardımcı: combobox'lardan seçilen node id'leri al
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

    # Dijkstra butonu
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

    # A* butonu
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

    # Bağlı bileşenler
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

    # Degree centrality (top 5)
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

    # Welsh-Powell renkleme
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

        self.output.insert("end", "\nTablo:\n")
        for r in table:
            self.output.insert(
                "end",
                f"- {r.name} (id={r.node_id}) degree={r.degree} -> color {r.color}\n",
            )
        self.output.see("end")


if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
