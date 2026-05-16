import json
import os
import time
import random

class SaveManager:

    def __init__(self, directory="store/saves"):
        self.directory = directory
        if os.path.exists(directory) == False:
            os.makedirs(directory)

    def create_new_save(self, level, score, level_seed, state_seed):
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
        try:
            f = open(filename, 'w')
            json.dump(data, f, indent=4)
            f.close()
        except:
            print("Error saving game")

    def list_saves(self):
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
