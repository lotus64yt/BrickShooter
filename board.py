import pygame
import random
from constants import (
    GRID_SIZE, INNER_START, INNER_END, CELL_SIZE, 
    BOARD_OFFSET_X, BOARD_OFFSET_Y, BLOCK_COLORS
)
from levels import LEVEL_DATA

class Board:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.level = 0
        self.animations = []
        self.pending_logic = False

    def generate_level(self, level_idx):
        self.level = level_idx
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        if level_idx < len(LEVEL_DATA):
            level_map = LEVEL_DATA[level_idx]
            for row_idx, row_str in enumerate(level_map):
                for col_idx, char in enumerate(row_str):
                    if char != 'X':
                        color_idx = int(char)
                        if color_idx < len(BLOCK_COLORS):
                            self.grid[INNER_START + row_idx][INNER_START + col_idx] = {
                                'color': BLOCK_COLORS[color_idx],
                                'dir': None
                            }
        else:
            num_colors = min(2 + level_idx, len(BLOCK_COLORS))
            available_colors = BLOCK_COLORS[:num_colors]
            
            fill_density = 0.3 + min(0.4, (level_idx - len(LEVEL_DATA)) * 0.05)
            for y in range(INNER_START + 1, INNER_END - 1):
                for x in range(INNER_START + 1, INNER_END - 1):
                    if random.random() < fill_density:
                        choices = available_colors[:]
                        random.shuffle(choices)
                        for color in choices:
                            h_count = 0
                            if x > INNER_START + 1 and self.grid[y][x-1] and self.grid[y][x-1]['color'] == color:
                                h_count += 1
                                if x > INNER_START + 2 and self.grid[y][x-2] and self.grid[y][x-2]['color'] == color:
                                    h_count += 1
                            
                            v_count = 0
                            if y > INNER_START + 1 and self.grid[y-1][x] and self.grid[y-1][x]['color'] == color:
                                v_count += 1
                                if y > INNER_START + 2 and self.grid[y-2][x] and self.grid[y-2][x]['color'] == color:
                                    v_count += 1
                            
                            if h_count < 2 and v_count < 2:
                                self.grid[y][x] = {
                                    'color': color,
                                    'dir': None
                                }
                                break
        
        num_colors = min(2 + level_idx, len(BLOCK_COLORS))
        available_colors = BLOCK_COLORS[:num_colors]
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x]: continue
                
                is_in_center = (INNER_START <= x < INNER_END) and (INNER_START <= y < INNER_END)
                if not is_in_center:
                    is_top_left = (x < INNER_START and y < INNER_START)
                    is_top_right = (x >= INNER_END and y < INNER_START)
                    is_bottom_left = (x < INNER_START and y >= INNER_END)
                    is_bottom_right = (x >= INNER_END and y >= INNER_END)
                    
                    if not (is_top_left or is_top_right or is_bottom_left or is_bottom_right):
                        direction = None
                        if y < INNER_START: direction = "down"
                        elif y >= INNER_END: direction = "up"
                        elif x < INNER_START: direction = "right"
                        elif x >= INNER_END: direction = "left"
                        
                        self.grid[y][x] = {
                            'color': random.choice(available_colors),
                            'dir': direction
                        }

    def get_firing_head(self, x, y):
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE): return None, None
        
        if INNER_START <= x < INNER_END and 0 <= y < INNER_START:
            for hy in range(INNER_START - 1, -1, -1):
                if self.grid[hy][x]: return (x, hy), "down"
        elif INNER_START <= x < INNER_END and INNER_END <= y < GRID_SIZE:
            for hy in range(INNER_END, GRID_SIZE):
                if self.grid[hy][x]: return (x, hy), "up"
        elif 0 <= x < INNER_START and INNER_START <= y < INNER_END:
            for hx in range(INNER_START - 1, -1, -1):
                if self.grid[y][hx]: return (hx, y), "right"
        elif INNER_END <= x < GRID_SIZE and INNER_START <= y < INNER_END:
            for hx in range(INNER_END, GRID_SIZE):
                if self.grid[y][hx]: return (hx, y), "left"
        return None, None

    def is_line_firable(self, x, y, direction):
        if direction == "down":
            if self.grid[INNER_START][x]: return False
        elif direction == "up":
            if self.grid[INNER_END - 1][x]: return False
        elif direction == "right":
            if self.grid[y][INNER_START]: return False
        elif direction == "left":
            if self.grid[y][INNER_END - 1]: return False
            
        if INNER_START <= x < INNER_END:
            for hy in range(INNER_START, INNER_END):
                if self.grid[hy][x]: return True
        if INNER_START <= y < INNER_END:
            for hx in range(INNER_START, INNER_END):
                if self.grid[y][hx]: return True
        
        return False

    def handle_click(self, mouse_pos):
        if self.animations: return
        
        rel_x = mouse_pos[0] - BOARD_OFFSET_X
        rel_y = mouse_pos[1] - BOARD_OFFSET_Y
        if 0 <= rel_x < GRID_SIZE * CELL_SIZE and 0 <= rel_y < GRID_SIZE * CELL_SIZE:
            grid_x = rel_x // CELL_SIZE
            grid_y = rel_y // CELL_SIZE
            
            head, direction = self.get_firing_head(grid_x, grid_y)
            if head and self.is_line_firable(grid_x, grid_y, direction):
                self.fire_block(head[0], head[1], direction)
                self.pending_logic = True

    def fire_block(self, x, y, direction):
        block = self.grid[y][x]
        self.grid[y][x] = None
        
        hit_pos = None
        if direction == "down":
            for hy in range(INNER_START, INNER_END):
                if self.grid[hy][x]:
                    hit_pos = (x, hy)
                    break
        elif direction == "up":
            for hy in range(INNER_END - 1, INNER_START - 1, -1):
                if self.grid[hy][x]:
                    hit_pos = (x, hy)
                    break
        elif direction == "right":
            for hx in range(INNER_START, INNER_END):
                if self.grid[y][hx]:
                    hit_pos = (hx, y)
                    break
        elif direction == "left":
            for hx in range(INNER_END - 1, INNER_START - 1, -1):
                if self.grid[y][hx]:
                    hit_pos = (hx, y)
                    break

        if hit_pos:
            tx, ty = x, y
            if direction == "down":
                for hy in range(y + 1, hit_pos[1]):
                    ty = hy
            elif direction == "up":
                for hy in range(y - 1, hit_pos[1], -1):
                    ty = hy
            elif direction == "right":
                for hx in range(x + 1, hit_pos[0]):
                    tx = hx
            elif direction == "left":
                for hx in range(x - 1, hit_pos[0], -1):
                    tx = hx

            if (tx, ty) != (x, y):
                self._add_move_anim(block, (x, y), (tx, ty))
            else:
                self.grid[y][x] = block
        else:
            target_pos = self._get_exit_pos(x, y, direction)
            self._add_move_anim(block, (x, y), target_pos, on_complete=lambda b=block: self.enter_column(x, y, direction, b))
        
        self.refill_column_or_row(x, y, direction)

    def apply_inertia(self):
        to_move = []
        for y in range(INNER_START, INNER_END):
            for x in range(INNER_START, INNER_END):
                cell = self.grid[y][x]
                if cell and cell['dir']:
                    dx, dy = 0, 0
                    if cell['dir'] == "down": dy = 1
                    elif cell['dir'] == "up": dy = -1
                    elif cell['dir'] == "right": dx = 1
                    elif cell['dir'] == "left": dx = -1
                    
                    nx, ny = x + dx, y + dy
                    if INNER_START <= nx < INNER_END and INNER_START <= ny < INNER_END:
                        if not self.grid[ny][nx]:
                            to_move.append((x, y, nx, ny, cell['dir']))
                    else:
                        to_move.append((x, y, None, None, cell['dir']))
        
        if to_move:
            for x, y, tx, ty, direction in to_move:
                block = self.grid[y][x]
                self.grid[y][x] = None
                if tx is not None:
                    self._add_move_anim(block, (x, y), (tx, ty))
                else:
                    target_pos = self._get_exit_pos(x, y, direction)
                    self._add_move_anim(block, (x, y), target_pos, on_complete=lambda b=block: self.enter_column(x, y, direction, b))
            return True
        return False

    def _get_exit_pos(self, x, y, direction):
        if direction == "down": return (x, INNER_END - 1)
        if direction == "up": return (x, INNER_START)
        if direction == "right": return (INNER_END - 1, y)
        if direction == "left": return (INNER_START, y)
        return (x, y)

    def _add_move_anim(self, block, start_grid, end_grid, on_complete=None):
        anim = {
            'type': 'move',
            'block': block,
            'start': pygame.Vector2(start_grid[0] * CELL_SIZE, start_grid[1] * CELL_SIZE),
            'end': pygame.Vector2(end_grid[0] * CELL_SIZE, end_grid[1] * CELL_SIZE),
            'pos': pygame.Vector2(start_grid[0] * CELL_SIZE, start_grid[1] * CELL_SIZE),
            'end_grid': end_grid,
            'progress': 0,
            'elapsed': 0,
            'duration': 150,
            'history': [],
            'on_complete': on_complete
        }
        self.animations.append(anim)

    def enter_column(self, x, y, direction, block):
        if direction == "down":
            for hy in range(GRID_SIZE - 1, INNER_END, -1):
                self.grid[hy][x] = self.grid[hy-1][x]
            self.grid[INNER_END][x] = block
        elif direction == "up":
            for hy in range(0, INNER_START - 1):
                self.grid[hy][x] = self.grid[hy+1][x]
            self.grid[INNER_START-1][x] = block
        elif direction == "right":
            for hx in range(GRID_SIZE - 1, INNER_END, -1):
                self.grid[y][hx] = self.grid[y][hx-1]
            self.grid[y][INNER_END] = block
        elif direction == "left":
            for hx in range(0, INNER_START - 1):
                self.grid[y][hx] = self.grid[y][hx+1]
            self.grid[y][INNER_START-1] = block

    def update_logic_step(self):
        matches = self.find_matches()
        if matches:
            num_blocks = len(matches)
            score = 30 * (2 ** (num_blocks - 3))
            self.game_manager.add_score(score)
            
            avg_x = sum(m[0] for m in matches) / num_blocks
            avg_y = sum(m[1] for m in matches) / num_blocks
            
            for mx, my in matches:
                block = self.grid[my][mx]
                self._add_fade_anim(block, (mx, my))
                self.grid[my][mx] = None
            
            self._add_score_text_anim(score, (avg_x, avg_y))
            return True
        
        if self.apply_inertia():
            return True
        return False

    def _add_fade_anim(self, block, grid_pos):
        anim = {
            'type': 'fade',
            'block': block,
            'pos': pygame.Vector2(grid_pos[0] * CELL_SIZE, grid_pos[1] * CELL_SIZE),
            'elapsed': 0,
            'duration': 400,
            'progress': 0
        }
        self.animations.append(anim)

    def _add_score_text_anim(self, score, grid_pos):
        anim = {
            'type': 'score_text',
            'text': f"+{score}",
            'start_pos': pygame.Vector2(grid_pos[0] * CELL_SIZE, grid_pos[1] * CELL_SIZE),
            'pos': pygame.Vector2(grid_pos[0] * CELL_SIZE, grid_pos[1] * CELL_SIZE),
            'elapsed': 0,
            'duration': 1000,
            'progress': 0
        }
        self.animations.append(anim)

    def update(self, dt):
        if not self.animations:
            if self.pending_logic:
                if not self.update_logic_step():
                    self.pending_logic = False
            return

        all_finished = True
        for anim in self.animations:
            anim['elapsed'] += dt
            if anim['elapsed'] >= anim['duration']:
                anim['progress'] = 1.0
                if anim['type'] == 'move' and not anim.get('completed', False):
                    tx, ty = anim['end_grid']
                    if anim['on_complete']:
                        anim['on_complete']()
                    elif not self.grid[ty][tx]:
                        self.grid[ty][tx] = anim['block']
                    anim['completed'] = True
            else:
                anim['progress'] = anim['elapsed'] / anim['duration']
                all_finished = False
            
            if anim['type'] == 'move':
                anim['pos'] = anim['start'].lerp(anim['end'], anim['progress'])
                anim['history'].append(anim['pos'].copy())
                if len(anim['history']) > 8:
                    anim['history'].pop(0)
            elif anim['type'] == 'score_text':
                anim['pos'].y = anim['start_pos'].y - (anim['progress'] * 40)

        if all_finished:
            self.animations = []

    def find_matches(self):
        to_remove = set()
        visited = set()
        for y in range(INNER_START, INNER_END):
            for x in range(INNER_START, INNER_END):
                if self.grid[y][x] and (x, y) not in visited:
                    color = self.grid[y][x]['color']
                    component = self._get_connected_component(x, y, color)
                    visited.update(component)
                    if len(component) >= 3:
                        to_remove.update(component)
        return to_remove

    def _get_connected_component(self, start_x, start_y, color):
        component = []
        stack = [(start_x, start_y)]
        visited = set([(start_x, start_y)])
        
        while stack:
            x, y = stack.pop()
            component.append((x, y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if INNER_START <= nx < INNER_END and INNER_START <= ny < INNER_END:
                    if self.grid[ny][nx] and self.grid[ny][nx]['color'] == color:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            stack.append((nx, ny))
        return component

    def refill_column_or_row(self, x, y, direction):
        num_colors = min(2 + self.level, len(BLOCK_COLORS))
        available_colors = BLOCK_COLORS[:num_colors]

        if direction == "down":
            for hy in range(y, 0, -1):
                self.grid[hy][x] = self.grid[hy-1][x]
            self.grid[0][x] = {'color': random.choice(available_colors), 'dir': 'down'}
        elif direction == "up":
            for hy in range(y, GRID_SIZE - 1):
                self.grid[hy][x] = self.grid[hy+1][x]
            self.grid[GRID_SIZE-1][x] = {'color': random.choice(available_colors), 'dir': 'up'}
        elif direction == "right":
            for hx in range(x, 0, -1):
                self.grid[y][hx] = self.grid[y][hx-1]
            self.grid[y][0] = {'color': random.choice(available_colors), 'dir': 'right'}
        elif direction == "left":
            for hx in range(x, GRID_SIZE - 1):
                self.grid[y][hx] = self.grid[y][hx+1]
            self.grid[y][GRID_SIZE-1] = {'color': random.choice(available_colors), 'dir': 'left'}

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        rel_x = mouse_pos[0] - BOARD_OFFSET_X
        rel_y = mouse_pos[1] - BOARD_OFFSET_Y
        grid_x, grid_y = -1, -1
        if 0 <= rel_x < GRID_SIZE * CELL_SIZE and 0 <= rel_y < GRID_SIZE * CELL_SIZE:
            grid_x = rel_x // CELL_SIZE
            grid_y = rel_y // CELL_SIZE

        hovered_head, direction = self.get_firing_head(grid_x, grid_y)
        firable = False
        if hovered_head:
            firable = self.is_line_firable(grid_x, grid_y, direction)

        center_rect = pygame.Rect(
            BOARD_OFFSET_X + INNER_START * CELL_SIZE,
            BOARD_OFFSET_Y + INNER_START * CELL_SIZE,
            (INNER_END - INNER_START) * CELL_SIZE,
            (INNER_END - INNER_START) * CELL_SIZE
        )
        pygame.draw.rect(surface, (25, 25, 25), center_rect)
        pygame.draw.rect(surface, (50, 50, 50), center_rect, 2)

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = self.grid[y][x]
                if cell:
                    self._draw_block_at(surface, cell, BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y + y * CELL_SIZE)
                    is_on_grid = (INNER_START <= x < INNER_END) and (INNER_START <= y < INNER_END)
                    if is_on_grid and cell['dir']:
                        block_rect = pygame.Rect(BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE).inflate(-6, -6)
                        self._draw_arrow(surface, block_rect, cell['dir'], color=(255, 255, 255), alpha=180)
                    if hovered_head == (x, y):
                        block_rect = pygame.Rect(BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE).inflate(-6, -6)
                        if firable:
                            self._draw_arrow(surface, block_rect, direction)
                        else:
                            self._draw_cross(surface, block_rect)

        for anim in self.animations:
            if anim['type'] == 'move':
                for i, h_pos in enumerate(anim['history']):
                    alpha = int(255 * (i / len(anim['history'])) * 0.3)
                    self._draw_block_at(surface, anim['block'], BOARD_OFFSET_X + h_pos.x, BOARD_OFFSET_Y + h_pos.y, alpha=alpha)
                self._draw_block_at(surface, anim['block'], BOARD_OFFSET_X + anim['pos'].x, BOARD_OFFSET_Y + anim['pos'].y)
            elif anim['type'] == 'fade':
                alpha = int(255 * (1.0 - anim['progress']))
                self._draw_block_at(surface, anim['block'], BOARD_OFFSET_X + anim['pos'].x, BOARD_OFFSET_Y + anim['pos'].y, alpha=alpha)
            elif anim['type'] == 'score_text':
                alpha = int(255 * (1.0 - anim['progress']))
                text_surf = self.game_manager.font_game.render(anim['text'], True, (255, 255, 255))
                text_surf.set_alpha(alpha)
                surface.blit(text_surf, (BOARD_OFFSET_X + anim['pos'].x + CELL_SIZE//2 - text_surf.get_width()//2, 
                                        BOARD_OFFSET_Y + anim['pos'].y))

    def _draw_block_at(self, surface, cell, x, y, alpha=255):
        color = cell['color']
        if alpha < 255:
            color = [int(c * (alpha/255) + 18 * (1 - alpha/255)) for c in color]

        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        block_rect = rect.inflate(-6, -6)
        pygame.draw.rect(surface, color, block_rect, border_radius=6)
        if alpha == 255:
            highlight_rect = pygame.Rect(block_rect.x + 3, block_rect.y + 3, block_rect.width - 6, block_rect.height // 2)
            highlight_color = [min(c + 40, 255) for c in color]
            pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=6)
            bottom_rect = pygame.Rect(block_rect.x, block_rect.y + block_rect.height // 2, block_rect.width, block_rect.height // 2)
            pygame.draw.rect(surface, color, bottom_rect, border_bottom_left_radius=6, border_bottom_right_radius=6)

    def _draw_arrow(self, surface, rect, direction, color=(255, 255, 255), alpha=255):
        center_x = rect.centerx
        center_y = rect.centery
        size = CELL_SIZE // 4
        if direction == "down":
            points = [(center_x - size, center_y - size), (center_x + size, center_y - size), (center_x, center_y + size)]
        elif direction == "up":
            points = [(center_x - size, center_y + size), (center_x + size, center_y + size), (center_x, center_y - size)]
        elif direction == "left":
            points = [(center_x + size, center_y - size), (center_x + size, center_y + size), (center_x - size, center_y)]
        elif direction == "right":
            points = [(center_x - size, center_y - size), (center_x - size, center_y + size), (center_x + size, center_y)]
        else: return
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 2)

    def _draw_cross(self, surface, rect):
        center_x = rect.centerx
        center_y = rect.centery
        size = CELL_SIZE // 4
        color = (255, 50, 50)
        pygame.draw.line(surface, (0, 0, 0), (center_x - size + 1, center_y - size + 1), (center_x + size + 1, center_y + size + 1), 5)
        pygame.draw.line(surface, (0, 0, 0), (center_x + size + 1, center_y - size + 1), (center_x - size + 1, center_y + size + 1), 5)
        pygame.draw.line(surface, color, (center_x - size, center_y - size), (center_x + size, center_y + size), 3)
        pygame.draw.line(surface, color, (center_x + size, center_y - size), (center_x - size, center_y + size), 3)

    def is_cleared(self):
        for y in range(INNER_START, INNER_END):
            for x in range(INNER_START, INNER_END):
                if self.grid[y][x]:
                    return False
        return True
