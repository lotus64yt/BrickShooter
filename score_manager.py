import json
import os

class ScoreManager:
    def __init__(self, filename="store/scores.json"):
        self.filename = filename
        self.ensure_directory()

    def ensure_directory(self):
        directory = os.path.dirname(self.filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_score(self, score, level):
        scores = self.load_scores()
        scores.append({
            "score": score,
            "level": level
        })
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(scores, f, indent=4)
        except Exception as e:
            print(f"Error saving scores: {e}")

    def load_scores(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scores: {e}")
            return []