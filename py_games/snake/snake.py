"""
Snake Game - Pygame Version (OOP Enhanced)
Classic snake game using all 4 OOP pillars:
Encapsulation, Abstraction, Inheritance, Polymorphism
"""

import pygame
import random
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 20
COLS = 36
ROWS = 24
WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE
FPS = 10

# Colors
BACKGROUND_COLOR = (11, 11, 11)
SNAKE_COLOR = (55, 174, 242)
FOOD_COLOR = (255, 77, 77)
TEXT_COLOR = (255, 255, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# ==========================================================
# OOP PILLAR #3: INHERITANCE + ABSTRACTION
# Base class for all drawable game objects
# ==========================================================
class GameObject:
    def draw(self, screen):
        raise NotImplementedError("Subclasses must implement draw()")

    def update(self):
        pass  # optional override for objects that move


# ==========================================================
# Snake Class (inherits GameObject)
# ==========================================================
class Snake(GameObject):
    def __init__(self, x, y):
        self.body = []
        initial_length = 4

        # Build initial snake from left → right, prevents instant self-collision
        for i in range(initial_length):
            self.body.append((x + i, y))

        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow_amount = 0
        self.alive = True
    
    def head(self):
        return self.body[-1]
    
    def set_direction(self, direction):
        # Prevent reversing into itself
        if len(self.body) > 1:
            if direction[0] == -self.direction[0] and direction[1] == -self.direction[1]:
                return
        self.next_direction = direction
    
    # OOP PILLAR #2: ABSTRACTION via update()
    def update(self):
        self.move()

    def move(self):
        if not self.alive:
            return
        
        self.direction = self.next_direction
        hx, hy = self.head()
        nx = hx + self.direction[0]
        ny = hy + self.direction[1]
        
        # Wall collision
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            self.alive = False
            return
        
        self.body.append((nx, ny))
        
        if self.grow_amount > 0:
            self.grow_amount -= 1
        else:
            self.body.pop(0)
    
    def grow(self, amount=1):
        self.grow_amount += amount
    
    def check_self_collision(self):
        head = self.head()
        return self.body.count(head) > 1

    # OOP PILLAR #4: POLYMORPHISM (override draw)
    def draw(self, screen):
        for i, (x, y) in enumerate(self.body):
            pygame.draw.rect(screen, SNAKE_COLOR,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if i == len(self.body) - 1:
                pygame.draw.rect(screen, TEXT_COLOR,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


# ==========================================================
# Food Class (inherits GameObject)
# ==========================================================
class Food(GameObject):
    def __init__(self):
        self.position = None
        self.spawn()

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if snake is None or (x, y) not in snake.body:
                self.position = (x, y)
                break

    # polymorphic draw()
    def draw(self, screen):
        if self.position:
            x, y = self.position
            pygame.draw.rect(screen, FOOD_COLOR,
                             (x * CELL_SIZE + 1, y * CELL_SIZE + 1,
                              CELL_SIZE - 2, CELL_SIZE - 2))


# ==========================================================
# Main Game Class (Encapsulation of entire game)
# ==========================================================
class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_running = False
        self.score = 0
        self.best_score = self.load_best_score()
        
        # Objects
        self.snake = None
        self.food = None
        
        # Fonts
        self.score_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 64)
        self.instruction_font = pygame.font.Font(None, 28)
    
    # Score persistence
    def load_best_score(self):
        try:
            if os.path.exists('.pygame_snake_best.json'):
                with open('.pygame_snake_best.json', 'r') as f:
                    return json.load(f).get('best_score', 0)
        except:
            pass
        return 0
    
    def save_best_score(self):
        try:
            with open('.pygame_snake_best.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass
    
    def start(self):
        self.game_running = True
        self.score = 0
        start_x = COLS // 2
        start_y = ROWS // 2
        self.snake = Snake(start_x, start_y)
        self.food = Food()
        self.food.spawn(self.snake)
    
    def update(self):
        if not self.game_running:
            return
        
        if not self.snake.alive:
            self.game_over()
            return
        
        self.snake.update()
        
        if self.snake.check_self_collision():
            self.snake.alive = False
            self.game_over()
            return
        
        # Food collision
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 10
            self.food.spawn(self.snake)
    
    def game_over(self):
        self.game_running = False
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()
        
        # Send score to API
        user_id, game_id = get_user_and_game_from_env()
        if user_id and game_id:
            send_score_to_api(user_id, game_id, self.score)
    
    # --- Drawing ---
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        title = self.title_font.render('SNAKE', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)
        
        instructions = [
            'Use Arrow Keys or WASD to move',
            'Eat food to grow longer',
            "Don\'t hit the walls or yourself!",
            '',
            'Press SPACE to Start'
        ]
        
        y = WINDOW_HEIGHT // 2
        for line in instructions:
            if line:
                text = self.instruction_font.render(line, True, TEXT_COLOR)
                rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
                self.screen.blit(text, rect)
            y += 35
        
        best = self.instruction_font.render(f'Best: {self.best_score}', True, FOOD_COLOR)
        best_rect = best.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(best, best_rect)
    
    def draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        
        score = self.score_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        self.screen.blit(score, (10, 10))

        best = self.score_font.render(f'Best: {self.best_score}', True, TEXT_COLOR)
        best_rect = best.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        self.screen.blit(best, best_rect)
    
    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        go = self.title_font.render('GAME OVER', True, TEXT_COLOR)
        go_rect = go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(go, go_rect)
        
        score = self.instruction_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        score_rect = score.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score, score_rect)
        
        best = self.instruction_font.render(f'Best: {self.best_score}', True, FOOD_COLOR)
        best_rect = best.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(best, best_rect)
        
        restart = self.instruction_font.render('Press SPACE to Restart', True, TEXT_COLOR)
        restart_rect = restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
        self.screen.blit(restart, restart_rect)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_running and self.snake.alive:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.snake.set_direction(UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.snake.set_direction(DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.snake.set_direction(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.snake.set_direction(RIGHT)
    
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
                    else:
                        self.handle_input(event)
            
            self.update()
            
            if not self.game_running:
                if self.snake and not self.snake.alive:
                    self.draw_game()
                    self.draw_game_over()
                else:
                    self.draw_start_screen()
            else:
                self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    SnakeGame().run()
