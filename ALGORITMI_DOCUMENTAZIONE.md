# 📚 Documentazione Algoritmi Sistema Taxi Intelligenti

## 🌟 Algoritmo A-STAR (A*)

### **Cos'è l'algoritmo A***
L'algoritmo A* è un algoritmo di ricerca del percorso ottimo che trova il cammino più breve tra due punti su una griglia. È utilizzato nel sistema taxi per calcolare i percorsi ottimali tra stazione, clienti e destinazioni.

### **Come funziona A***
A* utilizza una **funzione di valutazione f(n) = g(n) + h(n)** per ogni nodo:

#### **🔍 Componenti della funzione f = g + h:**

**1. g(n) - Costo Reale**
- **Cosa è**: Il costo effettivo per raggiungere il nodo corrente dalla partenza
- **Nel codice**: `costi_g[nodo_corrente] + 1`
- **Implementazione**: Ogni movimento ortogonale costa 1 step
- **Esempio**: Se sono a 3 passi dalla partenza, g(n) = 3

**2. h(n) - Euristica (Distanza Manhattan)**
- **Cosa è**: Stima del costo per raggiungere la destinazione dal nodo corrente
- **Nel codice**: `distanza_manhattan(vicino, end)`
- **Formula**: `abs(x1-x2) + abs(y1-y2)`
- **Perché Manhattan**: Permette solo movimenti ortogonali (su/giù/sinistra/destra)

**3. f(n) - Costo Totale Stimato**
- **Cosa è**: Stima del costo totale del percorso passando per questo nodo
- **Nel codice**: `costo_f = nuovo_costo_g + distanza_manhattan(vicino, end)`
- **Uso**: A* esplora sempre il nodo con f(n) più basso

### **🔧 Implementazione nel Codice**

```python
def percorso_astar(start, end):
    # Coda prioritaria: (f_score, nodo)
    coda_aperta = [(0, start)]
    
    # g(n): costo reale dalla partenza
    costi_g = {start: 0}
    
    # Predecessori per ricostruire il percorso
    predecessori = {start: None}
    
    while coda_aperta:
        # Prendi nodo con f(n) minimo
        _, nodo_corrente = heapq.heappop(coda_aperta)
        
        # Destinazione raggiunta
        if nodo_corrente == end:
            return ricostruisci_percorso(predecessori, end)
        
        # Esplora vicini ortogonali
        for vicino in get_vicini(nodo_corrente):
            # g(n) = costo attuale + 1 step
            nuovo_costo_g = costi_g[nodo_corrente] + 1
            
            # Se trovato percorso migliore
            if vicino not in costi_g or nuovo_costo_g < costi_g[vicino]:
                costi_g[vicino] = nuovo_costo_g
                
                # f(n) = g(n) + h(n)
                costo_f = nuovo_costo_g + distanza_manhattan(vicino, end)
                
                predecessori[vicino] = nodo_corrente
                heapq.heappush(coda_aperta, (costo_f, vicino))
```

### **🎯 Vantaggi di A***
- **Ottimalità**: Trova sempre il percorso più breve
- **Efficienza**: Esplora meno nodi rispetto a Dijkstra
- **Ammissibilità**: L'euristica Manhattan non sovrastima mai il costo reale

---

## 🤖 Distanza di Manhattan

### **Cos'è la Distanza Manhattan**
La distanza Manhattan (o "taxi distance") è la distanza tra due punti misurata lungo gli assi ortogonali, come se ci si muovesse in una griglia urbana.

### **🧮 Formula e Implementazione**
```python
def distanza_manhattan(punto_a, punto_b):
    # |x1-x2| + |y1-y2|
    return abs(punto_a[0] - punto_b[0]) + abs(punto_a[1] - punto_b[1])
```

### **📍 Esempio Pratico**
- Punto A: (1, 1)
- Punto B: (4, 3)
- Distanza Manhattan: |4-1| + |3-1| = 3 + 2 = 5 passi

### **🎯 Perché Manhattan nel Sistema Taxi**
- **Movimento Realistico**: I taxi si muovono su strade ortogonali
- **Euristica Ammissibile**: Non sovrastima mai la distanza reale
- **Calcolo Veloce**: Operazione O(1) molto efficiente

---

## 🎲 Algoritmo Greedy (Goloso)

### **Cos'è l'Algoritmo Greedy**
Un algoritmo greedy fa sempre la scelta localmente ottima, sperando di arrivare a una soluzione globalmente ottima. Nel sistema taxi è usato per:
1. **Accoppiamento clienti** per taxi condivisi
2. **Ordinamento visite** per minimizzare distanze

### **🚖 Accoppiamento Clienti Greedy**

#### **Obiettivo**
Accoppiare clienti vicini per massimizzare l'efficienza dei taxi condivisi.

