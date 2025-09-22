# ============================================================
# accoppiamento.py
# - Accoppiamento clienti entro raggio Manhattan (greedy)
# - Debug: stampa coppie candidate
# ============================================================

from typing import Dict, List, Tuple
from ..impostazioni_e_costanti_di_simulazione import Cella, STAZIONE
from ..funzioni_geometriche_euristiche import distanza_manhattan

def calcola_coppie_clienti_entra_raggio_manhattan(
    etichette: Dict[str, Cella], raggio: int = 2
) -> Tuple[List[Tuple[str, str]], List[str]]:
    """
    Restituisce (coppie, singoli_non_accoppiati).
    Selezione greedy: ordina per distanza crescente, evita conflitti.
    """
    labels = sorted(etichette.keys())
    candidati: List[Tuple[int, str, str]] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            d = distanza_manhattan(etichette[a], etichette[b])
            if d <= raggio:
                candidati.append((d, a, b))
    candidati.sort(
        key=lambda t: (
            t[0],
            distanza_manhattan(etichette[t[1]], STAZIONE) + distanza_manhattan(etichette[t[2]], STAZIONE),
            t[1], t[2]
        )
    )

    usati = set()
    coppie: List[Tuple[str, str]] = []
    for _, a, b in candidati:
        if a not in usati and b not in usati:
            coppie.append((a, b))
            usati.add(a); usati.add(b)

    singoli = sorted([p for p in labels if p not in usati])
    return coppie, singoli

def stampa_coppie_candidate_debug(etichette: Dict[str, Cella], raggio: int):
    """Stampa le coppie candidate entro raggio (per debug)."""
    cand = []
    labels = sorted(etichette.keys())
    for i in range(len(labels)):
        for j in range(i+1, len(labels)):
            a, b = labels[i], labels[j]
            d = distanza_manhattan(etichette[a], etichette[b])
            if d <= raggio:
                cand.append((d, a, b))
    cand.sort()
    print(f"[LOG][PAIRING] candidati (Manhattan ≤ {raggio}):", cand)
