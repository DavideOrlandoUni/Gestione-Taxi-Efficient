import heapq
from ..configurazione.costanti import GRIGLIA_LARGHEZZA, GRIGLIA_ALTEZZA, OSTACOLI

def distanza_manhattan(punto_a, punto_b):
    # EURISTICA MANHATTAN: |x1-x2| + |y1-y2|
    # Calcola la distanza "taxi" tra due punti (solo movimenti ortogonali)
    # Questa è l'euristica h(n) usata in A* - mai sovrastima la distanza reale
    distanza_x = abs(punto_a[0] - punto_b[0])  # Differenza coordinate X
    distanza_y = abs(punto_a[1] - punto_b[1])  # Differenza coordinate Y
    return distanza_x + distanza_y  # Somma = passi minimi necessari

def percorso_astar(start, end):
    # ALGORITMO A*: Trova il percorso più breve usando f(n) = g(n) + h(n)
    # g(n) = costo reale dalla partenza
    # h(n) = euristica (stima costo verso destinazione)
    # f(n) = stima costo totale del percorso
    
    # Caso base: già alla destinazione
    if start == end:
        return []
    
    # Verifica validità posizioni (dentro griglia e non ostacoli)
    if not posizione_valida(start) or not posizione_valida(end):
        return []
    
    # INIZIALIZZAZIONE A*:
    # Coda prioritaria: (f_score, nodo) - esplora sempre nodo con f(n) minimo
    coda_aperta = [(0, start)]  # f(start) = 0 + h(start,end)
    
    # g(n): costo reale per raggiungere ogni nodo dalla partenza
    costi_g = {start: 0}  # g(start) = 0 (costo per raggiungere se stesso)
    
    # Predecessori: per ricostruire il percorso alla fine
    predecessori = {start: None}  # start non ha predecessore
    
    # CICLO PRINCIPALE A*: esplora nodi in ordine di f(n) crescente
    while coda_aperta:
        # Prendi nodo con f(n) più basso (più promettente)
        _, nodo_corrente = heapq.heappop(coda_aperta)
        
        # SUCCESSO: raggiunta destinazione, ricostruisci percorso
        if nodo_corrente == end:
            return ricostruisci_percorso(predecessori, end)
        
        # ESPANSIONE: esplora tutti i vicini ortogonali del nodo corrente
        for vicino in get_vicini(nodo_corrente):
            # CALCOLO g(vicino): costo per raggiungere il vicino
            # g(vicino) = g(corrente) + 1 (ogni movimento costa 1)
            nuovo_costo_g = costi_g[nodo_corrente] + 1
            
            # AGGIORNAMENTO: se trovato percorso migliore verso questo vicino
            if vicino not in costi_g or nuovo_costo_g < costi_g[vicino]:
                # Salva il nuovo costo g(n) migliore
                costi_g[vicino] = nuovo_costo_g
                
                # CALCOLO f(n) = g(n) + h(n)
                # f(vicino) = costo_reale + euristica_manhattan
                costo_f = nuovo_costo_g + distanza_manhattan(vicino, end)
                
                # Salva da dove siamo arrivati (per ricostruire percorso)
                predecessori[vicino] = nodo_corrente
                
                # Aggiungi alla coda con priorità f(n)
                heapq.heappush(coda_aperta, (costo_f, vicino))
    
    # FALLIMENTO: nessun percorso trovato
    return []


def posizione_valida(pos):
    # VALIDAZIONE POSIZIONE: controlla se una cella è esplorabile
    # Usata da A* per evitare posizioni illegali
    x, y = pos
    
    # Controllo 1: dentro i confini della griglia
    if not (0 <= x < GRIGLIA_LARGHEZZA and 0 <= y < GRIGLIA_ALTEZZA):
        return False  # Fuori dai limiti
    
    # Controllo 2: non è un ostacolo (muro, edificio, ecc.)
    if pos in OSTACOLI:
        return False  # Posizione bloccata
    
    return True  # Posizione valida per il movimento


def get_vicini(pos):
    # GENERAZIONE VICINI: trova tutte le posizioni raggiungibili in 1 step
    # A* usa questa funzione per espandere ogni nodo
    x, y = pos
    vicini = []
    
    # MOVIMENTI ORTOGONALI: solo su/giù/sinistra/destra (no diagonali)
    # Questo simula il movimento realistico di un taxi su strade urbane
    movimenti = [(1, 0),   # Destra
                 (-1, 0),  # Sinistra  
                 (0, 1),   # Giù
                 (0, -1)]  # Su
    
    # Controlla ogni direzione possibile
    for dx, dy in movimenti:
        nuova_pos = (x + dx, y + dy)
        
        # Aggiungi solo se la posizione è valida (dentro griglia, no ostacoli)
        if posizione_valida(nuova_pos):
            vicini.append(nuova_pos)
    
    return vicini  # Lista delle posizioni esplorabili


def ricostruisci_percorso(predecessori, end):
    # RICOSTRUZIONE PERCORSO: segue i predecessori dalla destinazione alla partenza
    # A* salva da dove è arrivato a ogni nodo, qui ricostruiamo il cammino
    percorso = [end]  # Inizia dalla destinazione
    
    # BACKTRACKING: segui la catena dei predecessori
    nodo = end
    while predecessori[nodo] is not None:  # Finché non raggiungi la partenza
        nodo = predecessori[nodo]  # Vai al nodo precedente
        percorso.append(nodo)      # Aggiungilo al percorso
    
    # Il percorso è al contrario (end -> start), lo invertiamo
    percorso.reverse()  # Ora è (start -> end)
    
    # Rimuovi start e end: ritorna solo i nodi intermedi
    # Il taxi sa già dove parte e dove deve arrivare
    return percorso[1:-1]  # Solo i passi intermedi del percorso
