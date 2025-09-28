"""
Gestore Taxi
============

Implementa la logica di pianificazione per taxi singoli, condivisi e multi-taxi.
Gestisce l'ottimizzazione dei percorsi e l'assegnazione dei clienti.
"""

import heapq
from ..configurazione.costanti import STAZIONE, TAXI_SINGOLO, TAXI_CONDIVISO, DEBUG
from ..configurazione.modelli import PianoTaxi, PianoMultiTaxi
from ..algoritmi.ricerca_percorso import trova_percorso_astar, calcola_distanza_manhattan
from ..algoritmi.ottimizzazione import trova_coppie_clienti_per_raggio, stampa_debug_coppie_candidate


def pianifica_taxi_singolo_greedy(lista_clienti, posizioni_clienti):
    """
    Pianifica il percorso per un taxi singolo usando strategia greedy.
    
    Il taxi visita iterativamente il cliente più vicino alla sua posizione
    corrente, lo porta alla stazione, e ripete fino a servire tutti i clienti.
    Questa è una soluzione approssimata al problema del commesso viaggiatore.
    
    Args:
        lista_clienti (list): Lista delle etichette dei clienti da servire
        posizioni_clienti (dict): Mappa {etichetta: posizione}
    
    Returns:
        PianoTaxi: Piano completo per il taxi singolo
    
    Example:
        >>> clienti = ['A', 'B', 'C']
        >>> posizioni = {'A': (1, 1), 'B': (3, 3), 'C': (2, 1)}
        >>> piano = pianifica_taxi_singolo_greedy(clienti, posizioni)
        >>> print(len(piano.percorso))  # Lunghezza del percorso
    """
    if not lista_clienti:
        return PianoTaxi([STAZIONE], {}, {})
    
    posizione_corrente = STAZIONE
    percorso_completo = [STAZIONE]
    eventi_prelievo = {}
    eventi_discesa = {}
    
    clienti_rimanenti = set(lista_clienti)
    
    while clienti_rimanenti:
        # Trova il cliente più vicino alla posizione corrente usando heap
        heap_distanze = []
        for cliente in clienti_rimanenti:
            distanza = calcola_distanza_manhattan(posizione_corrente, posizioni_clienti[cliente])
            heapq.heappush(heap_distanze, (distanza, cliente))
        
        _, cliente_piu_vicino = heapq.heappop(heap_distanze)
        posizione_cliente = posizioni_clienti[cliente_piu_vicino]
        
        # Vai dal cliente (se non siamo già lì)
        if posizione_corrente != posizione_cliente:
            segmento_andata = trova_percorso_astar(posizione_corrente, posizione_cliente)
            percorso_completo.extend(segmento_andata)
            percorso_completo.append(posizione_cliente)
        
        # Registra evento prelievo
        indice_prelievo = len(percorso_completo) - 1
        eventi_prelievo[indice_prelievo] = [cliente_piu_vicino]
        
        # Torna alla stazione (se non siamo già lì)
        if posizione_cliente != STAZIONE:
            segmento_ritorno = trova_percorso_astar(posizione_cliente, STAZIONE)
            percorso_completo.extend(segmento_ritorno)
            percorso_completo.append(STAZIONE)
        
        # Registra evento discesa
        indice_discesa = len(percorso_completo) - 1
        eventi_discesa[indice_discesa] = [cliente_piu_vicino]
        
        # Aggiorna stato
        posizione_corrente = STAZIONE
        clienti_rimanenti.remove(cliente_piu_vicino)
    
    if DEBUG:
        print(f"[DEBUG] Piano taxi singolo: {len(lista_clienti)} clienti, {len(percorso_completo)} step")
    
    return PianoTaxi(percorso_completo, eventi_prelievo, eventi_discesa)


