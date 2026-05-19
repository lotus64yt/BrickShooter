import json
import os

class ScoreManager:
    """Gère l'enregistrement et le chargement des scores de jeu."""

    def __init__(self, filename="store/scores.json"):
        """Initialise le gestionnaire de scores en vérifiant l'existence du dossier de destination."""
        self.filename = filename
        self.ensure_directory()

    def ensure_directory(self):
        """Crée le dossier parent pour le fichier de scores s'il n'existe pas déjà."""
        directory = os.path.dirname(self.filename)
        if os.path.exists(directory) == False:
            os.makedirs(directory)

    def save_score(self, score, level, level_seed=None, state_seed=None, session_id=None):
        """Enregistre un nouveau score ou met à jour le score d'une session existante."""
        scores = self.load_scores()
        updated = False
        if session_id != None:
            for i in range(len(scores)):
                s = scores[i]
                if s.get('session_id') == session_id:
                    if score > s.get('score', 0):
                        s['score'] = score
                    if level > s.get('level', 0):
                        s['level'] = level
                    s['level_seed'] = level_seed
                    s['state_seed'] = state_seed
                    updated = True
                    break
        if updated == False:
            new_entry = {
                "score": score,
                "level": level,
                "level_seed": level_seed,
                "state_seed": state_seed,
                "session_id": session_id
            }
            scores.append(new_entry)
        try:
            f = open(self.filename, 'w')
            json.dump(scores, f, indent=4)
            f.close()
        except:
            print("Error saving scores")

    def load_scores(self):
        """Charge et renvoie la liste de tous les scores sauvegardés depuis le fichier JSON."""
        if os.path.exists(self.filename) == False:
            return []
        try:
            f = open(self.filename, 'r')
            data = json.load(f)
            f.close()
            return data
        except:
            print("Error loading scores")
            return []