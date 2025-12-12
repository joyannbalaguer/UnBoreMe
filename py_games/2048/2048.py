"""
2048 Game - Pygame Version (OOP Enhanced)
Classic number puzzle game
Refactor: adds Tile and Board classes, Board owns the grid and move logic.
"""

import pygame
import random
import json
import os
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
FPS = 60

# Grid settings
GRID_SIZE = 4
CELL_SIZE = 120
CELL_PADDING = 10
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 150

# Colors
BACKGROUND_COLOR = (250, 248, 239)
GRID_COLOR = (187, 173, 160)
TEXT_COLOR = (119, 110, 101)

CELL_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (60, 58, 50)
}

TEXT_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
}
DEFAULT_TEXT_COLOR = (249, 246, 242)


# ----------------------------
# Small GameObject interface
# ----------------------------
class GameObject:
    def update(self, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        raise NotImplementedError


# ----------------------------
# Tile: represents a single numeric tile (value only)
# ----------------------------
class Tile(GameObject):
    def __init__(self, value=0):
        self.value = value

    def is_empty(self):
        return self.value == 0

    def set(self, value):
        self.value = value

    def clear(self):
        self.value = 0

    def draw(self, surface, x, y):
        color = CELL_COLORS.get(self.value, CELL_COLORS[8192])
        pygame.draw.rect(surface, color, (x, y, CELL_SIZE, CELL_SIZE))
        if self.value != 0:
            text_color = TEXT_COLORS.get(self.value, DEFAULT_TEXT_COLOR)
            # Choose font size based on value
            if self.value < 100:
                font = pygame.font.Font(None, 64)
            elif self.value < 1000:
                font = pygame.font.Font(None, 56)
            elif self.value < 10000:
                font = pygame.font.Font(None, 48)
            else:
                font = pygame.font.Font(None, 40)
            text = font.render(str(self.value), True, text_color)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            surface.blit(text, text_rect)


# ----------------------------
# Board: contains grid and movement logic
# ----------------------------
class Board(GameObject):
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.grid = [[Tile(0) for _ in range(size)] for _ in range(size)]

    def reset(self):
        self.grid = [[Tile(0) for _ in range(self.size)] for _ in range(self.size)]

    def get_values(self):
        return [[self.grid[i][j].value for j in range(self.size)] for i in range(self.size)]

    def set_values(self, values):
        for i in range(self.size):
            for j in range(self.size):
                self.grid[i][j].value = values[i][j]

    def empty_cells(self):
        coords = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j].is_empty():
                    coords.append((i, j))
        return coords

    def add_random_tile(self):
        empties = self.empty_cells()
        if not empties:
            return False
        r, c = random.choice(empties)
        self.grid[r][c].set(2 if random.random() < 0.9 else 4)
        return True

    def is_game_over(self):
        # If any empty cell exists -> not over
        if self.empty_cells():
            return False
        # Check possible merges horizontally or vertically
        for i in range(self.size):
            for j in range(self.size):
                val = self.grid[i][j].value
                if (i < self.size - 1 and self.grid[i + 1][j].value == val) or \
                   (j < self.size - 1 and self.grid[i][j + 1].value == val):
                    return False
        return True

    def _compress_and_merge_line_left(self, line_vals):
        """
        Accepts a list of ints representing one row.
        Returns (new_line, score_gained, moved_bool)
        """
        # Remove zeros
        new_line = [v for v in line_vals if v != 0]
        score_gain = 0
        j = 0
        while j < len(new_line) - 1:
            if new_line[j] == new_line[j + 1]:
                new_line[j] *= 2
                score_gain += new_line[j]
                new_line.pop(j + 1)
                j += 1
            else:
                j += 1
        # Pad with zeros
        new_line.extend([0] * (self.size - len(new_line)))
        moved = new_line != line_vals
        return new_line, score_gain, moved

    def move(self, direction):
        """
        direction in 'left', 'right', 'up', 'down'
        returns (moved_bool, score_gained)
        """
        moved_any = False
        total_score = 0

        if direction == 'left':
            for i in range(self.size):
                row = [self.grid[i][j].value for j in range(self.size)]
                new_row, gained, moved = self._compress_and_merge_line_left(row)
                if moved:
                    moved_any = True
                total_score += gained
                for j in range(self.size):
                    self.grid[i][j].value = new_row[j]

        elif direction == 'right':
            for i in range(self.size):
                row = [self.grid[i][j].value for j in range(self.size)]
                reversed_row = list(reversed(row))
                new_rev, gained, moved = self._compress_and_merge_line_left(reversed_row)
                new_row = list(reversed(new_rev))
                if new_row != row:
                    moved_any = True
                total_score += gained
                for j in range(self.size):
                    self.grid[i][j].value = new_row[j]

        elif direction == 'up':
            for j in range(self.size):
                col = [self.grid[i][j].value for i in range(self.size)]
                new_col, gained, moved = self._compress_and_merge_line_left(col)
                if moved:
                    moved_any = True
                total_score += gained
                for i in range(self.size):
                    self.grid[i][j].value = new_col[i]

        elif direction == 'down':
            for j in range(self.size):
                col = [self.grid[i][j].value for i in range(self.size)]
                reversed_col = list(reversed(col))
                new_rev, gained, moved = self._compress_and_merge_line_left(reversed_col)
                new_col = list(reversed(new_rev))
                if new_col != col:
                    moved_any = True
                total_score += gained
                for i in range(self.size):
                    self.grid[i][j].value = new_col[i]

        return moved_any, total_score

    def draw(self, surface, offset_x=GRID_OFFSET_X, offset_y=GRID_OFFSET_Y):
        # Draw board background
        grid_width = self.size * CELL_SIZE + (self.size + 1) * CELL_PADDING
        grid_height = self.size * CELL_SIZE + (self.size + 1) * CELL_PADDING
        pygame.draw.rect(surface, GRID_COLOR, (offset_x - 10, offset_y - 10, grid_width, grid_height))
        # Draw tiles
        for i in range(self.size):
            for j in range(self.size):
                x = offset_x + j * (CELL_SIZE + CELL_PADDING)
                y = offset_y + i * (CELL_SIZE + CELL_PADDING)
                self.grid[i][j].draw(surface, x, y)


