import pygame
import random
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env

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
    (255, 0, 0),
    (255, 136, 0),
    (255, 255, 0),
    (255, 255, 0)
]


# BASE CLASS — INHERITANCE + ABSTRACTION

class GameObject:
    def update(self):
        pass  # children override if needed

    def draw(self, screen):
        raise NotImplementedError("Subclasses must override draw()")



# PLAYER

class Player(GameObject):
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
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x + 20, self.y - 10, 10, 10))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)



# BULLET

class Bullet(GameObject):
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 4
        self.height = 15

    def update(self):
        self.y += self.speed

    def is_off_screen(self):
        return self.y < 0 or self.y > WINDOW_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)



# ALIEN

class Alien(GameObject):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.color = color
        self.alive = True

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BACKGROUND_COLOR, (self.x + 8, self.y + 8, 6, 6))
            pygame.draw.rect(screen, BACKGROUND_COLOR, (self.x + 26, self.y + 8, 6, 6))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# MAIN GAME CLASS

class SpaceInvadersGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        self.game_running = False
        self.game_paused = False
        self.score = 0
        self.lives = 3
        self.level = 1

        self.player = Player(WINDOW_WIDTH // 2 - 25, WINDOW_HEIGHT - 80)
        self.bullets = []
        self.alien_bullets = []
        self.aliens = []

        self.alien_speed = 1
        self.alien_direction = 1

        self.bullet_cooldown = 0

        self.ui_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 56)
        self.instruction_font = pygame.font.Font(None, 24)
        self.pause_font = pygame.font.Font(None, 48)

    
    # Alien Grid
    
    def create_aliens(self):
        self.aliens = []
        rows = 4
        cols = 8
        padding = 20
        offset_x = 80
        offset_y = 60

        for r in range(rows):
            for c in range(cols):
                x = offset_x + c * (40 + padding)
                y = offset_y + r * (30 + padding)
                self.aliens.append(Alien(x, y, ALIEN_COLORS[r]))

    
    # Shoot Systems
    
    def shoot(self):
        if self.bullet_cooldown <= 0:
            b = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y, -7, BULLET_COLOR)
            self.bullets.append(b)
            self.bullet_cooldown = 20

    def alien_shoot(self):
        alive = [a for a in self.aliens if a.alive]
        if alive and random.random() < 0.02:
            shooter = random.choice(alive)
            b = Bullet(shooter.x + shooter.width // 2 - 2, shooter.y + shooter.height, 5, ALIEN_BULLET_COLOR)
            self.alien_bullets.append(b)

    
    # Game Flow
    
    def start(self):
        self.game_running = True
        self.game_paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        self.alien_speed = 1
        self.bullets = []
        self.alien_bullets = []
        self.player.x = WINDOW_WIDTH // 2 - 25
        self.create_aliens()

    def toggle_pause(self):
        if self.game_running:
            self.game_paused = not self.game_paused

    def next_level(self):
        self.level += 1
        self.alien_speed += 0.5
        self.bullets = []
        self.alien_bullets = []
        self.create_aliens()

    
    # UPDATE LOOP — demonstrates polymorphism via update()
    
    def update(self, keys):
        if not self.game_running or self.game_paused:
            return

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        for bullet in self.alien_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.alien_bullets.remove(bullet)

        alive_aliens = [a for a in self.aliens if a.alive]
        move_down = False

        # Move aliens
        for alien in alive_aliens:
            alien.x += self.alien_speed * self.alien_direction
            if alien.x <= 0 or alien.x + alien.width >= WINDOW_WIDTH:
                move_down = True

        if move_down:
            self.alien_direction *= -1
            for alien in alive_aliens:
                alien.y += 20
                if alien.y + alien.height >= self.player.y:
                    self.game_over()

        self.alien_shoot()

        # Bullet vs Alien
        for bullet in self.bullets[:]:
            for alien in self.aliens:
                if alien.alive and bullet.get_rect().colliderect(alien.get_rect()):
                    alien.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.score += 10
                    break

        # Alien Bullet vs Player
        for bullet in self.alien_bullets[:]:
            if bullet.get_rect().colliderect(self.player.get_rect()):
                if bullet in self.alien_bullets:
                    self.alien_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over()

        # Level Clear
        if not alive_aliens:
            self.next_level()

    
    # Game Over
    
    def game_over(self):
        self.game_running = False
        # Send score to API
        user_id, game_id = get_user_and_game_from_env()
        if user_id and game_id:
            send_score_to_api(user_id, game_id, self.score)

    
    # DRAWING — polymorphism: objects call .draw() differently
    
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        title = self.title_font.render("SPACE INVADERS", True, TEXT_COLOR)
        rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title, rect)

        instructions = [
            "Press SPACE to Start",
            "Arrow Keys / A,D to Move",
            "SPACE to Shoot",
            "P to Pause"
        ]

        y = WINDOW_HEIGHT // 2
        for line in instructions:
            text = self.instruction_font.render(line, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 35

    def draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)

        self.player.draw(self.screen)

        for b in self.bullets:
            b.draw(self.screen)

        for b in self.alien_bullets:
            b.draw(self.screen)

        for a in self.aliens:
            a.draw(self.screen)

        score = self.ui_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score, (10, 10))

        lives = self.ui_font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        self.screen.blit(lives, (10, 40))

        level = self.ui_font.render(f"Level: {self.level}", True, TEXT_COLOR)
        rect = level.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        self.screen.blit(level, rect)

    def draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        text = self.pause_font.render("PAUSED", True, TEXT_COLOR)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, rect)

        resume = self.instruction_font.render("Press P to Resume", True, TEXT_COLOR)
        rect = resume.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(resume, rect)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        text = self.pause_font.render("GAME OVER", True, TEXT_COLOR)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(text, rect)

        score = self.instruction_font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        rect = score.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score, rect)

        restart = self.instruction_font.render("Press SPACE to Restart", True, TEXT_COLOR)
        rect = restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(restart, rect)

    # MAIN LOOP
    
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


if __name__ == "__main__":
    SpaceInvadersGame().run()
