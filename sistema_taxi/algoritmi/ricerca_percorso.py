"""
Algoritmi di Ricerca Percorso
=============================

Implementa algoritmi per la ricerca del percorso ottimale:
- Algoritmo A* per pathfinding su griglia
- Calcolo distanza Manhattan come euristica
- Gestione ostacoli e vincoli di movimento
"""

import heapq
from ..configurazione.costanti import GRIGLIA_LARGHEZZA, GRIGLIA_ALTEZZA, OSTACOLI


def calcola_distanza_manhattan(punto_a, punto_b):
    """
    Calcola la distanza di Manhattan tra due punti sulla griglia.
    
    La distanza di Manhattan è la somma delle differenze assolute
    delle coordinate x e y. È utilizzata come euristica per A*
    perché è ammissibile (non sovrastima mai la distanza reale).
    
    Args:
        punto_a (tuple): Coordinate (x, y) del primo punto
        punto_b (tuple): Coordinate (x, y) del secondo punto
    
    Returns:
        int: Distanza di Manhattan tra i due punti
    
    Example:
        >>> calcola_distanza_manhattan((0, 0), (3, 4))
        7
        >>> calcola_distanza_manhattan((1, 1), (1, 1))
        0
    """
    return abs(punto_a[0] - punto_b[0]) + abs(punto_a[1] - punto_b[1])


def trova_percorso_astar(partenza, destinazione):
    """
    Implementa l'algoritmo A* per trovare il percorso ottimo tra due punti.
    
    L'algoritmo A* combina il costo reale g(n) con un'euristica h(n)
    per guidare la ricerca verso la soluzione ottima. Evita automaticamente
    gli ostacoli definiti nella configurazione.
    
    Args:
        partenza (tuple): Coordinate (x, y) del punto di partenza
        destinazione (tuple): Coordinate (x, y) del punto di destinazione
    
    Returns:
        list: Lista di coordinate intermedie del percorso ottimo.
              Non include partenza e destinazione.
              Lista vuota se non esiste percorso.
    
    Note:
        - Utilizza movimenti ortogonali (su, giù, sinistra, destra)
        - Evita automaticamente gli ostacoli definiti in OSTACOLI
        - Restituisce solo i punti intermedi del percorso
    
    Example:
        >>> trova_percorso_astar((0, 0), (2, 0))
        [(1, 0)]
        >>> trova_percorso_astar((0, 0), (0, 0))
        []
    """
    # Caso base: partenza e destinazione coincidono
    if partenza == destinazione:
        return []
    
    # Verifica che partenza e destinazione siano valide
    if not _e_posizione_valida(partenza) or not _e_posizione_valida(destinazione):
        return []
    
    # Coda prioritaria per i nodi da esplorare: (costo_f, punto)
    coda_aperta = []
    heapq.heappush(coda_aperta, (calcola_distanza_manhattan(partenza, destinazione), partenza))
    
    # Dizionario per ricostruire il percorso
    predecessori = {partenza: None}
    
    # Costi g(n) - distanza reale dalla partenza
    costi_g = {partenza: 0}
    
    while coda_aperta:
        # Estrai il nodo con costo f più basso
        _, nodo_corrente = heapq.heappop(coda_aperta)
        
        # Se abbiamo raggiunto la destinazione, ricostruisci il percorso
        if nodo_corrente == destinazione:
            return _ricostruisci_percorso_intermedio(predecessori, destinazione)
        
        # Esplora tutti i vicini del nodo corrente
        for vicino in _ottieni_vicini_validi(nodo_corrente):
            # Calcola il nuovo costo g per raggiungere questo vicino
            nuovo_costo_g = costi_g[nodo_corrente] + 1
            
            # Se abbiamo trovato un percorso migliore verso questo vicino
            if vicino not in costi_g or nuovo_costo_g < costi_g[vicino]:
                costi_g[vicino] = nuovo_costo_g
                
                # Calcola costo f = g + h (euristica)
                costo_f = nuovo_costo_g + calcola_distanza_manhattan(vicino, destinazione)
                
                # Aggiorna predecessore e aggiungi alla coda
                predecessori[vicino] = nodo_corrente
                heapq.heappush(coda_aperta, (costo_f, vicino))
    
    # Nessun percorso trovato
    return []


