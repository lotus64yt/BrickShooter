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
        
        border_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(surface, COLOR_ACCENT, border_rect, 0, 12)
        pygame.draw.rect(surface, color, self.rect, 0, 10)
        
        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

class Carousel:
    def __init__(self, x, y, width, height, items, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = items
        self.font = font
        self.current_index = 0

    def draw(self, surface):
        if not self.items:
            return
        
        items_list = list(self.items.values()) if isinstance(self.items, dict) else self.items
        item_image = items_list[self.current_index]
        scaled_image = pygame.transform.scale(item_image, (self.rect.width, self.rect.height))
        surface.blit(scaled_image, self.rect)

    def next_item(self):
        if self.items:
            self.current_index = (self.current_index + 1) % len(self.items)

    def previous_item(self):
        if self.items:
            self.current_index = (self.current_index - 1) % len(self.items)
            
class MenuList:
    def __init__(self, x, y, width, height, items, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = items
        self.font = font
        self.selected_index = 0

    def draw(self, surface):
        for index, item in enumerate(self.items):
            color = COLOR_ACCENT if index == self.selected_index else COLOR_TEXT
            text_surf = self.font.render(item, True, color)
            text_rect = text_surf.get_rect(topleft=(self.rect.x + 10, self.rect.y + index * 40))
            surface.blit(text_surf, text_rect)
    
    def hover_item(self, mouse_pos):
        for index in range(len(self.items)):
            item_rect = pygame.Rect(self.rect.x, self.rect.y + index * 40, self.rect.width, 40)
            if item_rect.collidepoint(mouse_pos):
                self.selected_index = index
                break
            else:
                self.selected_index = -1
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_item(pygame.mouse.get_pos())
    
    def get_selected_item(self):
        return self.items[self.selected_index] if self.items else None