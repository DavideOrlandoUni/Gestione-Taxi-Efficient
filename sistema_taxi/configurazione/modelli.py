"""
Modelli Dati del Sistema
========================

Definisce tutte le classi dati utilizzate dal sistema di gestione taxi.
"""


class PianoViaggio:
    """
    Rappresenta un piano di viaggio completo per un taxi.
    
    Contiene il percorso completo e gli eventi di prelievo/discesa
    associati a specifici punti del percorso.
    
    Attributi:
        percorso (list): Lista di coordinate (x, y) del percorso completo
        eventi_prelievo (dict): Mappa {indice_percorso: [lista_clienti]}
        eventi_discesa (dict): Mappa {indice_percorso: [lista_clienti]}
    """
    
    def __init__(self, percorso_completo, eventi_prelievo, eventi_discesa):
        """
        Inizializza un piano di viaggio.
        
        Args:
            percorso_completo: Lista di punti (x, y) del percorso
            eventi_prelievo: Dict {indice_percorso: [lista_clienti]}
            eventi_discesa: Dict {indice_percorso: [lista_clienti]}
        """
        self.percorso = percorso_completo
        self.eventi_prelievo = eventi_prelievo
        self.eventi_discesa = eventi_discesa
    
    def ottieni_lunghezza_percorso(self):
        """Restituisce la lunghezza totale del percorso."""
        return len(self.percorso)
    
    def ottieni_clienti_prelevati_a_step(self, indice):
        """Restituisce i clienti prelevati a un determinato step."""
        return self.eventi_prelievo.get(indice, [])
    
    def ottieni_clienti_scesi_a_step(self, indice):
        """Restituisce i clienti scesi a un determinato step."""
        return self.eventi_discesa.get(indice, [])
    
    def __str__(self):
        return f"PianoViaggio(lunghezza={len(self.percorso)}, prelievi={len(self.eventi_prelievo)}, discese={len(self.eventi_discesa)})"


class PianoTaxi:
    """
    Piano di viaggio per un singolo taxi con eventi associati.
    
    Versione semplificata di PianoViaggio per compatibilità con il sistema multi-taxi.
    
    Attributi:
        percorso (list): Lista di coordinate del percorso
        eventi_prelievo (dict): Eventi di prelievo clienti
        eventi_discesa (dict): Eventi di discesa clienti
    """
    
    def __init__(self, percorso, prelievi, discese):
        """
        Inizializza il piano per un taxi.
        
        Args:
            percorso: Lista di punti del percorso
            prelievi: Dict degli eventi di prelievo
            discese: Dict degli eventi di discesa
        """
        self.percorso = percorso
        self.eventi_prelievo = prelievi
        self.eventi_discesa = discese
    
    def ottieni_posizione_a_step(self, indice):
        """Restituisce la posizione del taxi a un determinato step."""
        if 0 <= indice < len(self.percorso):
            return self.percorso[indice]
        return None
    
    def e_completato_a_step(self, indice):
        """Verifica se il piano è completato a un determinato step."""
        return indice >= len(self.percorso) - 1
    
    def __str__(self):
        return f"PianoTaxi(percorso={len(self.percorso)} step)"


class PianoMultiTaxi:
    """
    Gestisce piani separati per più taxi e le etichette clienti.
    
    Coordina l'esecuzione di più taxi contemporaneamente, ognuno con
    il proprio piano di viaggio indipendente.
    
    Attributi:
        piani (dict): Mappa {nome_taxi: PianoTaxi}
        etichette (dict): Mappa {etichetta_cliente: posizione}
    """
    
    def __init__(self, piani_taxi, etichette_clienti):
        """
        Inizializza il piano multi-taxi.
        
        Args:
            piani_taxi: Dict {nome_taxi: PianoTaxi}
            etichette_clienti: Dict {etichetta_cliente: posizione}
        """
        self.piani = piani_taxi
        self.etichette = etichette_clienti
    
    def ottieni_nomi_taxi(self):
        """Restituisce la lista dei nomi dei taxi."""
        return list(self.piani.keys())
    
    def ottieni_piano_taxi(self, nome_taxi):
        """Restituisce il piano per un taxi specifico."""
        return self.piani.get(nome_taxi)
    
    def ottieni_numero_clienti(self):
        """Restituisce il numero totale di clienti."""
        return len(self.etichette)
    
    def tutti_taxi_completati(self, indici_correnti):
        """
        Verifica se tutti i taxi hanno completato i loro percorsi.
        
        Args:
            indici_correnti: Dict {nome_taxi: indice_corrente}
        
        Returns:
            bool: True se tutti i taxi sono arrivati alla fine
        """
        for nome_taxi, piano in self.piani.items():
            indice = indici_correnti.get(nome_taxi, 0)
            if not piano.e_completato_a_step(indice):
                return False
        return True
    
    def __str__(self):
        return f"PianoMultiTaxi(taxi={len(self.piani)}, clienti={len(self.etichette)})"


