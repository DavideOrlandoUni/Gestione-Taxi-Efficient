# ============================================================
# pianificazione.py
# - Piani per taxi singolo, condiviso e multi-taxi
# ============================================================

from typing import List, Tuple, Dict
import heapq
from ..impostazioni_e_costanti_di_simulazione import Cella, STAZIONE, DEBUG
from ..algoritmo_a_star_su_griglia import calcola_percorso_minimo_con_astar
from ..logica_accoppiamento_clienti_per_raggio import (
    calcola_coppie_clienti_entra_raggio_manhattan,
    stampa_coppie_candidate_debug,
)
from ..funzioni_geometriche_euristiche import distanza_manhattan

TAXI_SINGOLO   = "taxi_singolo"
TAXI_CONDIVISO = "taxi_condiviso"

class PianoTaxi:
    """Percorso ed eventi per UN singolo taxi."""
    def __init__(self, path: List[Cella], prelievi: Dict[int, List[str]], discese: Dict[int, List[str]]):
        self.path = path
        self.eventi_prelievo = prelievi
        self.eventi_discesa = discese

class PianoMultiTaxi:
    """Piani separati per ciascun taxi + mappa etichette clienti."""
    def __init__(self, piani: Dict[str, "PianoTaxi"], etichette: Dict[str, Cella]):
        self.piani = piani
        self.etichette = etichette

def pianifica_percorso_taxi_singolo_cliente_piu_vicino(clienti: List[str], pos: Dict[str, Cella]) -> "PianoTaxi":
    """Visita iterativamente il cliente più vicino dalla stazione (greedy)."""
    curr = STAZIONE
    percorso: List[Cella] = [STAZIONE]
    prelievi: Dict[int, List[str]] = {}
    discese: Dict[int, List[str]] = {}

    restanti = set(clienti)
    while restanti:
        heap: List[Tuple[int, str]] = []
        for p in restanti:
            heapq.heappush(heap, (distanza_manhattan(curr, pos[p]), p))
        _, p = heapq.heappop(heap)

        seg = calcola_percorso_minimo_con_astar(curr, pos[p]);   percorso += seg
        percorso.append(pos[p]);                                 prelievi[len(percorso)-1] = [p]
        seg = calcola_percorso_minimo_con_astar(pos[p], STAZIONE); percorso += seg
        percorso.append(STAZIONE);                               discese[len(percorso)-1] = [p]
        curr = STAZIONE
        restanti.remove(p)

    return PianoTaxi(percorso, prelievi, discese)

def pianifica_percorso_taxi_condiviso_su_coppie(coppie: List[Tuple[str, str]], singoli: List[str], pos: Dict[str, Cella]) -> "PianoTaxi":
    """Serve coppie vicine (accoppiate) e poi eventuali singoli."""
    percorso: List[Cella] = [STAZIONE]
    prelievi: Dict[int, List[str]] = {}
    discese: Dict[int, List[str]] = {}

    coppie_ord = sorted(coppie, key=lambda ab: distanza_manhattan(pos[ab[0]], pos[ab[1]]))

    for a, b in coppie_ord:
        ca, cb = pos[a], pos[b]
        primo, secondo = (a, ca), (b, cb)
        if distanza_manhattan(cb, STAZIONE) < distanza_manhattan(ca, STAZIONE):
            primo, secondo = (b, cb), (a, ca)

        seg = calcola_percorso_minimo_con_astar(STAZIONE, primo[1]);   percorso += seg
        percorso.append(primo[1]);                                    prelievi[len(percorso)-1] = [primo[0]]
        seg = calcola_percorso_minimo_con_astar(primo[1], secondo[1]); percorso += seg
        percorso.append(secondo[1]);                                  prelievi.setdefault(len(percorso)-1, []).append(secondo[0])
        seg = calcola_percorso_minimo_con_astar(secondo[1], STAZIONE); percorso += seg
        percorso.append(STAZIONE);                                    discese[len(percorso)-1] = [primo[0], secondo[0]]

    for p in singoli:
        seg = calcola_percorso_minimo_con_astar(STAZIONE, pos[p]);     percorso += seg
        percorso.append(pos[p]);                                       prelievi[len(percorso)-1] = [p]
        seg = calcola_percorso_minimo_con_astar(pos[p], STAZIONE);     percorso += seg
        percorso.append(STAZIONE);                                     discese.setdefault(len(percorso)-1, []).append(p)

    return PianoTaxi(percorso, prelievi, discese)

def costruisci_piani_per_taxi_singolo_e_condiviso(mappa_pickup: Dict[str, str], posizioni: Dict[str, Cella], raggio_coppia: int = 2) -> "PianoMultiTaxi":
    """Costruisce i piani per due taxi: uno singolo (tutti i singoli) e uno condiviso (solo coppie)."""
    etichette: Dict[str, Cella] = { p: posizioni[l] for p, l in mappa_pickup.items() if l in posizioni }
    coppie, singoli = calcola_coppie_clienti_entra_raggio_manhattan(etichette, raggio=raggio_coppia)

    if DEBUG:
        stampa_coppie_candidate_debug(etichette, raggio_coppia)
        print(f"[LOG][PAIRING] raggio=Manhattan<={raggio_coppia} | coppie={coppie} | singoli={singoli}")

    piano_singolo   = pianifica_percorso_taxi_singolo_cliente_piu_vicino(singoli, etichette)
    piano_condiviso = pianifica_percorso_taxi_condiviso_su_coppie(coppie, [], etichette)

    return PianoMultiTaxi(
        piani={TAXI_SINGOLO: piano_singolo, TAXI_CONDIVISO: piano_condiviso},
        etichette=etichette
    )
