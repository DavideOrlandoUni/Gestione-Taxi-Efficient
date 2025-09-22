## EFFICENT TAXI MANAGEMENT – Sistemi Intelligenti

PROGETTO DI Carlo Cairoli (MAT:741051) e Davide Orlando (MAT: 737376)



**Descrizione del progetto:**



Il progetto simula la gestione intelligente di taxi a partire da piani generati in PDDL tramite il planner FastDownward.



La città è rappresentata da una griglia 15×10 con ostacoli (quadrati neri), una stazione fissa (quadrato verde) e clienti dislocati in posizioni variabili (cerchietti azzurri).



Il sistema legge i piani esterni ("sas\_plan"), li traduce in un percorso concreto cella-per-cella con A\* e li visualizza in una GUI interattiva sviluppata in Tkinter, che mostra in tempo reale i movimenti dei taxi, le operazioni di pick-up e drop-off e la ripartizione dei costi.







**Funzionalità principali:**



* Lettura di piani generati da FastDownward e associazione con coordinate reali tramite file "locations.json".
* Calcolo dei percorsi cella-per-cella con algoritmo A\* e distanza di Manhattan come euristica.
* Gestione degli ostacoli e calcolo automatico di deviazioni minime.
* Dashboard dei costi in tempo reale con ripartizione equa nei tratti condivisi.
* Interfaccia grafica interattiva con controlli Play, Pause, Reset e regolazione della velocità.
* Log operativo su terminale con tracciamento delle azioni eseguite.
* Simulazione di diversi scenari:

   1) Problem 1: taxi con un solo cliente.

   2) Problem 2: taxi condiviso con due clienti.

   3) Problem 3: ride sharing dinamico con tre clienti (due serviti insieme, uno separato).







**Struttura del codice:**



* domain.pddl – definizione delle azioni di pianificazione (move, pickup, dropoff).
* problem1.pddl, problem2.pddl, problem3.pddl – scenari di test.
* location1.json, location2.json, location3.json – coordinate di stazione e clienti.
* sas\_plan – piani generati da Fast Downward.
* taxi\_visualizer.py – GUI Tkinter che legge i piani, li traduce in un TripPlan e gestisce animazione e costi.







**Parti principali del codice**



* read\_plan(filepath) → parsing del file piano PDDL.
* load\_locations(filepath) → associazione simboli–coordinate.
* find\_path(start, goal) → implementazione di A\\\* con euristica Manhattan.
* TripPlan → struttura dati che memorizza percorso, pick-up e drop-off ed esegue il calcolo dei costi.
* build\_share\_two\_closest\_trip → logica di ride sharing: identifica i due clienti più vicini e pianifica una corsa condivisa.
* TaxiApp → GUI che visualizza la griglia, anima il taxi e aggiorna la dashboard dei costi.









**Controlli dall’interfaccia grafica**



| Pulsante  | Azione                                                        |

| --------- | ------------------------------------------------------------- |

| Problem 1 | Carica il piano con un solo cliente                           |

| Problem 2 | Carica il piano con due clienti condivisi                     |

| Problem 3 | Carica il piano con tre clienti (due condivisi, uno separato) |

| Play      | Avvia l’animazione passo-passo                                |

| Pause     | Mette in pausa l’animazione                                   |

| Reset     | Riporta lo scenario allo stato iniziale                       |

| Velocità  | Permette di regolare l’intervallo di aggiornamento (in ms)    |









**Algoritmo A\* ed euristiche**



L’algoritmo A\* calcola il percorso minimo sulla griglia.



La funzione di valutazione è: f(n) = g(n) + h(n)



dove:

  - g(n): costo effettivo dal nodo iniziale a n

  - h(n): distanza euristica residua stimata con distanza Manhattan\*\*



La distanza di Manhattan  è ammissibile e consistente, garantendo sempre soluzioni ottimali.

Gli ostacoli sono esclusi durante l’esplorazione dei vicini, obbligando l’algoritmo a calcolare deviazioni minime solo quando necessario.









**Gestione dei Problem (scenari)**



1. **Scenario 1**: taxi singolo con un cliente (ST → cliente → ST).
2. **Scenario 2**: taxi condiviso con due clienti (ST → cliente1 → cliente2 → ST).
3. **Scenario 3**: ride sharing con tre clienti, i due più vicini vengono serviti insieme, il terzo con corsa dedicata.









**Log operativo**



Durante l’esecuzione, il terminale riporta log dettagliati:



* indice del passo,
* posizione attuale del taxi,
* clienti a bordo,
* costo totale accumulato.









**Prerequisiti**



1. Python 3.8 o superiore → \[Download Python](https://www.python.org/downloads/)

2\. Librerie richieste: pip install -r requirements.txt





N.B. Le librerie principali sono già incluse in Python (*tkinter, heapq, json, pathlib*).



Per la generazione dei piani è necessario FastDownward che è scaricabile qui:(https://github.com/aibasel/downward)









**Istruzioni per eseguire il codice**



 1. **Generare un piano con FastDownward**



  Da terminale, posizionarsi nella cartella del progetto e lanciare:



   *python fast-downward.py domain.pddl problem1.pddl --search "astar(blind())"*

*python fast-downward.py domain.pddl problem2.pddl --search "astar(blind())"*

*python fast-downward.py domain.pddl problem3.pddl --search "astar(blind())"*





  Verrà generato un file "sas\_plan".





 2. **Avviare la simulazione**



  - Su *Windows*: python taxi\_visualizer.py

  - Su *macOS/Linux*: python3 taxi\_visualizer.py





 3. **Selezionare lo scenario**



   Dalla GUI è possibile scegliere:



    - Problem1,

    - Problem2

    - Problem3,

    - avviare l’animazione,

    - modificarne la velocità

    - resettare.

 

