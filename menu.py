import webbrowser
import os
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, STATE_GAME, STATE_SCORES, STATE_SETTINGS
from ui_components import Button, Carousel, CarouselControls, MenuList
from load_images import loadImages

class Menu:
    """Gère l'affichage et les interactions du menu principal du jeu."""

    def __init__(self, game_manager):
        """Initialise les composants UI du menu principal (boutons, carrousel, listes)."""
        self.game_manager = game_manager
        self.font_button = pygame.font.SysFont("Arial", 32)
        btn_width = 200
        btn_height = 60
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT - btn_height - 50
        self.play_button = Button(
            btn_x, btn_y, btn_width, btn_height,
            self.game_manager.t("menu.play"), self.font_button,
            action=self.start_game
        )
        self.carousel_level = Carousel(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, 250, 250,
            loadImages("assets/images/menu/carousel"),
            self.font_button
        )
        self.carousel_controls = CarouselControls(self.carousel_level, self.font_button)

        items = []
        items.append(self.game_manager.t("menu.rules"))
        items.append(self.game_manager.t("menu.scores"))
        items.append(self.game_manager.t("menu.settings"))

        self.menu_list = MenuList(
            50, SCREEN_HEIGHT // 4, 200, 300,
            items,
            self.font_button
        )

    def start_game(self):
        """Change l'état pour démarrer ou reprendre le jeu."""
        self.game_manager.change_state(STATE_GAME)

    def handle_events(self, event):
        """Gère les événements Pygame reçus dans le menu."""
        self.play_button.handle_event(event)
        self.menu_list.handle_event(event)
        self.carousel_controls.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                item_selected = self.menu_list.get_selected_item()
                if item_selected == self.game_manager.t("menu.rules"):
                    lang = self.game_manager.settings_manager.get("language")
                    html_file = "reglefr.html"
                    if lang == "Anglais":
                        html_file = "regleang.html"
                    elif lang == "Espagnol":
                        html_file = "regleesp.html"

                    html_path = os.path.abspath("assets/rules/" + html_file)
                    webbrowser.open("file://" + html_path)
                elif item_selected == self.game_manager.t("menu.scores"):
                    self.game_manager.change_state(STATE_SCORES)
                elif item_selected == self.game_manager.t("menu.settings"):
                    self.game_manager.change_state(STATE_SETTINGS)

    def update(self):
        """Met à jour l'état des composants du menu selon la position de la souris."""
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.update(mouse_pos)

    def draw(self, surface):
        """Dessine les éléments graphiques du menu sur la surface donnée."""
        sw = surface.get_width()
        sh = surface.get_height()
        surface.fill(COLOR_BG)

        title_surf = pygame.image.load("assets/images/titre_jeu.png").convert_alpha()
        title_x = sw // 2 - title_surf.get_width() // 2
        surface.blit(title_surf, (title_x, 50))

        self.play_button.rect.x = sw // 2 - self.play_button.rect.width // 2
        self.play_button.rect.y = sh - 50 - self.play_button.rect.height

        self.carousel_level.rect.x = sw // 2 - self.carousel_level.rect.width // 2
        self.carousel_level.rect.y = sh // 3 - self.carousel_level.rect.height // 2
        self.carousel_controls.update_pos()

        self.menu_list.rect.x = 50
        self.menu_list.rect.y = sh // 4

        self.play_button.draw(surface)
        self.carousel_controls.draw(surface)
        self.menu_list.draw(surface)
