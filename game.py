import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, STATE_MENU, STATE_GAME, STATE_SCORES, STATE_SETTINGS, COLOR_BG, COLOR_TEXT, COLOR_ACCENT, BOARD_OFFSET_X, BOARD_OFFSET_Y, CELL_SIZE, GRID_SIZE
from menu import Menu
from board import Board
from score_screen import ScoreScreen
from score_manager import ScoreManager
from settings_screen import SettingsScreen
from save_manager import SaveManager
from i18n.i18n import create_translator
from audio_manager import AudioManager
from settings_manager import SettingsManager

class GameManager:
    def __init__(self):
        pygame.init()
        self.settings_manager = SettingsManager()

        try:
            flags = pygame.SCALED
        except AttributeError:
            flags = 0

        if self.settings_manager.get("fullscreen"):
            flags = flags | pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Brick Shooter")
        self.clock = pygame.time.Clock()
        self.running = True

        self.audio_manager = AudioManager(self.settings_manager)
        self.audio_manager.start_music()

        self.score_manager = ScoreManager()
        self.save_manager = SaveManager()
        self.current_state = STATE_MENU
        self.board = Board(self)

        self.update_language()

        self.level = 0
        self.score = 0
        self.current_session_id = None

        self.font_menu = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_game = pygame.font.SysFont('Arial', 24, bold=True)

    def change_state(self, new_state):
        if self.current_state == STATE_GAME:
            if new_state == STATE_MENU:
                if self.score > 0:
                    self.score_manager.save_score(
                        self.score,
                        self.level,
                        self.board.level_seed,
                        self.board.get_state_seed(),
                        self.current_session_id
                    )

                self.score = 0
                self.level = 0
                self.current_session_id = None

        self.current_state = new_state
        if new_state == STATE_GAME:
            if self.current_session_id == None:
                self.board.generate_level(self.level)
                self.current_session_id = self.save_manager.create_new_save(
                    self.level, self.score, self.board.level_seed, self.board.get_state_seed()
                )
        elif new_state == STATE_SCORES:
            self.score_screen.load_scores()

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
                        self.level = self.level + 1
                        self.board.generate_level(self.level)
                    elif event.key == pygame.K_p:
                        self.level = self.level - 1
                        if self.level < 0:
                            self.level = 0
                        self.board.generate_level(self.level)
            elif self.current_state == STATE_SCORES:
                self.score_screen.handle_events(event)
            elif self.current_state == STATE_SETTINGS:
                self.settings_screen.handle_events(event)

    def add_score(self, pts):
        self.score = self.score + pts

    def resume_game(self, entry):
        self.score = entry.get('score', 0)
        self.level = entry.get('level', 0)
        level_seed = entry.get('level_seed')
        state_seed = entry.get('state_seed')

        self.current_state = STATE_GAME
        self.board.generate_level(self.level, seed=level_seed)
        if state_seed != None:
            self.board.load_from_state_seed(state_seed)

        if entry.get('session_id') != None:
            self.current_session_id = entry.get('session_id')
        else:
            self.current_session_id = self.save_manager.create_new_save(
                self.level, self.score, level_seed, state_seed
            )

    def toggle_fullscreen(self, is_fullscreen):
        pygame.display.toggle_fullscreen()

    def auto_save(self):
        if self.current_session_id != None:
            if self.current_state == STATE_GAME:
                self.save_manager.update_save(
                    self.current_session_id,
                    self.level,
                    self.score,
                    self.board.level_seed,
                    self.board.get_state_seed()
                )

    def update_language(self):
        lang_name = self.settings_manager.get("language")
        current_lang = "fr"
        if lang_name == "Anglais":
            current_lang = "en"
        elif lang_name == "Espagnol":
            current_lang = "es"

        self.t = create_translator("i18n/locales", current_lang)

        self.menu = Menu(self)
        self.score_screen = ScoreScreen(self)
        self.settings_screen = SettingsScreen(self)

    def update(self, dt):
        if self.current_state == STATE_MENU:
            self.menu.update()
        elif self.current_state == STATE_GAME:
            self.board.update(dt)
            if len(self.board.animations) == 0:
                if self.board.pending_logic == False:
                    if self.board.is_cleared():
                        self.audio_manager.play_sfx("win")
                        self.level = self.level + 1
                        self.board.generate_level(self.level)
                        self.auto_save()
        elif self.current_state == STATE_SCORES:
            self.score_screen.update()
        elif self.current_state == STATE_SETTINGS:
            self.settings_screen.update()

    def draw(self):
        if self.current_state == STATE_MENU:
            self.menu.draw(self.screen)
        elif self.current_state == STATE_SCORES:
            self.score_screen.draw(self.screen)
        elif self.current_state == STATE_SETTINGS:
            self.settings_screen.draw(self.screen)
        elif self.current_state == STATE_GAME:
            self.screen.fill(COLOR_BG)
            self.board.draw(self.screen)

            level_text = self.font_game.render(self.t('ui.level') + ": " + str(self.level + 1), True, COLOR_TEXT)
            score_text = self.font_game.render(self.t('ui.score') + ": " + str(self.score), True, COLOR_ACCENT)

            self.screen.blit(level_text, (20, 20))
            self.screen.blit(score_text, (20, 55))

            hint_text = self.font_game.render(self.t("ui.hints"), True, (100, 100, 100))
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 40))

            if self.settings_manager.get("show_fps"):
                fps_val = int(self.clock.get_fps())
                fps_text = self.font_game.render(self.t("ui.fps", fps_val), True, (0, 255, 0))
                self.screen.blit(fps_text, (self.screen.get_width() - 100, 20))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
