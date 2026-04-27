import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, STATE_GAME
from ui_components import Button

class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_button = pygame.font.SysFont("Arial", 32)
        
        btn_width = 200
        btn_height = 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = (SCREEN_HEIGHT - btn_height) // 2
        
        self.play_button = Button(
            btn_x, btn_y, btn_width, btn_height, 
            "Jouer", self.font_button, 
            action=self.start_game
        )

    def start_game(self):
        self.game_manager.change_state(STATE_GAME)

    def handle_events(self, event):
        self.play_button.handle_event(event)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG)
        
        # Title
        title_surf = self.font_title.render("BRICK SHOOTER", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        surface.blit(title_surf, title_rect)
        
        self.play_button.draw(surface)
