import json
import os
import time
import random

class SaveManager:
    """Gère la création, mise à jour et lecture des sauvegardes de jeu."""

    def __init__(self, directory="store/saves"):
        """Initialise le gestionnaire et s'assure que le dossier de sauvegarde existe."""
        self.directory = directory
        if os.path.exists(directory) == False:
            os.makedirs(directory)

    def create_new_save(self, level, score, level_seed, state_seed):
        """Crée une nouvelle sauvegarde de session et renvoie l'ID de session."""
        session_id = str(random.randint(100000, 999999))
        filename = self.directory + "/save_" + session_id + ".json"
        save_data = {
            "session_id": session_id,
            "level": level,
            "score": score,
            "level_seed": level_seed,
            "state_seed": state_seed,
            "timestamp": time.time()
        }
        self.save_to_file(filename, save_data)
        return session_id

    def update_save(self, session_id, level, score, level_seed, state_seed):
        """Met à jour une sauvegarde existante avec les nouvelles données de jeu."""
        if session_id == None:
            return
        filename = self.directory + "/save_" + session_id + ".json"
        save_data = {
            "session_id": session_id,
            "level": level,
            "score": score,
            "level_seed": level_seed,
            "state_seed": state_seed,
            "timestamp": time.time()
        }
        self.save_to_file(filename, save_data)

    def save_to_file(self, filename, data):
        """Écrit les données de sauvegarde formattées en JSON dans un fichier."""
        try:
            f = open(filename, 'w')
            json.dump(data, f, indent=4)
            f.close()
        except:
            print("Error saving game")

    def list_saves(self):
        """Récupère la liste de toutes les sauvegardes, triées par date (du plus récent au plus ancien)."""
        if os.path.exists(self.directory) == False:
            return []
        saves = []
        files = os.listdir(self.directory)
        for f in files:
            if f.endswith(".json"):
                try:
                    path = self.directory + "/" + f
                    file = open(path, 'r')
                    data = json.load(file)
                    file.close()
                    saves.append(data)
                except:
                    pass
        
        for i in range(len(saves)):
            for j in range(i + 1, len(saves)):
                if saves[i]['timestamp'] < saves[j]['timestamp']:
                    temp = saves[i]
                    saves[i] = saves[j]
                    saves[j] = temp
                    
        return saves
