import pygame
import random
from constants import (
    GRID_SIZE, INNER_START, INNER_END, CELL_SIZE, 
    BOARD_OFFSET_X, BOARD_OFFSET_Y, BLOCK_COLORS
)

def draw_rect_compat(surface, color, rect, radius=0):
    try:
        pygame.draw.rect(surface, color, rect, 0, border_radius=radius)
    except:
        pygame.draw.rect(surface, color, rect, 0)
from levels import LEVEL_DATA

class Board:

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.grid = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                row.append(None)
            self.grid.append(row)
        self.level = 0
        self.level_seed = None
        self.rng = random.Random()
        self.animations = []
        self.pending_logic = False
        self.needs_save = False

    def generate_level(self, level_idx, seed=None):
        self.level = level_idx
        if seed == None:
            self.level_seed = random.randint(0, 999999)
        else:
            self.level_seed = seed
        self.rng.seed(self.level_seed)
        
        self.grid = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                row.append(None)
            self.grid.append(row)

        if level_idx < len(LEVEL_DATA):
            level_map = LEVEL_DATA[level_idx]
            for row_idx in range(len(level_map)):
                row_str = level_map[row_idx]
                for col_idx in range(len(row_str)):
                    char = row_str[col_idx]
                    if char != 'X':
                        color_idx = int(char)
                        if color_idx < len(BLOCK_COLORS):
                            self.grid[INNER_START + row_idx][INNER_START + col_idx] = {
                                'color': BLOCK_COLORS[color_idx],
                                'dir': None
                            }
        else:
            num_colors = 2 + level_idx
            if num_colors > len(BLOCK_COLORS):
                num_colors = len(BLOCK_COLORS)
            available_colors = []
            for i in range(num_colors):
                available_colors.append(BLOCK_COLORS[i])
            
            fill_density = 0.3 + (level_idx - len(LEVEL_DATA)) * 0.05
            if fill_density > 0.7:
                fill_density = 0.7
                
            for y in range(INNER_START + 1, INNER_END - 1):
                for x in range(INNER_START + 1, INNER_END - 1):
                    if self.rng.random() < fill_density:
                        choices = []
                        for c in available_colors:
                            choices.append(c)
                        self.rng.shuffle(choices)
                        for color in choices:
                            h_count = 0
                            if x > INNER_START + 1:
                                if self.grid[y][x-1] != None:
                                    if self.grid[y][x-1]['color'] == color:
                                        h_count = h_count + 1
                                        if x > INNER_START + 2:
                                            if self.grid[y][x-2] != None:
                                                if self.grid[y][x-2]['color'] == color:
                                                    h_count = h_count + 1
                            v_count = 0
                            if y > INNER_START + 1:
                                if self.grid[y-1][x] != None:
                                    if self.grid[y-1][x]['color'] == color:
                                        v_count = v_count + 1
                                        if y > INNER_START + 2:
                                            if self.grid[y-2][x] != None:
                                                if self.grid[y-2][x]['color'] == color:
                                                    v_count = v_count + 1
                            if h_count < 2 and v_count < 2:
                                self.grid[y][x] = {
                                    'color': color,
                                    'dir': None
                                }
                                break

        num_colors = 2 + level_idx
        if num_colors > len(BLOCK_COLORS):
            num_colors = len(BLOCK_COLORS)
        available_colors = []
        for i in range(num_colors):
            available_colors.append(BLOCK_COLORS[i])
            
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] != None:
                    continue
                
                is_in_center = False
                if x >= INNER_START and x < INNER_END:
                    if y >= INNER_START and y < INNER_END:
                        is_in_center = True
                
                if is_in_center == False:
                    is_top_left = (x < INNER_START and y < INNER_START)
                    is_top_right = (x >= INNER_END and y < INNER_START)
                    is_bottom_left = (x < INNER_START and y >= INNER_END)
                    is_bottom_right = (x >= INNER_END and y >= INNER_END)
                    
                    if not (is_top_left or is_top_right or is_bottom_left or is_bottom_right):
                        direction = None
                        if y < INNER_START:
                            direction = "down"
                        elif y >= INNER_END:
                            direction = "up"
                        elif x < INNER_START:
                            direction = "right"
                        elif x >= INNER_END:
                            direction = "left"
                        
                        self.grid[y][x] = {
                            'color': self.rng.choice(available_colors),
                            'dir': direction
                        }

    def get_firing_head(self, x, y):
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return None, None
            
        if x >= INNER_START and x < INNER_END and y < INNER_START:
            for hy in range(INNER_START - 1, -1, -1):
                if self.grid[hy][x] != None:
                    return (x, hy), "down"
        elif x >= INNER_START and x < INNER_END and y >= INNER_END:
            for hy in range(INNER_END, GRID_SIZE):
                if self.grid[hy][x] != None:
                    return (x, hy), "up"
        elif x < INNER_START and y >= INNER_START and y < INNER_END:
            for hx in range(INNER_START - 1, -1, -1):
                if self.grid[y][hx] != None:
                    return (hx, y), "right"
        elif x >= INNER_END and y >= INNER_START and y < INNER_END:
            for hx in range(INNER_END, GRID_SIZE):
                if self.grid[y][hx] != None:
                    return (hx, y), "left"
        return None, None

    def is_line_firable(self, x, y, direction):
        if direction == "down":
            if self.grid[INNER_START][x] != None:
                return False
        elif direction == "up":
            if self.grid[INNER_END - 1][x] != None:
                return False
        elif direction == "right":
            if self.grid[y][INNER_START] != None:
                return False
        elif direction == "left":
            if self.grid[y][INNER_END - 1] != None:
                return False
                
        if x >= INNER_START and x < INNER_END:
            for hy in range(INNER_START, INNER_END):
                if self.grid[hy][x] != None:
                    return True
        if y >= INNER_START and y < INNER_END:
            for hx in range(INNER_START, INNER_END):
                if self.grid[y][hx] != None:
                    return True
        return False

    def handle_click(self, mouse_pos):
        if len(self.animations) > 0:
            return
        rel_x = mouse_pos[0] - BOARD_OFFSET_X
        rel_y = mouse_pos[1] - BOARD_OFFSET_Y
        if rel_x >= 0 and rel_x < GRID_SIZE * CELL_SIZE and rel_y >= 0 and rel_y < GRID_SIZE * CELL_SIZE:
            grid_x = rel_x // CELL_SIZE
            grid_y = rel_y // CELL_SIZE
            head, direction = self.get_firing_head(grid_x, grid_y)
            if head != None:
                if self.is_line_firable(grid_x, grid_y, direction):
                    self.game_manager.audio_manager.play_sfx("move")
                    self.fire_block(head[0], head[1], direction)
                    self.pending_logic = True
                    self.needs_save = True

    def fire_block(self, x, y, direction):
        block = self.grid[y][x]
        block['dir'] = direction
        self.grid[y][x] = None
        hit_pos = None
        if direction == "down":
            for hy in range(INNER_START, INNER_END):
                if self.grid[hy][x] != None:
                    hit_pos = (x, hy)
                    break
        elif direction == "up":
            for hy in range(INNER_END - 1, INNER_START - 1, -1):
                if self.grid[hy][x] != None:
                    hit_pos = (x, hy)
                    break
        elif direction == "right":
            for hx in range(INNER_START, INNER_END):
                if self.grid[y][hx] != None:
                    hit_pos = (hx, y)
                    break
        elif direction == "left":
            for hx in range(INNER_END - 1, INNER_START - 1, -1):
                if self.grid[y][hx] != None:
                    hit_pos = (hx, y)
                    break
                    
        if hit_pos != None:
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
            if tx != x or ty != y:
                self._add_move_anim(block, (x, y), (tx, ty), None)
            else:
                self.grid[y][x] = block
        else:
            target_pos = self._get_exit_pos(x, y, direction)
            self._add_move_anim(block, (x, y), target_pos, "enter_column")
            
        self.refill_column_or_row(x, y, direction)

    def apply_inertia(self):
        to_move = []
        for y in range(INNER_START, INNER_END):
            for x in range(INNER_START, INNER_END):
                cell = self.grid[y][x]
                if cell != None:
                    if cell['dir'] != None:
                        dx, dy = 0, 0
                        if cell['dir'] == "down": dy = 1
                        elif cell['dir'] == "up": dy = -1
                        elif cell['dir'] == "right": dx = 1
                        elif cell['dir'] == "left": dx = -1
                        nx, ny = x + dx, y + dy
                        if nx >= INNER_START and nx < INNER_END and ny >= INNER_START and ny < INNER_END:
                            if self.grid[ny][nx] == None:
                                to_move.append((x, y, nx, ny, cell['dir']))
                        else:
                            to_move.append((x, y, None, None, cell['dir']))
        if len(to_move) > 0:
            occupied_targets = []
            for i in range(len(to_move)):
                x, y, tx, ty, direction = to_move[i]
                if tx != None:
                    already_occupied = False
                    for target in occupied_targets:
                        if target[0] == tx and target[1] == ty:
                            already_occupied = True
                            break
                    if already_occupied:
                        continue
                    occupied_targets.append((tx, ty))
                
                block = self.grid[y][x]
                self.grid[y][x] = None
                if tx != None:
                    self._add_move_anim(block, (x, y), (tx, ty), None)
                else:
                    target_pos = self._get_exit_pos(x, y, direction)
                    self._add_move_anim(block, (x, y), target_pos, "enter_column")
            return True
        return False

    def _get_exit_pos(self, x, y, direction):
        if direction == "down": return (x, INNER_END - 1)
        if direction == "up": return (x, INNER_START)
        if direction == "right": return (INNER_END - 1, y)
        if direction == "left": return (INNER_START, y)
        return (x, y)

    def _add_move_anim(self, block, start_grid, end_grid, special_action):
        anim = {
            'type': 'move',
            'block': block,
            'start_x': start_grid[0] * CELL_SIZE,
            'start_y': start_grid[1] * CELL_SIZE,
            'end_x': end_grid[0] * CELL_SIZE,
            'end_y': end_grid[1] * CELL_SIZE,
            'pos_x': start_grid[0] * CELL_SIZE,
            'pos_y': start_grid[1] * CELL_SIZE,
            'end_grid_x': end_grid[0],
            'end_grid_y': end_grid[1],
            'elapsed': 0,
            'duration': 150,
            'history': [],
            'special_action': special_action,
            'completed': False
        }
        self.animations.append(anim)

    def enter_column(self, x, y, direction, block):
        if direction == "down":
            block['dir'] = "up"
            for hy in range(GRID_SIZE - 1, INNER_END, -1):
                self.grid[hy][x] = self.grid[hy-1][x]
            self.grid[INNER_END][x] = block
        elif direction == "up":
            block['dir'] = "down"
            for hy in range(0, INNER_START - 1):
                self.grid[hy][x] = self.grid[hy+1][x]
            self.grid[INNER_START-1][x] = block
        elif direction == "right":
            block['dir'] = "left"
            for hx in range(GRID_SIZE - 1, INNER_END, -1):
                self.grid[y][hx] = self.grid[y][hx-1]
            self.grid[y][INNER_END] = block
        elif direction == "left":
            block['dir'] = "right"
            for hx in range(0, INNER_START - 1):
                self.grid[y][hx] = self.grid[y][hx+1]
            self.grid[y][INNER_START-1] = block

    def update_logic_step(self):
        matches = self.find_matches()
        if len(matches) > 0:
            self.game_manager.audio_manager.play_sfx("clear")
            num_blocks = len(matches)
            score = 30 * (2 ** (num_blocks - 3))
            self.game_manager.add_score(score)
            
            sum_x = 0
            sum_y = 0
            for m in matches:
                sum_x = sum_x + m[0]
                sum_y = sum_y + m[1]
            avg_x = sum_x / num_blocks
            avg_y = sum_y / num_blocks
            
            for m in matches:
                mx = m[0]
                my = m[1]
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
            'pos_x': grid_pos[0] * CELL_SIZE,
            'pos_y': grid_pos[1] * CELL_SIZE,
            'elapsed': 0,
            'duration': 400
        }
        self.animations.append(anim)

    def _add_score_text_anim(self, score, grid_pos):
        anim = {
            'type': 'score_text',
            'text': "+" + str(score),
            'start_x': grid_pos[0] * CELL_SIZE,
            'start_y': grid_pos[1] * CELL_SIZE,
            'pos_x': grid_pos[0] * CELL_SIZE,
            'pos_y': grid_pos[1] * CELL_SIZE,
            'elapsed': 0,
            'duration': 1000
        }
        self.animations.append(anim)

    def update(self, dt):
        if len(self.animations) == 0:
            if self.pending_logic:
                if self.update_logic_step() == False:
                    self.pending_logic = False
                    if self.needs_save:
                        self.game_manager.auto_save()
                        self.needs_save = False
            return
            
        all_finished = True
        for i in range(len(self.animations)):
            anim = self.animations[i]
            anim['elapsed'] = anim['elapsed'] + dt
            if anim['elapsed'] >= anim['duration']:
                progress = 1.0
                if anim['type'] == 'move' and anim['completed'] == False:
                    tx = anim['end_grid_x']
                    ty = anim['end_grid_y']
                    if anim['special_action'] == "enter_column":
                        self.enter_column(tx, ty, anim['block']['dir'], anim['block'])
                    elif self.grid[ty][tx] == None:
                        self.grid[ty][tx] = anim['block']
                    anim['completed'] = True
            else:
                progress = anim['elapsed'] / anim['duration']
                all_finished = False
            
            if anim['type'] == 'move':
                anim['pos_x'] = anim['start_x'] + (anim['end_x'] - anim['start_x']) * progress
                anim['pos_y'] = anim['start_y'] + (anim['end_y'] - anim['start_y']) * progress
                anim['history'].append((anim['pos_x'], anim['pos_y']))
                if len(anim['history']) > 8:
                    anim['history'].pop(0)
            elif anim['type'] == 'score_text':
                anim['pos_y'] = anim['start_y'] - (progress * 40)
                
        if all_finished:
            self.animations = []

    def find_matches(self):
        to_remove = []
        visited = []
        for y in range(INNER_START, INNER_END):
            for x in range(INNER_START, INNER_END):
                if self.grid[y][x] != None:
                    is_visited = False
                    for v in visited:
                        if v[0] == x and v[1] == y:
                            is_visited = True
                            break
                    if is_visited == False:
                        color = self.grid[y][x]['color']
                        component = self._get_connected_component(x, y, color)
                        for c in component:
                            visited.append(c)
                        if len(component) >= 3:
                            for c in component:
                                already_in = False
                                for r in to_remove:
                                    if r[0] == c[0] and r[1] == c[1]:
                                        already_in = True
                                        break
                                if already_in == False:
                                    to_remove.append(c)
        return to_remove

    def _get_connected_component(self, start_x, start_y, color):
        component = []
        stack = [(start_x, start_y)]
        visited = [(start_x, start_y)]
        while len(stack) > 0:
            pos = stack.pop()
            x = pos[0]
            y = pos[1]
            component.append((x, y))
            for diff in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx = x + diff[0]
                ny = y + diff[1]
                if nx >= INNER_START and nx < INNER_END and ny >= INNER_START and ny < INNER_END:
                    if self.grid[ny][nx] != None:
                        if self.grid[ny][nx]['color'] == color:
                            already_visited = False
                            for v in visited:
                                if v[0] == nx and v[1] == ny:
                                    already_visited = True
                                    break
                            if already_visited == False:
                                visited.append((nx, ny))
                                stack.append((nx, ny))
        return component

    def refill_column_or_row(self, x, y, direction):
        num_colors = 2 + self.level
        if num_colors > len(BLOCK_COLORS):
            num_colors = len(BLOCK_COLORS)
        available_colors = []
        for i in range(num_colors):
            available_colors.append(BLOCK_COLORS[i])
            
        if direction == "down":
            for hy in range(y, 0, -1):
                self.grid[hy][x] = self.grid[hy-1][x]
            self.grid[0][x] = {'color': self.rng.choice(available_colors), 'dir': 'down'}
        elif direction == "up":
            for hy in range(y, GRID_SIZE - 1):
                self.grid[hy][x] = self.grid[hy+1][x]
            self.grid[GRID_SIZE-1][x] = {'color': self.rng.choice(available_colors), 'dir': 'up'}
        elif direction == "right":
            for hx in range(x, 0, -1):
                self.grid[y][hx] = self.grid[y][hx-1]
            self.grid[y][0] = {'color': self.rng.choice(available_colors), 'dir': 'right'}
        elif direction == "left":
            for hx in range(x, GRID_SIZE - 1):
                self.grid[y][hx] = self.grid[y][hx+1]
            self.grid[y][GRID_SIZE-1] = {'color': self.rng.choice(available_colors), 'dir': 'left'}

    def draw(self, surface):
        sw = surface.get_width()
        sh = surface.get_height()
        board_size = GRID_SIZE * CELL_SIZE
        offset_x = (sw - board_size) // 2
        offset_y = (sh - board_size) // 2
        
        mouse_pos = pygame.mouse.get_pos()
        rel_x = mouse_pos[0] - offset_x
        rel_y = mouse_pos[1] - offset_y
        grid_x, grid_y = -1, -1
        if rel_x >= 0 and rel_x < board_size and rel_y >= 0 and rel_y < board_size:
            grid_x = rel_x // CELL_SIZE
            grid_y = rel_y // CELL_SIZE
            
        hovered_head, direction = self.get_firing_head(grid_x, grid_y)
        firable = False
        if hovered_head != None:
            firable = self.is_line_firable(grid_x, grid_y, direction)
            
        center_rect = pygame.Rect(
            offset_x + INNER_START * CELL_SIZE,
            offset_y + INNER_START * CELL_SIZE,
            (INNER_END - INNER_START) * CELL_SIZE,
            (INNER_END - INNER_START) * CELL_SIZE
        )
        draw_rect_compat(surface, (25, 25, 25), center_rect)
        pygame.draw.rect(surface, (50, 50, 50), center_rect, 2)
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = self.grid[y][x]
                if cell != None:
                    self._draw_block_at(surface, cell, offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, 255)
                    
                    is_on_grid = False
                    if x >= INNER_START and x < INNER_END and y >= INNER_START and y < INNER_END:
                        is_on_grid = True
                        
                    if is_on_grid and cell['dir'] != None:
                        block_rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE).inflate(-6, -6)
                        self._draw_arrow(surface, block_rect, cell['dir'], (255, 255, 255), 180)
                        
                    if hovered_head != None:
                        if hovered_head[0] == x and hovered_head[1] == y:
                            block_rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE).inflate(-6, -6)
                            if firable:
                                self._draw_arrow(surface, block_rect, direction, (255, 255, 255), 255)
                            else:
                                self._draw_cross(surface, block_rect)
                                
        for anim in self.animations:
            if anim['type'] == 'move':
                for i in range(len(anim['history'])):
                    h_pos = anim['history'][i]
                    alpha = int(255 * (i / len(anim['history'])) * 0.3)
                    self._draw_block_at(surface, anim['block'], offset_x + h_pos[0], offset_y + h_pos[1], alpha)
                self._draw_block_at(surface, anim['block'], offset_x + anim['pos_x'], offset_y + anim['pos_y'], 255)
            elif anim['type'] == 'fade':
                progress = anim['elapsed'] / anim['duration']
                if progress > 1.0:
                    progress = 1.0
                alpha = int(255 * (1.0 - progress))
                self._draw_block_at(surface, anim['block'], offset_x + anim['pos_x'], offset_y + anim['pos_y'], alpha)
            elif anim['type'] == 'score_text':
                progress = anim['elapsed'] / anim['duration']
                if progress > 1.0:
                    progress = 1.0
                alpha = int(255 * (1.0 - progress))
                text_surf = self.game_manager.font_game.render(anim['text'], True, (255, 255, 255))
                text_surf.set_alpha(alpha)
                surface.blit(text_surf, (offset_x + anim['pos_x'] + CELL_SIZE//2 - text_surf.get_width()//2, 
                                        offset_y + anim['pos_y']))

    def _draw_block_at(self, surface, cell, x, y, alpha):
        color = cell['color']
        if alpha < 255:
            r = int(color[0] * (alpha/255) + 18 * (1 - alpha/255))
            g = int(color[1] * (alpha/255) + 18 * (1 - alpha/255))
            b = int(color[2] * (alpha/255) + 18 * (1 - alpha/255))
            color = (r, g, b)
            
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        block_rect = rect.inflate(-6, -6)
        draw_rect_compat(surface, color, block_rect, 6)
        
        if alpha == 255:
            highlight_rect = pygame.Rect(block_rect.x + 3, block_rect.y + 3, block_rect.width - 6, block_rect.height // 2)
            r = min(color[0] + 40, 255)
            g = min(color[1] + 40, 255)
            b = min(color[2] + 40, 255)
            highlight_color = (r, g, b)
            draw_rect_compat(surface, highlight_color, highlight_rect, 6)
            bottom_rect = pygame.Rect(block_rect.x, block_rect.y + block_rect.height // 2, block_rect.width, block_rect.height // 2)
            draw_rect_compat(surface, color, bottom_rect, 6)

    def _draw_arrow(self, surface, rect, direction, color, alpha):
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
        else:
            return
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
                if self.grid[y][x] != None:
                    return False
        return True

    def get_state_seed(self):
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
        seed_parts = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = self.grid[y][x]
                if cell == None:
                    seed_parts.append(chars[0])
                else:
                    color_idx = 0
                    for i in range(len(BLOCK_COLORS)):
                        if BLOCK_COLORS[i] == cell['color']:
                            color_idx = i
                            break
                    
                    dir_idx = 0
                    if cell['dir'] == "up": dir_idx = 1
                    elif cell['dir'] == "down": dir_idx = 2
                    elif cell['dir'] == "left": dir_idx = 3
                    elif cell['dir'] == "right": dir_idx = 4
                    
                    val = (color_idx + 1) + (dir_idx * 10)
                    seed_parts.append(chars[val])
        return "".join(seed_parts)

    def load_from_state_seed(self, state_seed):
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
        if len(state_seed) != GRID_SIZE * GRID_SIZE:
            return False
        
        new_grid = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                row.append(None)
            new_grid.append(row)
            
        for i in range(len(state_seed)):
            char = state_seed[i]
            y = i // GRID_SIZE
            x = i % GRID_SIZE
            val = chars.find(char)
            if val <= 0:
                new_grid[y][x] = None
            else:
                dir_idx = val // 10
                color_idx = (val % 10) - 1
                
                direction = None
                if dir_idx == 1: direction = "up"
                elif dir_idx == 2: direction = "down"
                elif dir_idx == 3: direction = "left"
                elif dir_idx == 4: direction = "right"
                
                if color_idx >= 0 and color_idx < len(BLOCK_COLORS):
                    new_grid[y][x] = {
                        'color': BLOCK_COLORS[color_idx],
                        'dir': direction
                    }
        self.grid = new_grid
        return True
