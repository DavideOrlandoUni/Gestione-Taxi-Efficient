# Sistema Taxi Intelligenti

Sistema di gestione ottimizzata per taxi in ambiente urbano con architettura modulare.

## 📋 Descrizione

Il progetto simula un sistema intelligente per la gestione di taxi che operano in una città modellata come griglia 15x10. Il sistema ottimizza i movimenti dei taxi per ridurre i tempi di percorrenza e massimizzare l'efficienza, gestendo sia taxi singoli (1 cliente) che condivisi (max 2 clienti).

### Caratteristiche Principali

- **Griglia 15x10**: Ogni cella rappresenta un incrocio
- **Stazione Ferroviaria**: Posizione (0,9) - punto di partenza e arrivo
- **Ostacoli**: Celle bloccate che richiedono pathfinding
- **Algoritmo A***: Per calcolo percorso ottimale evitando ostacoli
- **Taxi Singoli**: Trasportano 1 cliente alla volta
- **Taxi Condivisi**: Trasportano max 2 clienti contemporaneamente
- **Accoppiamento Intelligente**: Clienti vicini vengono accoppiati automaticamente
- **Interfaccia Grafica**: Visualizzazione e animazione dei percorsi
- **Calcolo Costi**: Ripartizione automatica dei costi per cliente
- **Architettura Modulare**: Codice organizzato per ruoli specifici
- **Visualizzazione Percorsi**: Tracce colorate dei taxi in tempo reale
- **Gestione Dinamica Clienti**: Rimozione automatica clienti prelevati

## 🚀 Avvio Rapido

### Requisiti
- Python 3.6 o superiore
- Tkinter (incluso in Python standard)

### Esecuzione
```bash
python main.py
```

## 🏗️ Architettura Modulare

Il progetto segue le **best practices** con una struttura modulare ben organizzata:

```
PROGETTO_/
├── main.py                          # Entry point principale
├── README.md                        # Documentazione
├── sistema_taxi/                    # Package principale
│   ├── __init__.py
│   ├── configurazione/              # Costanti e modelli dati
│   │   ├── __init__.py
│   │   ├── costanti.py             # Configurazioni globali
│   │   └── modelli.py              # Classi dati (PianoViaggio, etc.)
│   ├── algoritmi/                   # Algoritmi di ottimizzazione
│   │   ├── __init__.py
│   │   ├── ricerca_percorso.py     # A* e pathfinding
│   │   └── ottimizzazione.py       # Accoppiamento clienti
│   ├── pianificazione/              # Logica di pianificazione
│   │   ├── __init__.py
│   │   ├── gestore_taxi.py         # Pianificazione taxi
│   │   └── costruttore_rotte.py    # Costruzione percorsi
│   ├── gestione_file/               # I/O e gestione file
│   │   ├── __init__.py
│   │   └── lettore_file.py         # Lettura piani e posizioni
│   └── interfaccia/                 # Interfaccia grafica
│       ├── __init__.py
│       └── finestra_principale.py  # GUI Tkinter
└── PDDL/                           # File di input (opzionali)
    ├── plans/
    │   ├── plan1, plan2, plan3, plan4
    └── locations/
        ├── location1.json, location2.json, etc.
```

### 🎯 Separazione delle Responsabilità

- **`configurazione/`**: Gestisce costanti, configurazioni e modelli dati
- **`algoritmi/`**: Implementa A*, Manhattan e ottimizzazione percorsi
- **`pianificazione/`**: Logica di pianificazione taxi singoli/condivisi
- **`gestione_file/`**: Lettura file piani SAS e posizioni JSON
- **`interfaccia/`**: Interfaccia grafica Tkinter e controlli utente

## 🎮 Come Utilizzare

### Interfaccia Grafica

1. **Avvio**: Esegui `python main.py`
2. **Carica Problema**: Clicca su "Problema 1", "Problema 2", etc.
3. **Animazione**: Usa il pulsante "▶ Play" per avviare l'animazione
4. **Controlli**: 
   - "⏸ Pause" per mettere in pausa
   - "⟲ Reset" per riavviare
   - Modifica velocità nel campo "Velocità (ms)"

### Tipi di Problemi

