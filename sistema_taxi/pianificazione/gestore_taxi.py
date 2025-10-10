from ..configurazione.costanti import STAZIONE, TAXI_SINGOLO, TAXI_CONDIVISO
from ..configurazione.modelli import PianoTaxi, PianiMultiTaxi
from ..algoritmi.ricerca_percorso import percorso_astar, distanza_manhattan
from ..algoritmi.ottimizzazione import trova_coppie_clienti, ordina_clienti_per_distanza_stazione


def pianifica_taxi_singolo_per_distanza(lista_clienti, posizioni_clienti):
    # Pianifica taxi singolo ordinando clienti per distanza dalla stazione
    if not lista_clienti:
        return PianoTaxi([STAZIONE], {}, {})
    
    # Ordina clienti per distanza dalla stazione (più vicini prima)
    clienti_ordinati = ordina_clienti_per_distanza_stazione(lista_clienti, posizioni_clienti)
    
    percorso_completo = [STAZIONE]
    eventi_prelievo = {}
    eventi_discesa = {}
    
    for cliente in clienti_ordinati:
        posizione_cliente = posizioni_clienti[cliente]
        
        # Vai dal cliente
        if STAZIONE != posizione_cliente:
            segmento_andata = percorso_astar(STAZIONE, posizione_cliente)
            percorso_completo.extend(segmento_andata)
        
        percorso_completo.append(posizione_cliente)
        indice_prelievo = len(percorso_completo) - 1
        eventi_prelievo[indice_prelievo] = [cliente]
        
        # Torna alla stazione
        if posizione_cliente != STAZIONE:
            segmento_ritorno = percorso_astar(posizione_cliente, STAZIONE)
            percorso_completo.extend(segmento_ritorno)
        
        percorso_completo.append(STAZIONE)
        indice_discesa = len(percorso_completo) - 1
        eventi_discesa[indice_discesa] = [cliente]
    
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
    
    # Ordina clienti per distanza dalla stazione (più vicino prima)
    dist_a_stazione = distanza_manhattan(pos_a, STAZIONE)
    dist_b_stazione = distanza_manhattan(pos_b, STAZIONE)
    
    if dist_a_stazione <= dist_b_stazione:
        primo_cliente, pos_primo = cliente_a, pos_a
        secondo_cliente, pos_secondo = cliente_b, pos_b
    else:
        primo_cliente, pos_primo = cliente_b, pos_b
        secondo_cliente, pos_secondo = cliente_a, pos_a
    
    # Vai al primo cliente
    if STAZIONE != pos_primo:
        segmento = percorso_astar(STAZIONE, pos_primo)
        percorso_completo.extend(segmento)
    
    percorso_completo.append(pos_primo)
    eventi_prelievo[len(percorso_completo) - 1] = [primo_cliente]
    
    # Vai al secondo cliente
    if pos_primo != pos_secondo:
        segmento = percorso_astar(pos_primo, pos_secondo)
        percorso_completo.extend(segmento)
    
    percorso_completo.append(pos_secondo)
    indice_secondo = len(percorso_completo) - 1
    if indice_secondo not in eventi_prelievo:
        eventi_prelievo[indice_secondo] = []
    eventi_prelievo[indice_secondo].append(secondo_cliente)
    
    # Torna alla stazione
    if pos_secondo != STAZIONE:
        segmento = percorso_astar(pos_secondo, STAZIONE)
        percorso_completo.extend(segmento)
    
    percorso_completo.append(STAZIONE)
    eventi_discesa[len(percorso_completo) - 1] = [primo_cliente, secondo_cliente]


def servi_cliente_singolo(cliente, posizioni_clienti, 
                         percorso_completo, eventi_prelievo, eventi_discesa):
    pos_cliente = posizioni_clienti[cliente]
    
    # Vai al cliente
    if STAZIONE != pos_cliente:
        segmento = percorso_astar(STAZIONE, pos_cliente)
        percorso_completo.extend(segmento)
    
    percorso_completo.append(pos_cliente)
    eventi_prelievo[len(percorso_completo) - 1] = [cliente]
    
    # Torna alla stazione
    if pos_cliente != STAZIONE:
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
            # Converte lista in tupla per compatibilità con A*
            pos = posizioni[location_label]
            if isinstance(pos, list):
                pos = tuple(pos)
            etichette_clienti[cliente] = pos
    
    if not etichette_clienti:
        piano_singolo = PianoTaxi([STAZIONE], {}, {})
        piano_condiviso = PianoTaxi([STAZIONE], {}, {})
        return PianiMultiTaxi({
            TAXI_SINGOLO: piano_singolo,
            TAXI_CONDIVISO: piano_condiviso
        }, etichette_clienti)
    
    coppie, clienti_singoli = trova_coppie_clienti(etichette_clienti, raggio_coppia)
    
    piano_singolo = pianifica_taxi_singolo_per_distanza(clienti_singoli, etichette_clienti)
    piano_condiviso = pianifica_taxi_condiviso_coppie(coppie, [], etichette_clienti)
    
    return PianiMultiTaxi(
        piani_taxi={
            TAXI_SINGOLO: piano_singolo,
            TAXI_CONDIVISO: piano_condiviso
        },
        etichette_clienti=etichette_clienti
    )




def trova_cliente_piu_vicino(posizione_corrente, clienti_rimanenti, posizioni_clienti):
    # Trova cliente più vicino usando distanza Manhattan
    cliente_piu_vicino = None
    distanza_minima = float('inf')
    
    for cliente in clienti_rimanenti:
        distanza = distanza_manhattan(posizione_corrente, posizioni_clienti[cliente])
        if distanza < distanza_minima:
            distanza_minima = distanza
            cliente_piu_vicino = cliente
    
    return cliente_piu_vicino


def ordina_coppie_per_distanza(coppie_clienti, posizioni_clienti):
    # Ordina coppie per distanza totale dalla stazione
    coppie_con_distanza = []
    for coppia in coppie_clienti:
        cliente_a, cliente_b = coppia
        dist_a = distanza_manhattan(posizioni_clienti[cliente_a], STAZIONE)
        dist_b = distanza_manhattan(posizioni_clienti[cliente_b], STAZIONE)
        distanza_totale = dist_a + dist_b
        coppie_con_distanza.append((distanza_totale, coppia))
    
    coppie_con_distanza.sort()
    coppie_ordinate = []
    for _, coppia in coppie_con_distanza:
        coppie_ordinate.append(coppia)
    
    return coppie_ordinate
