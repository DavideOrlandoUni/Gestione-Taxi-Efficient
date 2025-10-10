# Rappresenta il percorso completo di un viaggio taxi
class Viaggio:
    def __init__(self, percorso, eventi_prelievo, eventi_discesa):
        self.percorso = percorso
        self.eventi_prelievo = eventi_prelievo
        self.eventi_discesa = eventi_discesa

# Piano di movimento per singolo taxi
class PianoTaxi:
    def __init__(self, percorso, prelievi, discese):
        self.percorso = percorso
        self.eventi_prelievo = prelievi
        self.eventi_discesa = discese

    def completato(self, indice):
        return indice >= len(self.percorso) - 1

# Gestisce piani di più taxi contemporaneamente
class PianiMultiTaxi:
    def __init__(self, piani_taxi, etichette_clienti):
        self.piani = piani_taxi
        self.etichette = etichette_clienti

# Stato dell'animazione e costi del sistema
class StatoAnimazione:
    def __init__(self):
        self.attiva = False
        self.velocita = 200
        self.indici_taxi = {}
        self.costi_clienti = {}
        self.costo_taxi_singolo = 0.0
        self.costo_taxi_condiviso = 0.0
    
    def reset(self):
        self.attiva = False
        self.indici_taxi.clear()
        self.costi_clienti.clear()
        self.costo_taxi_singolo = 0.0
        self.costo_taxi_condiviso = 0.0

    def aggiorna_taxi(self, nome_taxi, nuovo_indice):
        self.indici_taxi[nome_taxi] = nuovo_indice

    def get_indice_taxi(self, nome_taxi):
        return self.indici_taxi.get(nome_taxi, 0)

    def aggiungi_costo(self, cliente, costo):
        if cliente not in self.costi_clienti:
            self.costi_clienti[cliente] = 0.0
        self.costi_clienti[cliente] += costo

    def get_costo(self, cliente):
        return self.costi_clienti.get(cliente, 0.0)

# Configurazione per ogni problema/scenario
class ConfigProblema:
    def __init__(self, numero, nome, percorso_piano, percorso_posizioni, 
                 usa_multi_taxi=False, taxi_condiviso=False, colore_taxi="#e74c3c"):
        self.numero = numero
        self.nome = nome
        self.percorso_piano = percorso_piano
        self.percorso_posizioni = percorso_posizioni
        self.usa_multi_taxi = usa_multi_taxi
        self.taxi_condiviso = taxi_condiviso
        self.colore_taxi = colore_taxi
