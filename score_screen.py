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
        self.visible_height = 0
        self.total_height = 0
        self.back_button = Button(
            20, 20, 120, 40, 
            self.game_manager.t("ui.back"), pygame.font.SysFont("Arial", 20, bold=True),
            action=lambda: self.game_manager.change_state(STATE_MENU)
        )

    def load_scores(self):
        finished_scores = self.score_manager.load_scores()
        active_saves = self.game_manager.save_manager.list_saves()
        self.scores = []
        seen_sessions = set()
        for save in active_saves:
            session_id = save.get('session_id')
            if session_id:
                seen_sessions.add(session_id)
                self.scores.append({
                    "score": save.get('score', 0),
                    "level": save.get('level', 0),
                    "level_seed": save.get('level_seed'),
                    "state_seed": save.get('state_seed'),
                    "session_id": session_id,
                    "status": self.game_manager.t("ui.ongoing")
                })
        for score in finished_scores:
            if score.get('session_id') not in seen_sessions:
                score['status'] = self.game_manager.t("ui.finished")
                self.scores.append(score)
            else:
                for s in self.scores:
                    if s.get('session_id') == score.get('session_id'):
                        s['is_high_score'] = True
        self.scores.sort(key=lambda x: x.get('score', 0), reverse=True)
        self.total_height = len(self.scores) * self.line_height
        self.scroll_y = 0

    def handle_events(self, event):
        sw, sh = self.game_manager.screen.get_size()
        self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.change_state(STATE_MENU)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            content_rect = pygame.Rect(50, 160, sw - 100, sh - 250)
            if content_rect.collidepoint(mouse_pos):
                for i, entry in enumerate(self.scores):
                    y_pos = i * self.line_height + self.scroll_y
                    abs_x = 50 + (sw - 230)
                    abs_y = 160 + y_pos
                    resume_rect = pygame.Rect(abs_x, abs_y, 100, 30)
                    if resume_rect.collidepoint(mouse_pos):
                        self.game_manager.resume_game(entry)
                        break
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
        sw, sh = surface.get_size()
        self.visible_height = sh - 250
        surface.fill(COLOR_BG)
        self.back_button.draw(surface)
        title_surf = self.font_title.render(self.game_manager.t("menu.scores").upper(), True, COLOR_ACCENT)
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
                rank_text = self.font_item.render(f"#{i}", True, color)
                score_val = entry.get('score', 0)
                level_val = entry.get('level', 0) + 1
                status_val = entry.get('status', 'Score')
                score_text = self.font_item.render(f"{score_val:,}", True, COLOR_TEXT)
                level_text = self.font_item.render(f"{self.game_manager.t('ui.level')} {level_val}", True, COLOR_TEXT)
                status_text = self.font_item.render(status_val, True, (0, 255, 0) if status_val == self.game_manager.t("ui.ongoing") else (150, 150, 150))
                scroll_surface.blit(rank_text, (30, y_pos))
                scroll_surface.blit(score_text, (150, y_pos))
                scroll_surface.blit(level_text, (300, y_pos))
                scroll_surface.blit(status_text, (450, y_pos))
                resume_rect = pygame.Rect(sw - 230, y_pos, 100, 30)
                mouse_pos = pygame.mouse.get_pos()
                adj_mouse_pos = (mouse_pos[0] - 50, mouse_pos[1] - 160)
                is_resume_hovered = resume_rect.collidepoint(adj_mouse_pos)
                btn_color = COLOR_ACCENT if is_resume_hovered else (60, 60, 60)
                pygame.draw.rect(scroll_surface, btn_color, resume_rect, 0, 5)
                res_text = self.font_item.render(self.game_manager.t("ui.resume"), True, COLOR_TEXT)
                res_rect = res_text.get_rect(center=resume_rect.center)
                scroll_surface.blit(res_text, res_rect)
            surface.blit(scroll_surface, (content_rect.x, content_rect.y))
        except Exception as e:
            print(f"Drawing error: {e}")
        if self.total_height > self.visible_height:
            bar_x = sw - 40
            bar_y = content_rect.y
            bar_w = 8
            bar_h = self.visible_height
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), 0, 4)
            handle_h = max(20, bar_h * (self.visible_height / self.total_height))
            handle_y = bar_y + (-self.scroll_y / (self.total_height - self.visible_height)) * (bar_h - handle_h) if self.total_height > self.visible_height else bar_y
            pygame.draw.rect(surface, COLOR_ACCENT, (bar_x, handle_y, bar_w, handle_h), 0, 4)
        footer_text = self.font_item.render(self.game_manager.t("ui.back") + " (Esc)", True, (100, 100, 100))
        surface.blit(footer_text, (sw // 2 - footer_text.get_width() // 2, sh - 60))
