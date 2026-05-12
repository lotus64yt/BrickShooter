import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT, STATE_MENU
from ui_components import Button
from score_manager import ScoreManager

class ScoreScreen:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.score_manager = ScoreManager()
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_item = pygame.font.SysFont("Arial", 24)
        self.scroll_y = 0
        self.scores = []
        self.line_height = 40
        self.visible_height = SCREEN_HEIGHT - 250
        self.total_height = 0
        
        self.back_button = Button(
            20, 20, 120, 40, 
            "Retour", pygame.font.SysFont("Arial", 20, bold=True),
            action=lambda: self.game_manager.change_state(STATE_MENU)
        )
        
    def load_scores(self):
        self.scores = self.score_manager.load_scores()
        self.scores.sort(key=lambda x: x.get('score', 0), reverse=True)
        self.total_height = len(self.scores) * self.line_height
        self.scroll_y = 0

    def handle_events(self, event):
        self.back_button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.change_state(STATE_MENU)
        
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 20
            self.limit_scroll()

    def limit_scroll(self):
        if self.total_height <= self.visible_height:
            self.scroll_y = 0
            return
            
        max_scroll = self.visible_height - self.total_height
        if self.scroll_y < max_scroll:
            self.scroll_y = max_scroll
        if self.scroll_y > 0:
            self.scroll_y = 0

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self.back_button.draw(surface)
        
        title_surf = self.font_title.render("CLASSEMENT", True, COLOR_ACCENT)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 40))
        
        header_y = 120
        pygame.draw.line(surface, COLOR_ACCENT, (50, header_y + 35), (SCREEN_WIDTH - 50, header_y + 35), 2)
        
        rank_h = self.font_item.render("Rang", True, COLOR_TEXT)
        score_h = self.font_item.render("Score", True, COLOR_TEXT)
        level_h = self.font_item.render("Niveau", True, COLOR_TEXT)
        
        surface.blit(rank_h, (100, header_y))
        surface.blit(score_h, (SCREEN_WIDTH // 2 - 30, header_y))
        surface.blit(level_h, (SCREEN_WIDTH - 200, header_y))
        
        content_rect = pygame.Rect(50, 160, SCREEN_WIDTH - 100, self.visible_height)
        
        try:
            scroll_surface = pygame.Surface((content_rect.width, content_rect.height))
            scroll_surface.fill(COLOR_BG)
            
            for i, entry in enumerate(self.scores):
                y_pos = i * self.line_height + self.scroll_y
                
                if y_pos + self.line_height < 0 or y_pos > self.visible_height:
                    continue
                    
                color = COLOR_TEXT
                if i == 0: color = (255, 215, 0)
                elif i == 1: color = (192, 192, 192)
                elif i == 2: color = (205, 127, 50)
                
                rank_text = self.font_item.render(f"#{i+1}", True, color)
                score_val = entry.get('score', 0)
                level_val = entry.get('level', 0) + 1
                
                score_text = self.font_item.render(f"{score_val:,}", True, COLOR_TEXT)
                level_text = self.font_item.render(f"Niv. {level_val}", True, COLOR_TEXT)
                
                scroll_surface.blit(rank_text, (50, y_pos))
                scroll_surface.blit(score_text, (SCREEN_WIDTH // 2 - 80, y_pos))
                scroll_surface.blit(level_text, (SCREEN_WIDTH - 250, y_pos))
                
            surface.blit(scroll_surface, (content_rect.x, content_rect.y))
        except Exception as e:
            print(f"Drawing error: {e}")
        
        if self.total_height > self.visible_height:
            bar_x = SCREEN_WIDTH - 40
            bar_y = content_rect.y
            bar_w = 8
            bar_h = self.visible_height
            
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), 0, 4)
            
            handle_h = max(20, bar_h * (self.visible_height / self.total_height))
            handle_y = bar_y + (-self.scroll_y / (self.total_height - self.visible_height)) * (bar_h - handle_h) if self.total_height > self.visible_height else bar_y
            
            pygame.draw.rect(surface, COLOR_ACCENT, (bar_x, handle_y, bar_w, handle_h), 0, 4)

        footer_text = self.font_item.render("Echap: Retour Menu", True, (100, 100, 100))
        surface.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 60))
