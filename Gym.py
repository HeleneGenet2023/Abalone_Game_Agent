from datetime import datetime
import time
import random
import os
import subprocess

# Trouver un port disponible pour le jeu
def findAvailablePort(used_ports, start_port=16001, end_port=18000):
    #On choisi un port au hasard
    port = random.choice(range(start_port, end_port))
    while port in used_ports:
        #Si le port est déjà utilisé on en reprend un autre
        port = random.choice(range(start_port, end_port))
    #On enregistre le port comme étant utilisé
    used_ports.append(port) 
    #On retourne le port choisi et la liste de ports utilisés
    return port, used_ports

# Classe pour gérer les jeux
class Gym:
    # Constructeur pour initialiser les chemins des agents et la commande de base
    def __init__(self, agent1Path, agent2Path):
        self.agent1Path = agent1Path #On défini le premier agent
        self.agent2Path = agent2Path #On défini le deuxieme agent
        #Commande de base pour le lancement de parties
        self.baseCommand = ["python", "main_abalone.py", "-t", "local", self.agent1Path, self.agent2Path]

    # Méthode pour jouer une partie
    def play(self, gui=False, record=False, type="classic", port=None, many=False):
        """Jouer une partie du jeu.

        Args:
            gui (bool): Si l'interface graphique doit être utilisée.
            record (bool): Si la partie doit être enregistrée.
            type (str): Type de jeu ("classic" ou "alien").
            port (int): Port à utiliser pour la partie.
            many (bool): Si plusieurs parties doivent être jouées en parallèle.

        Returns:
            subprocess.Popen: Le processus qui exécute la partie, si many=True.
        """
        playCommand = self.baseCommand.copy()
        if not gui: #Voir la partie en direct
            playCommand.append("-g")
        if record: #Enregistrer la partie
            playCommand.append("-r")
        if type == "alien": #Configuration intiale
            playCommand.append("-c")
            playCommand.append(type)
        if port is None: #Port a utiliser pour lancer la partie
            port, _ = findAvailablePort([])
        #On ajoute un argument pour le port à utiliser durant la partie
        playCommand.append("-p") 
        playCommand.append(str(port))
        #Indiquer que la partie est sur le point d'être lancée
        print(f"{datetime.now()} - Game run!")
        playCommand = " ".join(playCommand)
        if many: #Si on veut lancer plusieurs parties simultanément on utiliser subprocess.Popen
            with open(os.devnull, 'w') as fnull:
                p = subprocess.Popen(playCommand, stdout=fnull, stderr=fnull, shell=True)
            return p
        else: #Si on désire lancer une seule partie on run la commande sur un seul process
            with open(os.devnull, 'w') as fnull:
                subprocess.run(playCommand, shell=True, stdout=fnull, stderr=fnull)

    # Méthode pour entraîner les agents en jouant plusieurs parties
    def train(self, numberOfGames=10, gui=False, record=False, type="classic", port=None, use_threads=True):
        """Entraîner les agents en jouant plusieurs parties.

        Args:
            numberOfGames (int): Nombre de parties à jouer.
            gui (bool): Si l'interface graphique doit être utilisée.
            record (bool): Si les parties doivent être enregistrées.
            type (str): Type de jeu ("classic" ou "alien").
            port (int): Port à utiliser pour les parties.
            use_threads (bool): Si les parties doivent être jouées en parallèle.
        """
        usedPorts = []
        popen_list = []
        start = time.time()
        if use_threads: #Si l'on désire lancer des parties en simultanés
            for _ in range(numberOfGames):
                #On trouve un port non utilisé
                port, usedPorts = findAvailablePort(usedPorts)
                #On défini le process à lancer
                p = self.play(gui, record, type, port, use_threads)
                #On rajoute le process à la liste de process 
                popen_list.append(p)
            for p in popen_list:
                #On attend que les process soit terminés
                p.wait()
            finish = time.time()
            #Indication du temps total pour l'ensemble des parties
            print(f"Time to run {numberOfGames} games : {finish - start}")
            #Indication du temps moyen par partie
            print(f"Average runtime per game : {(finish - start)/numberOfGames}")
        else:#Si l'on désire lancer des parties de façon séquentielle
            for _ in range(numberOfGames):
                self.play(gui, record, type, port)

# Point d'entrée du programme
if __name__ == "__main__":
    agent1 = "my_player.py"
    test = Gym(agent1, agent1)
    test.train(2, record=False)
    print("Done")