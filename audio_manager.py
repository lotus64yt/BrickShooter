import pygame
import os

class AudioManager:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        pygame.mixer.init()
        
        self.sounds = {}
        self.music_playing = False
        
        self.load_assets()
        self.update_volumes()

    def load_assets(self):
        audio_dir = "assets/audio"
        sound_files = {
            "move": "move.mp3",
            "clear": "clear.mp3",
            "win": "win.mp3"
        }
        
        for key, filename in sound_files.items():
            path = os.path.join(audio_dir, filename)
            if os.path.exists(path):
                self.sounds[key] = pygame.mixer.Sound(path)
            else:
                print(f"Warning: Audio file not found: {path}")

        self.music_path = os.path.join(audio_dir, "music.mp3")

    def update_volumes(self):
        sfx_vol = self.settings_manager.get("volume_sfx") / 100.0
        music_vol = self.settings_manager.get("volume_music") / 100.0
        
        for sound in self.sounds.values():
            sound.set_volume(sfx_vol)
        
        pygame.mixer.music.set_volume(music_vol)

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def start_music(self):
        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1) # Loop indefinitely
            self.music_playing = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

    def toggle_music(self, play):
        if play and not self.music_playing:
            self.start_music()
        elif not play and self.music_playing:
            self.stop_music()
