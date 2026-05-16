import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT, STATE_MENU

def draw_rect_compat(surface, color, rect, radius=0):
    try:
        pygame.draw.rect(surface, color, rect, 0, border_radius=radius)
    except:
        pygame.draw.rect(surface, color, rect, 0)
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
        self.visible_height = 0
        self.total_height = 0
        self.back_button = Button(
            20, 20, 120, 40, 
            self.game_manager.t("ui.back"), pygame.font.SysFont("Arial", 20, bold=True),
            action=self.go_back
        )

    def go_back(self):
        self.game_manager.change_state(STATE_MENU)

    def load_scores(self):
        finished_scores = self.score_manager.load_scores()
        active_saves = self.game_manager.save_manager.list_saves()
        self.scores = []
        seen_sessions = []
        
        for i in range(len(active_saves)):
            save = active_saves[i]
            session_id = save.get('session_id')
            if session_id != None:
                seen_sessions.append(session_id)
                new_entry = {
                    "score": save.get('score', 0),
                    "level": save.get('level', 0),
                    "level_seed": save.get('level_seed'),
                    "state_seed": save.get('state_seed'),
                    "session_id": session_id,
                    "status": self.game_manager.t("ui.ongoing")
                }
                self.scores.append(new_entry)
                
        for i in range(len(finished_scores)):
            score = finished_scores[i]
            is_seen = False
            for s_id in seen_sessions:
                if score.get('session_id') == s_id:
                    is_seen = True
                    break
            
            if is_seen == False:
                score['status'] = self.game_manager.t("ui.finished")
                self.scores.append(score)
            else:
                for j in range(len(self.scores)):
                    if self.scores[j].get('session_id') == score.get('session_id'):
                        self.scores[j]['is_high_score'] = True
                        
        for i in range(len(self.scores)):
            for j in range(i + 1, len(self.scores)):
                if self.scores[i].get('score', 0) < self.scores[j].get('score', 0):
                    temp = self.scores[i]
                    self.scores[i] = self.scores[j]
                    self.scores[j] = temp
                    
        self.total_height = len(self.scores) * self.line_height
        self.scroll_y = 0

    def handle_events(self, event):
        sw = self.game_manager.screen.get_width()
        sh = self.game_manager.screen.get_height()
        self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.change_state(STATE_MENU)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if mouse_pos[0] >= 50 and mouse_pos[0] < sw - 50:
                    if mouse_pos[1] >= 160 and mouse_pos[1] < sh - 90:
                        for i in range(len(self.scores)):
                            entry = self.scores[i]
                            y_pos = i * self.line_height + self.scroll_y
                            abs_x = 50 + (sw - 230)
                            abs_y = 160 + y_pos
                            if mouse_pos[0] >= abs_x and mouse_pos[0] < abs_x + 100:
                                if mouse_pos[1] >= abs_y and mouse_pos[1] < abs_y + 30:
                                    self.game_manager.resume_game(entry)
                                    break
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = self.scroll_y + event.y * 20
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
        self.back_button.update(pygame.mouse.get_pos())

    def draw(self, surface):
        sw = surface.get_width()
        sh = surface.get_height()
        self.visible_height = sh - 250
        surface.fill(COLOR_BG)
        self.back_button.draw(surface)
        
        title_text = self.game_manager.t("menu.scores")
        title_surf = self.font_title.render(title_text.upper(), True, COLOR_ACCENT)
        surface.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 40))
        
        header_y = 120
        pygame.draw.line(surface, COLOR_ACCENT, (50, header_y + 35), (sw - 50, header_y + 35), 2)
        rank_h = self.font_item.render(self.game_manager.t("ui.rank"), True, COLOR_TEXT)
        score_h = self.font_item.render(self.game_manager.t("ui.score"), True, COLOR_TEXT)
        level_h = self.font_item.render(self.game_manager.t("ui.level"), True, COLOR_TEXT)
        status_h = self.font_item.render(self.game_manager.t("ui.status"), True, COLOR_TEXT)
        surface.blit(rank_h, (80, header_y))
        surface.blit(score_h, (200, header_y))
        surface.blit(level_h, (350, header_y))
        surface.blit(status_h, (500, header_y))
        
        content_rect = pygame.Rect(50, 160, sw - 100, self.visible_height)
        scroll_surface = pygame.Surface((content_rect.width, content_rect.height))
        scroll_surface.fill(COLOR_BG)
        
        for i in range(len(self.scores)):
            entry = self.scores[i]
            y_pos = i * self.line_height + self.scroll_y
            if y_pos + self.line_height < 0 or y_pos > self.visible_height:
                continue
            
            color = COLOR_TEXT
            if i == 0: color = (255, 215, 0)
            elif i == 1: color = (192, 192, 192)
            elif i == 2: color = (205, 127, 50)
            
            rank_text = self.font_item.render("#" + str(i), True, color)
            score_val = entry.get('score', 0)
            level_val = entry.get('level', 0) + 1
            status_val = entry.get('status', 'Score')
            
            score_text = self.font_item.render(str(score_val), True, COLOR_TEXT)
            level_text = self.font_item.render(self.game_manager.t('ui.level') + " " + str(level_val), True, COLOR_TEXT)
            
            status_color = (150, 150, 150)
            if status_val == self.game_manager.t("ui.ongoing"):
                status_color = (0, 255, 0)
            status_text = self.font_item.render(status_val, True, status_color)
            
            scroll_surface.blit(rank_text, (30, y_pos))
            scroll_surface.blit(score_text, (150, y_pos))
            scroll_surface.blit(level_text, (300, y_pos))
            scroll_surface.blit(status_text, (450, y_pos))
            
            resume_rect = pygame.Rect(sw - 230, y_pos, 100, 30)
            mouse_pos = pygame.mouse.get_pos()
            adj_mouse_pos = (mouse_pos[0] - 50, mouse_pos[1] - 160)
            
            is_resume_hovered = False
            if adj_mouse_pos[0] >= resume_rect.x and adj_mouse_pos[0] < resume_rect.x + resume_rect.width:
                if adj_mouse_pos[1] >= resume_rect.y and adj_mouse_pos[1] < resume_rect.y + resume_rect.height:
                    is_resume_hovered = True
                    
            btn_color = (60, 60, 60)
            if is_resume_hovered:
                btn_color = COLOR_ACCENT
            
            draw_rect_compat(scroll_surface, btn_color, resume_rect, 5)
            res_text = self.font_item.render(self.game_manager.t("ui.resume"), True, COLOR_TEXT)
            res_x = resume_rect.x + (resume_rect.width // 2 - res_text.get_width() // 2)
            res_y = resume_rect.y + (resume_rect.height // 2 - res_text.get_height() // 2)
            scroll_surface.blit(res_text, (res_x, res_y))
            
        surface.blit(scroll_surface, (content_rect.x, content_rect.y))
        
        if self.total_height > self.visible_height:
            bar_x = sw - 40
            bar_y = content_rect.y
            bar_w = 8
            bar_h = self.visible_height
            draw_rect_compat(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), 4)
            handle_h = bar_h * (self.visible_height / self.total_height)
            if handle_h < 20:
                handle_h = 20
            handle_y = bar_y + (-self.scroll_y / (self.total_height - self.visible_height)) * (bar_h - handle_h)
            draw_rect_compat(surface, COLOR_ACCENT, (bar_x, handle_y, bar_w, handle_h), 4)
            
        footer_text = self.font_item.render(self.game_manager.t("ui.back") + " (Esc)", True, (100, 100, 100))
        surface.blit(footer_text, (sw // 2 - footer_text.get_width() // 2, sh - 60))
