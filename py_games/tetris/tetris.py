import pygame
import random
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env

# Initialize Pygame
pygame.init()

# Constants
COLS = 10
ROWS = 20
CELL_SIZE = 30
WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE
FPS = 60

# Colors
BACKGROUND_COLOR = (26, 26, 46)
GRID_COLOR = (22, 33, 62)
TEXT_COLOR = (255, 255, 255)

PIECE_COLORS = [
    (0, 217, 255),   # I - Cyan
    (0, 255, 136),   # O - Green
    (255, 0, 110),   # T - Pink
    (255, 208, 0),   # S - Yellow
    (255, 102, 0),   # Z - Orange
    (157, 0, 255),   # L - Purple
    (0, 255, 255)    # J - Cyan
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]]   # J
]



# Base class for polymorphism

class GameObject:
    def update(self, *args, **kwargs):
        """Optional update hook for objects."""
        pass

    def draw(self, screen, *args, **kwargs):
        """Draw this object on screen. Subclasses must override."""
        raise NotImplementedError("Subclasses must implement draw()")



# Piece class (inherits GameObject)

class Piece(GameObject):
    def __init__(self, shape, color):
        self.shape = [row[:] for row in shape]
        self.color = color
        # starting position (x,y) in grid coordinates
        self.x = 3
        self.y = 0

    def rotate(self):
        rows = len(self.shape)
        cols = len(self.shape[0])
        new_shape = []
        for col in range(cols):
            new_row = []
            for row in range(rows - 1, -1, -1):
                new_row.append(self.shape[row][col])
            new_shape.append(new_row)
        self.shape = new_shape

    def clone(self):
        cloned = Piece([row[:] for row in self.shape], self.color)
        cloned.x = self.x
        cloned.y = self.y
        return cloned

    def update(self, *args, **kwargs):
        """Piece has no autonomous update in this design; TetrisGame controls drops."""
        pass

    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw piece in pixels with optional pixel offsets (used for preview)."""
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]:
                    px = (self.x + col) * CELL_SIZE + offset_x
                    py = (self.y + row) * CELL_SIZE + offset_y
                    pygame.draw.rect(screen, self.color,
                                     (px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2))


# Board class (inherits GameObject)

class Board(GameObject):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

    def is_valid_move(self, piece):
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col]:
                    new_x = piece.x + col
                    new_y = piece.y + row

                    if new_x < 0 or new_x >= self.cols or new_y >= self.rows:
                        return False

                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def merge_piece(self, piece):
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col]:
                    y = piece.y + row
                    x = piece.x + col
                    if y >= 0:
                        self.grid[y][x] = piece.color

    def clear_lines(self):
        lines_cleared = 0
        row = self.rows - 1

        while row >= 0:
            if all(cell != 0 for cell in self.grid[row]):
                self.grid.pop(row)
                self.grid.insert(0, [0 for _ in range(self.cols)])
                lines_cleared += 1
            else:
                row -= 1

        return lines_cleared

    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def update(self, *args, **kwargs):
        """Board doesn't need per-frame updates by default."""
        pass

    def draw(self, screen, offset_x=0, offset_y=0):
        # draw stored blocks
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col]:
                    color = self.grid[row][col]
                    px = col * CELL_SIZE + offset_x
                    py = row * CELL_SIZE + offset_y
                    pygame.draw.rect(screen, color,
                                     (px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2))



# TetrisGame orchestrator

