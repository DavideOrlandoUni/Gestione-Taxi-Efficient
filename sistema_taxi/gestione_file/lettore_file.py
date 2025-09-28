"""
Lettore File
============

Gestisce la lettura e il parsing di file esterni:
- File piani Fast Downward (.txt)
- File posizioni JSON (.json)
- Utilità per la ricerca file
"""

import json
from pathlib import Path
from ..configurazione.costanti import STAZIONE


def trova_primo_file_esistente(lista_candidati):
    """
    Trova il primo file esistente tra una lista di candidati.
    
    Utile per cercare file in percorsi alternativi o con nomi diversi.
    
    Args:
        lista_candidati (list): Lista di percorsi candidati (str o Path)
    
    Returns:
        str o None: Percorso del primo file esistente, None se nessuno esiste
    
    Example:
        >>> candidati = ["piano1.txt", "backup/piano1.txt", "piani/piano1.txt"]
        >>> percorso = trova_primo_file_esistente(candidati)
        >>> print(percorso)  # "backup/piano1.txt" (se esiste)
    """
    for candidato in lista_candidati:
        percorso = Path(candidato)
        if percorso.exists() and percorso.is_file():
            return str(percorso)
    return None


def leggi_azioni_da_piano(percorso_file):
    """
    Legge le azioni da un file di piano Fast Downward.
    
    Estrae solo le righe che contengono azioni valide (racchiuse tra parentesi)
    ignorando commenti (righe che iniziano con ';') e righe vuote.
    
    Args:
        percorso_file (str): Percorso del file di piano
    
    Returns:
        list: Lista delle azioni estratte in formato lowercase
    
    Raises:
        FileNotFoundError: Se il file non esiste
        ValueError: Se non vengono trovate azioni valide
    
    Example:
        File piano.txt:
        ```
        ; Piano generato da Fast Downward
        (move taxi1 st l1)
        (pickup taxi1 p1 l1)
        (move taxi1 l1 st)
        ```
        
        >>> azioni = leggi_azioni_da_piano("piano.txt")
        >>> print(azioni)
        ['(move taxi1 st l1)', '(pickup taxi1 p1 l1)', '(move taxi1 l1 st)']
    """
    azioni = []
    
    try:
        with open(percorso_file, "r", encoding="utf-8") as file:
            for numero_riga, riga in enumerate(file, 1):
                riga = riga.strip()
                
                # Salta righe vuote e commenti
                if not riga or riga.startswith(";"):
                    continue
                
                # Estrai azione tra parentesi
                if "(" in riga and ")" in riga:
                    # Trova l'ultima parentesi chiusa per gestire righe con testo extra
                    riga = riga[:riga.rfind(")") + 1]
                
                # Verifica che sia un'azione valida
                if riga.startswith("(") and riga.endswith(")"):
                    azioni.append(riga.lower())
                elif riga:  # Riga non vuota ma non valida
                    print(f"[WARNING] Riga {numero_riga} ignorata (formato non valido): {riga}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File piano non trovato: {percorso_file}")
    except Exception as e:
        raise ValueError(f"Errore durante la lettura del file piano {percorso_file}: {e}")
    
    if not azioni:
        raise ValueError(f"Nessuna azione valida trovata nel file: {percorso_file}")
    
    return azioni


def carica_posizioni_da_json(percorso_file):
    """
    Carica le posizioni dei clienti da un file JSON.
    
    Il file deve contenere una mappa etichetta -> [x, y].
    Aggiunge automaticamente la stazione come 'st' se non presente.
    
    Args:
        percorso_file (str): Percorso del file JSON
    
    Returns:
        dict: Mappa {etichetta_lowercase: (x, y)}
    
    Raises:
        FileNotFoundError: Se il file non esiste
        ValueError: Se il file JSON non è valido o ha formato errato
    
    Example:
        File locations.json:
        ```json
        {
            "L1": [2, 3],
            "L2": [5, 7],
            "ST": [0, 9]
        }
        ```
        
        >>> posizioni = carica_posizioni_da_json("locations.json")
        >>> print(posizioni)
        {'l1': (2, 3), 'l2': (5, 7), 'st': (0, 9)}
    """
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
    
    # Converti le posizioni dal JSON
    for etichetta, coordinate in dati.items():
        if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
            print(f"[WARNING] Coordinate non valide per {etichetta}: {coordinate}")
            continue
        
        try:
            x, y = int(coordinate[0]), int(coordinate[1])
            etichetta_lower = etichetta.lower()
            
            # Salta la stazione se già presente, verrà aggiunta dopo
            if etichetta_lower == "st":
                continue
                
            posizioni[etichetta_lower] = (x, y)
        except (ValueError, TypeError):
            print(f"[WARNING] Impossibile convertire coordinate per {etichetta}: {coordinate}")
            continue
    
    # Aggiungi sempre la stazione
    posizioni["st"] = STAZIONE
    
    if not posizioni:
        raise ValueError(f"Nessuna posizione valida trovata nel file: {percorso_file}")
    
    return posizioni


