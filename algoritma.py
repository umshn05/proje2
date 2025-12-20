# algoritma.py
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Optional, Tuple, Callable, Set
import heapq
import math

from graph import Graph, Node, Edge


# ================== Soyut Temel Sınıf ==================

class GraphAlgorithm(ABC):
    """Tüm graf algoritmaları için ortak arayüz."""

    @abstractmethod
    def run(self, graph: Graph, *args, **kwargs):
        """Algoritmayı çalıştırır."""
        raise NotImplementedError


# ================== BFS ==================

class BFS(GraphAlgorithm):
    """Genişlik öncelikli arama."""

    def run(self, graph: Graph, start_id: int) -> List[int]:
        visited: Set[int] = set()
        order: List[int] = []
        q = deque()

        visited.add(start_id)
        q.append(start_id)

        while q:
            u = q.popleft()
            order.append(u)
            for v in graph.neighbors(u):
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        return order


def bfs(graph: Graph, start_id: int) -> List[int]:
    """Fonksiyon şeklinde kullanım kolaylığı için."""
    return BFS().run(graph, start_id)


# ================== DFS ==================

class DFS(GraphAlgorithm):
    """Derinlik öncelikli arama (iteratif)."""

    def run(self, graph: Graph, start_id: int) -> List[int]:
        visited: Set[int] = set()
        order: List[int] = []
        stack: List[int] = [start_id]

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            order.append(u)
            # Komşuları tersten eklersek çıktıda daha okunaklı olur
            neighbors = list(graph.neighbors(u))
            neighbors.reverse()
            for v in neighbors:
                if v not in visited:
                    stack.append(v)

        return order


def dfs(graph: Graph, start_id: int) -> List[int]:
    return DFS().run(graph, start_id)


# ================== Dijkstra ==================

class Dijkstra(GraphAlgorithm):
    """Pozitif ağırlıklı kenarlarda en kısa yol."""

    def run(
        self, graph: Graph, source_id: int
    ) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
        dist: Dict[int, float] = {nid: math.inf for nid in graph.nodes}
        prev: Dict[int, Optional[int]] = {nid: None for nid in graph.nodes}

        dist[source_id] = 0.0
        pq: List[Tuple[float, int]] = [(0.0, source_id)]

        while pq:
            d_u, u = heapq.heappop(pq)
            if d_u > dist[u]:
                continue  # eski kayıt

            for e in graph.edges_from(u):
                v = e.to_id
                alt = dist[u] + e.weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))

        return dist, prev


def dijkstra(
    graph: Graph, source_id: int
) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    return Dijkstra().run(graph, source_id)


def reconstruct_path(prev: Dict[int, Optional[int]], target_id: int) -> List[int]:
    """Dijkstra/A* sonucu prev sözlüğünden yolu çıkarır."""
    path: List[int] = []
    cur: Optional[int] = target_id
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


# ================== A* (A Star) ==================

class AStar(GraphAlgorithm):
    """
    A* algoritması.
    heuristic: h(node_id) -> tahmini kalan maliyet.
    Heuristic verilmezse Dijkstra'ya eşdeğer olur (h=0).
    """

    def __init__(self, heuristic: Optional[Callable[[int], float]] = None) -> None:
        self.heuristic = heuristic or (lambda _: 0.0)

    def run(
        self, graph: Graph, source_id: int, target_id: int
    ) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
        h = self.heuristic

        g_score: Dict[int, float] = {nid: math.inf for nid in graph.nodes}
        f_score: Dict[int, float] = {nid: math.inf for nid in graph.nodes}
        prev: Dict[int, Optional[int]] = {nid: None for nid in graph.nodes}

        g_score[source_id] = 0.0
        f_score[source_id] = h(source_id)

        open_set: List[Tuple[float, int]] = [(f_score[source_id], source_id)]

        while open_set:
            _, u = heapq.heappop(open_set)
            if u == target_id:
                # hedefe ulaştık
                return g_score, prev

            for e in graph.edges_from(u):
                v = e.to_id
                tentative_g = g_score[u] + e.weight
                if tentative_g < g_score[v]:
                    g_score[v] = tentative_g
                    f_score[v] = tentative_g + h(v)
                    prev[v] = u
                    heapq.heappush(open_set, (f_score[v], v))

        # hedefe ulaşılamadıysa yine de mevcut skorları döndür
        return g_score, prev


def astar(
    graph: Graph,
    source_id: int,
    target_id: int,
    heuristic: Optional[Callable[[int], float]] = None,
) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    return AStar(heuristic).run(graph, source_id, target_id)


# ================== Bağlı Bileşenler ==================

class ConnectedComponents(GraphAlgorithm):
    """Grafın bağlı bileşenlerini bulur."""

    def run(self, graph: Graph) -> List[List[int]]:
        visited: Set[int] = set()
        components: List[List[int]] = []

        for nid in graph.nodes:
            if nid in visited:
                continue
            comp: List[int] = []
            q = deque([nid])
            visited.add(nid)

            while q:
                u = q.popleft()
                comp.append(u)
                for v in graph.neighbors(u):
                    if v not in visited:
                        visited.add(v)
                        q.append(v)

            components.append(comp)

        return components


def connected_components(graph: Graph) -> List[List[int]]:
    return ConnectedComponents().run(graph)


# ================== Degree Centrality ==================

class DegreeCentrality(GraphAlgorithm):
    """Node'ları degree değerine göre sıralar; ilk k tanesini döner."""

    def run(self, graph: Graph, k: int = 5) -> List[int]:
        # degree bilgisi node.degree alanında tutuluyor
        sorted_nodes = sorted(
            graph.nodes.values(), key=lambda n: n.degree, reverse=True
        )
        top = sorted_nodes[:k]
        return [n.id for n in top]


def degree_centrality(graph: Graph, k: int = 5) -> List[int]:
    return DegreeCentrality().run(graph, k)


# ================== Welsh–Powell Renklendirme ==================

class WelshPowellColoring(GraphAlgorithm):
    """
    Welsh–Powell graf renklendirme algoritması.
    Komşu düğümler aynı rengi alamaz.
    Çıktı: node_id -> renk numarası (1,2,3,...)
    """

    def run(self, graph: Graph) -> Dict[int, int]:
        # Node'ları degree'e göre azalan sırala
        nodes_sorted = sorted(
            graph.nodes.values(), key=lambda n: n.degree, reverse=True
        )

        color: Dict[int, int] = {}
        current_color = 0

        for node in nodes_sorted:
            if node.id in color:
                continue
            current_color += 1
            color[node.id] = current_color

            # Aynı renge boyanabilecek diğer node'ları bul
            for other in nodes_sorted:
                if other.id in color:
                    continue
                # Diğer node, bu renge atanmış node'lardan hiçbiriyle komşu olmamalı
                conflict = False
                for nid, c in color.items():
                    if c == current_color:
                        # nid ile other komşu mu?
                        if other.id in graph.neighbors(nid):
                            conflict = True
                            break
                if not conflict:
                    color[other.id] = current_color

        return color


def welsh_powell(graph: Graph) -> Dict[int, int]:
    return WelshPowellColoring().run(graph)
