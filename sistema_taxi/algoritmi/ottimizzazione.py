"""
Algoritmi di Ottimizzazione
===========================

Implementa algoritmi per l'ottimizzazione dei percorsi taxi:
- Accoppiamento clienti per raggio Manhattan
- Selezione greedy delle coppie ottimali
- Ottimizzazione ordine di visita clienti
"""

from .ricerca_percorso import calcola_distanza_manhattan
from ..configurazione.costanti import STAZIONE, DEBUG, RAGGIO_ACCOPPIAMENTO_DEFAULT


def trova_coppie_clienti_per_raggio(etichette_clienti, raggio_massimo=RAGGIO_ACCOPPIAMENTO_DEFAULT):
    """
    Trova coppie di clienti entro un raggio Manhattan specificato.
    
    Utilizza un algoritmo greedy che seleziona le coppie con distanza minore
    evitando conflitti (un cliente può appartenere a una sola coppia).
    Le coppie sono ordinate per:
    1. Distanza tra i clienti (crescente)
    2. Distanza totale dalla stazione (crescente)
    3. Ordine alfabetico (per determinismo)
    
    Args:
        etichette_clienti (dict): Mappa {etichetta_cliente: posizione}
        raggio_massimo (int): Distanza Manhattan massima per formare una coppia
    
    Returns:
        tuple: (lista_coppie, lista_clienti_singoli)
            - lista_coppie: Lista di tuple (cliente_a, cliente_b)
            - lista_clienti_singoli: Lista di clienti senza coppia
    
    Example:
        >>> clienti = {'A': (1, 1), 'B': (1, 2), 'C': (5, 5)}
        >>> coppie, singoli = trova_coppie_clienti_per_raggio(clienti, 2)
        >>> print(coppie)  # [('A', 'B')]
        >>> print(singoli)  # ['C']
    """
    etichette_ordinate = sorted(etichette_clienti.keys())
    
    # Trova tutte le coppie candidate entro il raggio
    coppie_candidate = _trova_coppie_candidate(etichette_clienti, etichette_ordinate, raggio_massimo)
    
    # Ordina le coppie per priorità
    coppie_candidate = _ordina_coppie_per_priorita(coppie_candidate, etichette_clienti)
    
    # Selezione greedy delle coppie (evita conflitti)
    coppie_selezionate, clienti_utilizzati = _seleziona_coppie_greedy(coppie_candidate)
    
    # Clienti rimasti senza coppia
    
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#ATTENZIONE, SEMPLIFICARE 
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    clienti_singoli = sorted([
        cliente for cliente in etichette_ordinate 
        if cliente not in clienti_utilizzati
    ])
    
    if DEBUG:
        print(f"[DEBUG] Accoppiamento clienti:")
        print(f"        Raggio Manhattan ≤ {raggio_massimo}")
        print(f"        Coppie trovate: {coppie_selezionate}")
        print(f"        Clienti singoli: {clienti_singoli}")
    
    return coppie_selezionate, clienti_singoli


def _trova_coppie_candidate(etichette_clienti, etichette_ordinate, raggio_massimo):
    """
    Trova tutte le coppie di clienti entro il raggio specificato.
    
    Args:
        etichette_clienti (dict): Posizioni dei clienti
        etichette_ordinate (list): Lista ordinata delle etichette
        raggio_massimo (int): Raggio massimo per l'accoppiamento
    
    Returns:
        list: Lista di tuple (distanza, cliente_a, cliente_b)
    """
    coppie_candidate = []
    
    for i in range(len(etichette_ordinate)):
        for j in range(i + 1, len(etichette_ordinate)):
            cliente_a = etichette_ordinate[i]
            cliente_b = etichette_ordinate[j]
            
            distanza = calcola_distanza_manhattan(
                etichette_clienti[cliente_a], 
                etichette_clienti[cliente_b]
            )
            
            if distanza <= raggio_massimo:
                coppie_candidate.append((distanza, cliente_a, cliente_b))
    
    return coppie_candidate





# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#ATTENZIONE, SEMPLIFICARE FUNZIONE DENTRO FUNZIONE
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def _ordina_coppie_per_priorita(coppie_candidate, etichette_clienti):
    """
    Ordina le coppie candidate per priorità di selezione.
    
    Criteri di ordinamento:
    1. Distanza tra i clienti (crescente)
    2. Distanza totale dalla stazione (crescente)  
    3. Ordine alfabetico (per determinismo)
    
    Args:
        coppie_candidate (list): Lista di coppie candidate
        etichette_clienti (dict): Posizioni dei clienti
    
    Returns:
        list: Lista ordinata di coppie candidate
    """
    def chiave_ordinamento(coppia):
        distanza, cliente_a, cliente_b = coppia
        
        # Distanza totale dalla stazione
        distanza_stazione_a = calcola_distanza_manhattan(etichette_clienti[cliente_a], STAZIONE)
        distanza_stazione_b = calcola_distanza_manhattan(etichette_clienti[cliente_b], STAZIONE)
        distanza_totale_stazione = distanza_stazione_a + distanza_stazione_b
        
        return (distanza, distanza_totale_stazione, cliente_a, cliente_b)
    
    return sorted(coppie_candidate, key=chiave_ordinamento)


