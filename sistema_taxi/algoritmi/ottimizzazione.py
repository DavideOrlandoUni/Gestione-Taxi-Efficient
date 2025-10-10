# Algoritmo di ottimizzazione greedy per accoppiamento clienti
from .ricerca_percorso import distanza_manhattan
from ..configurazione.costanti import STAZIONE, RAGGIO_ACCOPPIAMENTO_DEFAULT

def trova_coppie_clienti(clienti, raggio_max=RAGGIO_ACCOPPIAMENTO_DEFAULT):
    # ALGORITMO GREEDY ACCOPPIAMENTO: trova coppie ottimali per taxi condivisi
    # Obiettivo: massimizzare efficienza raggruppando clienti vicini
    lista_clienti = sorted(clienti.keys())  # Ordine deterministico
    
    # FASE 1: Trova tutte le coppie possibili entro il raggio
    coppie_possibili = trova_coppie_vicine(clienti, lista_clienti, raggio_max)
    
    # FASE 2: Ordina per priorità (distanza + vicinanza stazione)
    coppie_ordinate = ordina_per_priorita(coppie_possibili, clienti)
    
    # FASE 3: SCELTA GREEDY - prendi sempre la migliore disponibile
    coppie_finali, clienti_usati = seleziona_greedy(coppie_ordinate)
    
    # RISULTATO: clienti rimasti senza coppia (andranno su taxi singoli)
    clienti_singoli = sorted([
        cliente for cliente in lista_clienti 
        if cliente not in clienti_usati  # Non ancora accoppiati
    ])
    
    return coppie_finali, clienti_singoli


def trova_coppie_vicine(clienti, lista_clienti, raggio_max):
    # Trova tutte le coppie di clienti entro il raggio
    coppie_vicine = []
    
    for i in range(len(lista_clienti)):
        for j in range(i + 1, len(lista_clienti)):
            cliente1 = lista_clienti[i]
            cliente2 = lista_clienti[j]
            
            dist = distanza_manhattan(
                clienti[cliente1], 
                clienti[cliente2]
            )
            
            if dist <= raggio_max:
                coppie_vicine.append((dist, cliente1, cliente2))
    
    return coppie_vicine


def ordina_per_priorita(coppie_vicine, clienti):
    # Ordina coppie per distanza e vicinanza alla stazione
    coppie_con_punteggio = []
    for coppia in coppie_vicine:
        dist, cliente1, cliente2 = coppia
        
        dist_stazione1 = distanza_manhattan(clienti[cliente1], STAZIONE)
        dist_stazione2 = distanza_manhattan(clienti[cliente2], STAZIONE)
        dist_totale = dist_stazione1 + dist_stazione2
        
        punteggio = (dist, dist_totale, cliente1, cliente2)
        coppie_con_punteggio.append((punteggio, coppia))
    
    coppie_con_punteggio.sort()
    
    coppie_ordinate = []
    for punteggio, coppia in coppie_con_punteggio:
        coppie_ordinate.append(coppia)
    
    return coppie_ordinate


def seleziona_greedy(coppie_ordinate):
    # CORE ALGORITMO GREEDY: scelta miope ma efficace
    # Strategia: prendi sempre la prima coppia disponibile (localmente ottima)
    clienti_usati = set()  # Traccia clienti già assegnati
    coppie_scelte = []     # Coppie selezionate per taxi condivisi
    
    # Scorri coppie in ordine di priorità (migliori prima)
    for _, cliente1, cliente2 in coppie_ordinate:
        # DECISIONE GREEDY: se entrambi liberi, prendili subito!
        # Non considera combinazioni future - scelta immediata
        if cliente1 not in clienti_usati and cliente2 not in clienti_usati:
            coppie_scelte.append((cliente1, cliente2))  # Accoppia
            clienti_usati.add(cliente1)  # Marca come usato
            clienti_usati.add(cliente2)  # Marca come usato
            # Nota: questa scelta è irreversibile (caratteristica greedy)
    
    return coppie_scelte, clienti_usati


def ordina_visita_greedy(clienti, posizioni, partenza=STAZIONE):
    # ALGORITMO GREEDY NEAREST NEIGHBOR: visita sempre il più vicino
    # Problema: Traveling Salesman semplificato
    # Strategia: scelta miope ma veloce O(n²)
    if not clienti:
        return []  # Nessun cliente da visitare
    
    clienti_da_visitare = set(clienti)  # Clienti ancora da servire
    ordine = []           # Sequenza ottimizzata di visite
    pos_attuale = partenza  # Posizione corrente del taxi
    
    # CICLO GREEDY: finché ci sono clienti da visitare
    while clienti_da_visitare:
        cliente_vicino = None      # Candidato migliore
        dist_min = float('inf')   # Distanza minima trovata
        
        # RICERCA LOCALE: trova il cliente più vicino alla posizione attuale
        for cliente in clienti_da_visitare:
            dist = distanza_manhattan(pos_attuale, posizioni[cliente])
            if dist < dist_min:  # Trovato uno più vicino
                dist_min = dist
                cliente_vicino = cliente
        
        # SCELTA GREEDY: prendi il più vicino (decisione irreversibile)
        ordine.append(cliente_vicino)
        clienti_da_visitare.remove(cliente_vicino)
        pos_attuale = posizioni[cliente_vicino]  # Aggiorna posizione
        
        # Nota: non considera l'impatto globale, solo beneficio immediato
    
    return ordine  # Sequenza di visite ottimizzata localmente


def trova_cliente_vicino(pos_ref, clienti, posizioni):
    # Trova cliente più vicino a posizione di riferimento
    if not clienti:
        return None
    
    cliente_vicino = None
    dist_min = float('inf')
    
    for cliente in clienti:
        dist = distanza_manhattan(pos_ref, posizioni[cliente])
        if dist < dist_min:
            dist_min = dist
            cliente_vicino = cliente
    
    return cliente_vicino
