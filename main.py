# main.py
# Bu dosya şu an kullanılmıyor.
# Asıl giriş noktası: gui.py (masaüstü arayüz)
# main.py

import os

from graph import Graph,Node
from dinamik_agirlik import calculate_weight
from dijkstra import dijkstra_shortest_path
from astar import astar_shortest_path
from centrality import top_k_degree_centrality
from components import connected_components
from welsh_powell import welsh_powell_coloring

CSV_PATH ="test_graf.csv"

def build_default_graph() -> Graph:
    """
    CSV dosyası yoksa kullanılacak örnek grafı oluşturur
    ve test_graf.csv dosyasına yazar.
    """
    g = Graph()

    # Burayı istersen kendi senaryona göre isimlendir.
    g.add_node(Node(1, "Node1", 0.8, 12))
    g.add_node(Node(2, "Node2", 0.6, 7))
    g.add_node(Node(3, "Node3", 0.7, 9))
    g.add_node(Node(4, "Node4", 0.9, 15))
    g.add_node(Node(5, "Node5", 0.3, 3))

    def add_edge(a, b):
        g.add_undirected_edge(a, b, calculate_weight(g.nodes[a], g.nodes[b]))

    add_edge(1, 2)
    add_edge(1, 3)
    add_edge(2, 3)
    add_edge(3, 4)
    add_edge(4, 5)

    # Oluşturulan grafı CSV'ye yaz
    g.to_csv(CSV_PATH)
    return g


def load_graph() -> Graph:
    """
    Önce CSV var mı kontrol eder,
    varsa CSV'den okur, yoksa yeni graf oluşturur.
    """
    if os.path.exists(CSV_PATH):
        return Graph.from_csv(CSV_PATH, calculate_weight)
    else:
        return build_default_graph()



if __name__ == "__main__":
    g = load_graph()

    print("Nodes:", len(g.nodes))
    print("Adj list:", g.adjacency_list())

    res = dijkstra_shortest_path(g, 1, 5)
    print("Dijkstra distance:", res.distance)
    print("Dijkstra path:", res.path)

    res2 = astar_shortest_path(g, 1, 5)
    print("A* distance:", res2.distance)
    print("A* path:", res2.path)
    print("\nTop 5 Degree Centrality:")
    top5 = top_k_degree_centrality(g, 5)
    for r in top5:
        print(f"- {r.name} (id={r.node_id}) degree={r.degree} centrality={r.centrality:.3f}")
    comps = connected_components(g)
    print("\nConnected Components:")
    for i, comp in enumerate(comps, start=1):
        names = [g.nodes[n].name for n in comp]
        print(f"- Component {i}: {comp} -> {names}")
    color_map, table = welsh_powell_coloring(g)
    print("\nWelsh-Powell Coloring:")
    # node_id:color şeklinde kısa çıktı
    print("Color map:", {nid: color_map[nid] for nid in sorted(color_map)})

    print("\nColoring Table:")
    for r in table:
        print(f"- {r.name} (id={r.node_id}) degree={r.degree} -> color {r.color}")