- **Problema 1**: Taxi singolo standard
- **Problema 2**: Taxi condiviso
- **Problema 3**: Sistema multi-taxi automatico
- **Problema 4**: Sistema multi-taxi automatico

### Visualizzazione

- **Quadrato Verde**: Stazione ferroviaria (ST)
- **Cerchi Azzurri**: Clienti con etichette (scompaiono quando prelevati)
- **Quadrati Neri**: Ostacoli
- **Quadrato Rosso**: Taxi singolo
- **Quadrato Viola**: Taxi condiviso
- **Linee Arancioni**: Traccia percorso taxi singolo
- **Linee Viola**: Traccia percorso taxi condiviso
- **Punti Colorati**: Tappe del percorso

## 🔧 Configurazione

### Parametri Modificabili

Nel file `taxi_manager.py`, sezione "CONFIGURAZIONE E COSTANTI GLOBALI":

```python
# Dimensioni griglia
GRIGLIA_LARGHEZZA = 15
GRIGLIA_ALTEZZA = 10

# Posizione stazione
STAZIONE = (0, 9)

# Ostacoli
OSTACOLI = [(5, 5), (5, 6), ...]

# Costo per step
COSTO_PER_STEP = 1.0

# Debug
DEBUG = True
```

## 🧮 Algoritmi Implementati

### 1. Algoritmo A*
- **Scopo**: Pathfinding ottimale evitando ostacoli
- **Euristica**: Distanza di Manhattan
- **Output**: Percorso più breve tra due punti

### 2. Accoppiamento Clienti
- **Strategia**: Greedy per distanza Manhattan
- **Raggio**: Configurabile (default: 2)
- **Evita Conflitti**: Un cliente per coppia massimo

### 3. Pianificazione Taxi
- **Singolo**: Visita cliente più vicino (greedy)
- **Condiviso**: Ottimizza ordine prelievo per coppie
- **Multi-taxi**: Separa clienti tra taxi singolo e condiviso

## 📊 Calcolo Costi

Il sistema calcola automaticamente:
- **Costo per step**: 1€ per movimento
- **Ripartizione**: Costo diviso tra clienti a bordo
- **Visualizzazione**: Dashboard in tempo reale

### Formula
```
Costo_Cliente = Σ(Costo_Step / Numero_Clienti_A_Bordo)
```

## 🛠️ Personalizzazione

### Aggiungere Nuovi Problemi

1. Crea file piano in `PDDL/plans/`
2. Crea file posizioni in `PDDL/locations/`
3. Aggiungi metodo nella classe `AppGestoreTaxi`:

```python
def carica_problema_5(self):
    self.carica_da_file(
        candidati_piano=[Path("PDDL/plans/plan5")],
        candidati_posizioni=[Path("PDDL/locations/location5.json")],
        titolo="Problema 5",
        usa_accoppiamento_automatico=True
    )
```

### Modificare Ostacoli

Modifica la lista `OSTACOLI` con nuove coordinate:
```python
OSTACOLI = [
    (x1, y1), (x2, y2), ...
]
```

## 🔍 Debug

Attiva il debug impostando `DEBUG = True` per vedere:
- Coppie candidate per accoppiamento
- Informazioni di caricamento file
- Statistiche di pianificazione

## 📝 Note Tecniche

### Semplificazioni Implementate
- **Nomi Funzioni**: Italiani e descrittivi
- **Commenti**: Estensivi in italiano
- **Struttura**: Modulo unico invece di 10 separati
- **Sintassi**: Python base, no type hints complessi
- **Dipendenze**: Solo librerie standard

### Compatibilità
- **Python**: 3.6+
- **OS**: Windows, macOS, Linux
- **GUI**: Tkinter (incluso in Python)

## 🎓 Progetto Universitario

Questo è un progetto per il corso di **Sistemi Intelligenti** che dimostra:
- Algoritmi di ricerca (A*)
- Ottimizzazione percorsi
- Interfacce grafiche
- Gestione stati complessi
- Programmazione orientata agli oggetti

---

**Autore**: Progetto Sistemi Intelligenti  
**Anno Accademico**: 2024/2025  
**Università**: [Nome Università]
