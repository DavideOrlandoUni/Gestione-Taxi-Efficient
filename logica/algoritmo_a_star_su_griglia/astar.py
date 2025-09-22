# ============================================================
# astar.py
# - Algoritmo A* su griglia ortogonale con ostacoli
# - Ritorna SOLO le celle intermedie tra partenza e arrivo
# ============================================================

from typing import List, Tuple, Dict, Optional
import heapq
from ..impostazioni_e_costanti_di_simulazione import Cella, GRIGLIA_L, GRIGLIA_H, OSTACOLI
from ..funzioni_geometriche_euristiche import distanza_manhattan

def calcola_percorso_minimo_con_astar(partenza: Cella, arrivo: Cella) -> List[Cella]:
    """Percorso minimo (A*). Ritorna solo le intermedie; [] se non esiste."""
    if partenza == arrivo:
        return []

    coda_aperta: List[Tuple[int, Cella]] = []
    heapq.heappush(coda_aperta, (distanza_manhattan(partenza, arrivo), partenza))

    predecessore: Dict[Cella, Optional[Cella]] = {partenza: None}
    costo_g: Dict[Cella, int] = {partenza: 0}

    while coda_aperta:
        _, corrente = heapq.heappop(coda_aperta)

        if corrente == arrivo:
            percorso: List[Cella] = [arrivo]
            while predecessore[percorso[-1]] is not None:
                percorso.append(predecessore[percorso[-1]])
            percorso.reverse()
            return percorso[1:-1]

        x, y = corrente
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < GRIGLIA_L and 0 <= ny < GRIGLIA_H:
                vicino = (nx, ny)
                if vicino in OSTACOLI:
                    continue
                nuovo_g = costo_g[corrente] + 1
                if vicino not in costo_g or nuovo_g < costo_g[vicino]:
                    costo_g[vicino] = nuovo_g
                    f = nuovo_g + distanza_manhattan(vicino, arrivo)
                    predecessore[vicino] = corrente
                    heapq.heappush(coda_aperta, (f, vicino))
    return []
