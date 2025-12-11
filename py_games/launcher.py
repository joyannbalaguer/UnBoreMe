"""
Pygame Games Launcher
Select and launch any pygame game
"""

import pygame
import sys
import os
import subprocess

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
FPS = 60

# Colors
BACKGROUND_COLOR = (26, 26, 46)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (52, 152, 219)
BUTTON_HOVER_COLOR = (41, 128, 185)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Games list
GAMES = [
    ('2048', '2048/2048.py', 'Number puzzle - merge tiles to reach 2048'),
    ('Breakout', 'breakout/breakout.py', 'Break bricks with ball and paddle'),
    ('Flappy Bird', 'flappybird/flappybird.py', 'Fly through pipes without crashing'),
    ('Memory Match', 'memorymatch/memorymatch.py', 'Match pairs of cards'),
    ('Pong', 'pong/pong.py', 'Classic paddle game vs AI'),
    ('Snake', 'snake/snake.py', 'Eat food and grow longer'),
    ('Space Invaders', 'spaceinvaders/spaceinvaders.py', 'Shoot down alien invaders'),
    ('Tetris', 'tetris/tetris.py', 'Fit falling blocks together'),
]

class Button:
    def __init__(self, x, y, width, height, text, description):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.description = description
        self.hovered = False
    
    def draw(self, screen, font, desc_font):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 2, border_radius=5)
        
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
        screen.blit(text_surface, text_rect)
        
        desc_surface = desc_font.render(self.description, True, BUTTON_TEXT_COLOR)
        desc_rect = desc_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 15))
        screen.blit(desc_surface, desc_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False

class Launcher:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pygame Games Launcher")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.button_font = pygame.font.Font(None, 28)
        self.desc_font = pygame.font.Font(None, 18)
        self.footer_font = pygame.font.Font(None, 20)
        
        # Create buttons
        self.buttons = []
        button_width = 520
        button_height = 70
        start_y = 100
        spacing = 10
        
        for i, (name, path, description) in enumerate(GAMES):
            x = (WINDOW_WIDTH - button_width) // 2
            y = start_y + i * (button_height + spacing)
            button = Button(x, y, button_width, button_height, name, description)
            button.game_path = path
            self.buttons.append(button)
    
    def launch_game(self, game_path):
        """Launch a game in a new process"""
        try:
            # Get the directory where launcher.py is located
            launcher_dir = os.path.dirname(os.path.abspath(__file__))
            game_full_path = os.path.join(launcher_dir, game_path)
            
            if os.path.exists(game_full_path):
                # Launch the game
                subprocess.Popen([sys.executable, game_full_path])
            else:
                print(f"Game not found: {game_full_path}")
        except Exception as e:
            print(f"Error launching game: {e}")
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw title
        title = self.title_font.render('Pygame Games', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.button_font, self.desc_font)
        
        # Draw footer
        footer = self.footer_font.render('Click a game to launch | ESC to exit', True, TEXT_COLOR)
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        self.screen.blit(footer, footer_rect)
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
                # Handle button events
                for button in self.buttons:
                    if button.handle_event(event):
                        self.launch_game(button.game_path)
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    launcher = Launcher()
    launcher.run()
