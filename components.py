# components.py
from __future__ import annotations
from typing import Dict, List
from collections import deque

from graph import Graph


def connected_components(g: Graph) -> List[List[int]]:
    """
    Yönsüz graf için bağlı bileşenleri döner.
    Çıktı: [[1,2,3], [4,5], ...] gibi
    """
    visited = set()
    comps: List[List[int]] = []

    for start in g.nodes.keys():
        if start in visited:
            continue

        q = deque([start])
        visited.add(start)
        comp: List[int] = []

        while q:
            u = q.popleft()
            comp.append(u)
            for v in g.neighbors(u):
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        comps.append(sorted(comp))

    # Büyük bileşen önce gelsin (istersen)
    comps.sort(key=len, reverse=True)
    return comps


def component_index_map(components: List[List[int]]) -> Dict[int, int]:
    """
    node_id -> component_id map
    """
    mp: Dict[int, int] = {}
    for i, comp in enumerate(components):
        for nid in comp:
            mp[nid] = i
    return mp