#### **🔄 Processo Step-by-Step**

**1. Trova Coppie Vicine**
```python
def trova_coppie_vicine(clienti, lista_clienti, raggio_max):
    for i in range(len(lista_clienti)):
        for j in range(i + 1, len(lista_clienti)):
            dist = distanza_manhattan(clienti[cliente1], clienti[cliente2])
            if dist <= raggio_max:
                coppie_vicine.append((dist, cliente1, cliente2))
```

**2. Ordina per Priorità**
```python
def ordina_per_priorita(coppie_vicine, clienti):
    # Criterio: (distanza_tra_clienti, distanza_totale_da_stazione)
    punteggio = (dist, dist_stazione1 + dist_stazione2)
```

**3. Selezione Greedy**
```python
def seleziona_greedy(coppie_ordinate):
    # Prendi la prima coppia disponibile (scelta greedy)
    for _, cliente1, cliente2 in coppie_ordinate:
        if cliente1 not in clienti_usati and cliente2 not in clienti_usati:
            # SCELTA GREEDY: prendi subito questa coppia
            coppie_scelte.append((cliente1, cliente2))
```

### **🗺️ Ordinamento Visite Greedy**

#### **Obiettivo**
Visitare i clienti nell'ordine che minimizza la distanza totale percorsa.

#### **🔄 Processo**
```python
def ordina_visita_greedy(clienti, posizioni, partenza):
    pos_attuale = partenza
    
    while clienti_da_visitare:
        # SCELTA GREEDY: prendi sempre il cliente più vicino
        cliente_vicino = trova_piu_vicino(pos_attuale, clienti_da_visitare)
        
        ordine.append(cliente_vicino)
        pos_attuale = posizioni[cliente_vicino]
        clienti_da_visitare.remove(cliente_vicino)
```

### **⚡ Caratteristiche Greedy**

**Vantaggi:**
- **Velocità**: Decisioni rapide O(n²)
- **Semplicità**: Facile da implementare e capire
- **Buone Soluzioni**: Spesso produce risultati accettabili

**Limitazioni:**
- **Non Ottimale**: Non garantisce la soluzione migliore globale
- **Miope**: Considera solo il beneficio immediato

### **🎯 Perché Greedy nel Sistema Taxi**
- **Tempo Reale**: Decisioni rapide per sistema interattivo
- **Scalabilità**: Gestisce facilmente molti clienti
- **Praticità**: Soluzioni "abbastanza buone" per uso reale

---

## 🔗 Integrazione degli Algoritmi

### **🚀 Flusso Completo del Sistema**

1. **Input**: Posizioni clienti e stazione
2. **Greedy Accoppiamento**: Trova coppie clienti per taxi condivisi
3. **A* Pathfinding**: Calcola percorsi ottimi per ogni tratta
4. **Greedy Ordinamento**: Ottimizza sequenza visite
5. **Output**: Piano completo di movimento taxi

### **🎪 Esempio Pratico Integrato**

```
Clienti: P1(2,3), P2(2,5), P3(8,1)
Stazione: ST(0,9)

1. GREEDY ACCOPPIAMENTO:
   - Distanza P1-P2: |2-2| + |3-5| = 2 ≤ raggio_max
   - Coppia: (P1,P2), Singolo: P3

2. A* PATHFINDING:
   - ST → P1: percorso_astar((0,9), (2,3)) = [(0,8),(0,7),...,(2,3)]
   - P1 → P2: percorso_astar((2,3), (2,5)) = [(2,4),(2,5)]
   - P2 → ST: percorso_astar((2,5), (0,9)) = [(2,6),(1,6),...,(0,9)]

3. GREEDY ORDINAMENTO:
   - Da ST: P1 più vicino di P2 → visita P1 prima

4. RISULTATO:
   - Taxi Condiviso: ST → P1 → P2 → ST
   - Taxi Singolo: ST → P3 → ST
```

### **📊 Complessità Computazionale**

- **A***: O(b^d) dove b=branching factor, d=profondità
- **Greedy Accoppiamento**: O(n²) per n clienti
- **Greedy Ordinamento**: O(n²) per n clienti
- **Totale Sistema**: O(n² + k×b^d) dove k=numero percorsi

---

## 🏆 Conclusioni

Il sistema taxi combina **precisione di A*** con **velocità del Greedy** per ottenere:

- ✅ **Percorsi Ottimi**: A* garantisce distanze minime
- ✅ **Decisioni Rapide**: Greedy per accoppiamenti e ordinamenti
- ✅ **Scalabilità**: Gestisce sistemi con molti clienti
- ✅ **Praticità**: Soluzioni utilizzabili in tempo reale

Questa combinazione rende il sistema **efficiente, veloce e pratico** per la gestione intelligente di flotte taxi.
