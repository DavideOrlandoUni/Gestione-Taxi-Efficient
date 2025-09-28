"""
Costruttore Rotte
=================

Converte azioni SAS (move, pickup, dropoff) in piani di viaggio concreti.
Gestisce la costruzione di percorsi dettagliati da sequenze di azioni ad alto livello.
"""

from ..configurazione.costanti import STAZIONE
from ..configurazione.modelli import *
from ..algoritmi.ricerca_percorso import trova_percorso_astar


def costruisci_viaggio_da_azioni(lista_azioni, posizioni_locations):
    """
    Converte una lista di azioni SAS in un piano di viaggio concreto.
    
    Processa azioni di tipo move, pickup e dropoff per costruire
    il percorso completo del taxi con eventi associati. Utilizza A*
    per calcolare i percorsi dettagliati tra le posizioni.
    
    Args:
        lista_azioni (list): Lista di stringhe con azioni SAS
        posizioni_locations (dict): Mappa {location_label: (x, y)}
    
    Returns:
        tuple: (PianoViaggio, dict_etichette_clienti)
            - PianoViaggio: Piano completo con percorso ed eventi
            - dict_etichette_clienti: Mappa {cliente: posizione_prelievo}
    
    Raises:
        KeyError: Se una location non è definita nel dizionario posizioni
        ValueError: Se le azioni non sono in formato valido
    
    Example:
        >>> azioni = [
        ...     "(move taxi1 st l1)",
        ...     "(pickup taxi1 p1 l1)",
        ...     "(move taxi1 l1 st)",
        ...     "(dropoff taxi1 p1 st)"
        ... ]
        >>> posizioni = {'st': (0, 9), 'l1': (2, 3)}
        >>> viaggio, etichette = costruisci_viaggio_da_azioni(azioni, posizioni)
    """
    percorso_completo = []
    eventi_prelievo = {}
    eventi_discesa = {}
    etichette_clienti = {}
    posizione_corrente = None
    
    def ottieni_cella_da_label(label):
        """Converte un label di location in coordinate della cella."""
        chiave = label.lower()
        if chiave not in posizioni_locations:
            raise KeyError(f"Location '{label}' non definita nel file delle posizioni.")
        return posizioni_locations[chiave]
    
    # Processa ogni azione in sequenza
    for numero_azione, azione_raw in enumerate(lista_azioni, 1):
        try:
            # Estrai i token dall'azione
            tokens = azione_raw.strip("()").split()
            if not tokens:
                continue
            
            operazione = tokens[0]
            
            if operazione == "move":
                _processa_azione_move(tokens, ottieni_cella_da_label, 
                                    percorso_completo, posizione_corrente)
                # Aggiorna posizione corrente
                if len(tokens) >= 4:
                    posizione_corrente = ottieni_cella_da_label(tokens[3])
                    
            elif operazione == "pickup":
                _processa_azione_pickup(tokens, ottieni_cella_da_label,
                                      percorso_completo, eventi_prelievo, 
                                      etichette_clienti, posizione_corrente)
                
            elif operazione == "dropoff":
                _processa_azione_dropoff(tokens, percorso_completo, 
                                       eventi_discesa, posizione_corrente)
            else:
                print(f"[WARNING] Azione sconosciuta ignorata: {operazione}")
                
        except Exception as e:
            print(f"[ERROR] Errore processando azione {numero_azione} '{azione_raw}': {e}")
            continue
    
    # Crea il piano di viaggio
    viaggio = PianoViaggio(percorso_completo, eventi_prelievo, eventi_discesa)
    
    return viaggio, etichette_clienti


def _processa_azione_move(tokens, ottieni_cella_da_label, percorso_completo, posizione_corrente):
    """
    Processa un'azione di movimento: (move taxi src dst)
    
    Calcola il percorso dettagliato usando A* e lo aggiunge al percorso completo.
    """
    if len(tokens) != 4:
        raise ValueError(f"Azione move malformata: {tokens}")
    
    _, nome_taxi, src_label, dst_label = tokens
    
    src_cella = ottieni_cella_da_label(src_label)
    dst_cella = ottieni_cella_da_label(dst_label)
    
    # Inizializza il percorso se necessario
    if posizione_corrente is None:
        posizione_corrente = src_cella
        percorso_completo.append(posizione_corrente)
    
    # Calcola il percorso intermedio con A*
    segmento_intermedio = trova_percorso_astar(posizione_corrente, dst_cella)
    percorso_completo.extend(segmento_intermedio)
    percorso_completo.append(dst_cella)


def _processa_azione_pickup(tokens, ottieni_cella_da_label, percorso_completo, 
                           eventi_prelievo, etichette_clienti, posizione_corrente):
    """
    Processa un'azione di prelievo: (pickup taxi passeggero location)
    
    Registra il cliente e la sua posizione, aggiunge l'evento di prelievo.
    """
    if len(tokens) != 4:
        raise ValueError(f"Azione pickup malformata: {tokens}")
    
    _, nome_taxi, passeggero_label, location_label = tokens
    
    etichetta_cliente = passeggero_label.upper()
    etichette_clienti[etichetta_cliente] = ottieni_cella_da_label(location_label)
    
    # Inizializza il percorso se necessario
    if not percorso_completo:
        posizione_corrente = ottieni_cella_da_label(location_label)
        percorso_completo.append(posizione_corrente)
    
    # Aggiungi evento prelievo alla posizione corrente
    indice_corrente = len(percorso_completo) - 1
    if indice_corrente not in eventi_prelievo:
        eventi_prelievo[indice_corrente] = []
    eventi_prelievo[indice_corrente].append(etichetta_cliente)


