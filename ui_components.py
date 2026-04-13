import pygame
from constants import COLOR_TEXT, COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_ACCENT

class Button:
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON
        
        # Shadow/Border effect
        border_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(surface, COLOR_ACCENT, border_rect, border_radius=12)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        
        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()
