# dijkstra.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import heapq

from graph import Graph


@dataclass
class PathResult:
    distance: float
    path: List[int]
    visited_order: List[int]


def dijkstra_shortest_path(g: Graph, start: int, goal: int) -> PathResult:
    if start not in g.nodes or goal not in g.nodes:
        raise ValueError("Start/goal graf içinde yok")

    dist: Dict[int, float] = {nid: float("inf") for nid in g.nodes}
    prev: Dict[int, Optional[int]] = {nid: None for nid in g.nodes}
    dist[start] = 0.0

    pq: List[Tuple[float, int]] = [(0.0, start)]
    visited = set()
    visited_order: List[int] = []

    while pq:
        cur_dist, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        visited_order.append(u)

        if u == goal:
            break

        for e in g.edges_from(u):
            v = e.to_id
            if v in visited:
                continue
            nd = cur_dist + float(e.weight)
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if dist[goal] == float("inf"):
        return PathResult(distance=float("inf"), path=[], visited_order=visited_order)

    path: List[int] = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    return PathResult(distance=dist[goal], path=path, visited_order=visited_order)
