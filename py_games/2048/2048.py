"""
2048 Game - Pygame Version
Classic number puzzle game
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

class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_running = False
        self.score = 0
        self.best_score = self.load_best_score()
        
        # Grid
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.score_label_font = pygame.font.Font(None, 20)
        self.score_font = pygame.font.Font(None, 36)
        self.cell_font_large = pygame.font.Font(None, 64)
        self.cell_font_medium = pygame.font.Font(None, 56)
        self.cell_font_small = pygame.font.Font(None, 48)
        self.cell_font_tiny = pygame.font.Font(None, 40)
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
    
    def init_grid(self):
        """Initialize empty grid"""
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def add_random_tile(self):
        """Add a random tile (2 or 4) to an empty cell"""
        empty_cells = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.grid[row][col] = 2 if random.random() < 0.9 else 4
    
    def move(self, direction):
        """Move tiles in the specified direction"""
        old_grid = [row[:] for row in self.grid]
        
        if direction == 'left':
            for i in range(GRID_SIZE):
                row = [val for val in self.grid[i] if val != 0]
                j = 0
                while j < len(row) - 1:
                    if row[j] == row[j + 1]:
                        row[j] *= 2
                        self.score += row[j]
                        row.pop(j + 1)
                    j += 1
                row.extend([0] * (GRID_SIZE - len(row)))
                self.grid[i] = row
                
        elif direction == 'right':
            for i in range(GRID_SIZE):
                row = [val for val in self.grid[i] if val != 0]
                j = len(row) - 1
                while j > 0:
                    if row[j] == row[j - 1]:
                        row[j] *= 2
                        self.score += row[j]
                        row.pop(j - 1)
                        j -= 1
                    j -= 1
                row = [0] * (GRID_SIZE - len(row)) + row
                self.grid[i] = row
                
        elif direction == 'up':
            for j in range(GRID_SIZE):
                col = [self.grid[i][j] for i in range(GRID_SIZE) if self.grid[i][j] != 0]
                i = 0
                while i < len(col) - 1:
                    if col[i] == col[i + 1]:
                        col[i] *= 2
                        self.score += col[i]
                        col.pop(i + 1)
                    i += 1
                col.extend([0] * (GRID_SIZE - len(col)))
                for i in range(GRID_SIZE):
                    self.grid[i][j] = col[i]
                    
        elif direction == 'down':
            for j in range(GRID_SIZE):
                col = [self.grid[i][j] for i in range(GRID_SIZE) if self.grid[i][j] != 0]
                i = len(col) - 1
                while i > 0:
                    if col[i] == col[i - 1]:
                        col[i] *= 2
                        self.score += col[i]
                        col.pop(i - 1)
                        i -= 1
                    i -= 1
                col = [0] * (GRID_SIZE - len(col)) + col
                for i in range(GRID_SIZE):
                    self.grid[i][j] = col[i]
        
        # Check if move was successful
        moved = old_grid != self.grid
        
        if moved and self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()
        
        return moved
    
    def is_game_over(self):
        """Check if game is over"""
        # Check for empty cells
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == 0:
                    return False
        
        # Check for possible merges
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                current = self.grid[i][j]
                if (i < GRID_SIZE - 1 and self.grid[i + 1][j] == current) or \
                   (j < GRID_SIZE - 1 and self.grid[i][j + 1] == current):
                    return False
        
        return True
    
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
        
        # Title
        title = self.title_font.render('2048', True, TEXT_COLOR)
        self.screen.blit(title, (50, 20))
        
        # Score boxes
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
        
        # Grid background
        grid_width = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING
        grid_height = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING
        pygame.draw.rect(self.screen, GRID_COLOR,
                        (GRID_OFFSET_X - 10, GRID_OFFSET_Y - 10, grid_width, grid_height))
        
        # Draw cells
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                value = self.grid[i][j]
                x = GRID_OFFSET_X + j * (CELL_SIZE + CELL_PADDING)
                y = GRID_OFFSET_Y + i * (CELL_SIZE + CELL_PADDING)
                
                # Cell background
                color = CELL_COLORS.get(value, CELL_COLORS[8192])
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                
                # Cell value
                if value != 0:
                    text_color = TEXT_COLORS.get(value, DEFAULT_TEXT_COLOR)
                    
                    # Choose font size based on value
                    if value < 100:
                        font = self.cell_font_large
                    elif value < 1000:
                        font = self.cell_font_medium
                    elif value < 10000:
                        font = self.cell_font_small
                    else:
                        font = self.cell_font_tiny
                    
                    text = font.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)
        
        # Instructions
        instruction = self.instruction_font.render('Use arrow keys or WASD to move tiles', 
                                                   True, TEXT_COLOR)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_game_over(self):
        """Draw game over overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING,
                                 GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING))
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
        self.init_grid()
        self.add_random_tile()
        self.add_random_tile()
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.game_running:
            if event.key == pygame.K_SPACE:
                self.start()
            return
        
        moved = False
        
        if event.key in (pygame.K_UP, pygame.K_w):
            moved = self.move('up')
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            moved = self.move('down')
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            moved = self.move('left')
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            moved = self.move('right')
        
        if moved:
            self.add_random_tile()
            if self.is_game_over():
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
                if self.is_game_over() and not game_over_drawn:
                    pygame.time.wait(500)
                    self.draw_game_over()
                    game_over_drawn = True
                elif self.is_game_over():
                    self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game2048()
    game.run()
