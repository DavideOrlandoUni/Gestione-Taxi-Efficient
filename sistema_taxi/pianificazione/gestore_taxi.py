import heapq
from ..configurazione.costanti import STAZIONE, TAXI_SINGOLO, TAXI_CONDIVISO
from ..configurazione.modelli import PianoTaxi, PianiMultiTaxi
from ..algoritmi.ricerca_percorso import percorso_astar, distanza_manhattan
from ..algoritmi.ottimizzazione import trova_coppie_clienti


def pianifica_taxi_singolo_greedy(lista_clienti, posizioni_clienti):
    # Pianifica taxi singolo con strategia greedy
    if not lista_clienti:
        return PianoTaxi([STAZIONE], {}, {})
    
    posizione_corrente = STAZIONE
    percorso_completo = [STAZIONE]
    eventi_prelievo = {}
    eventi_discesa = {}
    
    clienti_rimanenti = set(lista_clienti)
    
    while clienti_rimanenti:
        # Trova cliente più vicino
        cliente_piu_vicino = trova_cliente_piu_vicino(posizione_corrente, clienti_rimanenti, posizioni_clienti)
        posizione_cliente = posizioni_clienti[cliente_piu_vicino]
        
        # Vai dal cliente
        if posizione_corrente != posizione_cliente:
            segmento_andata = percorso_astar(posizione_corrente, posizione_cliente)
            percorso_completo.extend(segmento_andata)
            percorso_completo.append(posizione_cliente)
        
        indice_prelievo = len(percorso_completo) - 1
        eventi_prelievo[indice_prelievo] = [cliente_piu_vicino]
        
        # Torna alla stazione
        if posizione_cliente != STAZIONE:
            segmento_ritorno = percorso_astar(posizione_cliente, STAZIONE)
            percorso_completo.extend(segmento_ritorno)
            percorso_completo.append(STAZIONE)
        
        indice_discesa = len(percorso_completo) - 1
        eventi_discesa[indice_discesa] = [cliente_piu_vicino]
        
        posizione_corrente = STAZIONE
        clienti_rimanenti.remove(cliente_piu_vicino)
    
    return PianoTaxi(percorso_completo, eventi_prelievo, eventi_discesa)


def pianifica_taxi_condiviso_coppie(coppie_clienti, clienti_singoli, posizioni_clienti):
    percorso_completo = [STAZIONE]
    eventi_prelievo = {}
    eventi_discesa = {}
    
    coppie_ordinate = ordina_coppie_per_distanza(coppie_clienti, posizioni_clienti)
    
    for cliente_a, cliente_b in coppie_ordinate:
        servi_coppia_clienti(cliente_a, cliente_b, posizioni_clienti, 
                            percorso_completo, eventi_prelievo, eventi_discesa)
    
    for cliente in clienti_singoli:
        servi_cliente_singolo(cliente, posizioni_clienti, 
                             percorso_completo, eventi_prelievo, eventi_discesa)
    
    return PianoTaxi(percorso_completo, eventi_prelievo, eventi_discesa)


def servi_coppia_clienti(cliente_a, cliente_b, posizioni_clienti, 
                        percorso_completo, eventi_prelievo, eventi_discesa):
    pos_a = posizioni_clienti[cliente_a]
    pos_b = posizioni_clienti[cliente_b]
    
    dist_a_stazione = distanza_manhattan(pos_a, STAZIONE)
    dist_b_stazione = distanza_manhattan(pos_b, STAZIONE)
    
    if dist_b_stazione < dist_a_stazione:
        primo_cliente, pos_primo = cliente_b, pos_b
        secondo_cliente, pos_secondo = cliente_a, pos_a
    else:
        primo_cliente, pos_primo = cliente_a, pos_a
        secondo_cliente, pos_secondo = cliente_b, pos_b
    
    segmento = percorso_astar(STAZIONE, pos_primo)
    percorso_completo.extend(segmento)
    percorso_completo.append(pos_primo)
    eventi_prelievo[len(percorso_completo) - 1] = [primo_cliente]
    
    segmento = percorso_astar(pos_primo, pos_secondo)
    percorso_completo.extend(segmento)
    percorso_completo.append(pos_secondo)
    
    indice_secondo = len(percorso_completo) - 1
    if indice_secondo not in eventi_prelievo:
        eventi_prelievo[indice_secondo] = []
    eventi_prelievo[indice_secondo].append(secondo_cliente)
    
    segmento = percorso_astar(pos_secondo, STAZIONE)
    percorso_completo.extend(segmento)
    percorso_completo.append(STAZIONE)
    eventi_discesa[len(percorso_completo) - 1] = [primo_cliente, secondo_cliente]


