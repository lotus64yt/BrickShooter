import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, STATE_MENU, STATE_GAME, COLOR_BG, COLOR_TEXT, COLOR_ACCENT, BOARD_OFFSET_X, BOARD_OFFSET_Y, CELL_SIZE, GRID_SIZE
from menu import Menu
from board import Board

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Brick Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.current_state = STATE_MENU
        self.menu = Menu(self)
        self.board = Board(self)
        self.level = 0
        self.score = 0
        
        self.font_menu = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_game = pygame.font.SysFont('Arial', 24, bold=True)

    def change_state(self, new_state):
        self.current_state = new_state
        if new_state == STATE_GAME:
            self.board.generate_level(self.level)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.current_state == STATE_MENU:
                self.menu.handle_events(event)
            elif self.current_state == STATE_GAME:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.board.handle_click(event.pos)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.change_state(STATE_MENU)
                    elif event.key == pygame.K_n:
                        self.level += 1
                        self.board.generate_level(self.level)
                    elif event.key == pygame.K_p:
                        self.level = max(0, self.level - 1)
                        self.board.generate_level(self.level)

    def add_score(self, pts):
        self.score += pts

    def update(self, dt):
        if self.current_state == STATE_MENU:
            self.menu.update()
        elif self.current_state == STATE_GAME:
            self.board.update(dt)
            if not self.board.animations and not self.board.pending_logic:
                if self.board.is_cleared():
                    self.level += 1
                    self.board.generate_level(self.level)

    def draw(self):
        if self.current_state == STATE_MENU:
            self.menu.draw(self.screen)
        elif self.current_state == STATE_GAME:
            self.screen.fill(COLOR_BG)
            self.board.draw(self.screen)
            
            level_text = self.font_game.render(f"Niveau: {self.level + 1}", True, COLOR_TEXT)
            score_text = self.font_game.render(f"Score: {self.score}", True, COLOR_ACCENT)
            
            self.screen.blit(level_text, (20, 20))
            self.screen.blit(score_text, (20, 55))
            
            hint_text = self.font_game.render("N: Suivant | P: Précédent | Echap: Menu", True, (100, 100, 100))
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
