# welsh_powell.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from graph import Graph


@dataclass
class ColoringRow:
    node_id: int
    name: str
    degree: int
    color: int  # 1,2,3...


def welsh_powell_coloring(g: Graph, nodes_subset: Optional[List[int]] = None) -> Tuple[Dict[int, int], List[ColoringRow]]:
    """
    Welsh-Powell (greedy) graph coloring.
    - nodes_subset verilirse sadece o düğümler renklendirilir (bileşen bazlı).
    Dönen:
      - color_map: node_id -> color_id (1..k)
      - table: ColoringRow listesi
    """
    if nodes_subset is None:
        nodes_subset = list(g.nodes.keys())

    # Degree'a göre azalan sırala
    ordered = sorted(nodes_subset, key=lambda nid: g.nodes[nid].degree, reverse=True)

    color_map: Dict[int, int] = {}
    current_color = 0

    for u in ordered:
        if u in color_map:
            continue

        current_color += 1
        color_map[u] = current_color

        # Bu renge boyanmış node'lar ile çakışmayanları aynı renge boya
        for v in ordered:
            if v in color_map:
                continue

            conflict = False
            for x, c in color_map.items():
                if c != current_color:
                    continue
                if g.has_edge(v, x) or g.has_edge(x, v):
                    conflict = True
                    break

            if not conflict:
                color_map[v] = current_color

    table: List[ColoringRow] = [
        ColoringRow(
            node_id=nid,
            name=g.nodes[nid].name,
            degree=g.nodes[nid].degree,
            color=color_map[nid],
        )
        for nid in ordered
    ]

    # düzenli görünmesi için: renk, sonra degree
    table.sort(key=lambda r: (r.color, -r.degree, r.node_id))
    return color_map, table