class StatoAnimazione:
    """
    Mantiene lo stato dell'animazione dell'interfaccia grafica.
    
    Centralizza tutte le informazioni necessarie per gestire
    l'animazione dei taxi sulla griglia.
    
    Attributi:
        attiva (bool): Se l'animazione è in corso
        velocita (int): Velocità in millisecondi tra frame
        indici_taxi (dict): Indici correnti per ogni taxi
        costi_clienti (dict): Costi accumulati per cliente
        costo_taxi_singolo (float): Costo totale taxi singolo
        costo_taxi_condiviso (float): Costo totale taxi condiviso
    """
    
    def __init__(self):
        """Inizializza lo stato dell'animazione."""
        self.attiva = False
        self.velocita = 200  # millisecondi
        self.indici_taxi = {}
        self.costi_clienti = {}
        self.costo_taxi_singolo = 0.0
        self.costo_taxi_condiviso = 0.0
    
    def reset(self):
        """Resetta lo stato dell'animazione."""
        self.attiva = False
        self.indici_taxi.clear()
        self.costi_clienti.clear()
        self.costo_taxi_singolo = 0.0
        self.costo_taxi_condiviso = 0.0
    
    def aggiorna_indice_taxi(self, nome_taxi, nuovo_indice):
        """Aggiorna l'indice corrente per un taxi."""
        self.indici_taxi[nome_taxi] = nuovo_indice
    
    def ottieni_indice_taxi(self, nome_taxi):
        """Restituisce l'indice corrente per un taxi."""
        return self.indici_taxi.get(nome_taxi, 0)
    
    def aggiungi_costo_cliente(self, cliente, costo):
        """Aggiunge un costo per un cliente specifico."""
        if cliente not in self.costi_clienti:
            self.costi_clienti[cliente] = 0.0
        self.costi_clienti[cliente] += costo
    
    def ottieni_costo_cliente(self, cliente):
        """Restituisce il costo totale per un cliente."""
        return self.costi_clienti.get(cliente, 0.0)
    
    def __str__(self):
        return f"StatoAnimazione(attiva={self.attiva}, taxi={len(self.indici_taxi)})"


class ConfigurazioneProblema:
    """
    Rappresenta la configurazione di un problema specifico.
    
    Incapsula tutte le informazioni necessarie per caricare
    e configurare un problema del sistema taxi.
    
    Attributi:
        numero (int): Numero identificativo del problema
        nome (str): Nome descrittivo
        percorso_piano (str): Percorso del file piano
        percorso_posizioni (str): Percorso del file posizioni
        usa_multi_taxi (bool): Se utilizzare il sistema multi-taxi
        taxi_condiviso (bool): Se il taxi è condiviso (legacy)
        colore_taxi (str): Colore per la visualizzazione
    """
    
    def __init__(self, numero, nome, percorso_piano, percorso_posizioni, 
                 usa_multi_taxi=False, taxi_condiviso=False, colore_taxi="#e74c3c"):
        """
        Inizializza la configurazione del problema.
        
        Args:
            numero: Numero identificativo
            nome: Nome descrittivo
            percorso_piano: Percorso file piano
            percorso_posizioni: Percorso file posizioni
            usa_multi_taxi: Se usare sistema multi-taxi
            taxi_condiviso: Se taxi è condiviso (legacy)
            colore_taxi: Colore visualizzazione
        """
        self.numero = numero
        self.nome = nome
        self.percorso_piano = percorso_piano
        self.percorso_posizioni = percorso_posizioni
        self.usa_multi_taxi = usa_multi_taxi
        self.taxi_condiviso = taxi_condiviso
        self.colore_taxi = colore_taxi
    
    def __str__(self):
        return f"ConfigurazioneProblema({self.numero}: {self.nome})"
