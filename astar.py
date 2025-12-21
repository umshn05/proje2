# astar.py
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


def heuristic(g: Graph, a: int, b: int) -> float:
    """
    A* için basit heuristic:
    Node özellik farklarını kullanıyoruz.
    (activity farkı + interaction farkı) küçük bir ölçekle.
    """
    na = g.nodes[a]
    nb = g.nodes[b]
    return abs(na.activity - nb.activity) + (abs(na.interaction - nb.interaction) / 100.0)


def astar_shortest_path(g: Graph, start: int, goal: int) -> PathResult:
    if start not in g.nodes or goal not in g.nodes:
        raise ValueError("Start/goal graf içinde yok")

    g_score: Dict[int, float] = {nid: float("inf") for nid in g.nodes}
    prev: Dict[int, Optional[int]] = {nid: None for nid in g.nodes}
    g_score[start] = 0.0

    # (f_score, g_score, node)
    pq: List[Tuple[float, float, int]] = [(heuristic(g, start, goal), 0.0, start)]
    visited_order: List[int] = []
    closed = set()

    while pq:
        f, cur_g, u = heapq.heappop(pq)

        if u in closed:
            continue
        closed.add(u)
        visited_order.append(u)

        if u == goal:
            break

        for e in g.edges_from(u):
            v = e.to_id
            if v in closed:
                continue

            tentative_g = cur_g + float(e.weight)
            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                prev[v] = u
                f_score = tentative_g + heuristic(g, v, goal)
                heapq.heappush(pq, (f_score, tentative_g, v))

    if g_score[goal] == float("inf"):
        return PathResult(distance=float("inf"), path=[], visited_order=visited_order)

    # path reconstruct
    path: List[int] = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    return PathResult(distance=g_score[goal], path=path, visited_order=visited_order)