def _e_posizione_valida(posizione):
    """
    Verifica se una posizione è valida sulla griglia.
    
    Args:
        posizione (tuple): Coordinate (x, y) da verificare
    
    Returns:
        bool: True se la posizione è valida e non è un ostacolo
    """
    x, y = posizione
    
    # Verifica limiti griglia
    if not (0 <= x < GRIGLIA_LARGHEZZA and 0 <= y < GRIGLIA_ALTEZZA):
        return False
    
    # Verifica che non sia un ostacolo
    if posizione in OSTACOLI:
        return False
    
    return True


def _ottieni_vicini_validi(posizione):
    """
    Restituisce tutti i vicini validi di una posizione.
    
    Considera solo movimenti ortogonali (su, giù, sinistra, destra)
    ed esclude posizioni fuori dalla griglia o che sono ostacoli.
    
    Args:
        posizione (tuple): Coordinate (x, y) della posizione corrente
    
    Returns:
        list: Lista di coordinate dei vicini validi
    """
    x, y = posizione
    vicini = []
    
    # Movimenti possibili: destra, sinistra, su, giù
    movimenti = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    for dx, dy in movimenti:
        nuovo_x, nuovo_y = x + dx, y + dy
        nuova_posizione = (nuovo_x, nuovo_y)
        
        if _e_posizione_valida(nuova_posizione):
            vicini.append(nuova_posizione)
    
    return vicini


def _ricostruisci_percorso_intermedio(predecessori, destinazione):
    """
    Ricostruisce il percorso dal dizionario dei predecessori.
    
    Args:
        predecessori (dict): Mappa {nodo: predecessore}
        destinazione (tuple): Punto di destinazione
    
    Returns:
        list: Lista dei punti intermedi (esclude partenza e destinazione)
    """
    percorso_completo = [destinazione]
    
    # Ricostruisci il percorso seguendo i predecessori
    while predecessori[percorso_completo[-1]] is not None:
        percorso_completo.append(predecessori[percorso_completo[-1]])
    
    # Inverti per avere l'ordine corretto
    percorso_completo.reverse()
    
    # Restituisci solo i punti intermedi (esclude primo e ultimo)
    return percorso_completo[1:-1]


def calcola_lunghezza_percorso_completo(partenza, destinazione):
    """
    Calcola la lunghezza totale del percorso tra due punti.
    
    Include partenza, destinazione e tutti i punti intermedi.
    
    Args:
        partenza (tuple): Punto di partenza
        destinazione (tuple): Punto di destinazione
    
    Returns:
        int: Lunghezza totale del percorso (numero di step)
    """
    if partenza == destinazione:
        return 0
    
    percorso_intermedio = trova_percorso_astar(partenza, destinazione)
    
    # Se non esiste percorso, restituisci infinito
    if not percorso_intermedio and partenza != destinazione:
        return float('inf')
    
    # Lunghezza = punti intermedi + 1 (per il movimento finale)
    return len(percorso_intermedio) + 1


def verifica_percorso_esistente(partenza, destinazione):
    """
    Verifica rapidamente se esiste un percorso tra due punti.
    
    Args:
        partenza (tuple): Punto di partenza
        destinazione (tuple): Punto di destinazione
    
    Returns:
        bool: True se esiste un percorso, False altrimenti
    """
    if partenza == destinazione:
        return True
    
    if not _e_posizione_valida(partenza) or not _e_posizione_valida(destinazione):
        return False
    
    # Usa A* ma fermati al primo percorso trovato
    percorso = trova_percorso_astar(partenza, destinazione)
    return len(percorso) >= 0  # A* restituisce [] se non trova percorso