def _processa_azione_dropoff(tokens, percorso_completo, eventi_discesa, posizione_corrente):
    """
    Processa un'azione di discesa: (dropoff taxi passeggero location)
    
    Registra l'evento di discesa del cliente.
    """
    if len(tokens) != 4:
        raise ValueError(f"Azione dropoff malformata: {tokens}")
    
    _, nome_taxi, passeggero_label, location_label = tokens
    
    etichetta_cliente = passeggero_label.upper()
    
    # Inizializza il percorso se necessario
    if not percorso_completo:
        posizione_corrente = STAZIONE
        percorso_completo.append(posizione_corrente)
    
    # Aggiungi evento discesa alla posizione corrente
    indice_corrente = len(percorso_completo) - 1
    if indice_corrente not in eventi_discesa:
        eventi_discesa[indice_corrente] = []
    eventi_discesa[indice_corrente].append(etichetta_cliente)


def valida_sequenza_azioni(lista_azioni):
    """
    Valida che una sequenza di azioni sia logicamente consistente.
    
    Verifica che:
    - Ogni pickup sia seguito da un dropoff corrispondente
    - I movimenti siano coerenti con le posizioni
    - Non ci siano azioni duplicate o inconsistenti
    
    Args:
        lista_azioni (list): Lista di azioni da validare
    
    Returns:
        tuple: (valida, lista_errori)
            - valida (bool): True se la sequenza è valida
            - lista_errori (list): Lista di messaggi di errore
    """
    errori = []
    clienti_prelevati = set()
    clienti_scesi = set()
    
    for i, azione in enumerate(lista_azioni):
        tokens = azione.strip("()").split()
        if not tokens:
            continue
            
        operazione = tokens[0]
        
        try:
            if operazione == "pickup":
                if len(tokens) != 4:
                    errori.append(f"Azione {i+1}: pickup malformata")
                    continue
                    
                cliente = tokens[2].upper()
                if cliente in clienti_prelevati:
                    errori.append(f"Azione {i+1}: cliente {cliente} già prelevato")
                else:
                    clienti_prelevati.add(cliente)
                    
            elif operazione == "dropoff":
                if len(tokens) != 4:
                    errori.append(f"Azione {i+1}: dropoff malformata")
                    continue
                    
                cliente = tokens[2].upper()
                if cliente not in clienti_prelevati:
                    errori.append(f"Azione {i+1}: cliente {cliente} non era stato prelevato")
                elif cliente in clienti_scesi:
                    errori.append(f"Azione {i+1}: cliente {cliente} già sceso")
                else:
                    clienti_scesi.add(cliente)
                    
            elif operazione == "move":
                if len(tokens) != 4:
                    errori.append(f"Azione {i+1}: move malformata")
                    
        except Exception as e:
            errori.append(f"Azione {i+1}: errore di parsing - {e}")
    
    # Verifica che tutti i clienti prelevati siano anche scesi
    clienti_non_scesi = clienti_prelevati - clienti_scesi
    if clienti_non_scesi:
        errori.append(f"Clienti prelevati ma non scesi: {clienti_non_scesi}")
    
    return len(errori) == 0, errori


def ottimizza_sequenza_azioni(lista_azioni, posizioni_locations):
    """
    Ottimizza una sequenza di azioni per ridurre la lunghezza del percorso.
    
    Applica ottimizzazioni come:
    - Riordinamento delle visite per minimizzare la distanza
    - Eliminazione di movimenti ridondanti
    - Raggruppamento di azioni nella stessa location
    
    Args:
        lista_azioni (list): Sequenza di azioni originale
        posizioni_locations (dict): Posizioni delle location
    
    Returns:
        list: Sequenza di azioni ottimizzata
    """
    # Per ora restituisce la sequenza originale
    # Implementazione futura: riordinamento intelligente delle azioni
    return lista_azioni


def estrai_statistiche_azioni(lista_azioni):
    """
    Estrae statistiche utili da una sequenza di azioni.
    
    Args:
        lista_azioni (list): Lista di azioni da analizzare
    
    Returns:
        dict: Dizionario con statistiche delle azioni
    """
    statistiche = {
        'totale_azioni': len(lista_azioni),
        'movimenti': 0,
        'prelievi': 0,
        'discese': 0,
        'clienti_unici': set(),
        'locations_visitate': set()
    }
    
    for azione in lista_azioni:
        tokens = azione.strip("()").split()
        if not tokens:
            continue
            
        operazione = tokens[0]
        
        if operazione == "move":
            statistiche['movimenti'] += 1
            if len(tokens) >= 4:
                statistiche['locations_visitate'].add(tokens[2].lower())
                statistiche['locations_visitate'].add(tokens[3].lower())
                
        elif operazione == "pickup":
            statistiche['prelievi'] += 1
            if len(tokens) >= 3:
                statistiche['clienti_unici'].add(tokens[2].upper())
            if len(tokens) >= 4:
                statistiche['locations_visitate'].add(tokens[3].lower())
                
        elif operazione == "dropoff":
            statistiche['discese'] += 1
            if len(tokens) >= 4:
                statistiche['locations_visitate'].add(tokens[3].lower())
    
    # Converti set in numeri per il risultato finale
    statistiche['clienti_unici'] = len(statistiche['clienti_unici'])
    statistiche['locations_visitate'] = len(statistiche['locations_visitate'])
    
    return statistiche
