import json
import os

class SettingsManager:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.defaults = {
            "volume_music": {"val": 70, "type": "int", "range": (0, 100), "label": "Volume Musique"},
            "volume_sfx": {"val": 80, "type": "int", "range": (0, 100), "label": "Volume Bruitages"},
            "fullscreen": {"val": False, "type": "bool", "label": "Plein Écran"},
            "difficulty": {"val": "Normal", "type": "choice", "options": ["Facile", "Normal", "Difficile"], "label": "Difficulté"},
            "language": {"val": "Français", "type": "choice", "options": ["Français", "Anglais", "Espagnol"], "label": "Langue"},
            "show_fps": {"val": True, "type": "bool", "label": "Afficher FPS"}
        }
        self.settings = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    loaded = json.load(f)
                    for key, spec in self.defaults.items():
                        self.settings[key] = spec.copy()
                        if key in loaded:
                            self.settings[key]["val"] = loaded[key]
            except Exception as e:
                print(f"Error loading config: {e}")
                self.reset_to_defaults()
        else:
            self.reset_to_defaults()
            self.save()

    def reset_to_defaults(self):
        self.settings = {k: v.copy() for k, v in self.defaults.items()}

    def save(self):
        to_save = {k: v["val"] for k, v in self.settings.items()}
        try:
            with open(self.filename, 'w') as f:
                json.dump(to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.settings.get(key, {}).get("val")

    def set(self, key, value):
        if key in self.settings:
            self.settings[key]["val"] = value
            self.save()
