# ============================================================
# app.py
# - GUI Tkinter per caricare/visualizzare i piani e i costi
# - Logica invariata; import aggiornati ai nuovi nomi
# ============================================================

from typing import List, Tuple, Dict, Optional
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ..impostazioni_e_costanti_di_simulazione import Cella, GRIGLIA_L, GRIGLIA_H, PIX_CELLA, STAZIONE, OSTACOLI
from ..lettura_piani_e_posizioni_da_file import trova_primo_file_esistente, leggi_azioni_piano_fast_downward, carica_mappa_posizioni_da_json
from ..costruzione_viaggio_da_azioni_sas import PianoViaggio, costruisci_viaggio_da_azioni, estrai_primi_pickup_da_azioni
from ..pianificazione_taxi_singolo_condiviso_multi import (
    PianoTaxi, PianoMultiTaxi, TAXI_SINGOLO, TAXI_CONDIVISO, costruisci_piani_per_taxi_singolo_e_condiviso
)
from ..algoritmo_a_star_su_griglia import calcola_percorso_minimo_con_astar
from ..utilita_logging_console import log_sicuro_console_compatibile

class AppTaxi:
    """Interfaccia grafica per visualizzare i plan e mostrare i costi"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gestore Taxi - GUI (piani esterni)")
        self.is_playing = False
        self.play_interval_ms = 200

        # === stato multi-taxi ===
        self.piano_multi: Optional[PianoMultiTaxi] = None
        self.taxi_ids: Dict[str, int] = {}   # canvas ids per ogni taxi
        self.indici: Dict[str, int] = {}     # indice corrente sul percorso di ogni taxi

        # dimensione cella dinamica (parte dal valore costante)
        self.pix_cella = PIX_CELLA

        # Canvas
        self.canvas = tk.Canvas(root, width=GRIGLIA_L * PIX_CELLA, height=GRIGLIA_H * PIX_CELLA, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=20, sticky="nsew", padx=8, pady=8)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Pannello controlli
        ctrl = ttk.Frame(root)
        ctrl.grid(row=0, column=1, sticky="ns", padx=8, pady=8)
        ttk.Label(ctrl, text="Problemi (piani esterni)").pack(anchor="w")
        ttk.Button(ctrl, text="Problem 1", command=self.carica_problema_1).pack(fill="x", pady=2)
        ttk.Button(ctrl, text="Problem 2", command=self.carica_problema_2).pack(fill="x", pady=2)
        ttk.Button(ctrl, text="Problem 3", command=self.carica_problema_3).pack(fill="x", pady=2)
        ttk.Button(ctrl, text="Problem 4", command=self.carica_problema_4).pack(fill="x", pady=2)
        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=6)

        # Controlli animazione
        self.btn_play = ttk.Button(ctrl, text="Play ⏵", command=self.avvia_pausa)
        self.btn_reset = ttk.Button(ctrl, text="Reset ⟲", command=self.reset)
        self.btn_play.pack(fill="x", pady=2)
        self.btn_reset.pack(fill="x", pady=2)

        # Velocità animazione
        ttk.Label(ctrl, text="Velocità (ms)").pack(anchor="w", pady=(8, 0))
        self.speed_var = tk.IntVar(value=self.play_interval_ms)
        ttk.Entry(ctrl, textvariable=self.speed_var, width=8).pack(anchor="w")

        # --- DASHBOARD COSTI ---
        self.costo_step = 1.0  # € per passo
        self.var_costo_singolo   = tk.StringVar(value="Taxi singolo: 0")
        self.var_costo_condiviso = tk.StringVar(value="Taxi condiviso: 0")

        box = ttk.LabelFrame(ctrl, text="Dashboard costi (€/step = 1)")
        box.pack(fill="x")

        ttk.Label(box, textvariable=self.var_costo_singolo,   font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 0))
        ttk.Label(box, textvariable=self.var_costo_condiviso, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

        # Contenitore righe clienti
        self.cost_frame = ttk.Frame(box)
        self.cost_frame.pack(fill="x")
        self.cost_labels: Dict[str, tk.StringVar] = {}
        
        # Stato dinamico
        self.piano: Optional[PianoViaggio] = None
        self.etichette_clienti: Dict[str, Cella] = {}
        self.costi_clienti: Dict[str, float] = {}
        
        self.indice_percorso: int = 0
        self.taxi_id = None

        # Impostazioni taxi legacy (quando non siamo in modalità multi-taxi)
        self.legacy_is_shared = False
        self.legacy_color = "#e74c3c"  # rosso default

        # Griglia
        self.disegna_griglia()

        # Default: carica Problem 1
        self.carica_problema_1()

    def _on_canvas_resize(self, ev: tk.Event):
        new_pix = max(8, min(ev.width // GRIGLIA_L, ev.height // GRIGLIA_H))
        if new_pix == self.pix_cella:
            return
        self.pix_cella = new_pix
        self.canvas.config(width=GRIGLIA_L * self.pix_cella, height=GRIGLIA_H * self.pix_cella)
        self.disegna_griglia()

    def _pad(self, k: float) -> int:
        """Restituisce un padding proporzionale alla cella (k è una frazione)."""
        return max(2, int(self.pix_cella * k))

    # --- Caricamento piani ---
    def carica_problema_1(self):
        self.legacy_is_shared = False
        self.legacy_color = "#e74c3c"
        self._carica_da_file(
    		plan_candidates=[
        		Path("PDDL/plans/plan1"),
    		],
    		loc_candidates=[Path("PDDL/locations/location1.json")],
    		title="Problem 1",
    		auto_share_pair=False
	)

    def carica_problema_2(self):
        self.legacy_is_shared = True
        self.legacy_color = "#9b59b6"  # viola
        self._carica_da_file(
    		plan_candidates=[
        		Path("PDDL/plans/plan2"),
    		],
    		loc_candidates=[Path("PDDL/locations/location2.json")],
    		title="Problem 2",
    		auto_share_pair=False
	)

    def carica_problema_3(self):
        self.legacy_is_shared = False
        self.legacy_color = "#e74c3c"
        self._carica_da_file(
    		plan_candidates=[
        		Path("PDDL/plans/plan3"),
		],
    		loc_candidates=[Path("PDDL/locations/location3.json")],
    		title="Problem 3",
    		auto_share_pair=True
	)

    def carica_problema_4(self):
        self.legacy_is_shared = False
        self.legacy_color = "#e74c3c"
        self._carica_da_file(
    		plan_candidates=[
        		Path("PDDL/plans/plan4"),
    		],
    		loc_candidates=[Path("PDDL/locations/location4.json")],
    		title="Problem 4",
    		auto_share_pair=True
        )

    def _carica_da_file(self, plan_candidates: List[Path], loc_candidates: List[Path], title: str, auto_share_pair: bool):
        plan_path = trova_primo_file_esistente(plan_candidates)
        if not plan_path:
            print(f"[ERRORE] Nessun file piano trovato tra: {', '.join(map(str, plan_candidates))}")
            return

        loc_path = trova_primo_file_esistente(loc_candidates)
        if not loc_path:
            print(f"[ERRORE] File locations non trovato tra: {', '.join(map(str, loc_candidates))}")
            return

        try:
            azioni = leggi_azioni_piano_fast_downward(plan_path)
            locs = carica_mappa_posizioni_da_json(loc_path)

            if auto_share_pair:
                mapping = estrai_primi_pickup_da_azioni(azioni)
                multi = costruisci_piani_per_taxi_singolo_e_condiviso(mapping, locs, raggio_coppia=2)
                self.piano_multi = multi
                self.piano = None
                viaggio, etichette = None, multi.etichette
            else:
                viaggio, etichette = costruisci_viaggio_da_azioni(azioni, locs)
                self.piano_multi = None

        except Exception as e:
            log_sicuro_console_compatibile("[ERRORE] Impossibile caricare piano/locations: ", e)
            return

        # aggiorna stato GUI
        self.root.title(f"Gestore Taxi - {title}")
        self.piano, self.etichette_clienti = viaggio, etichette

        self.reset_costi()
        self.ridisegna_scenario()
        print(f"[LOG] Caricato {title} | plan={plan_path} | locations={loc_path} | auto_share={auto_share_pair}")

    # --- Disegno scena ---
    def disegna_griglia(self):
        self.canvas.delete("gridline", "obstacle")
        w = GRIGLIA_L * self.pix_cella
        h = GRIGLIA_H * self.pix_cella

        for x in range(GRIGLIA_L + 1):
            self.canvas.create_line(x * self.pix_cella, 0, x * self.pix_cella, h, fill="#ddd", tags="gridline")

        for y in range(GRIGLIA_H + 1):
            self.canvas.create_line(0, y * self.pix_cella, w, y * self.pix_cella, fill="#ddd", tags="gridline")

        for ox, oy in OSTACOLI:
            x1, y1, x2, y2 = self.cella_in_pixel((ox, oy))
            self.canvas.create_rectangle(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill="black", outline="black", tags="obstacle")

    def cella_in_pixel(self, p: Cella) -> Tuple[int, int, int, int]:
        x, y = p
        yy = GRIGLIA_H - 1 - y
        x1 = x * self.pix_cella
        y1 = yy * self.pix_cella
        return x1, y1, x1 + self.pix_cella, y1 + self.pix_cella

    def ridisegna_scenario(self):
        self.disegna_griglia()
        self.canvas.delete("station", "taxi", "client", "trace")

        x1, y1, x2, y2 = self.cella_in_pixel(STAZIONE)
        pad = self._pad(0.15)
        self.canvas.create_rectangle(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill="#2ecc71", outline="#1b8f4a", width=2, tags="station")
        self.canvas.create_text((x1 + x2) // 2, y1 + 12, text="ST", fill="#1b8f4a", font=("Segoe UI", 9, "bold"))

        for label, pos in self.etichette_clienti.items():
            x1, y1, x2, y2 = self.cella_in_pixel(pos)
            pad_c = self._pad(0.25)
            self.canvas.create_oval(x1 + pad_c, y1 + pad_c, x2 - pad_c, y2 - pad_c, fill="#3498db", outline="#21618c", width=2, tags="client")
            self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=label, fill="white", font=("Segoe UI", 9, "bold"))

        self.indice_percorso = 0
        self.taxi_id = None
        self.taxi_ids.clear()
        self.indici.clear()

        if self.piano_multi:
            colori = {TAXI_SINGOLO: "#e74c3c", TAXI_CONDIVISO: "#9b59b6"}
            for nome, piano in self.piano_multi.piani.items():
                if not piano.path:
                    continue
                if piano.path[0] != STAZIONE:
                    piano.path = [STAZIONE] + piano.path
                x1, y1, x2, y2 = self.cella_in_pixel(piano.path[0])
                pad_t = self._pad(0.20)
                tid = self.canvas.create_rectangle(
                    x1 + pad_t, y1 + pad_t, x2 - pad_t, y2 - pad_t,
                    fill=colori.get(nome, "#e67e22"),
                    outline="#2c3e50", width=2, tags=f"taxi {nome}"
                )
                self.taxi_ids[nome] = tid
                self.indici[nome] = 0
            for nome, piano in self.piano_multi.piani.items():
                self._aggiorna_traccia_multi(nome, 0, piano.path)

        elif self.piano and self.piano.path:
            x1, y1, x2, y2 = self.cella_in_pixel(self.piano.path[0])
            pad_t = self._pad(0.20)
            self.taxi_id = self.canvas.create_rectangle(
                x1 + pad_t, y1 + pad_t, x2 - pad_t, y2 - pad_t,
                fill=self.legacy_color, outline="#2c3e50", width=2, tags="taxi"
            )

        self.disegna_traccia(0)
        self.mostra_tabella_costi()

    def disegna_traccia(self, fino_indice: int):
        self.canvas.delete("trace")
        if not self.piano:
            return
        for i in range(1, fino_indice + 1):
            a = self.piano.path[i - 1]
            b = self.piano.path[i]
            x1a, y1a, x2a, y2a = self.cella_in_pixel(a)
            x1b, y1b, x2b, y2b = self.cella_in_pixel(b)
            xa = (x1a + x2a) // 2
            ya = (y1a + y2a) // 2
            xb = (x1b + x2b) // 2
            yb = (y1b + y2b) // 2
            self.canvas.create_line(xa, ya, xb, yb, fill="#bdc3c7", width=2, tags="trace")

    # --- Costi e animazione ---
    def reset_costi(self):
        self.costo_singolo = 0
        self.costo_condiviso = 0
        self.costi_clienti = {k: 0.0 for k in (self.etichette_clienti.keys() if self.etichette_clienti else [])}
        self.var_costo_singolo.set(f"Taxi singolo: {self.costo_singolo}")
        self.var_costo_condiviso.set(f"Taxi condiviso: {self.costo_condiviso}")
        for w in self.cost_frame.winfo_children():
            w.destroy()
        self.cost_labels.clear()

    def mostra_tabella_costi(self):
        if not self.costi_clienti:
            return
        for label in sorted(self.costi_clienti.keys()):
            self._ensure_cost_row(label)
            self.cost_labels[label].set(f"{self.costi_clienti[label]:.2f} €")

    def _aggiorna_traccia_multi(self, nome_taxi: str, fino_a: int, path: List[Cella]):
        for i in range(1, fino_a + 1):
            a, b = path[i - 1], path[i]
            x1a, y1a, x2a, y2a = self.cella_in_pixel(a)
            x1b, y1b, x2b, y2b = self.cella_in_pixel(b)
            xa = (x1a + x2a) // 2;  ya = (y1a + y2a) // 2
            xb = (x1b + x2b) // 2;  yb = (y1b + y2b) // 2
            colore = "#95a5a6" if nome_taxi == TAXI_SINGOLO else "#7f8c8d"
            self.canvas.create_line(xa, ya, xb, yb, fill=colore, width=2, tags=f"trace {nome_taxi}")

    def _aggiorna_costi_multi(self, piano: "PianoTaxi", idx_prev: int, nome_taxi: str):
        a_bordo: List[str] = []
        for i in range(idx_prev + 1):
            if i in piano.eventi_prelievo:
                for c in piano.eventi_prelievo[i]:
                    if c not in a_bordo:
                        a_bordo.append(c)
            if i in piano.eventi_discesa:
                for c in piano.eventi_discesa[i]:
                    if c in a_bordo:
                        a_bordo.remove(c)

        if a_bordo and idx_prev < len(piano.path) - 1:
            quota = self.costo_step / len(a_bordo)
            for c in a_bordo:
                self.costi_clienti[c] = round(self.costi_clienti.get(c, 0.0) + quota, 2)
                self._ensure_cost_row(c)
            if nome_taxi == TAXI_SINGOLO:
                self.costo_singolo += 1
            else:
                self.costo_condiviso += 1

        self.var_costo_singolo.set(f"Taxi singolo: {self.costo_singolo}")
        self.var_costo_condiviso.set(f"Taxi condiviso: {self.costo_condiviso}")
        self.mostra_tabella_costi()

    def aggiorna_costo_step(self, idx: int):
        """Aggiorna la ripartizione dei costi (modalità singolo taxi)."""
        if not self.piano:
            return
        a_bordo: List[str] = []
        for i in range(idx + 1):
            if i in self.piano.eventi_prelievo:
                for c in self.piano.eventi_prelievo[i]:
                    if c not in a_bordo:
                        a_bordo.append(c)
            if i in self.piano.eventi_discesa:
                for c in self.piano.eventi_discesa[i]:
                    if c in a_bordo:
                        a_bordo.remove(c)
        if a_bordo and idx < len(self.piano.path) - 1:
            quota = self.costo_step / len(a_bordo)
            for c in a_bordo:
                self.costi_clienti[c] = round(self.costi_clienti.get(c, 0.0) + quota, 2)
                self._ensure_cost_row(c)
            if self.legacy_is_shared:
                self.costo_condiviso += 1
            else:
                self.costo_singolo += 1

        self.var_costo_singolo.set(f"Taxi singolo: {self.costo_singolo}")
        self.var_costo_condiviso.set(f"Taxi condiviso: {self.costo_condiviso}")
        self.mostra_tabella_costi()

    def avanza_passo(self):
        # modalità multi-taxi
        if self.piano_multi:
            avanzato = False
            for nome, piano in self.piano_multi.piani.items():
                if nome not in self.indici:
                    continue
                idx = self.indici[nome]
                if idx >= len(piano.path) - 1:
                    continue

                idx += 1
                self.indici[nome] = idx
                x1, y1, x2, y2 = self.cella_in_pixel(piano.path[idx])
                pad_t = self._pad(0.20)
                self.canvas.coords(self.taxi_ids[nome], x1 + pad_t, y1 + pad_t, x2 - pad_t, y2 - pad_t)
                self._aggiorna_traccia_multi(nome, idx, piano.path)
                self._aggiorna_costi_multi(piano, idx - 1, nome_taxi=nome)
                avanzato = True

            if not avanzato:
                self.is_playing = False
                self.btn_play.config(text="Play ⏵")
                print("[LOG] Fine percorso (multi-taxi).")
            return

        # modalità singolo taxi
        if not self.piano or not self.piano.path or self.taxi_id is None:
            return
        if self.indice_percorso >= len(self.piano.path) - 1:
            self.is_playing = False
            self.btn_play.config(text="Play ⏵")
            print("[LOG] Fine del percorso.")
            return
        self.indice_percorso += 1
        x1, y1, x2, y2 = self.cella_in_pixel(self.piano.path[self.indice_percorso])
        pad_t = self._pad(0.20)
        self.canvas.coords(self.taxi_id, x1 + pad_t, y1 + pad_t, x2 - pad_t, y2 - pad_t)
        self.disegna_traccia(self.indice_percorso)
        self.aggiorna_costo_step(self.indice_percorso - 1)

    def _ensure_cost_row(self, label: str):
        if label in self.cost_labels:
            return
        row = ttk.Frame(self.cost_frame)
        row.pack(fill="x", pady=1)
        ttk.Label(row, text=label).pack(side="left")
        var = tk.StringVar(value="0.00 €")
        ttk.Label(row, textvariable=var).pack(side="right")
        self.cost_labels[label] = var

    def avvia_pausa(self):
        """Avvia/mette in pausa l'animazione."""
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="Play ⏵")
        else:
            self.is_playing = True
            try:
                self.play_interval_ms = max(1, int(self.speed_var.get()))
            except Exception:
                self.play_interval_ms = 200
            self.btn_play.config(text="Pause ⏸")
            self._loop_animazione()

    def _loop_animazione(self):
        """Loop di animazione: chiama `avanza_passo` e ripianifica se in play."""
        if not self.is_playing:
            return
        self.avanza_passo()
        if self.is_playing:
            self.root.after(self.play_interval_ms, self._loop_animazione)

    def reset(self):
        """Ferma l'animazione e ripristina la scena allo stato iniziale del piano caricato."""
        self.is_playing = False
        self.btn_play.config(text="Play ⏵")
        self.indice_percorso = 0
        self.indici = {k: 0 for k in self.indici}  # anche multi-taxi
        self.reset_costi()
        self.ridisegna_scenario()
