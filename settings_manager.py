import json
import os

class SettingsManager:

    def __init__(self, filename="config.json"):
        self.filename = filename
        self.defaults = {
            "volume_music": {"val": 70, "type": "int", "range": (0, 100), "label": "Volume Musique"},
            "volume_sfx": {"val": 80, "type": "int", "range": (0, 100), "label": "Volume Bruitages"},
            "fullscreen": {"val": False, "type": "bool", "label": "Plein Écran"},
            "language": {"val": "Français", "type": "choice", "options": ["Français", "Anglais", "Espagnol"], "label": "Langue"},
            "show_fps": {"val": True, "type": "bool", "label": "Afficher FPS"},
            "troll_mode": {"val": False, "type": "bool", "label": "Mode Troll"}
        }
        self.settings = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                f = open(self.filename, 'r')
                loaded = json.load(f)
                f.close()
                
                keys = list(self.defaults.keys())
                for i in range(len(keys)):
                    key = keys[i]
                    spec = self.defaults[key]
                    self.settings[key] = spec.copy()
                    if key in loaded:
                        self.settings[key]["val"] = loaded[key]
            except:
                self.reset_to_defaults()
        else:
            self.reset_to_defaults()
            self.save()

    def reset_to_defaults(self):
        self.settings = {}
        keys = list(self.defaults.keys())
        for i in range(len(keys)):
            key = keys[i]
            self.settings[key] = self.defaults[key].copy()

    def save(self):
        to_save = {}
        keys = list(self.settings.keys())
        for i in range(len(keys)):
            key = keys[i]
            to_save[key] = self.settings[key]["val"]
            
        try:
            f = open(self.filename, 'w')
            json.dump(to_save, f, indent=4)
            f.close()
        except:
            print("Error saving config")

    def get(self, key):
        if key in self.settings:
            return self.settings[key]["val"]
        return None

    def set(self, key, value):
        if key in self.settings:
            self.settings[key]["val"] = value
            self.save()
