# Algoritmo di accoppiamento clienti basato su distanza Manhattan
from .ricerca_percorso import distanza_manhattan
from ..configurazione.costanti import STAZIONE, RAGGIO_ACCOPPIAMENTO_DEFAULT

def trova_coppie_clienti(clienti, raggio_max=RAGGIO_ACCOPPIAMENTO_DEFAULT):
    # Trova coppie di clienti entro il raggio massimo usando solo distanza Manhattan
    lista_clienti = sorted(clienti.keys())
    
    # Trova tutte le coppie possibili entro il raggio
    coppie_possibili = trova_coppie_vicine(clienti, lista_clienti, raggio_max)
    
    # Ordina per distanza dalla stazione (più vicini alla stazione prima)
    coppie_ordinate = ordina_per_distanza_stazione(coppie_possibili, clienti)
    
    # Seleziona coppie senza sovrapposizioni
    coppie_finali, clienti_usati = seleziona_coppie_senza_sovrapposizioni(coppie_ordinate)
    
    # Clienti rimasti senza coppia (andranno su taxi singoli)
    clienti_singoli = sorted([
        cliente for cliente in lista_clienti 
        if cliente not in clienti_usati
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


def ordina_per_distanza_stazione(coppie_vicine, clienti):
    # Ordina coppie per distanza totale dalla stazione (più vicine prima)
    coppie_con_distanza = []
    for coppia in coppie_vicine:
        dist, cliente1, cliente2 = coppia
        
        dist_stazione1 = distanza_manhattan(clienti[cliente1], STAZIONE)
        dist_stazione2 = distanza_manhattan(clienti[cliente2], STAZIONE)
        dist_totale_stazione = dist_stazione1 + dist_stazione2
        
        coppie_con_distanza.append((dist_totale_stazione, coppia))
    
    coppie_con_distanza.sort()
    
    coppie_ordinate = []
    for _, coppia in coppie_con_distanza:
        coppie_ordinate.append(coppia)
    
    return coppie_ordinate


def seleziona_coppie_senza_sovrapposizioni(coppie_ordinate):
    # Seleziona coppie senza sovrapposizioni di clienti
    clienti_usati = set()
    coppie_scelte = []
    
    for _, cliente1, cliente2 in coppie_ordinate:
        if cliente1 not in clienti_usati and cliente2 not in clienti_usati:
            coppie_scelte.append((cliente1, cliente2))
            clienti_usati.add(cliente1)
            clienti_usati.add(cliente2)
    
    return coppie_scelte, clienti_usati


def ordina_clienti_per_distanza_stazione(clienti, posizioni):
    # Ordina clienti per distanza Manhattan dalla stazione
    if not clienti:
        return []
    
    clienti_con_distanza = []
    for cliente in clienti:
        distanza = distanza_manhattan(posizioni[cliente], STAZIONE)
        clienti_con_distanza.append((distanza, cliente))
    
    clienti_con_distanza.sort()
    
    ordine = []
    for _, cliente in clienti_con_distanza:
        ordine.append(cliente)
    
    return ordine