def estrai_prima_mappatura_pickup(lista_azioni):
    """
    Estrae la prima associazione passeggero -> location dalle azioni pickup.
    
    Utile per identificare dove ogni passeggero deve essere prelevato
    la prima volta, ignorando eventuali pickup successivi.
    
    Args:
        lista_azioni (list): Lista di azioni SAS
    
    Returns:
        dict: Mappa {passeggero_uppercase: location_lowercase}
    
    Example:
        >>> azioni = [
        ...     "(move taxi1 st l1)",
        ...     "(pickup taxi1 p1 l1)",
        ...     "(pickup taxi1 p2 l2)",
        ...     "(pickup taxi1 p1 l3)"  # Ignorato (p1 già mappato)
        ... ]
        >>> mappa = estrai_prima_mappatura_pickup(azioni)
        >>> print(mappa)
        {'P1': 'l1', 'P2': 'l2'}
    """
    mappa_pickup = {}
    
    for azione_raw in lista_azioni:
        tokens = azione_raw.strip("()").split()
        
        # Verifica che sia un'azione pickup valida
        if len(tokens) == 4 and tokens[0] == "pickup":
            _, taxi, passeggero, location = tokens
            
            passeggero_upper = passeggero.upper()
            location_lower = location.lower()
            
            # Registra solo la prima occorrenza di ogni passeggero
            if passeggero_upper not in mappa_pickup:
                mappa_pickup[passeggero_upper] = location_lower
    
    return mappa_pickup


def valida_file_piano(percorso_file):
    """
    Valida che un file di piano sia leggibile e contenga azioni valide.
    
    Args:
        percorso_file (str): Percorso del file da validare
    
    Returns:
        tuple: (valido, messaggio_errore)
            - valido (bool): True se il file è valido
            - messaggio_errore (str): Descrizione dell'errore se non valido
    """
    try:
        azioni = leggi_azioni_da_piano(percorso_file)
        
        if not azioni:
            return False, "File vuoto o senza azioni valide"
        
        # Verifica che ci siano azioni di base
        tipi_azioni = set()
        for azione in azioni:
            tokens = azione.strip("()").split()
            if tokens:
                tipi_azioni.add(tokens[0])
        
        if not tipi_azioni:
            return False, "Nessun tipo di azione riconosciuto"
        
        return True, f"File valido con {len(azioni)} azioni ({', '.join(sorted(tipi_azioni))})"
    
    except Exception as e:
        return False, str(e)


def valida_file_posizioni(percorso_file):
    """
    Valida che un file di posizioni sia leggibile e contenga dati validi.
    
    Args:
        percorso_file (str): Percorso del file da validare
    
    Returns:
        tuple: (valido, messaggio_errore)
            - valido (bool): True se il file è valido
            - messaggio_errore (str): Descrizione dell'errore se non valido
    """
    try:
        posizioni = carica_posizioni_da_json(percorso_file)
        
        if not posizioni:
            return False, "File vuoto o senza posizioni valide"
        
        # Verifica che ci sia almeno una posizione oltre alla stazione
        posizioni_clienti = {k: v for k, v in posizioni.items() if k != "st"}
        
        if not posizioni_clienti:
            return False, "Nessuna posizione cliente trovata"
        
        return True, f"File valido con {len(posizioni_clienti)} posizioni clienti"
    
    except Exception as e:
        return False, str(e)


def stampa_errore_sicuro(prefisso, errore):
    """
    Stampa errori in modo sicuro anche su console non-UTF.
    
    Gestisce automaticamente problemi di encoding che possono verificarsi
    su sistemi con configurazioni console diverse.
    
    Args:
        prefisso (str): Stringa di prefisso per l'errore
        errore (Exception): Oggetto Exception da stampare
    """
    try:
        print(f"{prefisso}{errore}")
    except UnicodeEncodeError:
        # Fallback per console che non supportano UTF-8
        print(f"{prefisso}{repr(errore)}")
    except Exception:
        # Fallback estremo
        print(f"{prefisso}[Errore non visualizzabile]")
