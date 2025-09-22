# ============================================================
# costruzione_viaggio.py
# - Converte azioni SAS (move/pickup/dropoff) in un viaggio concreto
# - Estrae la prima mappatura pickup passeggero->location
# ============================================================

from typing import List, Dict, Tuple, Optional
from ..impostazioni_e_costanti_di_simulazione import Cella, STAZIONE
from ..algoritmo_a_star_su_griglia import calcola_percorso_minimo_con_astar

class PianoViaggio:
    """Percorso completo del taxi + eventi pickup/dropoff."""
    def __init__(self, percorso_completo: List[Cella], eventi_prelievo: Dict[int, List[str]], eventi_discesa: Dict[int, List[str]]):
        self.path = percorso_completo
        self.eventi_prelievo = eventi_prelievo
        self.eventi_discesa = eventi_discesa

def costruisci_viaggio_da_azioni(azioni: List[str], locs: Dict[str, Cella]) -> Tuple[PianoViaggio, Dict[str, Cella]]:
    """Traduce le azioni SAS in un PianoViaggio + etichette clienti."""
    percorso: List[Cella] = []
    prelievi: Dict[int, List[str]] = {}
    discese: Dict[int, List[str]] = {}
    etichette: Dict[str, Cella] = {}
    corrente: Optional[Cella] = None

    def cella_di(label: str) -> Cella:
        key = label.lower()
        if key not in locs:
            raise KeyError(f"Location '{label}' non definita nel file locations.")
        return locs[key]

    for raw in azioni:
        tokens = raw.strip("()").split()
        if not tokens:
            continue
        op = tokens[0]

        if op == "move":
            _, _taxi, src, dst = tokens
            src_c = cella_di(src)
            dst_c = cella_di(dst)
            if corrente is None:
                corrente = src_c
                percorso.append(corrente)
            seg = calcola_percorso_minimo_con_astar(corrente, dst_c)
            percorso += seg
            percorso.append(dst_c)
            corrente = dst_c

        elif op == "pickup":
            _, _taxi, p, l = tokens
            label = p.upper()
            etichette[label] = cella_di(l)
            if not percorso:
                corrente = cella_di(l)
                percorso.append(corrente)
            prelievi.setdefault(len(percorso) - 1, []).append(label)

        elif op == "dropoff":
            _, _taxi, p, _l = tokens
            label = p.upper()
            if not percorso:
                corrente = STAZIONE
                percorso.append(corrente)
            discese.setdefault(len(percorso) - 1, []).append(label)

    viaggio = PianoViaggio(percorso, prelievi, discese)
    return viaggio, etichette

def estrai_primi_pickup_da_azioni(azioni: List[str]) -> Dict[str, str]:
    """Prima associazione passeggero->location (es. 'P1'->'l1')."""
    mappa_pickup: Dict[str, str] = {}
    for raw in azioni:
        tok = raw.strip("()").split()
        if len(tok) == 4 and tok[0] == "pickup":
            p = tok[2].upper()
            l = tok[3].lower()
            if p not in mappa_pickup:
                mappa_pickup[p] = l
    return mappa_pickup