def pianifica_taxi_condiviso_coppie(coppie_clienti, clienti_singoli, posizioni_clienti):
    """
    Pianifica il percorso per un taxi condiviso che serve coppie di clienti.
    
    Il taxi raccoglie prima il cliente più vicino alla stazione di ogni coppia,
    poi l'altro cliente, e infine li porta entrambi alla stazione.
    Dopo le coppie, serve eventuali clienti singoli rimasti.
    
    Args:
        coppie_clienti (list): Lista di tuple (cliente_a, cliente_b)
        clienti_singoli (list): Lista di clienti senza coppia
        posizioni_clienti (dict): Mappa {etichetta: posizione}
    
    Returns:
        PianoTaxi: Piano completo per il taxi condiviso
    
    Example:
        >>> coppie = [('A', 'B'), ('C', 'D')]
        >>> singoli = ['E']
        >>> posizioni = {'A': (1, 1), 'B': (1, 2), 'C': (3, 3), 'D': (3, 4), 'E': (5, 5)}
        >>> piano = pianifica_taxi_condiviso_coppie(coppie, singoli, posizioni)
    """
    percorso_completo = [STAZIONE]
    eventi_prelievo = {}
    eventi_discesa = {}
    
    # Ordina le coppie per distanza interna crescente (coppie più "compatte" prima)
    coppie_ordinate = sorted(coppie_clienti, key=lambda coppia: 
        calcola_distanza_manhattan(posizioni_clienti[coppia[0]], posizioni_clienti[coppia[1]])
    )
    
    # Servi ogni coppia
    for cliente_a, cliente_b in coppie_ordinate:
        _servi_coppia_clienti(cliente_a, cliente_b, posizioni_clienti, 
                             percorso_completo, eventi_prelievo, eventi_discesa)
    
    # Servi i clienti singoli rimasti
    for cliente in clienti_singoli:
        _servi_cliente_singolo(cliente, posizioni_clienti, 
                              percorso_completo, eventi_prelievo, eventi_discesa)
    
    if DEBUG:
        print(f"[DEBUG] Piano taxi condiviso: {len(coppie_clienti)} coppie, {len(clienti_singoli)} singoli, {len(percorso_completo)} step")
    
    return PianoTaxi(percorso_completo, eventi_prelievo, eventi_discesa)


def _servi_coppia_clienti(cliente_a, cliente_b, posizioni_clienti, 
                         percorso_completo, eventi_prelievo, eventi_discesa):
    """
    Serve una coppia di clienti ottimizzando l'ordine di prelievo.
    
    Preleva prima il cliente più vicino alla stazione per minimizzare
    il tempo di attesa del secondo cliente.
    """
    pos_a = posizioni_clienti[cliente_a]
    pos_b = posizioni_clienti[cliente_b]
    
    # Determina l'ordine di prelievo (prima il più vicino alla stazione)
    dist_a_stazione = calcola_distanza_manhattan(pos_a, STAZIONE)
    dist_b_stazione = calcola_distanza_manhattan(pos_b, STAZIONE)
    
    if dist_b_stazione < dist_a_stazione:
        primo_cliente, pos_primo = cliente_b, pos_b
        secondo_cliente, pos_secondo = cliente_a, pos_a
    else:
        primo_cliente, pos_primo = cliente_a, pos_a
        secondo_cliente, pos_secondo = cliente_b, pos_b
    
    # Vai al primo cliente
    segmento = trova_percorso_astar(STAZIONE, pos_primo)
    percorso_completo.extend(segmento)
    percorso_completo.append(pos_primo)
    eventi_prelievo[len(percorso_completo) - 1] = [primo_cliente]
    
    # Vai al secondo cliente
    segmento = trova_percorso_astar(pos_primo, pos_secondo)
    percorso_completo.extend(segmento)
    percorso_completo.append(pos_secondo)
    
    # Aggiungi secondo cliente agli eventi prelievo
    indice_secondo = len(percorso_completo) - 1
    if indice_secondo not in eventi_prelievo:
        eventi_prelievo[indice_secondo] = []
    eventi_prelievo[indice_secondo].append(secondo_cliente)
    
    # Torna alla stazione
    segmento = trova_percorso_astar(pos_secondo, STAZIONE)
    percorso_completo.extend(segmento)
    percorso_completo.append(STAZIONE)
    eventi_discesa[len(percorso_completo) - 1] = [primo_cliente, secondo_cliente]


def _servi_cliente_singolo(cliente, posizioni_clienti, 
                          percorso_completo, eventi_prelievo, eventi_discesa):
    """
    Serve un cliente singolo nel taxi condiviso.
    """
    pos_cliente = posizioni_clienti[cliente]
    
    # Vai al cliente
    segmento = trova_percorso_astar(STAZIONE, pos_cliente)
    percorso_completo.extend(segmento)
    percorso_completo.append(pos_cliente)
    eventi_prelievo[len(percorso_completo) - 1] = [cliente]
    
    # Torna alla stazione
    segmento = trova_percorso_astar(pos_cliente, STAZIONE)
    percorso_completo.extend(segmento)
    percorso_completo.append(STAZIONE)
    
    indice_discesa = len(percorso_completo) - 1
    if indice_discesa not in eventi_discesa:
        eventi_discesa[indice_discesa] = []
    eventi_discesa[indice_discesa].append(cliente)


