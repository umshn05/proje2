# backend_test_alg.py
from graph import Graph, Node
from dinamikAgırlık import calculate_weight
from algoritma import (
    bfs, dfs, dijkstra, reconstruct_path,
    connected_components, degree_centrality, welsh_powell
)

g = Graph()
g.add_node(Node(1, "Ayşe",0.8, 12))
g.add_node(Node(2, "Ali",  0.6, 7))
g.add_node(Node(3, "Mehmet",  0.7, 9))
g.add_node(Node(4, "Zeynep", 0.9, 15))
g.add_node(Node(5, "Can", 0.3, 3))

def add_edge(a, b):
    g.add_undirected_edge(a, b, calculate_weight(g.nodes[a], g.nodes[b]))

add_edge(1, 2)
add_edge(1, 3)
add_edge(2, 3)
add_edge(3, 4)
add_edge(4, 5)

print("BFS:", bfs(g, 1))
print("DFS:", dfs(g, 1))

dist, prev = dijkstra(g, 1)
path = reconstruct_path(prev, 5)
print("Dijkstra yol 1->5:", path, "mesafe:", dist[5])

print("Bileşenler:", connected_components(g))
print("En yüksek degree 3 düğüm:", degree_centrality(g, k=3))
print("Welsh–Powell renkler:", welsh_powell(g))

print("\nKomşuluk listesi:", g.adjacency_list())
ids, mat = g.adjacency_matrix()
print("Matris sıra:", ids)
for row in mat:
        print(row)

    # CSV'ye kaydet
g.to_csv("test_graf.csv")
print("\nGraf test_graf.csv dosyasına kaydedildi.")

    # CSV'den tekrar yükle (kontrol)
from dinamikAgırlık import calculate_weight
from graph import Graph
g2 = Graph.from_csv("test_graf.csv", calculate_weight)
print("CSV'den yüklenen graf - node sayısı:", len(g2.nodes))
print("CSV'den yüklenen graf - komşuluk listesi:", g2.adjacency_list())
