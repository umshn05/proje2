# main.py
# Bu dosya şu an kullanılmıyor.
# Asıl giriş noktası: gui.py (masaüstü arayüz)
# main.py
from graph import Graph
from dinamik_agirlik import calculate_weight
from dijkstra import dijkstra_shortest_path
from astar import astar_shortest_path
from centrality import top_k_degree_centrality
from components import connected_components
from welsh_powell import welsh_powell_coloring



if __name__ == "__main__":
    g = Graph.from_csv("test_graf.csv", calculate_weight)

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
