import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, STATE_GAME, STATE_SCORES, STATE_SETTINGS
from ui_components import Button, Carousel, CarouselControls, MenuList
from load_images import loadImages

class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_button = pygame.font.SysFont("Arial", 32)
        
        btn_width = 200
        btn_height = 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT - btn_height - 50
        
        self.play_button = Button(
            btn_x, btn_y, btn_width, btn_height, 
            "Jouer", self.font_button, 
            action=self.start_game
        )
        
        self.carousel_level = Carousel(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, 300, 300,
            loadImages("assets/images/menu/carousel"), 
            self.font_button
        )
        self.carousel_controls = CarouselControls(self.carousel_level, self.font_button)
        
        self.menu_list = MenuList(
            50, SCREEN_HEIGHT // 4, 200, 300,
            ["Règles", "Scores", "Paramètres"],
            self.font_button
        )

    def start_game(self):
        self.game_manager.change_state(STATE_GAME)

    def handle_events(self, event):
        self.play_button.handle_event(event)
        self.menu_list.handle_event(event)
        self.carousel_controls.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            item_selected = self.menu_list.get_selected_item()
            if item_selected == "Règles":
                print("Afficher les règles du jeu")
            elif item_selected == "Scores":
                self.game_manager.change_state(STATE_SCORES)
            elif item_selected == "Paramètres":
                self.game_manager.change_state(STATE_SETTINGS)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG)
        
        title_surf = self.font_title.render("BRICK SHOOTER", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 3, 50))
        surface.blit(title_surf, title_rect)
        
        self.play_button.draw(surface)
        
        self.carousel_controls.draw(surface)
        
        self.menu_list.draw(surface)
