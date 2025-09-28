#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Taxi Intelligenti - Entry Point Principale
==================================================

Punto di ingresso principale per l'applicazione di gestione taxi intelligenti.
Avvia l'interfaccia grafica e gestisce l'inizializzazione del sistema.

Utilizzo:
    python main.py

Autore: Progetto Sistemi Intelligenti
Versione: 2.0.0
"""

import sys
from pathlib import Path

# Aggiungi il percorso del sistema taxi al path Python
sys.path.insert(0, str(Path(__file__).parent))

from sistema_taxi.interfaccia.finestra_principale import avvia_interfaccia_grafica
from sistema_taxi.configurazione.costanti import configura_encoding_console


def stampa_banner():
    """Stampa il banner di avvio dell'applicazione."""
    print("=" * 70)
    print("🚖 SISTEMA TAXI INTELLIGENTI 🚖")
    print("=" * 70)
    print("Sistema di ottimizzazione percorsi taxi urbani")
    print("Università - Progetto Sistemi Intelligenti")
    print("Versione 2.0.0 - Architettura Modulare")
    print("=" * 70)
    print()


def verifica_dipendenze():
    """
    Verifica che tutte le dipendenze necessarie siano disponibili.
    
    Returns:
        bool: True se tutte le dipendenze sono soddisfatte
    """
    dipendenze_mancanti = []
    
    # Verifica Tkinter
    try:
        import tkinter
        import tkinter.ttk
    except ImportError:
        dipendenze_mancanti.append("tkinter (GUI)")
    
    # Verifica moduli standard
    moduli_standard = ['json', 'pathlib', 'heapq', 'sys']
    for modulo in moduli_standard:
        try:
            __import__(modulo)
        except ImportError:
            dipendenze_mancanti.append(f"{modulo} (standard library)")
    
    if dipendenze_mancanti:
        print("❌ ERRORE: Dipendenze mancanti:")
        for dipendenza in dipendenze_mancanti:
            print(f"   - {dipendenza}")
        print("\nInstalla le dipendenze mancanti e riprova.")
        return False
    
    print("✅ Tutte le dipendenze sono soddisfatte")
    return True


def verifica_struttura_progetto():
    """
    Verifica che la struttura del progetto sia corretta.
    
    Returns:
        bool: True se la struttura è corretta
    """
    percorso_base = Path(__file__).parent
    
    # Cartelle richieste
    cartelle_richieste = [
        "sistema_taxi",
        "sistema_taxi/configurazione",
        "sistema_taxi/algoritmi", 
        "sistema_taxi/pianificazione",
        "sistema_taxi/gestione_file",
        "sistema_taxi/interfaccia"
    ]
    
    # File richiesti
    file_richiesti = [
        "sistema_taxi/__init__.py",
        "sistema_taxi/configurazione/costanti.py",
        "sistema_taxi/configurazione/modelli.py",
        "sistema_taxi/algoritmi/ricerca_percorso.py",
        "sistema_taxi/algoritmi/ottimizzazione.py",
        "sistema_taxi/pianificazione/gestore_taxi.py",
        "sistema_taxi/pianificazione/costruttore_rotte.py",
        "sistema_taxi/gestione_file/lettore_file.py",
        "sistema_taxi/interfaccia/finestra_principale.py"
    ]
    
    elementi_mancanti = []
    
    # Verifica cartelle
    for cartella in cartelle_richieste:
        percorso_cartella = percorso_base / cartella
        if not percorso_cartella.exists() or not percorso_cartella.is_dir():
            elementi_mancanti.append(f"Cartella: {cartella}")
    
    # Verifica file
    for file in file_richiesti:
        percorso_file = percorso_base / file
        if not percorso_file.exists() or not percorso_file.is_file():
            elementi_mancanti.append(f"File: {file}")
    
    if elementi_mancanti:
        print("❌ ERRORE: Struttura progetto incompleta:")
        for elemento in elementi_mancanti:
            print(f"   - {elemento}")
        print("\nRipristina la struttura completa del progetto.")
        return False
    
    print("✅ Struttura del progetto corretta")
    return True


def mostra_informazioni_sistema():
    """Mostra informazioni utili sul sistema."""
    print("📋 INFORMAZIONI SISTEMA:")
    print(f"   • Python: {sys.version.split()[0]}")
    print(f"   • Piattaforma: {sys.platform}")
    print(f"   • Percorso progetto: {Path(__file__).parent}")
    print()
    
    print("🎮 CONTROLLI:")
    print("   • Seleziona un problema (1-4) dai pulsanti")
    print("   • Usa ▶ Play per avviare l'animazione")
    print("   • Usa ⏸ Pause per mettere in pausa")
    print("   • Usa ⟲ Reset per riavviare")
    print("   • Modifica la velocità nel campo 'Velocità (ms)'")
    print()
    
    print("🚖 TIPI DI PROBLEMI:")
    print("   • Problema 1: Taxi singolo standard")
    print("   • Problema 2: Taxi condiviso")
    print("   • Problema 3: Sistema multi-taxi automatico")
    print("   • Problema 4: Sistema multi-taxi avanzato")
    print()


def main():
    """
    Funzione principale dell'applicazione.
    
    Gestisce l'inizializzazione e l'avvio del sistema taxi.
    """
    # Configura encoding console
    configura_encoding_console()
    
    # Stampa banner
    stampa_banner()
    
    print("🔍 Verifica sistema in corso...")
    
    # Verifica dipendenze
    if not verifica_dipendenze():
        sys.exit(1)
    
    # Verifica struttura progetto
    if not verifica_struttura_progetto():
        sys.exit(1)
    
    print()
    
    # Mostra informazioni
    mostra_informazioni_sistema()
    
    print("🚀 Avvio interfaccia grafica...")
    print("   (Chiudi la finestra o premi Ctrl+C per uscire)")
    print()
    
    try:
        # Avvia l'interfaccia grafica
        avvia_interfaccia_grafica()
        
    except KeyboardInterrupt:
        print("\n")
        print("👋 Applicazione chiusa dall'utente")
        
    except ImportError as e:
        print(f"\n❌ ERRORE: Impossibile importare moduli necessari: {e}")
        print("Verifica che tutti i file del progetto siano presenti.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERRORE CRITICO: {e}")
        print("Controlla i log per maggiori dettagli.")
        sys.exit(1)
    
    print("✅ Applicazione terminata correttamente")


if __name__ == "__main__":
    main()
