"""
Costanti e Configurazioni del Sistema
====================================

Definisce tutte le costanti globali utilizzate dal sistema di gestione taxi.
"""

import sys

# =============================================================================
# CONFIGURAZIONE DEBUG
# =============================================================================

DEBUG = False

# =============================================================================
# CONFIGURAZIONE GRIGLIA
# =============================================================================

# Dimensioni della griglia urbana
GRIGLIA_LARGHEZZA = 15  # numero di colonne
GRIGLIA_ALTEZZA = 10    # numero di righe

# Dimensioni grafiche
PIXEL_PER_CELLA = 40    # pixel per ogni cella nella visualizzazione

# =============================================================================
# POSIZIONI SPECIALI
# =============================================================================

# Posizione della stazione ferroviaria (angolo alto-sinistra)
STAZIONE = (0, GRIGLIA_ALTEZZA - 1)  # (0, 9)

# Lista degli ostacoli fissi sulla griglia
OSTACOLI = [
    (5, 5), (5, 6), (5, 7), (5, 8),  # barriera verticale centrale
    (8, 2), (9, 2),                   # ostacoli isolati
    (0, 4),                           # ostacolo vicino alla stazione
]

# =============================================================================
# CONFIGURAZIONE TAXI
# =============================================================================

# Identificatori tipi di taxi
TAXI_SINGOLO = "taxi_singolo"
TAXI_CONDIVISO = "taxi_condiviso"

# Capacità massima taxi
CAPACITA_TAXI_SINGOLO = 1
CAPACITA_TAXI_CONDIVISO = 2

# =============================================================================
# CONFIGURAZIONE COSTI
# =============================================================================

# Costo per ogni step di movimento (in euro)
COSTO_PER_STEP = 1.0

# =============================================================================
# CONFIGURAZIONE ALGORITMI
# =============================================================================

# Raggio massimo per accoppiamento clienti (distanza Manhattan)
RAGGIO_ACCOPPIAMENTO_DEFAULT = 2

# =============================================================================
# CONFIGURAZIONE INTERFACCIA GRAFICA
# =============================================================================

# Dimensioni finestra principale
LARGHEZZA_FINESTRA = 1020
ALTEZZA_FINESTRA = 512

# Velocità animazione default (millisecondi)
VELOCITA_ANIMAZIONE_DEFAULT = 200

# Colori interfaccia
COLORI = {
    'stazione': '#2ecc71',
    'stazione_bordo': '#1b8f4a',
    'cliente': '#3498db',
    'cliente_bordo': '#21618c',
    'cliente_prelevato': '#95a5a6',   # Grigio per clienti prelevati
    'cliente_prelevato_bordo': '#7f8c8d',  # Bordo grigio per clienti prelevati
    'taxi_singolo': '#e74c3c',
    'taxi_condiviso': '#9b59b6',
    'taxi_bordo': '#2c3e50',
    'ostacolo': 'black',
    'griglia': '#ddd',
    'traccia_singolo': '#e67e22',     # Arancione per taxi singolo
    'traccia_condiviso': '#8e44ad',   # Viola per taxi condiviso  
    #'traccia_generale': '#95a5a6',    # Grigio generale
    #'traccia_completata': '#95a5a6',  # Grigio per percorsi completati
    'sfondo': 'white'
}

# =============================================================================
# CONFIGURAZIONE LOGGING
# =============================================================================

def configura_encoding_console():
    """
    Configura l'encoding UTF-8 per stdout/stderr se necessario.
    Previene errori di visualizzazione caratteri speciali.
    """
    try:
        if sys.stdout and (not sys.stdout.encoding or "utf" not in sys.stdout.encoding.lower()):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and (not sys.stderr.encoding or "utf" not in sys.stderr.encoding.lower()):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configura automaticamente all'import
configura_encoding_console()

# =============================================================================
# PERCORSI FILE
# =============================================================================

# Percorsi relativi per i file di input
PERCORSI_PIANI = {
    1: "PDDL/plans/plan1",
    2: "PDDL/plans/plan2", 
    3: "PDDL/plans/plan3",
    4: "PDDL/plans/plan4",
    5: "PDDL/plans/plan5"
}

PERCORSI_POSIZIONI = {
    1: "PDDL/locations/location1.json",
    2: "PDDL/locations/location2.json",
    3: "PDDL/locations/location3.json", 
    4: "PDDL/locations/location4.json",
    5: "PDDL/locations/location5.json"
}

# =============================================================================
# CONFIGURAZIONE PROBLEMI
# =============================================================================

# Configurazione per ogni problema
CONFIGURAZIONE_PROBLEMI = {
    1: {
        'nome': 'Problema 1',
        'descrizione': 'Taxi singolo standard',
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': False
    },
    2: {
        'nome': 'Problema 2', 
        'descrizione': 'Taxi condiviso',
        'taxi_condiviso': True,
        'colore_taxi': COLORI['taxi_condiviso'],
        'usa_multi_taxi': False
    },
    3: {
        'nome': 'Problema 3',
        'descrizione': 'Sistema multi-taxi automatico',
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': True
    },
    4: {
        'nome': 'Problema 4',
        'descrizione': 'Sistema multi-taxi automatico avanzato', 
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': True
    },
    5: {
        'nome': 'Problema 5',
        'descrizione': 'Sistema multi-taxi con 20 clienti', 
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': True
    }
}
