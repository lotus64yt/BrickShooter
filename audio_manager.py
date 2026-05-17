import os
import pygame
class AudioManager:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        pygame.mixer.init()

        # On initialise proprement toutes les variables
        self.sounds = {}
        self.music_path = None
        self.music_playing = False

        # On charge les données
        self.load_assets()
        self.update_volumes()
    def load_assets(self):
        # Détection du dossier absolu
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(base_dir, "assets", "audio")
        names = ["move", "clear", "win"]
        files = ["move.mp3", "clear.mp3", "win.mp3"]

        for i in range(len(names)):
            name = names[i]
            filename = files[i]
            path = os.path.join(audio_dir, filename)
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
            else:
                print("Warning: Audio file not found: " + path)
        # Cette ligne est maintenant bien lue et exécutée à coup sûr
        self.music_path = os.path.join(audio_dir, "music.mp3")
    def update_volumes(self):
        sfx_vol = self.settings_manager.get("volume_sfx") / 100.0
        music_vol = self.settings_manager.get("volume_music") / 100.0

        keys = list(self.sounds.keys())
        for i in range(len(keys)):
            name = keys[i]
            sound = self.sounds[name]
            sound.set_volume(sfx_vol)

        pygame.mixer.music.set_volume(music_vol)
    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()
    def start_music(self):
        # Grâce au "self.music_path = None" du début, plus aucun crash possible ici
        if self.music_path and os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
            self.music_playing = True
        else:
            print("Warning: Fichier musique introuvable ou chemin non défini.")
    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
    def toggle_music(self, play):
        if play is True:
            if not self.music_playing:
                self.start_music()
        else:
            if self.music_playing:
                self.stop_music()