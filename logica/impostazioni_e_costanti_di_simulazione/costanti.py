# ============================================================
# costanti.py
# - Costanti globali, alias di tipo, ostacoli e stazione
# ============================================================

from typing import Tuple, List

DEBUG = True

Cella = Tuple[int, int]  # (x, y)

GRIGLIA_L, GRIGLIA_H = 15, 10
PIX_CELLA = 40

STAZIONE: Cella = (0, GRIGLIA_H - 1)  # (0,9) con GRIGLIA_H=10

OSTACOLI: List[Cella] = [
    (5, 5), (5, 6), (5, 7), (5, 8),
    (8, 2), (9, 2),
    (0, 4),
]
