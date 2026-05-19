import os
import pygame
class AudioManager:
    """Gestionnaire pour les effets sonores et la musique du jeu."""
    
    def __init__(self, settings_manager):
        """
        Initialise le gestionnaire audio, configure le mixer Pygame 
        et charge les paramètres de base.
        """
        self.settings_manager = settings_manager
        pygame.mixer.init()

        self.sounds = {}
        self.music_path = None
        self.music_playing = False

        self.load_assets()
        self.update_volumes()

    def load_assets(self):
        """
        Charge les fichiers audio (bruitages et musique) depuis 
        le dossier des ressources (assets).
        """
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
        self.music_path = os.path.join(audio_dir, "music.mp3")

    def update_volumes(self):
        """
        Met à jour le volume de tous les sons et de la musique 
        en fonction des valeurs définies dans les paramètres.
        """
        sfx_vol = self.settings_manager.get("volume_sfx") / 100.0
        music_vol = self.settings_manager.get("volume_music") / 100.0

        keys = list(self.sounds.keys())
        for i in range(len(keys)):
            name = keys[i]
            sound = self.sounds[name]
            sound.set_volume(sfx_vol)

        pygame.mixer.music.set_volume(music_vol)

    def play_sfx(self, name):
        """
        Joue un effet sonore spécifique identifié par son nom.
        """
        if name in self.sounds:
            self.sounds[name].play()

    def start_music(self):
        """
        Démarre la lecture de la musique d'ambiance en boucle.
        """
        if self.music_path and os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
            self.music_playing = True
        else:
            print("Warning: Fichier musique introuvable ou chemin non défini.")

    def stop_music(self):
        """
        Arrête la lecture de la musique d'ambiance.
        """
        pygame.mixer.music.stop()
        self.music_playing = False

    def toggle_music(self, play):
        """
        Active ou désactive la musique en fonction du paramètre 'play'.
        """
        if play is True:
            if not self.music_playing:
                self.start_music()
        else:
            if self.music_playing:
                self.stop_music()