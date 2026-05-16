import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT, STATE_MENU

def draw_rect_compat(surface, color, rect, radius=0):
    try:
        pygame.draw.rect(surface, color, rect, 0, border_radius=radius)
    except:
        pygame.draw.rect(surface, color, rect, 0)
from ui_components import Button
from settings_manager import SettingsManager

class SettingsScreen:

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.settings_manager = self.game_manager.settings_manager
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_label = pygame.font.SysFont("Arial", 28)
        self.font_val = pygame.font.SysFont("Arial", 24, bold=True)
        self.scroll_y = 0
        self.line_height = 80
        self.visible_height = 0
        self.back_button = Button(
            20, 20, 120, 40, 
            self.game_manager.t("ui.back"), pygame.font.SysFont("Arial", 20, bold=True),
            action=self.go_back
        )
        self.interactives = []

    def go_back(self):
        self.game_manager.change_state(STATE_MENU)

    def handle_events(self, event):
        self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.change_state(STATE_MENU)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = self.scroll_y + event.y * 20
            self.limit_scroll()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        for i in range(len(self.interactives)):
            item = self.interactives[i]
            rect = item[0]
            action_type = item[1]
            key = item[2]
            
            if rect.collidepoint(pos):
                if action_type == "toggle_bool":
                    val = self.settings_manager.get(key)
                    new_val = not val
                    self.settings_manager.set(key, new_val)
                    if key == "fullscreen":
                        self.game_manager.toggle_fullscreen(new_val)
                elif action_type == "change_int":
                    delta = item[3]
                    spec = self.settings_manager.settings[key]
                    val = spec["val"]
                    low = spec["range"][0]
                    high = spec["range"][1]
                    new_val = val + delta
                    if new_val < low: new_val = low
                    if new_val > high: new_val = high
                    self.settings_manager.set(key, new_val)
                    if key.startswith("volume"):
                        self.game_manager.audio_manager.update_volumes()
                elif action_type == "change_choice":
                    direction = item[3]
                    spec = self.settings_manager.settings[key]
                    options = spec["options"]
                    val = spec["val"]
                    idx = -1
                    for j in range(len(options)):
                        if options[j] == val:
                            idx = j
                            break
                    
                    if direction == "next":
                        new_idx = (idx + 1) % len(options)
                    else:
                        new_idx = (idx - 1) % len(options)
                        
                    new_val = options[new_idx]
                    self.settings_manager.set(key, new_val)
                    if key == "language":
                        self.game_manager.update_language()
                break

    def limit_scroll(self):
        total_height = len(self.settings_manager.settings) * self.line_height
        if total_height <= self.visible_height:
            self.scroll_y = 0
            return
        max_scroll = self.visible_height - total_height
        if self.scroll_y < max_scroll:
            self.scroll_y = max_scroll
        if self.scroll_y > 0:
            self.scroll_y = 0

    def update(self):
        self.back_button.update(pygame.mouse.get_pos())

    def draw(self, surface):
        sw = surface.get_width()
        sh = surface.get_height()
        self.visible_height = sh - 250
        surface.fill(COLOR_BG)
        self.back_button.draw(surface)
        
        title_text = self.game_manager.t("menu.settings")
        title_surf = self.font_title.render(title_text.upper(), True, COLOR_ACCENT)
        surface.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 40))
        
        content_rect = pygame.Rect(50, 160, sw - 100, self.visible_height)
        self.interactives = [] 
        
        scroll_surface = pygame.Surface((content_rect.width, content_rect.height))
        scroll_surface.fill(COLOR_BG)
        
        y_offset = self.scroll_y
        keys = list(self.settings_manager.settings.keys())
        for i in range(len(keys)):
            key = keys[i]
            spec = self.settings_manager.settings[key]
            row_rect = pygame.Rect(0, y_offset, content_rect.width, self.line_height)
            if row_rect.y + row_rect.height > 0 and row_rect.y < self.visible_height:
                self.draw_setting_row(scroll_surface, key, spec, row_rect, (content_rect.x, content_rect.y))
            y_offset = y_offset + self.line_height
            
        surface.blit(scroll_surface, (content_rect.x, content_rect.y))
        
        total_height = len(self.settings_manager.settings) * self.line_height
        if total_height > self.visible_height:
            bar_x = sw - 40
            bar_y = content_rect.y
            bar_w = 8
            bar_h = self.visible_height
            draw_rect_compat(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), 4)
            handle_h = bar_h * (self.visible_height / total_height)
            if handle_h < 20:
                handle_h = 20
            handle_y = bar_y + (-self.scroll_y / (total_height - self.visible_height)) * (bar_h - handle_h)
            draw_rect_compat(surface, COLOR_ACCENT, (bar_x, handle_y, bar_w, handle_h), 4)
            
        footer_text = self.font_label.render(self.game_manager.t("ui.back") + " (Esc)", True, (100, 100, 100))
        surface.blit(footer_text, (sw // 2 - footer_text.get_width() // 2, sh - 60))

    def draw_setting_row(self, surface, key, spec, rect, screen_offset):
        label_text = self.game_manager.t("settings." + key)
        label_surf = self.font_label.render(label_text, True, COLOR_TEXT)
        surface.blit(label_surf, (20, rect.y + (rect.height // 2 - label_surf.get_height() // 2)))
        
        val = spec["val"]
        type = spec["type"]
        val_center_x = rect.width - 150
        
        if type == "bool":
            toggle_rect = pygame.Rect(val_center_x - 30, rect.y + (rect.height // 2 - 15), 60, 30)
            color = (80, 80, 80)
            if val == True:
                color = COLOR_ACCENT
            draw_rect_compat(surface, color, toggle_rect, 15)
            
            circle_x = toggle_rect.x + 15
            if val == True:
                circle_x = toggle_rect.x + toggle_rect.width - 15
            pygame.draw.circle(surface, (255, 255, 255), (circle_x, toggle_rect.y + 15), 12)
            
            abs_rect = pygame.Rect(toggle_rect.x + screen_offset[0], toggle_rect.y + screen_offset[1], toggle_rect.width, toggle_rect.height)
            self.interactives.append((abs_rect, "toggle_bool", key))
            
        elif type == "int":
            l_arrow_rect = pygame.Rect(val_center_x - 70, rect.y + (rect.height // 2 - 15), 30, 30)
            self.draw_arrow(surface, l_arrow_rect, "left")
            val_surf = self.font_val.render(str(val), True, COLOR_TEXT)
            surface.blit(val_surf, (val_center_x - val_surf.get_width() // 2, rect.y + (rect.height // 2 - val_surf.get_height() // 2)))
            r_arrow_rect = pygame.Rect(val_center_x + 40, rect.y + (rect.height // 2 - 15), 30, 30)
            self.draw_arrow(surface, r_arrow_rect, "right")
            
            abs_l = pygame.Rect(l_arrow_rect.x + screen_offset[0], l_arrow_rect.y + screen_offset[1], 30, 30)
            abs_r = pygame.Rect(r_arrow_rect.x + screen_offset[0], r_arrow_rect.y + screen_offset[1], 30, 30)
            self.interactives.append((abs_l, "change_int", key, -5))
            self.interactives.append((abs_r, "change_int", key, 5))
            
        elif type == "choice":
            l_arrow_rect = pygame.Rect(val_center_x - 110, rect.y + (rect.height // 2 - 15), 30, 30)
            self.draw_arrow(surface, l_arrow_rect, "left")
            
            display_val = self.game_manager.t("settings." + key + "_options." + val)
            val_surf = self.font_val.render(display_val, True, COLOR_TEXT)
            surface.blit(val_surf, (val_center_x - val_surf.get_width() // 2, rect.y + (rect.height // 2 - val_surf.get_height() // 2)))
            
            r_arrow_rect = pygame.Rect(val_center_x + 80, rect.y + (rect.height // 2 - 15), 30, 30)
            self.draw_arrow(surface, r_arrow_rect, "right")
            
            abs_l = pygame.Rect(l_arrow_rect.x + screen_offset[0], l_arrow_rect.y + screen_offset[1], 30, 30)
            abs_r = pygame.Rect(r_arrow_rect.x + screen_offset[0], r_arrow_rect.y + screen_offset[1], 30, 30)
            self.interactives.append((abs_l, "change_choice", key, "prev"))
            self.interactives.append((abs_r, "change_choice", key, "next"))

    def draw_arrow(self, surface, rect, direction):
        color = COLOR_ACCENT
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2
        size = 8
        if direction == "left":
            points = [(center_x + size, center_y - size), (center_x + size, center_y + size), (center_x - size, center_y)]
        else:
            points = [(center_x - size, center_y - size), (center_x - size, center_y + size), (center_x + size, center_y)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 1)
