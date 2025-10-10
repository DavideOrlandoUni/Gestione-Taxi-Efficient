import json
from pathlib import Path
from ..configurazione.costanti import STAZIONE

def trova_primo_file_esistente(lista_candidati):
    for candidato in lista_candidati:
        percorso = Path(candidato)
        if percorso.exists() and percorso.is_file():
            return str(percorso)
    return None

def leggi_azioni_da_piano(percorso_file):
    azioni = []
    
    try:
        with open(percorso_file, "r", encoding="utf-8") as file:
            for numero_riga, riga in enumerate(file, 1):
                riga = riga.strip()
                
                if not riga or riga.startswith(";"):
                    continue
                
                if "(" in riga and ")" in riga:
                    riga = riga[:riga.rfind(")") + 1]
                
                if riga.startswith("(") and riga.endswith(")"):
                    azioni.append(riga.lower())
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File piano non trovato: {percorso_file}")
    except Exception as e:
        raise ValueError(f"Errore durante la lettura del file piano {percorso_file}: {e}")
    
    if not azioni:
        raise ValueError(f"Nessuna azione valida trovata nel file: {percorso_file}")
    
    return azioni


def carica_posizioni_da_json(percorso_file):
    try:
        with open(percorso_file, "r", encoding="utf-8") as file:          
            dati = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File posizioni non trovato: {percorso_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"File JSON non valido {percorso_file}: {e}")
    except Exception as e:
        raise ValueError(f"Errore durante la lettura del file posizioni {percorso_file}: {e}")
    
    if not isinstance(dati, dict):
        raise ValueError(f"Il file JSON deve contenere un oggetto, trovato: {type(dati)}")
    
    posizioni = {}
    
    for etichetta, coordinate in dati.items():
        if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
            continue
        
        try:
            x, y = int(coordinate[0]), int(coordinate[1])
            etichetta_lower = etichetta.lower()
            
            if etichetta_lower == "st":
                continue
                
            posizioni[etichetta_lower] = (x, y)
        except (ValueError, TypeError):
            continue
    
    posizioni["st"] = STAZIONE
    
    if not posizioni:
        raise ValueError(f"Nessuna posizione valida trovata nel file: {percorso_file}")
    
    return posizioni


def estrai_prima_mappatura_pickup(lista_azioni):
    mappa_pickup = {}
    
    for azione_raw in lista_azioni:
        tokens = azione_raw.strip("()").split()
        
        if len(tokens) == 4 and tokens[0] == "pickup":
            _, taxi, passeggero, location = tokens
            
            passeggero_upper = passeggero.upper()
            location_lower = location.lower()
            
            if passeggero_upper not in mappa_pickup:
                mappa_pickup[passeggero_upper] = location_lower
    
    return mappa_pickup
