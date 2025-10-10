# Interfaccia grafica principale sistema taxi

import tkinter as tk
from tkinter import ttk

from ..configurazione.costanti import (
    GRIGLIA_LARGHEZZA, GRIGLIA_ALTEZZA, PIXEL_PER_CELLA, STAZIONE, OSTACOLI,
    TAXI_SINGOLO, TAXI_CONDIVISO, COSTO_PER_STEP, COLORI,
    PERCORSI_PIANI, PERCORSI_POSIZIONI, CONFIGURAZIONE_PROBLEMI,
    VELOCITA_ANIMAZIONE_DEFAULT
)
from ..configurazione.modelli import StatoAnimazione, ConfigProblema
from ..gestione_file.lettore_file import (
    trova_primo_file_esistente, leggi_azioni_da_piano, carica_posizioni_da_json,
    estrai_prima_mappatura_pickup
)
from ..pianificazione.costruttore_rotte import costruisci_viaggio_da_azioni
from ..pianificazione.gestore_taxi import costruisci_piani_taxi_singolo_e_condiviso


class FinestraPrincipale:
    # Finestra principale applicazione taxi
    
    def __init__(self, finestra_tk):
        # Inizializza finestra principale
        self.finestra = finestra_tk
        self.finestra.title("Sistema Taxi Intelligenti")
        
        # Stato dell'applicazione
        self.stato_animazione = StatoAnimazione()
        self.piano_multi_taxi = None
        self.piano_viaggio_singolo = None
        self.etichette_clienti = {}
        
        # Stato interfaccia grafica
        self.pixel_per_cella = PIXEL_PER_CELLA
        self.id_taxi_canvas = {}  # ID oggetti taxi nel canvas
        self.id_taxi_singolo = None
        self.id_clienti_canvas = {}  # ID oggetti clienti nel canvas
        self.clienti_prelevati = set()  # Set dei clienti già prelevati
        self.percorsi_completati = {}  # Percorsi completati per ogni cliente {cliente: [(x1,y1), (x2,y2), ...]}
        self.clienti_consegnati = set()  # Set dei clienti consegnati
        self.pulsanti_problemi = {}  # Riferimenti ai pulsanti dei problemi
        self.problema_attivo = None  # Numero del problema attualmente attivo alla stazione
        
        # Configurazione problema corrente
        self.configurazione_corrente = None
        
        # Variabili Tkinter per i costi
        self.var_costo_singolo = tk.StringVar(value="Taxi singolo: 0€")
        self.var_costo_condiviso = tk.StringVar(value="Taxi condiviso: 0€")
        self.etichette_costi_clienti = {}
        
        # Inizializza l'interfaccia
        self.crea_interfaccia()
        self.configura_layout()
        self.disegna_griglia_iniziale()
        
        # Carica il primo problema dopo che l'interfaccia è completamente renderizzata
        self.finestra.after(100, lambda: self.carica_problema(1))
    
    def crea_interfaccia(self):
        # Crea tutti i componenti dell'interfaccia grafica
        # Canvas principale per la griglia
        self.canvas = tk.Canvas(
            self.finestra,
            width=GRIGLIA_LARGHEZZA * PIXEL_PER_CELLA,
            height=GRIGLIA_ALTEZZA * PIXEL_PER_CELLA,
            bg=COLORI['sfondo']
        )
        self.canvas.grid(row=0, column=0, rowspan=20, sticky="nsew", padx=8, pady=8)
        self.canvas.bind("<Configure>", self.ridimensiona_canvas)
        
        # Pannello controlli laterale
        self.pannello_controlli = ttk.Frame(self.finestra)
        self.pannello_controlli.grid(row=0, column=1, sticky="ns", padx=8, pady=8)
        
        self.crea_controlli_problemi()
        self.crea_controlli_animazione()
        self.crea_dashboard_costi()
    
    def crea_controlli_problemi(self):
        # Crea i pulsanti per caricare i problemi
        ttk.Label(self.pannello_controlli, text="Problemi Disponibili", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        for numero in range(1, 6):  # Ora include anche il problema 5
            config = CONFIGURAZIONE_PROBLEMI[numero]
            pulsante = ttk.Button(
                self.pannello_controlli,
                text=f"{config['nome']}"
            )
            pulsante.config(command=self.crea_comando_carica_problema(numero))
            pulsante.pack(fill="x", pady=2)
            # Salva riferimento per aggiornamenti futuri
            self.pulsanti_problemi[numero] = pulsante
        
        ttk.Separator(self.pannello_controlli, orient="horizontal").pack(fill="x", pady=8)
    
    def crea_comando_carica_problema(self, numero):
        # Crea comando per caricare problema specifico
        def comando():
            self.carica_problema(numero)
        return comando
    
    def aggiorna_pulsanti_problemi(self, numero_attivo):
        # Aggiorna l'aspetto dei pulsanti problemi per evidenziare quello attivo
        self.problema_attivo = numero_attivo
        
        for numero, pulsante in self.pulsanti_problemi.items():
            if numero == numero_attivo:
                # Pulsante attivo: stile evidenziato
                pulsante.config(style="Accent.TButton")
            else:
                # Pulsanti inattivi: stile normale
                pulsante.config(style="TButton")
    
    def crea_controlli_animazione(self):
        # Crea i controlli per l'animazione
        ttk.Label(self.pannello_controlli, text="Controlli Animazione", 
                 font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Pulsanti play/pause e reset
        self.pulsante_play = ttk.Button(
            self.pannello_controlli, 
            text="▶ Play", 
            command=self.avvia_pausa_animazione
        )
        self.pulsante_reset = ttk.Button(
            self.pannello_controlli, 
            text="⟲ Reset", 
            command=self.reset_animazione
        )
        
        self.pulsante_play.pack(fill="x", pady=2)
        self.pulsante_reset.pack(fill="x", pady=2)
        
        # Controllo velocità
        ttk.Label(self.pannello_controlli, text="Velocità (ms)").pack(anchor="w", pady=(8, 0))
        self.variabile_velocita = tk.IntVar(value=VELOCITA_ANIMAZIONE_DEFAULT)
        ttk.Entry(self.pannello_controlli, textvariable=self.variabile_velocita, width=8).pack(anchor="w")
        
        ttk.Separator(self.pannello_controlli, orient="horizontal").pack(fill="x", pady=8)
    
    def crea_dashboard_costi(self):
        # Crea la dashboard per visualizzare i costi
        box_costi = ttk.LabelFrame(self.pannello_controlli, text="Dashboard Costi (€/step = 1)")
        box_costi.pack(fill="x", pady=(0, 8))
        
        # Costi totali taxi
        ttk.Label(box_costi, textvariable=self.var_costo_singolo, 
                 font=("Arial", 10, "bold"), foreground="black").pack(anchor="w", pady=2)
        ttk.Label(box_costi, textvariable=self.var_costo_condiviso, 
                 font=("Arial", 10, "bold"), foreground="black").pack(anchor="w", pady=2)
        
        # Frame per i costi individuali dei clienti
        self.frame_costi_clienti = ttk.Frame(box_costi)
        self.frame_costi_clienti.pack(fill="x", pady=(5, 0))
    
    def configura_layout(self):
        # Configura il layout responsivo della finestra
        self.finestra.rowconfigure(0, weight=1)
        self.finestra.columnconfigure(0, weight=1)
    
    def ridimensiona_canvas(self, evento):
        # Gestisce il ridimensionamento dinamico del canvas
        nuovo_pixel = max(8, min(evento.width // GRIGLIA_LARGHEZZA, evento.height // GRIGLIA_ALTEZZA))
        if nuovo_pixel == self.pixel_per_cella:
            return
        
        self.pixel_per_cella = nuovo_pixel
        self.canvas.config(
            width=GRIGLIA_LARGHEZZA * self.pixel_per_cella,
            height=GRIGLIA_ALTEZZA * self.pixel_per_cella
        )
        self.disegna_griglia_iniziale()
    
    def calcola_padding(self, frazione):
        # Calcola padding proporzionale alla dimensione della cella
        return max(2, int(self.pixel_per_cella * frazione))
    
    def converti_cella_in_pixel(self, posizione):
        # Converte coordinate cella in pixel canvas
        x, y = posizione
        # Inverti y per avere (0,0) in basso a sinistra
        y_canvas = GRIGLIA_ALTEZZA - 1 - y
        
        x1 = x * self.pixel_per_cella
        y1 = y_canvas * self.pixel_per_cella
        x2 = x1 + self.pixel_per_cella
        y2 = y1 + self.pixel_per_cella
        
        return x1, y1, x2, y2
    
    def disegna_griglia_iniziale(self):
        # Disegna la griglia di base con linee e ostacoli
        # Cancella elementi precedenti
        self.canvas.delete("griglia", "ostacolo")
        
        larghezza_canvas = GRIGLIA_LARGHEZZA * self.pixel_per_cella
        altezza_canvas = GRIGLIA_ALTEZZA * self.pixel_per_cella
        
        # Linee verticali
        for x in range(GRIGLIA_LARGHEZZA + 1):
            x_pos = x * self.pixel_per_cella
            self.canvas.create_line(x_pos, 0, x_pos, altezza_canvas, 
                                  fill=COLORI['griglia'], tags="griglia")
        
        # Linee orizzontali
        for y in range(GRIGLIA_ALTEZZA + 1):
            y_pos = y * self.pixel_per_cella
            self.canvas.create_line(0, y_pos, larghezza_canvas, y_pos, 
                                  fill=COLORI['griglia'], tags="griglia")
        
        # Disegna ostacoli
        for ostacolo_x, ostacolo_y in OSTACOLI:
            x1, y1, x2, y2 = self.converti_cella_in_pixel((ostacolo_x, ostacolo_y))
            self.canvas.create_rectangle(
                x1 + 4, y1 + 4, x2 - 4, y2 - 4,
                fill=COLORI['ostacolo'], outline=COLORI['ostacolo'], tags="ostacolo"
            )
    
    def carica_problema(self, numero_problema):
        # Carica problema specifico
        if numero_problema not in CONFIGURAZIONE_PROBLEMI:
            return
        
        config = CONFIGURAZIONE_PROBLEMI[numero_problema]
        
        # Crea configurazione problema
        self.configurazione_corrente = ConfigProblema(
            numero=numero_problema,
            nome=config['nome'],
            percorso_piano=PERCORSI_PIANI[numero_problema],
            percorso_posizioni=PERCORSI_POSIZIONI[numero_problema],
            usa_multi_taxi=config['usa_multi_taxi'],
            taxi_condiviso=config['taxi_condiviso'],
            colore_taxi=config['colore_taxi']
        )
        
        self.carica_da_configurazione(self.configurazione_corrente)
        self.aggiorna_pulsanti_problemi(numero_problema)
    
    def carica_da_configurazione(self, configurazione):
        # Carica problema da configurazione
        # Trova i file
        percorso_piano = trova_primo_file_esistente([configurazione.percorso_piano])
        if not percorso_piano:
            return
        
        percorso_posizioni = trova_primo_file_esistente([configurazione.percorso_posizioni])
        if not percorso_posizioni:
            return
        
        # Carica i dati
        azioni = leggi_azioni_da_piano(percorso_piano)
        posizioni = carica_posizioni_da_json(percorso_posizioni)
        
        if configurazione.usa_multi_taxi:
            # Modalità multi-taxi con accoppiamento automatico
            mappa_pickup = estrai_prima_mappatura_pickup(azioni)
            self.piano_multi_taxi = costruisci_piani_taxi_singolo_e_condiviso(
                mappa_pickup, posizioni, raggio_coppia=2
            )
            self.piano_viaggio_singolo = None
            self.etichette_clienti = self.piano_multi_taxi.etichette
        else:
            # Modalità taxi singolo
            viaggio, etichette = costruisci_viaggio_da_azioni(azioni, posizioni)
            self.piano_multi_taxi = None
            self.piano_viaggio_singolo = viaggio
            self.etichette_clienti = etichette
        
        # Aggiorna interfaccia
        self.finestra.title(f"Sistema Taxi Intelligenti - {configurazione.nome}")
        self.reset_stato()
        self.ridisegna_scenario_completo()
        
        # Forza aggiornamento completo dell'interfaccia
        self.finestra.update_idletasks()
        self.finestra.update()
        
    
    def reset_stato(self):
        # Resetta lo stato dell'animazione e dei costi
        self.stato_animazione.reset()
        
        # Inizializza gli indici per i taxi correnti
        if self.piano_multi_taxi:
            for nome_taxi in self.piano_multi_taxi.piani.keys():
                self.stato_animazione.aggiorna_taxi(nome_taxi, 0)
        else:
            self.stato_animazione.aggiorna_taxi("singolo", 0)
        
        # Inizializza i costi per i clienti correnti
        for cliente in self.etichette_clienti.keys():
            self.stato_animazione.costi_clienti[cliente] = 0.0
        
        # Pulisce le etichette costi clienti dall'interfaccia
        for widget in self.frame_costi_clienti.winfo_children():
            widget.destroy()
        self.etichette_costi_clienti.clear()
        
        # Reset stato clienti
        self.clienti_prelevati.clear()
        self.clienti_consegnati.clear()
        self.percorsi_completati.clear()
        self.id_clienti_canvas.clear()
        
        self.aggiorna_visualizzazione_costi()
    
    def ridisegna_scenario_completo(self):
        # Ridisegna l'intero scenario con griglia, stazione, clienti e taxi
        self.disegna_griglia_iniziale()
        self.canvas.delete("stazione", "stazione_primo_piano", "stazione_testo", "taxi", "cliente", "traccia")
        
        # Disegna i clienti
        self.disegna_clienti()
        
        # Reset ID taxi
        self.id_taxi_singolo = None
        self.id_taxi_canvas.clear()
        
        # Disegna taxi
        if self.piano_multi_taxi:
            self.disegna_taxi_multi()
        elif self.piano_viaggio_singolo:
            self.disegna_taxi_singolo()
        
        # Disegna la stazione ferroviaria (in primo piano)
        self.disegna_stazione()
        
        # Disegna tracce iniziali
        self.disegna_tracce_iniziali()
    
    def disegna_stazione(self):
        # Disegna la stazione ferroviaria (in primo piano)
        x1, y1, x2, y2 = self.converti_cella_in_pixel(STAZIONE)
        padding = self.calcola_padding(0.15)
        
        # Crea rettangolo stazione con z-order alto
        self.canvas.create_rectangle(
            x1 + padding, y1 + padding, x2 - padding, y2 - padding,
            fill=COLORI['stazione'], outline=COLORI['stazione_bordo'], 
            width=3, tags="stazione_primo_piano"
        )
        
        # Testo ST centrato e adattivo
        centro_x = (x1 + x2) // 2
        centro_y = (y1 + y2) // 2
        dimensione_font = max(8, int(PIXEL_PER_CELLA * 0.25))
        
        self.canvas.create_text(
            centro_x, centro_y,
            text="ST", fill="white", 
            font=("Arial", dimensione_font, "bold"),
            tags="stazione_testo"
        )
    
    def disegna_clienti(self):
        # Disegna tutti i clienti sulla griglia
        for etichetta, posizione in self.etichette_clienti.items():
            x1, y1, x2, y2 = self.converti_cella_in_pixel(posizione)
            padding_cliente = self.calcola_padding(0.25)
            
            # Determina il colore in base allo stato del cliente
            if etichetta in self.clienti_prelevati:
                # Cliente prelevato: cerchio grigio
                colore_riempimento = COLORI['cliente_prelevato']
                colore_bordo = COLORI['cliente_prelevato_bordo']
                colore_testo = "white"
            else:
                # Cliente non ancora prelevato: cerchio blu
                colore_riempimento = COLORI['cliente']
                colore_bordo = COLORI['cliente_bordo']
                colore_testo = "white"
            
            # Disegna il cerchio del cliente
            id_cerchio = self.canvas.create_oval(
                x1 + padding_cliente, y1 + padding_cliente,
                x2 - padding_cliente, y2 - padding_cliente,
                fill=colore_riempimento, outline=colore_bordo, 
                width=2, tags=f"cliente {etichetta}"
            )
            
            # Disegna il testo del cliente
            id_testo = self.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=etichetta, fill=colore_testo, font=("Arial", 9, "bold"),
                tags=f"cliente {etichetta}"
            )
            
            # Memorizza gli ID per poterli aggiornare successivamente
            self.id_clienti_canvas[etichetta] = (id_cerchio, id_testo)
    
    def disegna_taxi_multi(self):
        # Disegna i taxi per il sistema multi-taxi
        colori_taxi = {TAXI_SINGOLO: COLORI['taxi_singolo'], TAXI_CONDIVISO: COLORI['taxi_condiviso']}
        
        for nome_taxi, piano in self.piano_multi_taxi.piani.items():
            if not piano.percorso:
                continue
            
            # Assicurati che il percorso inizi dalla stazione
            if piano.percorso[0] != STAZIONE:
                piano.percorso = [STAZIONE] + piano.percorso
            
            # Disegna il taxi
            x1, y1, x2, y2 = self.converti_cella_in_pixel(piano.percorso[0])
            padding_taxi = self.calcola_padding(0.20)
            id_taxi = self.canvas.create_rectangle(
                x1 + padding_taxi, y1 + padding_taxi,
                x2 - padding_taxi, y2 - padding_taxi,
                fill=colori_taxi.get(nome_taxi, COLORI['taxi_singolo']),
                outline=COLORI['taxi_bordo'], width=2, tags=f"taxi {nome_taxi}"
            )
            
            self.id_taxi_canvas[nome_taxi] = id_taxi
            self.stato_animazione.aggiorna_taxi(nome_taxi, 0)
    
    def disegna_taxi_singolo(self):
        # Disegna il taxi per modalità singola
        if not self.piano_viaggio_singolo or not self.piano_viaggio_singolo.percorso:
            return
        
        x1, y1, x2, y2 = self.converti_cella_in_pixel(self.piano_viaggio_singolo.percorso[0])
        padding_taxi = self.calcola_padding(0.20)
        
        colore = (self.configurazione_corrente.colore_taxi 
                 if self.configurazione_corrente else COLORI['taxi_singolo'])
        
        self.id_taxi_singolo = self.canvas.create_rectangle(
            x1 + padding_taxi, y1 + padding_taxi,
            x2 - padding_taxi, y2 - padding_taxi,
            fill=colore, outline=COLORI['taxi_bordo'], width=2, tags="taxi"
        )
        
        # Inizializza l'indice per il taxi singolo
        self.stato_animazione.aggiorna_taxi("singolo", 0)
    
    def disegna_tracce_iniziali(self):
        # Disegna le tracce iniziali dei percorsi
        # Le tracce vengono disegnate dinamicamente durante l'animazione
        pass
    
    def marca_cliente_prelevato(self, etichetta_cliente):
        # Marca cliente prelevato (colore grigio)
        if etichetta_cliente in self.id_clienti_canvas:
            id_cerchio, id_testo = self.id_clienti_canvas[etichetta_cliente]
            
            # Cambia il colore del cerchio in grigio
            self.canvas.itemconfig(id_cerchio, 
                                 fill=COLORI['cliente_prelevato'], 
                                 outline=COLORI['cliente_prelevato_bordo'])
            
            # Aggiungi ai clienti prelevati
            self.clienti_prelevati.add(etichetta_cliente)
    
    def inizia_tracciamento_percorso(self, etichetta_cliente, percorso_taxi, indice_prelievo):
        # Inizia tracciamento percorso cliente prelevato
        # Salva percorso prelievo-stazione
        if etichetta_cliente not in self.percorsi_completati:
            # Percorso stazione-cliente + cliente-stazione
            percorso_verso_cliente = percorso_taxi[:indice_prelievo + 1]
            self.percorsi_completati[etichetta_cliente] = {
                'percorso_verso_cliente': percorso_verso_cliente,
                'percorso_verso_stazione': [],
                'indice_prelievo': indice_prelievo,
                'completato': False
            }
    
    def aggiorna_tracciamento_percorso(self, etichetta_cliente, percorso_taxi, indice_corrente):
        # Aggiorna tracciamento percorso cliente a bordo
        if etichetta_cliente in self.percorsi_completati and not self.percorsi_completati[etichetta_cliente]['completato']:
            # Aggiorna percorso verso stazione
            indice_prelievo = self.percorsi_completati[etichetta_cliente]['indice_prelievo']
            if indice_corrente > indice_prelievo:
                self.percorsi_completati[etichetta_cliente]['percorso_verso_stazione'] = percorso_taxi[indice_prelievo:indice_corrente + 1]
    
    def completa_tracciamento_percorso(self, etichetta_cliente):
        # Completa tracciamento e cancella traccia completata
        if etichetta_cliente in self.percorsi_completati:
            self.percorsi_completati[etichetta_cliente]['completato'] = True
            self.clienti_consegnati.add(etichetta_cliente)
            
            # Cancella la traccia completata
            self.cancella_traccia_cliente(etichetta_cliente)
    
    def cancella_traccia_cliente(self, etichetta_cliente):
        # Cancella traccia specifica cliente
        # Cancella le tracce di questo cliente per entrambi i tipi di taxi
        self.canvas.delete(f"traccia_cliente_{etichetta_cliente}_{TAXI_SINGOLO}")
        self.canvas.delete(f"traccia_cliente_{etichetta_cliente}_{TAXI_CONDIVISO}")
    
    def disegna_tracce_clienti_attivi(self, piano, indice_corrente, nome_taxi):
        # Disegna tracce per clienti attualmente a bordo
        clienti_a_bordo = self.calcola_clienti_a_bordo(piano, indice_corrente)
        
        # Cancella tracce dei clienti non più a bordo
        for cliente_esistente in list(self.percorsi_completati.keys()):
            if cliente_esistente not in clienti_a_bordo or self.percorsi_completati[cliente_esistente]['completato']:
                self.canvas.delete(f"traccia_cliente_{cliente_esistente}_{nome_taxi}")
        
        # Disegna traccia per ogni cliente a bordo
        for cliente in clienti_a_bordo:
            if cliente in self.percorsi_completati and not self.percorsi_completati[cliente]['completato']:
                self.disegna_traccia_cliente_attivo(cliente, piano, indice_corrente, nome_taxi)
    
    def disegna_traccia_cliente_attivo(self, etichetta_cliente, piano, indice_corrente, nome_taxi):
        # Disegna traccia per cliente attivo
        if etichetta_cliente not in self.percorsi_completati:
            return
            
        dati_percorso = self.percorsi_completati[etichetta_cliente]
        indice_prelievo = dati_percorso['indice_prelievo']
        
        # Colore traccia basato su tipo taxi
        colore_traccia = COLORI['traccia_singolo'] if nome_taxi == TAXI_SINGOLO else COLORI['traccia_condiviso']
        
        # Disegna percorso dal prelievo alla posizione corrente
        if indice_corrente > indice_prelievo:
            percorso_attivo = piano.percorso[indice_prelievo:indice_corrente + 1]
            # Tag unico per cliente e tipo taxi
            tag_unico = f"traccia_cliente_{etichetta_cliente}_{nome_taxi}"
            self.disegna_traccia_percorso(
                percorso_attivo, 
                len(percorso_attivo) - 1, 
                colore_traccia, 
                tag_unico
            )
    
    def disegna_traccia_percorso(self, percorso, fino_a_indice, colore_traccia=None, nome_taxi=None):
        # Disegna traccia percorso fino a indice specificato
        if not percorso or fino_a_indice < 1:
            return
        
        # Colore traccia
        if colore_traccia is None:
            colore_traccia = COLORI['traccia_singolo']
        
        # Tag traccia
        tag_traccia = f"traccia {nome_taxi}" if nome_taxi else "traccia"
        
        # Disegna linee percorso
        for i in range(1, min(fino_a_indice + 1, len(percorso))):
            punto_a = percorso[i - 1]
            punto_b = percorso[i]
            
            x1a, y1a, x2a, y2a = self.converti_cella_in_pixel(punto_a)
            x1b, y1b, x2b, y2b = self.converti_cella_in_pixel(punto_b)
            
            centro_xa = (x1a + x2a) // 2
            centro_ya = (y1a + y2a) // 2
            centro_xb = (x1b + x2b) // 2
            centro_yb = (y1b + y2b) // 2
            
            # Crea una linea più visibile per il percorso
            self.canvas.create_line(
                centro_xa, centro_ya, centro_xb, centro_yb,
                fill=colore_traccia, width=4, tags=tag_traccia,
                capstyle="round", joinstyle="round"
            )
            
            # Aggiungi piccoli punti per indicare le tappe
            raggio_punto = 2
            self.canvas.create_oval(
                centro_xb - raggio_punto, centro_yb - raggio_punto,
                centro_xb + raggio_punto, centro_yb + raggio_punto,
                fill=colore_traccia, outline=colore_traccia, tags=tag_traccia
            )
    
    # === GESTIONE ANIMAZIONE ===
    
    def avvia_pausa_animazione(self):
        # Avvia o mette in pausa l'animazione
        if self.stato_animazione.attiva:
            self.stato_animazione.attiva = False
            self.pulsante_play.config(text="▶ Play")
        else:
            self.stato_animazione.attiva = True
            # Imposta velocità animazione
            velocita_input = self.variabile_velocita.get()
            if velocita_input and velocita_input > 0:
                self.stato_animazione.velocita = velocita_input
            else:
                self.stato_animazione.velocita = VELOCITA_ANIMAZIONE_DEFAULT
            
            self.pulsante_play.config(text="⏸ Pause")
            self.loop_animazione()
    
    def reset_animazione(self):
        # Resetta l'animazione allo stato iniziale
        self.stato_animazione.attiva = False
        self.pulsante_play.config(text="▶ Play")
        self.reset_stato()
        self.ridisegna_scenario_completo()
    
    def loop_animazione(self):
        # Loop principale dell'animazione
        if not self.stato_animazione.attiva:
            return
        
        self.avanza_step_animazione()
        
        if self.stato_animazione.attiva:
            self.finestra.after(self.stato_animazione.velocita, self.loop_animazione)
    
    def avanza_step_animazione(self):
        # Avanza di un step nell'animazione
        # Modalità multi-taxi
        if self.piano_multi_taxi:
            movimento_effettuato = self.avanza_multi_taxi()
            if not movimento_effettuato:
                self.stato_animazione.attiva = False
                self.pulsante_play.config(text="▶ Play")
            return
        
        # Modalità taxi singolo
        if self.piano_viaggio_singolo:
            if self.avanza_taxi_singolo():
                return
            else:
                self.stato_animazione.attiva = False
                self.pulsante_play.config(text="▶ Play")
    
    def avanza_multi_taxi(self):
        # Avanza l'animazione per il sistema multi-taxi
        movimento_effettuato = False
        
        for nome_taxi, piano in self.piano_multi_taxi.piani.items():
            indice_corrente = self.stato_animazione.get_indice_taxi(nome_taxi)
            
            if indice_corrente >= len(piano.percorso) - 1:
                continue
            
            # Avanza di un step
            nuovo_indice = indice_corrente + 1
            self.stato_animazione.aggiorna_taxi(nome_taxi, nuovo_indice)
            
            # Muovi il taxi
            self.muovi_taxi_multi(nome_taxi, piano.percorso[nuovo_indice])
            
            # Gestisci eventi di prelievo
            self.gestisci_eventi_prelievo(piano, nuovo_indice)
            
            # Gestisci eventi di consegna
            self.gestisci_eventi_consegna(piano, nuovo_indice)
            
            # Aggiorna tracciamento percorsi per clienti a bordo
            self.aggiorna_tracciamenti_percorsi(piano, nuovo_indice)
            
            # Disegna tracce clienti attivi
            self.disegna_tracce_clienti_attivi(piano, nuovo_indice, nome_taxi)
            
            # Aggiorna costi
            self.aggiorna_costi_multi_taxi(piano, indice_corrente, nome_taxi)
            movimento_effettuato = True
        
        return movimento_effettuato
    
    def avanza_taxi_singolo(self):
        # Avanza l'animazione per il taxi singolo
        if not self.piano_viaggio_singolo or not self.piano_viaggio_singolo.percorso:
            return False
        
        indice_corrente = self.stato_animazione.get_indice_taxi("singolo")
        
        if indice_corrente >= len(self.piano_viaggio_singolo.percorso) - 1:
            return False
        
        # Avanza di un step
        nuovo_indice = indice_corrente + 1
        self.stato_animazione.aggiorna_taxi("singolo", nuovo_indice)
        
        # Muovi il taxi
        nuova_posizione = self.piano_viaggio_singolo.percorso[nuovo_indice]
        self.muovi_taxi_singolo(nuova_posizione)
        
        # Gestisci eventi di prelievo
        self.gestisci_eventi_prelievo(self.piano_viaggio_singolo, nuovo_indice)
        
        # Gestisci eventi di consegna
        self.gestisci_eventi_consegna(self.piano_viaggio_singolo, nuovo_indice)
        
        # Aggiorna tracciamento percorsi per clienti a bordo
        self.aggiorna_tracciamenti_percorsi(self.piano_viaggio_singolo, nuovo_indice)
        
        # Disegna tracce clienti attivi
        # Per taxi singolo, usa sempre TAXI_SINGOLO indipendentemente dalla configurazione
        nome_taxi = TAXI_SINGOLO
        self.disegna_tracce_clienti_attivi(self.piano_viaggio_singolo, nuovo_indice, nome_taxi)
        
        # Aggiorna costi
        self.aggiorna_costi_taxi_singolo(indice_corrente)
        
        return True
    
    def muovi_taxi_multi(self, nome_taxi, nuova_posizione):
        # Muove un taxi specifico nel sistema multi-taxi
        if nome_taxi not in self.id_taxi_canvas:
            return
        
        x1, y1, x2, y2 = self.converti_cella_in_pixel(nuova_posizione)
        padding_taxi = self.calcola_padding(0.20)
        
        self.canvas.coords(
            self.id_taxi_canvas[nome_taxi],
            x1 + padding_taxi, y1 + padding_taxi,
            x2 - padding_taxi, y2 - padding_taxi
        )
    
    def muovi_taxi_singolo(self, nuova_posizione):
        # Muove il taxi singolo
        if not self.id_taxi_singolo:
            return
        
        x1, y1, x2, y2 = self.converti_cella_in_pixel(nuova_posizione)
        padding_taxi = self.calcola_padding(0.20)
        
        self.canvas.coords(
            self.id_taxi_singolo,
            x1 + padding_taxi, y1 + padding_taxi,
            x2 - padding_taxi, y2 - padding_taxi
        )
    
    def gestisci_eventi_prelievo(self, piano, indice):
        # Gestisce eventi prelievo clienti
        if not hasattr(piano, 'eventi_prelievo') or indice not in piano.eventi_prelievo:
            return
        
        # Marca tutti i clienti prelevati a questo step
        for cliente in piano.eventi_prelievo[indice]:
            self.marca_cliente_prelevato(cliente)
            # Inizia a tracciare il percorso per questo cliente
            self.inizia_tracciamento_percorso(cliente, piano.percorso, indice)
    
    def gestisci_eventi_consegna(self, piano, indice):
        # Gestisce eventi consegna clienti
        # Verifica se siamo alla stazione e ci sono clienti a bordo da consegnare
        if indice < len(piano.percorso) and piano.percorso[indice] == STAZIONE:
            # Trova i clienti che devono essere consegnati
            clienti_a_bordo = self.calcola_clienti_a_bordo(piano, indice - 1)
            for cliente in clienti_a_bordo:
                if cliente in self.clienti_prelevati and cliente not in self.clienti_consegnati:
                    self.completa_tracciamento_percorso(cliente)
    
    def aggiorna_tracciamenti_percorsi(self, piano, indice):
        # Aggiorna tracciamento percorsi clienti a bordo
        clienti_a_bordo = self.calcola_clienti_a_bordo(piano, indice - 1)
        for cliente in clienti_a_bordo:
            if cliente in self.clienti_prelevati and cliente not in self.clienti_consegnati:
                self.aggiorna_tracciamento_percorso(cliente, piano.percorso, indice)
    
    # === GESTIONE COSTI ===
    
    def aggiorna_costi_multi_taxi(self, piano, indice_precedente, nome_taxi):
        # Aggiorna i costi per il sistema multi-taxi
        # Calcola chi è a bordo
        clienti_a_bordo = self.calcola_clienti_a_bordo(piano, indice_precedente)
        
        # Calcola costi se ci sono clienti a bordo
        if clienti_a_bordo and indice_precedente < len(piano.percorso) - 1:
            costo_per_cliente = COSTO_PER_STEP / len(clienti_a_bordo)
            
            for cliente in clienti_a_bordo:
                self.stato_animazione.aggiungi_costo(cliente, costo_per_cliente)
                self.assicura_riga_costo_cliente(cliente)
            
            # Aggiorna contatori
            if nome_taxi == TAXI_SINGOLO:
                self.stato_animazione.costo_taxi_singolo += 1
            else:
                self.stato_animazione.costo_taxi_condiviso += 1
        
        self.aggiorna_visualizzazione_costi()
    
    def aggiorna_costi_taxi_singolo(self, indice_precedente):
        # Aggiorna i costi per il taxi singolo
        if not self.piano_viaggio_singolo:
            return
        
        # Calcola chi è a bordo
        clienti_a_bordo = self.calcola_clienti_a_bordo(self.piano_viaggio_singolo, indice_precedente)
        
        # Calcola costi se ci sono clienti a bordo
        if clienti_a_bordo and indice_precedente < len(self.piano_viaggio_singolo.percorso) - 1:
            costo_per_cliente = COSTO_PER_STEP / len(clienti_a_bordo)
            
            for cliente in clienti_a_bordo:
                self.stato_animazione.aggiungi_costo(cliente, costo_per_cliente)
                self.assicura_riga_costo_cliente(cliente)
            
            # Aggiorna contatori
            if self.configurazione_corrente and self.configurazione_corrente.taxi_condiviso:
                self.stato_animazione.costo_taxi_condiviso += 1
            else:
                self.stato_animazione.costo_taxi_singolo += 1
        
        self.aggiorna_visualizzazione_costi()
    
    def calcola_clienti_a_bordo(self, piano, indice):
        # Calcola quali clienti sono a bordo a un determinato indice
        clienti_a_bordo = []
        
        # Scorre tutti gli step fino all'indice corrente
        for i in range(indice + 1):
            # Aggiungi clienti prelevati
            if hasattr(piano, 'eventi_prelievo') and i in piano.eventi_prelievo:
                for cliente in piano.eventi_prelievo[i]:
                    if cliente not in clienti_a_bordo:
                        clienti_a_bordo.append(cliente)
            
            # Rimuovi clienti scesi
            if hasattr(piano, 'eventi_discesa') and i in piano.eventi_discesa:
                for cliente in piano.eventi_discesa[i]:
                    if cliente in clienti_a_bordo:
                        clienti_a_bordo.remove(cliente)
        
        return clienti_a_bordo
    
    def aggiorna_visualizzazione_costi(self):
        # Aggiorna visualizzazione costi
        self.var_costo_singolo.set(f"Taxi singolo: {self.stato_animazione.costo_taxi_singolo}€")
        self.var_costo_condiviso.set(f"Taxi condiviso: {self.stato_animazione.costo_taxi_condiviso}€")
        
        # Aggiorna costi clienti
        for etichetta in sorted(self.stato_animazione.costi_clienti.keys()):
            self.assicura_riga_costo_cliente(etichetta)
            costo = self.stato_animazione.get_costo(etichetta)
            self.etichette_costi_clienti[etichetta].set(f"{costo:.2f}€")
    
    def assicura_riga_costo_cliente(self, etichetta):
        # Crea una riga per il costo del cliente se non esiste
        if etichetta in self.etichette_costi_clienti:
            return
        
        riga = ttk.Frame(self.frame_costi_clienti)
        riga.pack(fill="x", pady=1)
        
        ttk.Label(riga, text=etichetta, font=("Arial", 9)).pack(side="left")
        
        variabile_costo = tk.StringVar(value="0.00€")
        ttk.Label(riga, textvariable=variabile_costo, font=("Arial", 9)).pack(side="right")
        
        self.etichette_costi_clienti[etichetta] = variabile_costo


def avvia_interfaccia_grafica():
    # Funzione di utilità per avviare l'interfaccia grafica
    # Crea la finestra principale e avvia il loop Tkinter
    finestra_principale = tk.Tk()
    finestra_principale.geometry("1020x512")
    finestra_principale.resizable(True, True)
    
    app = FinestraPrincipale(finestra_principale)
    
    # Avvia loop principale interfaccia
    finestra_principale.mainloop()