def costruisci_piani_taxi_singolo_e_condiviso(mappa_pickup_clienti, posizioni, raggio_coppia=2):
    """
    Costruisce piani separati per taxi singolo e condiviso.
    
    Il taxi singolo serve tutti i clienti singoli, mentre il taxi condiviso
    serve solo le coppie di clienti entro il raggio specificato.
    Questa è la strategia ottimale per il sistema multi-taxi.
    
    Args:
        mappa_pickup_clienti (dict): Mappa {cliente: location_label}
        posizioni (dict): Mappa {location_label: (x, y)}
        raggio_coppia (int): Raggio Manhattan per formare coppie
    
    Returns:
        PianoMultiTaxi: Piani per entrambi i taxi
    
    Example:
        >>> mappa = {'P1': 'l1', 'P2': 'l2', 'P3': 'l3', 'P4': 'l4'}
        >>> pos = {'l1': (1, 1), 'l2': (1, 2), 'l3': (5, 5), 'l4': (6, 6)}
        >>> piano_multi = costruisci_piani_taxi_singolo_e_condiviso(mappa, pos, 2)
        >>> print(piano_multi.ottieni_nomi_taxi())  # ['taxi_singolo', 'taxi_condiviso']
    """
    # Crea mappa etichette clienti -> posizioni
    etichette_clienti = {}
    for cliente, location_label in mappa_pickup_clienti.items():
        if location_label in posizioni:
            etichette_clienti[cliente] = posizioni[location_label]
    
    if not etichette_clienti:
        # Nessun cliente valido, crea piani vuoti
        piano_singolo = PianoTaxi([STAZIONE], {}, {})
        piano_condiviso = PianoTaxi([STAZIONE], {}, {})
        return PianoMultiTaxi({
            TAXI_SINGOLO: piano_singolo,
            TAXI_CONDIVISO: piano_condiviso
        }, etichette_clienti)
    
    # Trova coppie e clienti singoli
    coppie, clienti_singoli = trova_coppie_clienti_per_raggio(etichette_clienti, raggio_coppia)
    
    if DEBUG:
        stampa_debug_coppie_candidate(etichette_clienti, raggio_coppia)
        print(f"[DEBUG] Sistema multi-taxi:")
        print(f"        Raggio accoppiamento: Manhattan ≤ {raggio_coppia}")
        print(f"        Coppie per taxi condiviso: {coppie}")
        print(f"        Singoli per taxi singolo: {clienti_singoli}")
    
    # Crea piani per i due taxi
    piano_singolo = pianifica_taxi_singolo_greedy(clienti_singoli, etichette_clienti)
    piano_condiviso = pianifica_taxi_condiviso_coppie(coppie, [], etichette_clienti)
    
    return PianoMultiTaxi(
        piani_taxi={
            TAXI_SINGOLO: piano_singolo,
            TAXI_CONDIVISO: piano_condiviso
        },
        etichette_clienti=etichette_clienti
    )


def ottimizza_piano_taxi(piano_taxi, posizioni_clienti):
    """
    Ottimizza un piano taxi esistente riordinando le visite.
    
    Applica ottimizzazioni locali per ridurre la lunghezza totale del percorso.
    
    Args:
        piano_taxi (PianoTaxi): Piano da ottimizzare
        posizioni_clienti (dict): Posizioni dei clienti
    
    Returns:
        PianoTaxi: Piano ottimizzato
    """
    # Per ora restituisce il piano originale
    # Possibili ottimizzazioni future: 2-opt, riordinamento visite, etc.
    return piano_taxi


def calcola_statistiche_piano(piano_taxi):
    """
    Calcola statistiche utili su un piano taxi.
    
    Args:
        piano_taxi (PianoTaxi): Piano da analizzare
    
    Returns:
        dict: Dizionario con statistiche del piano
    """
    return {
        'lunghezza_percorso': len(piano_taxi.percorso),
        'numero_prelievi': len(piano_taxi.eventi_prelievo),
        'numero_discese': len(piano_taxi.eventi_discesa),
        'clienti_serviti': len(set(
            cliente for clienti_list in piano_taxi.eventi_prelievo.values() 
            for cliente in clienti_list
        ))
    }
