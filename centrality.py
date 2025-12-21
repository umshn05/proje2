# centrality.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from graph import Graph


@dataclass
class CentralityRow:
    node_id: int
    name: str
    degree: int
    centrality: float  # normalize edilmiş degree centrality


def degree_centrality(g: Graph) -> List[CentralityRow]:
    """
    Degree centrality:
      C_D(v) = deg(v) / (n - 1)
    """
    n = len(g.nodes)
    if n <= 1:
        return []

    rows: List[CentralityRow] = []
    for nid, node in g.nodes.items():
        c = node.degree / (n - 1)
        rows.append(
            CentralityRow(
                node_id=nid,
                name=node.name,
                degree=node.degree,
                centrality=c,
            )
        )

    # büyükten küçüğe sırala
    rows.sort(key=lambda r: r.degree, reverse=True)
    return rows


def top_k_degree_centrality(g: Graph, k: int = 5) -> List[CentralityRow]:
    return degree_centrality(g)[:k]

