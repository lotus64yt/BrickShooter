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

    def save_score(self, score, level, level_seed=None, state_seed=None, session_id=None):
        scores = self.load_scores()
        updated = False
        if session_id:
            for s in scores:
                if s.get('session_id') == session_id:
                    s['score'] = max(score, s.get('score', 0))
                    s['level'] = max(level, s.get('level', 0))
                    s['level_seed'] = level_seed
                    s['state_seed'] = state_seed
                    updated = True
                    break
        if not updated:
            scores.append({
                "score": score,
                "level": level,
                "level_seed": level_seed,
                "state_seed": state_seed,
                "session_id": session_id
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