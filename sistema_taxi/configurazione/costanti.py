import sys

# Configurazione griglia
GRIGLIA_LARGHEZZA = 15
GRIGLIA_ALTEZZA = 10
PIXEL_PER_CELLA = 40

# Posizioni importanti
STAZIONE = (0, GRIGLIA_ALTEZZA - 1)  # Stazione ferroviaria
OSTACOLI = [
    (5, 5), (5, 6), (5, 7), (5, 8),  # Barriera verticale
    (8, 2), (9, 2),                   # Ostacoli isolati
    (0, 4),                           # Vicino stazione
]

# Tipi taxi
TAXI_SINGOLO = "taxi_singolo"
TAXI_CONDIVISO = "taxi_condiviso"

# Parametri sistema
COSTO_PER_STEP = 1.0
RAGGIO_ACCOPPIAMENTO_DEFAULT = 2

# Interfaccia grafica
VELOCITA_ANIMAZIONE_DEFAULT = 200

COLORI = {
    'stazione': '#2ecc71',
    'stazione_bordo': '#1b8f4a',
    'cliente': '#3498db',
    'cliente_bordo': '#21618c',
    'cliente_prelevato': '#95a5a6',
    'cliente_prelevato_bordo': '#7f8c8d',
    'taxi_singolo': '#e74c3c',
    'taxi_condiviso': '#9b59b6',
    'taxi_bordo': '#2c3e50',
    'ostacolo': 'black',
    'griglia': '#ddd',
    'traccia_singolo': '#e67e22',
    'traccia_condiviso': '#8e44ad',
    'sfondo': 'white'
}

def configura_encoding_console():
    try:
        if sys.stdout and (not sys.stdout.encoding or "utf" not in sys.stdout.encoding.lower()):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and (not sys.stderr.encoding or "utf" not in sys.stderr.encoding.lower()):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

configura_encoding_console()

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

CONFIGURAZIONE_PROBLEMI = {
    1: {
        'nome': 'Problema 1',
        'descrizione': 'Taxi singolo',
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
        'descrizione': 'Multi-taxi automatico',
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': True
    },
    4: {
        'nome': 'Problema 4',
        'descrizione': 'Multi-taxi avanzato', 
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': True
    },
    5: {
        'nome': 'Problema 5',
        'descrizione': 'Multi-taxi 20 clienti', 
        'taxi_condiviso': False,
        'colore_taxi': COLORI['taxi_singolo'],
        'usa_multi_taxi': True
    }
}
