"""
Space Invaders Game - Pygame Version
Classic arcade shooter game
"""

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 255, 0)
BULLET_COLOR = (255, 255, 255)
ALIEN_BULLET_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)

ALIEN_COLORS = [
    (255, 0, 0),     # Red - top row
    (255, 136, 0),   # Orange - second row
    (255, 255, 0),   # Yellow - third row
    (255, 255, 0)    # Yellow - fourth row
]

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.speed = 5
    
    def move_left(self):
        self.x = max(0, self.x - self.speed)
    
    def move_right(self):
        self.x = min(WINDOW_WIDTH - self.width, self.x + self.speed)
    
    def draw(self, screen):
        # Player body
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))
        # Cannon
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x + 20, self.y - 10, 10, 10))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 15
        self.speed = speed
        self.color = color
    
    def update(self):
        self.y += self.speed
    
    def is_off_screen(self):
        return self.y < 0 or self.y > WINDOW_HEIGHT
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Alien:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.color = color
        self.alive = True
    
    def draw(self, screen):
        if self.alive:
            # Alien body
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Eyes
            pygame.draw.rect(screen, BACKGROUND_COLOR, (self.x + 8, self.y + 8, 6, 6))
            pygame.draw.rect(screen, BACKGROUND_COLOR, (self.x + 26, self.y + 8, 6, 6))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class SpaceInvadersGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_running = False
        self.game_paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        
        # Game objects
        self.player = Player(WINDOW_WIDTH // 2 - 25, WINDOW_HEIGHT - 80)
        self.bullets = []
        self.alien_bullets = []
        self.aliens = []
        
        # Alien settings
        self.alien_speed = 1
        self.alien_direction = 1
        
        # Bullet settings
        self.bullet_cooldown = 0
        
        # Fonts
        self.ui_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 56)
        self.instruction_font = pygame.font.Font(None, 24)
        self.pause_font = pygame.font.Font(None, 48)
    
    def create_aliens(self):
        self.aliens = []
        alien_rows = 4
        alien_cols = 8
        alien_width = 40
        alien_height = 30
        padding = 20
        offset_x = 80
        offset_y = 60
        
        for row in range(alien_rows):
            for col in range(alien_cols):
                x = offset_x + col * (alien_width + padding)
                y = offset_y + row * (alien_height + padding)
                color = ALIEN_COLORS[row]
                self.aliens.append(Alien(x, y, color))
    
    def shoot(self):
        if self.bullet_cooldown <= 0:
            bullet = Bullet(self.player.x + self.player.width // 2 - 2,
                          self.player.y, -7, BULLET_COLOR)
            self.bullets.append(bullet)
            self.bullet_cooldown = 20
    
    def alien_shoot(self):
        alive_aliens = [a for a in self.aliens if a.alive]
        if alive_aliens and random.random() < 0.02:
            shooter = random.choice(alive_aliens)
            bullet = Bullet(shooter.x + shooter.width // 2 - 2,
                          shooter.y + shooter.height, 5, ALIEN_BULLET_COLOR)
            self.alien_bullets.append(bullet)
    
    def start(self):
        self.game_running = True
        self.game_paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        self.alien_speed = 1
        self.bullets = []
        self.alien_bullets = []
        self.create_aliens()
        self.player.x = WINDOW_WIDTH // 2 - 25
    
    def toggle_pause(self):
        if self.game_running:
            self.game_paused = not self.game_paused
    
    def next_level(self):
        self.level += 1
        self.alien_speed += 0.5
        self.bullets = []
        self.alien_bullets = []
        self.create_aliens()
    
    def update(self, keys):
        if not self.game_running or self.game_paused:
            return
        
        # Update player
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        
        # Update bullet cooldown
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        for bullet in self.alien_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.alien_bullets.remove(bullet)
        
        # Move aliens
        move_down = False
        alive_aliens = [a for a in self.aliens if a.alive]
        
        for alien in alive_aliens:
            alien.x += self.alien_speed * self.alien_direction
            if alien.x <= 0 or alien.x + alien.width >= WINDOW_WIDTH:
                move_down = True
        
        if move_down:
            self.alien_direction *= -1
            for alien in alive_aliens:
                alien.y += 20
                # Check if aliens reached player
                if alien.y + alien.height >= self.player.y:
                    self.game_over()
        
        # Alien shooting
        self.alien_shoot()
        
        # Collision detection - bullets vs aliens
        for bullet in self.bullets[:]:
            for alien in self.aliens:
                if alien.alive and bullet.get_rect().colliderect(alien.get_rect()):
                    alien.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.score += 10
                    break
        
        # Collision detection - alien bullets vs player
        for bullet in self.alien_bullets[:]:
            if bullet.get_rect().colliderect(self.player.get_rect()):
                if bullet in self.alien_bullets:
                    self.alien_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over()
        
        # Check if all aliens dead
        if not alive_aliens:
            self.next_level()
    
    def game_over(self):
        self.game_running = False
    
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Title
        title = self.title_font.render('SPACE INVADERS', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            'Press SPACE to Start',
            'Arrow Keys / A,D to Move',
            'SPACE to Shoot',
            'P to Pause'
        ]
        
        y_offset = WINDOW_HEIGHT // 2
        for instruction in instructions:
            text = self.instruction_font.render(instruction, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35
    
    def draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for bullet in self.alien_bullets:
            bullet.draw(self.screen)
        
        # Draw aliens
        for alien in self.aliens:
            alien.draw(self.screen)
        
        # Draw UI
        score_text = self.ui_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.ui_font.render(f'Lives: {self.lives}', True, TEXT_COLOR)
        self.screen.blit(lives_text, (10, 40))
        
        level_text = self.ui_font.render(f'Level: {self.level}', True, TEXT_COLOR)
        level_rect = level_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        self.screen.blit(level_text, level_rect)
    
    def draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.pause_font.render('PAUSED', True, TEXT_COLOR)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.instruction_font.render('Press P to Resume', True, TEXT_COLOR)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.pause_font.render('GAME OVER', True, TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.instruction_font.render(f'Final Score: {self.score}', True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.instruction_font.render('Press SPACE to Restart', True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        running = True
        game_over_drawn = False
        
        while running:
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if not self.game_running:
                            self.start()
                            game_over_drawn = False
                        elif not self.game_paused:
                            self.shoot()
                    elif event.key == pygame.K_p:
                        self.toggle_pause()
            
            self.update(keys)
            
            if not self.game_running and not game_over_drawn:
                self.draw_start_screen()
            else:
                self.draw_game()
                if self.game_paused:
                    self.draw_pause_overlay()
                elif not self.game_running:
                    self.draw_game_over()
                    game_over_drawn = True
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = SpaceInvadersGame()
    game.run()
