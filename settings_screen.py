import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT, STATE_MENU
from ui_components import Button
from settings_manager import SettingsManager

class SettingsScreen:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.settings_manager = SettingsManager()
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_label = pygame.font.SysFont("Arial", 28)
        self.font_val = pygame.font.SysFont("Arial", 24, bold=True)
        
        self.scroll_y = 0
        self.line_height = 80
        self.visible_height = SCREEN_HEIGHT - 250
        
        self.back_button = Button(
            20, 20, 120, 40, 
            self.game_manager.t("ui.back"), pygame.font.SysFont("Arial", 20, bold=True),
            action=lambda: self.game_manager.change_state(STATE_MENU)
        )
        
        self.interactives = []

    def handle_events(self, event):
        self.back_button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.change_state(STATE_MENU)
        
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 20
            self.limit_scroll()
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def handle_click(self, pos):
        for rect, action in self.interactives:
            if rect.collidepoint(pos):
                action()
                break

    def limit_scroll(self):
        total_height = len(self.settings_manager.settings) * self.line_height
        if total_height <= self.visible_height:
            self.scroll_y = 0
            return
        max_scroll = self.visible_height - total_height
        if self.scroll_y < max_scroll: self.scroll_y = max_scroll
        if self.scroll_y > 0: self.scroll_y = 0

    def update(self):
        self.back_button.update(pygame.mouse.get_pos())

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self.back_button.draw(surface)
        
        title_surf = self.font_title.render(self.game_manager.t("menu.settings").upper(), True, COLOR_ACCENT)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 40))
        
        content_rect = pygame.Rect(50, 160, SCREEN_WIDTH - 100, self.visible_height)
        self.interactives = [] 
        
        scroll_surface = pygame.Surface((content_rect.width, content_rect.height))
        scroll_surface.fill(COLOR_BG)
        
        y_offset = self.scroll_y
        for key, spec in self.settings_manager.settings.items():
            row_rect = pygame.Rect(0, y_offset, content_rect.width, self.line_height)
            
            if row_rect.bottom > 0 and row_rect.top < self.visible_height:
                self.draw_setting_row(scroll_surface, key, spec, row_rect, content_rect.topleft)
            
            y_offset += self.line_height
            
        surface.blit(scroll_surface, content_rect.topleft)
        
        total_height = len(self.settings_manager.settings) * self.line_height
        if total_height > self.visible_height:
            bar_x = SCREEN_WIDTH - 40
            bar_y = content_rect.y
            bar_w = 8
            bar_h = self.visible_height
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), 0, 4)
            handle_h = max(20, bar_h * (self.visible_height / total_height))
            handle_y = bar_y + (-self.scroll_y / (total_height - self.visible_height)) * (bar_h - handle_h)
            pygame.draw.rect(surface, COLOR_ACCENT, (bar_x, handle_y, bar_w, handle_h), 0, 4)

        footer_text = self.font_label.render(self.game_manager.t("ui.back") + " (Esc)", True, (100, 100, 100))
        surface.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 60))

    def draw_setting_row(self, surface, key, spec, rect, screen_offset):
        label_text = self.game_manager.t(f"settings.{key}")
        label_surf = self.font_label.render(label_text, True, COLOR_TEXT)
        surface.blit(label_surf, (20, rect.centery - label_surf.get_height() // 2))
        
        val = spec["val"]
        type = spec["type"]
        val_center_x = rect.width - 150
        
        if type == "bool":
            toggle_rect = pygame.Rect(val_center_x - 30, rect.centery - 15, 60, 30)
            color = COLOR_ACCENT if val else (80, 80, 80)
            pygame.draw.rect(surface, color, toggle_rect, 0, 15)
            circle_x = toggle_rect.right - 15 if val else toggle_rect.left + 15
            pygame.draw.circle(surface, (255, 255, 255), (circle_x, toggle_rect.centery), 12)
            self.interactives.append((toggle_rect.move(screen_offset), lambda: self.settings_manager.set(key, not val)))
            
        elif type == "int":
            l_arrow_rect = pygame.Rect(val_center_x - 70, rect.centery - 15, 30, 30)
            self.draw_arrow(surface, l_arrow_rect, "left")
            val_surf = self.font_val.render(str(val), True, COLOR_TEXT)
            surface.blit(val_surf, (val_center_x - val_surf.get_width() // 2, rect.centery - val_surf.get_height() // 2))
            r_arrow_rect = pygame.Rect(val_center_x + 40, rect.centery - 15, 30, 30)
            self.draw_arrow(surface, r_arrow_rect, "right")
            low, high = spec["range"]
            self.interactives.append((l_arrow_rect.move(screen_offset), lambda: self.settings_manager.set(key, max(low, val - 5))))
            self.interactives.append((r_arrow_rect.move(screen_offset), lambda: self.settings_manager.set(key, min(high, val + 5))))
            
        elif type == "choice":
            l_arrow_rect = pygame.Rect(val_center_x - 110, rect.centery - 15, 30, 30)
            self.draw_arrow(surface, l_arrow_rect, "left")
            
            # Traduction de la valeur affichée pour les choix
            display_val = self.game_manager.t(f"settings.{key}_options.{val}")
            val_surf = self.font_val.render(display_val, True, COLOR_TEXT)
            
            surface.blit(val_surf, (val_center_x - val_surf.get_width() // 2, rect.centery - val_surf.get_height() // 2))
            r_arrow_rect = pygame.Rect(val_center_x + 80, rect.centery - 15, 30, 30)
            self.draw_arrow(surface, r_arrow_rect, "right")
            options = spec["options"]
            idx = options.index(val)
            
            def change_choice(new_val):
                self.settings_manager.set(key, new_val)
                if key == "language":
                    self.game_manager.update_language()

            self.interactives.append((l_arrow_rect.move(screen_offset), lambda: change_choice(options[(idx - 1) % len(options)])))
            self.interactives.append((r_arrow_rect.move(screen_offset), lambda: change_choice(options[(idx + 1) % len(options)])))

    def draw_arrow(self, surface, rect, direction):
        color = COLOR_ACCENT
        center = rect.center
        size = 8
        if direction == "left":
            points = [(center[0] + size, center[1] - size), (center[0] + size, center[1] + size), (center[0] - size, center[1])]
        else:
            points = [(center[0] - size, center[1] - size), (center[0] - size, center[1] + size), (center[0] + size, center[1])]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 1)
