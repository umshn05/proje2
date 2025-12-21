# weights.py
from graph import Node


def calculate_weight(a: Node, b: Node) -> float:
    """
    İki düğüm arasındaki ağırlığı hesaplar.
    Formül:
    1 / (1 + (aktiflik farkı)^2 + (etkileşim farkı)^2 + (bağlantı farkı)^2)
    """
    da = float(a.activity) - float(b.activity)
    di = float(a.interaction) - float(b.interaction)
    dd = float(a.degree) - float(b.degree)


    sum_square = 1 + da * da + di * di + dd * dd
    return 1.0 / sum_square
