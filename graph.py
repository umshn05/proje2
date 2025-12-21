# graph.py
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Node:
    id: int
    name: str
    activity: float       # Aktiflik
    interaction: int      # Etkileşim
    degree: int = 0          # Bağlantı sayısı (kaç komşu)

    def __repr__(self) -> str:
        return f"{self.name}(id={self.id})"


@dataclass
class Edge:
    from_id: int
    to_id: int
    weight: float         # Kenar ağırlığı


class Graph:
    def __init__(self):
        # node_id -> Node
        self.nodes: Dict[int, Node] = {}
        # node_id -> List[Edge]
        self.adj: Dict[int, List[Edge]] = {}

    def add_node(self, node: Node):
        """Graf'a yeni düğüm ekler."""
        if node.id in self.nodes:
            raise ValueError(f"Bu id zaten var: {node.id}")
        self.nodes[node.id] = node
        self.adj[node.id] = []

    def has_edge(self, a: int, b: int) -> bool:
        """İki node arasında kenar var mı kontrol eder."""
        return any(e.to_id == b for e in self.adj.get(a, []))

    def add_undirected_edge(self, a: int, b: int, weight: float):
        """
        Yönsüz bir kenar ekler.
        a-b ve b-a olarak iki kenar ekler.
        """
        if a == b:
            raise ValueError("Self-loop yasak! (Node kendine bağlanamaz.)")

        if self.has_edge(a, b) or self.has_edge(b, a):
            return

        self.adj[a].append(Edge(a, b, weight))
        self.adj[b].append(Edge(b, a, weight))
        self.nodes[a].degree += 1  #eklenenler
        self.nodes[b].degree += 1

    def neighbors(self, node_id: int) -> List[int]:
        """Bir node'un komşu node id'lerini döner."""
        return [e.to_id for e in self.adj.get(node_id, [])]

    def edges_from(self, node_id: int) -> List[Edge]:
        """Bir node'dan çıkan kenarları döner."""
        return self.adj.get(node_id, [])

    # ---------- Komşuluk Listesi / Matrisi ----------

    def adjacency_list(self) -> dict[int, list[int]]:
        """
        Her düğüm için komşularının id listesini döner.
        Örnek: {1: [2,3], 2: [1,3], ...}
        """
        return {nid: [e.to_id for e in edges] for nid, edges in self.adj.items()}

    def adjacency_matrix(self) -> tuple[list[int], list[list[int]]]:
        """
        Komşuluk matrisini döner.
        Dönen:
          - node_ids: [1,2,3,...] sıra
          - matrix : 0/1 matrisi (node_ids sırasına göre)
        """
        node_ids = sorted(self.nodes.keys())
        index = {nid: i for i, nid in enumerate(node_ids)}
        n = len(node_ids)
        mat = [[0] * n for _ in range(n)]

        for a in node_ids:
            for e in self.adj[a]:
                b = e.to_id
                i, j = index[a], index[b]
                mat[i][j] = 1

        return node_ids, mat

    # ---------- CSV içe/dışa aktarma ----------

    @classmethod
    def from_csv(cls, path: str, weight_func) -> "Graph":
        """
        CSV'den graf oluşturur.
        Beklenen kolon isimleri:
          DugumId, Ozellik_I, Ozellik_II, Ozellik_III, Komsular
        Komsular: '2,4,5' gibi virgülle ayrılmış id listesi
        weight_func: iki Node alıp ağırlık dönen fonksiyon (calculate_weight)
        """
        g = cls()
        rows = []

        # Önce tüm düğümleri ekle
        import csv
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                rows.append(row)
                node_id = int(row["DugumId"])
                activity = float(row["Ozellik_I"])
                interaction = int(row["Ozellik_II"])
                # name veya Ozellik_III zorunlu değil
                node = Node(id=node_id, name=f"Node{node_id}",
                            activity=activity, interaction=interaction)
                g.add_node(node)

        # Sonra komşuluklara göre edge ekle

        for row in rows:
            a_id = int(row["DugumId"])
            neighbors_str = row.get("Komsular", "").strip()
            if not neighbors_str:
                continue
            neighbor_ids = [int(x) for x in neighbors_str.split(",") if x.strip()]
            for b_id in neighbor_ids:
                if b_id not in g.nodes:
                    continue
                a = g.nodes[a_id]
                b = g.nodes[b_id]
                w = weight_func(a, b)
                g.add_undirected_edge(a_id, b_id, w)

        return g

    def to_csv(self, path: str) -> None:
        """
        Grafı CSV'ye yazar.
        Kolonlar:
          DugumId, Ozellik_I (aktiflik), Ozellik_II (etkileşim),
          Ozellik_III (degree), Komsular (virgülle ayrılmış id listesi)
        """
        import csv
        fieldnames = ["DugumId", "Ozellik_I", "Ozellik_II", "Ozellik_III", "Komsular"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for node_id, node in self.nodes.items():
                neighbors = ",".join(str(nid) for nid in self.neighbors(node_id))
                writer.writerow(
                    {
                        "DugumId": node_id,
                        "Ozellik_I": node.activity,
                        "Ozellik_II": node.interaction,
                        "Ozellik_III": node.degree,
                        "Komsular": neighbors,
                    }
                )
