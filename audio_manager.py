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
        
        names = ["move", "clear", "win"]
        files = ["move.mp3", "clear.mp3", "win.mp3"]
        
        for i in range(len(names)):
            name = names[i]
            filename = files[i]
            path = audio_dir + "/" + filename
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
            else:
                print("Warning: Audio file not found: " + path)

        self.music_path = audio_dir + "/music.mp3"

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
        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
            self.music_playing = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

    def toggle_music(self, play):
        if play == True:
            if self.music_playing == False:
                self.start_music()
        else:
            if self.music_playing == True:
                self.stop_music()