def servi_cliente_singolo(cliente, posizioni_clienti, 
                         percorso_completo, eventi_prelievo, eventi_discesa):
    pos_cliente = posizioni_clienti[cliente]
    
    segmento = percorso_astar(STAZIONE, pos_cliente)
    percorso_completo.extend(segmento)
    percorso_completo.append(pos_cliente)
    eventi_prelievo[len(percorso_completo) - 1] = [cliente]
    
    segmento = percorso_astar(pos_cliente, STAZIONE)
    percorso_completo.extend(segmento)
    percorso_completo.append(STAZIONE)
    
    indice_discesa = len(percorso_completo) - 1
    if indice_discesa not in eventi_discesa:
        eventi_discesa[indice_discesa] = []
    eventi_discesa[indice_discesa].append(cliente)


def costruisci_piani_taxi_singolo_e_condiviso(mappa_pickup_clienti, posizioni, raggio_coppia=2):
    etichette_clienti = {}
    for cliente, location_label in mappa_pickup_clienti.items():
        if location_label in posizioni:
            etichette_clienti[cliente] = posizioni[location_label]
    
    if not etichette_clienti:
        piano_singolo = PianoTaxi([STAZIONE], {}, {})
        piano_condiviso = PianoTaxi([STAZIONE], {}, {})
        return PianiMultiTaxi({
            TAXI_SINGOLO: piano_singolo,
            TAXI_CONDIVISO: piano_condiviso
        }, etichette_clienti)
    
    coppie, clienti_singoli = trova_coppie_clienti(etichette_clienti, raggio_coppia)
    
    piano_singolo = pianifica_taxi_singolo_greedy(clienti_singoli, etichette_clienti)
    piano_condiviso = pianifica_taxi_condiviso_coppie(coppie, [], etichette_clienti)
    
    return PianiMultiTaxi(
        piani_taxi={
            TAXI_SINGOLO: piano_singolo,
            TAXI_CONDIVISO: piano_condiviso
        },
        etichette_clienti=etichette_clienti
    )


def ottimizza_piano_taxi(piano_taxi, posizioni_clienti):
    return piano_taxi


def calcola_statistiche_piano(piano_taxi):
    clienti_serviti = set()
    for clienti_list in piano_taxi.eventi_prelievo.values():
        for cliente in clienti_list:
            clienti_serviti.add(cliente)
    
    return {
        'lunghezza_percorso': len(piano_taxi.percorso),
        'numero_prelievi': len(piano_taxi.eventi_prelievo),
        'numero_discese': len(piano_taxi.eventi_discesa),
        'clienti_serviti': len(clienti_serviti)
    }


def trova_cliente_piu_vicino(posizione_corrente, clienti_rimanenti, posizioni_clienti):
    heap_distanze = []
    for cliente in clienti_rimanenti:
        distanza = distanza_manhattan(posizione_corrente, posizioni_clienti[cliente])
        heapq.heappush(heap_distanze, (distanza, cliente))
    
    _, cliente_piu_vicino = heapq.heappop(heap_distanze)
    return cliente_piu_vicino


def ordina_coppie_per_distanza(coppie_clienti, posizioni_clienti):
    coppie_con_distanza = []
    for coppia in coppie_clienti:
        distanza = distanza_manhattan(posizioni_clienti[coppia[0]], posizioni_clienti[coppia[1]])
        coppie_con_distanza.append((distanza, coppia))
    
    coppie_con_distanza.sort()
    coppie_ordinate = []
    for _, coppia in coppie_con_distanza:
        coppie_ordinate.append(coppia)
    
    return coppie_ordinate