def _seleziona_coppie_greedy(coppie_candidate):
    """
    Seleziona le coppie usando strategia greedy evitando conflitti.
    
    Args:
        coppie_candidate (list): Lista ordinata di coppie candidate
    
    Returns:
        tuple: (coppie_selezionate, clienti_utilizzati)
    """
    clienti_utilizzati = set()
    coppie_selezionate = []
    
    for _, cliente_a, cliente_b in coppie_candidate:
        if cliente_a not in clienti_utilizzati and cliente_b not in clienti_utilizzati:
            coppie_selezionate.append((cliente_a, cliente_b))
            clienti_utilizzati.add(cliente_a)
            clienti_utilizzati.add(cliente_b)
    
    return coppie_selezionate, clienti_utilizzati


def stampa_debug_coppie_candidate(etichette_clienti, raggio):
    """
    Stampa informazioni di debug sulle coppie candidate.
    
    Utile per analizzare il processo di accoppiamento e debug.
    
    Args:
        etichette_clienti (dict): Posizioni dei clienti
        raggio (int): Raggio massimo per le coppie
    """
    if not DEBUG:
        return
    
    candidate = []
    etichette = sorted(etichette_clienti.keys())
    
    for i in range(len(etichette)):
        for j in range(i + 1, len(etichette)):
            cliente_a, cliente_b = etichette[i], etichette[j]
            distanza = calcola_distanza_manhattan(
                etichette_clienti[cliente_a], 
                etichette_clienti[cliente_b]
            )
            
            if distanza <= raggio:
                candidate.append((distanza, cliente_a, cliente_b))
    
    candidate.sort()
    print(f"[DEBUG] Coppie candidate (Manhattan ≤ {raggio}): {candidate}")


def ottimizza_ordine_visita_clienti(lista_clienti, posizioni_clienti, posizione_partenza=STAZIONE):
    """
    Ottimizza l'ordine di visita dei clienti usando strategia greedy.
    
    Seleziona iterativamente il cliente più vicino alla posizione corrente.
    Questo è un'approssimazione del problema del commesso viaggiatore (TSP).
    
    Args:
        lista_clienti (list): Lista delle etichette dei clienti
        posizioni_clienti (dict): Posizioni dei clienti
        posizione_partenza (tuple): Posizione di partenza (default: stazione)
    
    Returns:
        list: Lista ordinata dei clienti da visitare
    
    Example:
        >>> clienti = ['A', 'B', 'C']
        >>> posizioni = {'A': (1, 1), 'B': (5, 5), 'C': (2, 1)}
        >>> ordine = ottimizza_ordine_visita_clienti(clienti, posizioni)
        >>> print(ordine)  # ['A', 'C', 'B'] (ordine ottimizzato)
    """
    if not lista_clienti:
        return []
    
    clienti_rimanenti = set(lista_clienti)
    ordine_visita = []
    posizione_corrente = posizione_partenza
    

    
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#ATTENZIONE, SEMPLIFICARE FUNZIONE DENTRO FUNZIONE
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    while clienti_rimanenti:
        # Trova il cliente più vicino alla posizione corrente
        cliente_piu_vicino = min(
            clienti_rimanenti,
            key=lambda c: calcola_distanza_manhattan(posizione_corrente, posizioni_clienti[c])
        )
        
        # Aggiungi all'ordine e rimuovi dai rimanenti
        ordine_visita.append(cliente_piu_vicino)
        clienti_rimanenti.remove(cliente_piu_vicino)
        posizione_corrente = posizioni_clienti[cliente_piu_vicino]
    
    return ordine_visita


def calcola_costo_totale_percorso(lista_clienti, posizioni_clienti, posizione_base=STAZIONE):
    """
    Calcola il costo totale per visitare tutti i clienti e tornare alla base.
    
    Args:
        lista_clienti (list): Lista ordinata dei clienti da visitare
        posizioni_clienti (dict): Posizioni dei clienti
        posizione_base (tuple): Posizione base (partenza e arrivo)
    
    Returns:
        int: Costo totale del percorso (numero di step)
    """
    if not lista_clienti:
        return 0
    
    costo_totale = 0
    posizione_corrente = posizione_base
    
    # Costo per visitare ogni cliente
    for cliente in lista_clienti:
        posizione_cliente = posizioni_clienti[cliente]
        costo_totale += calcola_distanza_manhattan(posizione_corrente, posizione_cliente)
        posizione_corrente = posizione_cliente
    
    # Costo per tornare alla base
    costo_totale += calcola_distanza_manhattan(posizione_corrente, posizione_base)
    
    return costo_totale


def trova_cliente_piu_vicino(posizione_riferimento, lista_clienti, posizioni_clienti):
    """
    Trova il cliente più vicino a una posizione di riferimento.
    
    Args:
        posizione_riferimento (tuple): Posizione di riferimento
        lista_clienti (list): Lista dei clienti da considerare
        posizioni_clienti (dict): Posizioni dei clienti
    
    Returns:
        str: Etichetta del cliente più vicino, None se lista vuota
    """
    if not lista_clienti:
        return None
    
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#ATTENZIONE, SEMPLIFICARE FUNZIONE DENTRO FUNZIONE
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return min(
        lista_clienti,
        key=lambda c: calcola_distanza_manhattan(posizione_riferimento, posizioni_clienti[c])
    )
