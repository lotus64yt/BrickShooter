import json
import os
import time
import uuid

class SaveManager:

    def __init__(self, directory="store/saves"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def create_new_save(self, level, score, level_seed, state_seed):
        session_id = str(uuid.uuid4())[:8]
        filename = f"{self.directory}/save_{session_id}.json"
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
        if not session_id:
            return
        filename = f"{self.directory}/save_{session_id}.json"
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
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")

    def list_saves(self):
        if not os.path.exists(self.directory):
            return []
        saves = []
        for f in os.listdir(self.directory):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(self.directory, f), 'r') as file:
                        saves.append(json.load(file))
                except:
                    pass
        return sorted(saves, key=lambda x: x.get('timestamp', 0), reverse=True)