class TetrisGame:
    def __init__(self):
        # window includes side UI panel (200px)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH + 200, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        # Game state
        self.game_running = False
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines = 0

        # Game objects
        self.board = Board(ROWS, COLS)
        self.current_piece = None
        self.next_piece = None

        # Timing
        self.drop_interval = 1000  # milliseconds
        self.last_drop_time = 0

        # Fonts
        self.ui_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.instruction_font = pygame.font.Font(None, 24)

    def create_random_piece(self):
        shape_index = random.randint(0, len(SHAPES) - 1)
        shape = [row[:] for row in SHAPES[shape_index]]
        color = PIECE_COLORS[shape_index]
        return Piece(shape, color)

    def start(self):
        self.game_running = True
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines = 0
        self.drop_interval = 1000
        self.board.reset()
        self.current_piece = self.create_random_piece()
        self.next_piece = self.create_random_piece()
        self.last_drop_time = pygame.time.get_ticks()

    def move_piece(self, dx, dy):
        new_piece = self.current_piece.clone()
        new_piece.x += dx
        new_piece.y += dy

        if self.board.is_valid_move(new_piece):
            self.current_piece = new_piece
            return True
        return False

    def rotate_piece(self):
        new_piece = self.current_piece.clone()
        new_piece.rotate()

        if self.board.is_valid_move(new_piece):
            self.current_piece = new_piece

    def drop_piece(self):
        if not self.move_piece(0, 1):
            self.board.merge_piece(self.current_piece)
            lines_cleared = self.board.clear_lines()

            if lines_cleared > 0:
                self.lines += lines_cleared
                self.score += lines_cleared * 100 * self.level
                self.level = self.lines // 10 + 1
                self.drop_interval = max(100, 1000 - (self.level - 1) * 50)

            self.current_piece = self.next_piece
            self.next_piece = self.create_random_piece()

            if not self.board.is_valid_move(self.current_piece):
                self.game_over = True
                self.game_running = False
                # Send score to API
                user_id, game_id = get_user_and_game_from_env()
                if user_id and game_id:
                    send_score_to_api(user_id, game_id, self.score)

    def update(self):
        if not self.game_running or self.game_over:
            return

        # time-based drop
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time > self.drop_interval:
            self.drop_piece()
            self.last_drop_time = current_time

        # Call polymorphic updates (no-op for board and pieces by default,
        # but keeps the loop generic and extensible)
        for obj in (self.board, self.current_piece, self.next_piece):
            if obj:
                obj.update()

    # Drawing helpers (use polymorphic draw for board and pieces)
    def draw_grid(self):
        # Draw grid lines
        for row in range(ROWS + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (0, row * CELL_SIZE), (WINDOW_WIDTH, row * CELL_SIZE))
        for col in range(COLS + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (col * CELL_SIZE, 0), (col * CELL_SIZE, WINDOW_HEIGHT))

    # UI and rendering
    def draw_ui(self):
        # Draw UI background
        pygame.draw.rect(self.screen, BACKGROUND_COLOR,
                         (WINDOW_WIDTH, 0, 200, WINDOW_HEIGHT))

        # Score
        score_text = self.ui_font.render('Score:', True, TEXT_COLOR)
        self.screen.blit(score_text, (WINDOW_WIDTH + 20, 20))
        score_value = self.ui_font.render(str(self.score), True, TEXT_COLOR)
        self.screen.blit(score_value, (WINDOW_WIDTH + 20, 50))

        # Level
        level_text = self.ui_font.render('Level:', True, TEXT_COLOR)
        self.screen.blit(level_text, (WINDOW_WIDTH + 20, 100))
        level_value = self.ui_font.render(str(self.level), True, TEXT_COLOR)
        self.screen.blit(level_value, (WINDOW_WIDTH + 20, 130))

        # Lines
        lines_text = self.ui_font.render('Lines:', True, TEXT_COLOR)
        self.screen.blit(lines_text, (WINDOW_WIDTH + 20, 180))
        lines_value = self.ui_font.render(str(self.lines), True, TEXT_COLOR)
        self.screen.blit(lines_value, (WINDOW_WIDTH + 20, 210))

        # Next piece
        next_text = self.ui_font.render('Next:', True, TEXT_COLOR)
        self.screen.blit(next_text, (WINDOW_WIDTH + 20, 280))

        if self.next_piece:
            preview = self.next_piece.clone()
            preview.x = 0
            preview.y = 0
            # draw piece in preview area using pixel offsets
            preview.draw(self.screen, WINDOW_WIDTH + 40, 320)

        # Controls
        controls_y = WINDOW_HEIGHT - 150
        controls = [
            'Controls:',
            'Arrows - Move',
            'Up/W - Rotate',
            'Down - Drop'
        ]
        for i, text in enumerate(controls):
            control_text = self.instruction_font.render(text, True, TEXT_COLOR)
            self.screen.blit(control_text, (WINDOW_WIDTH + 20, controls_y + i * 30))

    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Title
        title = self.title_font.render('TETRIS', True, TEXT_COLOR)
        title_rect = title.get_rect(center=((WINDOW_WIDTH + 200) // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)

        # Instructions
        instructions = [
            'Press SPACE to Start',
            '',
            'Arrow Keys to Move',
            'Up / W / Space to Rotate',
            'Down to Drop Faster'
        ]

        y_offset = WINDOW_HEIGHT // 2
        for instruction in instructions:
            if instruction:
                text = self.instruction_font.render(instruction, True, TEXT_COLOR)
                text_rect = text.get_rect(center=((WINDOW_WIDTH + 200) // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 35

    def draw_game(self):
        # Draw game area background
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        # Grid lines
        self.draw_grid()

        # Polymorphic draw: board (blocks) then active piece
        self.board.draw(self.screen)

        if self.current_piece:
            self.current_piece.draw(self.screen)

        # UI
        self.draw_ui()

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.title_font.render('GAME OVER', True, TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.instruction_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        restart_text = self.instruction_font.render('Press SPACE to Restart', True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if not self.game_running:
                            self.start()
                        elif not self.game_over:
                            self.rotate_piece()
                    elif self.game_running and not self.game_over:
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            self.move_piece(-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.move_piece(1, 0)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.move_piece(0, 1)
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            self.rotate_piece()

            # game logic
            self.update()

            # rendering
            if not self.game_running:
                self.draw_start_screen()
            else:
                self.draw_game()
                if self.game_over:
                    self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    TetrisGame().run()
