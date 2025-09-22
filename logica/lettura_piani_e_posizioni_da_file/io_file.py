# ============================================================
# io_file.py
# - I/O dei piani (Fast Downward) e delle posizioni (JSON)
# ============================================================

from pathlib import Path
from typing import List, Dict, Optional
import json
from ..impostazioni_e_costanti_di_simulazione import Cella, STAZIONE

def trova_primo_file_esistente(candidati: List[Path]) -> Optional[str]:
    """Ritorna il primo path esistente tra i candidati."""
    for p in candidati:
        if p.exists() and p.is_file():
            return str(p)
    return None

def leggi_azioni_piano_fast_downward(percorso_file: str) -> List[str]:
    """Estrae solo le azioni tra parentesi dal piano Fast Downward."""
    azioni: List[str] = []
    with open(percorso_file, "r", encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith(";"):
                continue
            if "(" in s and ")" in s:
                s = s[:s.rfind(")") + 1]
            if s.startswith("(") and s.endswith(")"):
                azioni.append(s.lower())
    if not azioni:
        raise ValueError(f"Nessuna azione valida nel piano: {percorso_file}")
    return azioni

def carica_mappa_posizioni_da_json(percorso_file: str) -> Dict[str, Cella]:
    """Carica mappa 'etichetta -> (x,y)' da JSON. Aggiunge 'st' = STAZIONE."""
    with open(percorso_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    posizioni: Dict[str, Cella] = {}
    for k, v in data.items():
        if k.lower() == "st":
            continue
        posizioni[k.lower()] = (int(v[0]), int(v[1]))
    posizioni["st"] = STAZIONE
    return posizioni
