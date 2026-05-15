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
        self._x = x
        self._y = y
        self.rect = pygame.Rect(x, y, width, height)
        self.items = items
        self.font = font
        self.current_index = 0

    @property
    def x(self): return self._x
    @x.setter
    def x(self, val):
        self._x = val
        self.rect.x = val - self.rect.width // 2
    @property
    def y(self): return self._y
    @y.setter
    def y(self, val):
        self._y = val
        self.rect.y = val - self.rect.height // 2

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

class CarouselControls:

    def __init__(self, carousel, font):
        self.carousel = carousel
        self.font = font
        self.button_size = 40
        self.update_pos()

    def update_pos(self):
        self.left_button_rect = pygame.Rect(self.carousel.rect.x - self.button_size - 20, self.carousel.rect.centery - self.button_size // 2, self.button_size, self.button_size)
        self.right_button_rect = pygame.Rect(self.carousel.rect.right + 20, self.carousel.rect.centery - self.button_size // 2, self.button_size, self.button_size)

    def draw(self, surface):
        pygame.draw.polygon(surface, COLOR_ACCENT, [
            (self.left_button_rect.centerx + 10, self.left_button_rect.centery - 10),
            (self.left_button_rect.centerx + 10, self.left_button_rect.centery + 10),
            (self.left_button_rect.centerx - 10, self.left_button_rect.centery)
        ])
        pygame.draw.polygon(surface, COLOR_ACCENT, [
            (self.right_button_rect.centerx - 10, self.right_button_rect.centery - 10),
            (self.right_button_rect.centerx - 10, self.right_button_rect.centery + 10),
            (self.right_button_rect.centerx + 10, self.right_button_rect.centery)
        ])
        self.carousel.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.left_button_rect.collidepoint(mouse_pos):
                self.carousel.previous_item()
            elif self.right_button_rect.collidepoint(mouse_pos):
                self.carousel.next_item()

class MenuList:

    def __init__(self, x, y, width, height, items, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = items
        self.font = font
        self.selected_index = 0

    @property
    def x(self): return self.rect.x
    @x.setter
    def x(self, val): self.rect.x = val
    @property
    def y(self): return self.rect.y
    @y.setter
    def y(self, val): self.rect.y = val

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
        if self.selected_index >= 0 and self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None