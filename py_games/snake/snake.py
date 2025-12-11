"""
Snake Game - Pygame Version
Classic snake game with food
"""

import pygame
import random
import json
import os
import sys

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

class Snake:
    def __init__(self, x, y):
        self.body = []
        # Build initial body of length 4
        for i in range(4):
            self.body.append((x - i, y))
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow_amount = 0
        self.alive = True
    
    def head(self):
        return self.body[-1]
    
    def set_direction(self, direction):
        # Prevent immediate reversal
        if len(self.body) > 1:
            if direction[0] == -self.direction[0] and direction[1] == -self.direction[1]:
                return
        self.next_direction = direction
    
    def move(self):
        if not self.alive:
            return
        
        self.direction = self.next_direction
        hx, hy = self.head()
        nx = hx + self.direction[0]
        ny = hy + self.direction[1]
        
        # Check wall collision
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
    
    def draw(self, screen):
        for i, (x, y) in enumerate(self.body):
            pygame.draw.rect(screen, SNAKE_COLOR, 
                           (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            # Draw head with border
            if i == len(self.body) - 1:
                pygame.draw.rect(screen, TEXT_COLOR,
                               (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

class Food:
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
    
    def draw(self, screen):
        if self.position:
            x, y = self.position
            pygame.draw.rect(screen, FOOD_COLOR,
                           (x * CELL_SIZE + 1, y * CELL_SIZE + 1, 
                            CELL_SIZE - 2, CELL_SIZE - 2))

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_running = False
        self.score = 0
        self.best_score = self.load_best_score()
        
        # Game objects
        self.snake = None
        self.food = None
        
        # Fonts
        self.score_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 64)
        self.instruction_font = pygame.font.Font(None, 28)
    
    def load_best_score(self):
        """Load best score from file"""
        try:
            if os.path.exists('.pygame_snake_best.json'):
                with open('.pygame_snake_best.json', 'r') as f:
                    data = json.load(f)
                    return data.get('best_score', 0)
        except:
            pass
        return 0
    
    def save_best_score(self):
        """Save best score to file"""
        try:
            with open('.pygame_snake_best.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass
    
    def start(self):
        self.game_running = True
        self.score = 0
        start_x = COLS // 4
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
        
        # Move snake
        self.snake.move()
        
        # Check self collision
        if self.snake.check_self_collision():
            self.snake.alive = False
            self.game_over()
            return
        
        # Check food collision
        if self.snake.alive and self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 10
            self.food.spawn(self.snake)
    
    def game_over(self):
        self.game_running = False
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()
    
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Title
        title = self.title_font.render('SNAKE', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            'Use Arrow Keys or WASD to move',
            'Eat food to grow longer',
            "Don't hit the walls or yourself!",
            '',
            'Press SPACE to Start'
        ]
        
        y_offset = WINDOW_HEIGHT // 2
        for instruction in instructions:
            if instruction:
                text = self.instruction_font.render(instruction, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 35
        
        # Best score
        best_text = self.instruction_font.render(f'Best: {self.best_score}', True, FOOD_COLOR)
        best_rect = best_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(best_text, best_rect)
    
    def draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw food
        self.food.draw(self.screen)
        
        # Draw snake
        self.snake.draw(self.screen)
        
        # Draw score
        score_text = self.score_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        
        best_text = self.score_font.render(f'Best: {self.best_score}', True, TEXT_COLOR)
        best_rect = best_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        self.screen.blit(best_text, best_rect)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.title_font.render('GAME OVER', True, TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = self.instruction_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        
        # Best
        if self.score == self.best_score and self.score > 0:
            new_best = self.instruction_font.render('NEW BEST!', True, FOOD_COLOR)
            new_best_rect = new_best.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.screen.blit(new_best, new_best_rect)
        else:
            best_text = self.instruction_font.render(f'Best: {self.best_score}', True, TEXT_COLOR)
            best_rect = best_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.screen.blit(best_text, best_rect)
        
        # Restart
        restart_text = self.instruction_font.render('Press SPACE to Restart', True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_running and self.snake and self.snake.alive:
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
                    # Draw game then overlay
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
    game = SnakeGame()
    game.run()