# ----------------------------
# Game orchestrator
# ----------------------------
class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()

        # Game state
        self.game_running = False
        self.score = 0
        self.best_score = self.load_best_score()

        # Board
        self.board = Board(GRID_SIZE)

        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.score_label_font = pygame.font.Font(None, 20)
        self.score_font = pygame.font.Font(None, 36)
        self.instruction_font = pygame.font.Font(None, 22)
        self.start_font = pygame.font.Font(None, 36)
        self.gameover_font = pygame.font.Font(None, 80)

    def load_best_score(self):
        """Load best score from file"""
        try:
            if os.path.exists('.pygame_2048_best.json'):
                with open('.pygame_2048_best.json', 'r') as f:
                    data = json.load(f)
                    return data.get('best_score', 0)
        except:
            pass
        return 0

    def save_best_score(self):
        """Save best score to file"""
        try:
            with open('.pygame_2048_best.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass

    def draw_start_screen(self):
        """Draw the start screen"""
        self.screen.fill(BACKGROUND_COLOR)

        # Title
        title = self.title_font.render('2048', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)

        # Instructions
        texts = [
            ('Join the numbers and get to the 2048 tile!', self.instruction_font, 0),
            ('', self.instruction_font, 30),
            ('Use Arrow Keys or WASD to move', self.instruction_font, 50),
            ('When two tiles with the same number touch,', self.instruction_font, 80),
            ('they merge into one!', self.instruction_font, 105),
        ]

        for text, font, offset in texts:
            if text:
                rendered = font.render(text, True, TEXT_COLOR)
                rect = rendered.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + offset))
                self.screen.blit(rendered, rect)

        # Start prompt
        start_text = self.start_font.render('Press SPACE to Start', True, TEXT_COLOR)
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 160))
        self.screen.blit(start_text, start_rect)

    def draw_game(self):
        """Draw the game screen"""
        self.screen.fill(BACKGROUND_COLOR)

        # Title and score boxes
        title = self.title_font.render('2048', True, TEXT_COLOR)
        self.screen.blit(title, (50, 20))

        score_box_width = 120
        score_box_height = 60
        score_box_y = 30

        # Current score
        pygame.draw.rect(self.screen, GRID_COLOR,
                         (WINDOW_WIDTH - 260, score_box_y, score_box_width, score_box_height))
        score_label = self.score_label_font.render('SCORE', True, (238, 228, 218))
        score_label_rect = score_label.get_rect(center=(WINDOW_WIDTH - 200, score_box_y + 20))
        self.screen.blit(score_label, score_label_rect)
        score_value = self.score_font.render(str(self.score), True, (255, 255, 255))
        score_value_rect = score_value.get_rect(center=(WINDOW_WIDTH - 200, score_box_y + 45))
        self.screen.blit(score_value, score_value_rect)

        # Best score
        pygame.draw.rect(self.screen, GRID_COLOR,
                         (WINDOW_WIDTH - 130, score_box_y, score_box_width, score_box_height))
        best_label = self.score_label_font.render('BEST', True, (238, 228, 218))
        best_label_rect = best_label.get_rect(center=(WINDOW_WIDTH - 70, score_box_y + 20))
        self.screen.blit(best_label, best_label_rect)
        best_value = self.score_font.render(str(self.best_score), True, (255, 255, 255))
        best_value_rect = best_value.get_rect(center=(WINDOW_WIDTH - 70, score_box_y + 45))
        self.screen.blit(best_value, best_value_rect)

        # Draw board (Board draws tiles)
        self.board.draw(self.screen)

        # Instructions
        instruction = self.instruction_font.render('Use arrow keys or WASD to move tiles',
                                                   True, TEXT_COLOR)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        self.screen.blit(instruction, instruction_rect)

    def draw_game_over(self):
        """Draw game over overlay"""
        grid_width = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING
        grid_height = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING
        overlay = pygame.Surface((grid_width, grid_height))
        overlay.set_alpha(186)  # 73% opacity
        overlay.fill((238, 228, 218))
        self.screen.blit(overlay, (GRID_OFFSET_X - 10, GRID_OFFSET_Y - 10))

        # Game over text
        game_over_text = self.gameover_font.render('Game Over!', True, TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(game_over_text, game_over_rect)

        # Try again text
        try_again_text = self.instruction_font.render('Press SPACE to try again', True, TEXT_COLOR)
        try_again_rect = try_again_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(try_again_text, try_again_rect)

    def start(self):
        """Start a new game"""
        self.game_running = True
        self.score = 0
        self.board.reset()
        self.board.add_random_tile()
        self.board.add_random_tile()
        # update best score if necessary
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()

    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.game_running:
            if event.key == pygame.K_SPACE:
                self.start()
            return

        moved = False
        gained = 0

        if event.key in (pygame.K_UP, pygame.K_w):
            moved, gained = self.board.move('up')
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            moved, gained = self.board.move('down')
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            moved, gained = self.board.move('left')
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            moved, gained = self.board.move('right')

        if moved:
            self.score += gained
            if self.score > self.best_score:
                self.best_score = self.score
                self.save_best_score()
            self.board.add_random_tile()
            if self.board.is_game_over():
                self.game_running = False

    def run(self):
        """Main game loop"""
        running = True
        game_over_drawn = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_input(event)
                        game_over_drawn = False

            if not self.game_running:
                self.draw_start_screen()
            else:
                self.draw_game()
                if self.board.is_game_over() and not game_over_drawn:
                    pygame.time.wait(500)
                    self.draw_game_over()
                    game_over_drawn = True
                elif self.board.is_game_over():
                    self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game2048().run()
