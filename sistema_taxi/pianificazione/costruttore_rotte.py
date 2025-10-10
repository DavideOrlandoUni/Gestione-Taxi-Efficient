from ..configurazione.costanti import STAZIONE
from ..configurazione.modelli import Viaggio, PianoTaxi
from ..algoritmi.ricerca_percorso import percorso_astar

def ottieni_cella_da_label(label, posizioni_locations):
    chiave = label.lower()
    if chiave not in posizioni_locations:
        raise KeyError(f"Location '{label}' non definita nel file delle posizioni.")
    return posizioni_locations[chiave]


def costruisci_viaggio_da_azioni(lista_azioni, posizioni_locations):
    # Converte azioni SAS in piano viaggio
    percorso_completo = []
    eventi_prelievo = {}
    eventi_discesa = {}
    etichette_clienti = {}
    posizione_corrente = None
    
    # Processa ogni azione
    for numero_azione, azione_raw in enumerate(lista_azioni, 1):
        try:
            tokens = azione_raw.strip("()").split()
            if not tokens:
                continue
            
            operazione = tokens[0]
            
            if operazione == "move":
                posizione_corrente = processa_azione_move(tokens, posizioni_locations, 
                                                        percorso_completo, posizione_corrente)
                    
            elif operazione == "pickup":
                processa_azione_pickup(tokens, posizioni_locations,
                                     percorso_completo, eventi_prelievo, 
                                     etichette_clienti, posizione_corrente)
                
            elif operazione == "dropoff":
                processa_azione_dropoff(tokens, percorso_completo, 
                                      eventi_discesa, posizione_corrente)
            else:
                print(f"[WARNING] Azione sconosciuta ignorata: {operazione}")
                
        except Exception as e:
            print(f"[ERROR] Errore azione {numero_azione}: {e}")
            continue
    
    viaggio = Viaggio(percorso_completo, eventi_prelievo, eventi_discesa)
    
    return viaggio, etichette_clienti


def processa_azione_move(tokens, posizioni_locations, percorso_completo, posizione_corrente):
    if len(tokens) != 4:
        raise ValueError(f"Azione move malformata: {tokens}")
    
    _, nome_taxi, src_label, dst_label = tokens
    
    src_cella = ottieni_cella_da_label(src_label, posizioni_locations)
    dst_cella = ottieni_cella_da_label(dst_label, posizioni_locations)
    
    if posizione_corrente is None:
        posizione_corrente = src_cella
        percorso_completo.append(posizione_corrente)
    
    segmento_intermedio = percorso_astar(posizione_corrente, dst_cella)
    percorso_completo.extend(segmento_intermedio)
    percorso_completo.append(dst_cella)
    
    return dst_cella


def processa_azione_pickup(tokens, posizioni_locations, percorso_completo, 
                          eventi_prelievo, etichette_clienti, posizione_corrente):
    if len(tokens) != 4:
        raise ValueError(f"Azione pickup malformata: {tokens}")
    
    _, nome_taxi, passeggero_label, location_label = tokens
    
    etichetta_cliente = passeggero_label.upper()
    etichette_clienti[etichetta_cliente] = ottieni_cella_da_label(location_label, posizioni_locations)
    
    if not percorso_completo:
        posizione_corrente = ottieni_cella_da_label(location_label, posizioni_locations)
        percorso_completo.append(posizione_corrente)
    
    indice_corrente = len(percorso_completo) - 1
    if indice_corrente not in eventi_prelievo:
        eventi_prelievo[indice_corrente] = []
    eventi_prelievo[indice_corrente].append(etichetta_cliente)


def processa_azione_dropoff(tokens, percorso_completo, eventi_discesa, posizione_corrente):
    if len(tokens) != 4:
        raise ValueError(f"Azione dropoff malformata: {tokens}")
    
    _, nome_taxi, passeggero_label, location_label = tokens
    
    etichetta_cliente = passeggero_label.upper()
    
    if not percorso_completo:
        posizione_corrente = STAZIONE
        percorso_completo.append(posizione_corrente)
    
    indice_corrente = len(percorso_completo) - 1
    if indice_corrente not in eventi_discesa:
        eventi_discesa[indice_corrente] = []
    eventi_discesa[indice_corrente].append(etichetta_cliente)


def valida_sequenza_azioni(lista_azioni):
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
    
    clienti_non_scesi = clienti_prelevati - clienti_scesi
    if clienti_non_scesi:
        errori.append(f"Clienti prelevati ma non scesi: {clienti_non_scesi}")
    
    return len(errori) == 0, errori


def ottimizza_sequenza_azioni(lista_azioni, posizioni_locations):
    return lista_azioni


def estrai_statistiche_azioni(lista_azioni):
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
    
    statistiche['clienti_unici'] = len(statistiche['clienti_unici'])
    statistiche['locations_visitate'] = len(statistiche['locations_visitate'])
    
    return statistiche
