# ============================================================
# manhattan.py
# - Euristica: distanza di Manhattan su griglia (no diagonali)
# ============================================================

from ..impostazioni_e_costanti_di_simulazione import Cella

def distanza_manhattan(a: Cella, b: Cella) -> int:
    """Distanza di Manhattan tra due celle."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
