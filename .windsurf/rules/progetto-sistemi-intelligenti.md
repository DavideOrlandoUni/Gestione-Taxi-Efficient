---
trigger: always_on
---

# Descrizione del progetto

Affrontare la gestione efficiente degli spostamenti dei taxi nei pressi di una stazione
ferroviaria rappresenta una sfida cruciale nell’ambito dei sistemi intelligenti.
In scenari urbani ad alta densità, i flussi dei taxi risultano spesso disorganizzati: la
concentrazione di più veicoli nello stesso punto, i tempi di attesa non coordinati e
l’assenza di un sistema di smistamento ottimizzato possono generare congestione e
inefficienze, con ripercussioni sia sui conducenti sia sui passeggeri.

Il nostro obiettivo è stato quello di progettare e simulare un sistema in grado di
ottimizzare i movimenti dei taxi, riducendo i tempi di percorrenza e massimizzando
l’efficienza degli spostamenti, in modo che i veicoli possano viaggiare, quando possibile,
con il numero massimo di clienti consentito.

Per rappresentare il contesto, la città è stata modellata come una griglia 15x10: ogni cella corrisponde a un incrocio; il quadrato verde, posto in alto a sinistra (0, 9), identifica la stazione ferroviaria e rappresenta sia il punto di partenza sia il punto di arrivo di ciascunmtaxi; i cerchi azzurri indicano i punti in cui vengono localizzati i clienti al momento della prenotazione della corsa, mentre il quadrato rosso rappresenta il taxi, che si muove con spostamenti ortogonali. 

Sono stati introdotti, inoltre, ostacoli strutturali (celle bloccate) rappresentati da quadrati neri, che obbligano il pathfinding a deviare, rendendo necessaria l’integrazione dell’algoritmo di ricerca A* per il calcolo del percorso ottimale.

L’obiettivo rimane la minimizzazione dei passi, calcolato step per step, garantendo la
corretta gestione delle operazioni di pick-up e drop-off.

Un aspetto centrale del sistema è la distinzione tra taxi normali, adibiti al trasporto di un solo cliente, e taxi condivisibili (shareable), che per semplicità progettuale possono
trasportare al massimo due clienti.

Questo approccio consente di rappresentare in modo chiaro la quantità di clienti in
attesa, la loro posizione e la distanza rispetto alla stazione ferroviaria