"""
Flappy Bird Game - Pygame Version (OOP Enhanced)
Classic flappy bird style game
Refactor: adds GameObject base, Bird and Pipe inherit and override update()/draw()
"""

import pygame
import random
import json
import os
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
FPS = 60

# Colors
SKY_COLOR_TOP = (78, 192, 202)
SKY_COLOR_BOTTOM = (135, 206, 235)
PIPE_COLOR = (46, 204, 113)
PIPE_DARK = (39, 174, 96)
GROUND_COLOR = (218, 165, 32)
GROUND_DARK = (205, 133, 63)
BIRD_BODY = (255, 215, 0)
BIRD_WING = (255, 165, 0)
BIRD_EYE = (0, 0, 0)
BIRD_BEAK = (255, 99, 71)
TEXT_COLOR = (255, 255, 255)
TEXT_OUTLINE = (0, 0, 0)


# -------------------------
# Base class for polymorphism
# -------------------------
class GameObject:
    def update(self, *args, **kwargs):
        """Optional: override in subclasses"""
        pass

    def draw(self, screen, *args, **kwargs):
        """Must override in subclasses"""
        raise NotImplementedError("Subclasses must implement draw()")


# -------------------------
# Bird class
# -------------------------
class Bird(GameObject):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 34
        self.height = 24
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.rotation = 0

    def flap(self):
        self.velocity = self.jump_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        # Update rotation based on velocity
        self.rotation = max(min(self.velocity * 3, 90), -30)

    def draw(self, screen):
        # Create a surface for the bird
        bird_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)

        # Draw bird body
        pygame.draw.rect(bird_surface, BIRD_BODY, (5, 5, self.width, self.height))

        # Draw wing
        pygame.draw.rect(bird_surface, BIRD_WING, (10, 10, 15, 8))

        # Draw eye
        pygame.draw.circle(bird_surface, BIRD_EYE, (int(5 + self.width * 0.75), int(5 + self.height * 0.25)), 3)

        # Draw beak
        beak_points = [
            (5 + self.width, 5 + self.height // 2),
            (5 + self.width + 8, 5 + self.height // 2 - 2),
            (5 + self.width, 5 + self.height // 2 + 2)
        ]
        pygame.draw.polygon(bird_surface, BIRD_BEAK, beak_points)

        # Rotate bird
        rotated_bird = pygame.transform.rotate(bird_surface, -self.rotation)
        bird_rect = rotated_bird.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))

        screen.blit(rotated_bird, bird_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# -------------------------
# Pipe class
# -------------------------
class Pipe(GameObject):
    def __init__(self, x, top_height, gap):
        self.x = x
        self.top_height = top_height
        self.bottom_y = top_height + gap
        self.width = 60
        self.speed = 2
        self.scored = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen, ground_height):
        # Top pipe
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, PIPE_DARK, (self.x, 0, self.width, self.top_height), 3)

        # Top pipe cap
        pygame.draw.rect(screen, PIPE_DARK, (self.x - 5, self.top_height - 30, self.width + 10, 30))

        # Bottom pipe
        bottom_height = WINDOW_HEIGHT - ground_height - self.bottom_y
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, self.bottom_y, self.width, bottom_height))
        pygame.draw.rect(screen, PIPE_DARK, (self.x, self.bottom_y, self.width, bottom_height), 3)

        # Bottom pipe cap
        pygame.draw.rect(screen, PIPE_DARK, (self.x - 5, self.bottom_y, self.width + 10, 30))

    def collides_with(self, bird):
        bird_rect = bird.get_rect()
        bird_left = bird_rect.left
        bird_right = bird_rect.right
        bird_top = bird_rect.top
        bird_bottom = bird_rect.bottom

        pipe_left = self.x
        pipe_right = self.x + self.width

        # Check if bird is in pipe's x range
        if bird_right > pipe_left and bird_left < pipe_right:
            # Check if bird hit top or bottom pipe
            if bird_top < self.top_height or bird_bottom > self.bottom_y:
                return True

        return False

    def is_off_screen(self):
        return self.x + self.width < 0


# -------------------------
# FlappyBirdGame orchestrator
# -------------------------
class FlappyBirdGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()

        # Game state
        self.game_running = False
        self.score = 0
        self.best_score = self.load_best_score()

        # Game objects
        self.bird = Bird(80, WINDOW_HEIGHT // 2)
        self.pipes = []

        # Pipe settings
        self.pipe_gap = 150
        self.pipe_frequency = 90
        self.frame_count = 0

        # Ground
        self.ground_height = 100
        self.ground_x = 0

        # Fonts
        self.score_font = pygame.font.Font(None, 64)
        self.best_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 64)
        self.instruction_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 28)

    def load_best_score(self):
        """Load best score from file"""
        try:
            if os.path.exists('.pygame_flappy_best.json'):
                with open('.pygame_flappy_best.json', 'r') as f:
                    data = json.load(f)
                    return data.get('best_score', 0)
        except:
            pass
        return 0

    def save_best_score(self):
        """Save best score to file"""
        try:
            with open('.pygame_flappy_best.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass

    def start(self):
        self.game_running = True
        self.score = 0
        self.bird = Bird(80, WINDOW_HEIGHT // 2)
        self.pipes = []
        self.frame_count = 0
        self.ground_x = 0

    def flap(self):
        if self.game_running:
            self.bird.flap()

    def update(self):
        if not self.game_running:
            return

        # Update bird (polymorphic)
        if self.bird:
            self.bird.update()

        # Check ground collision
        if self.bird.y + self.bird.height >= WINDOW_HEIGHT - self.ground_height:
            self.game_over()
            return

        # Check ceiling collision
        if self.bird.y <= 0:
            self.bird.y = 0
            self.bird.velocity = 0

        # Update frame count and add pipes
        self.frame_count += 1

        if self.frame_count % self.pipe_frequency == 0:
            min_height = 50
            max_height = WINDOW_HEIGHT - self.ground_height - self.pipe_gap - min_height
            height = random.randint(min_height, max_height)
            self.pipes.append(Pipe(WINDOW_WIDTH, height, self.pipe_gap))

        # Update pipes (polymorphic)
        for pipe in self.pipes[:]:
            pipe.update()

            # Check collision
            if pipe.collides_with(self.bird):
                self.game_over()
                return

            # Score point
            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                if self.score > self.best_score:
                    self.best_score = self.score
                    self.save_best_score()

            # Remove off-screen pipes
            if pipe.is_off_screen():
                self.pipes.remove(pipe)

        # Update ground
        self.ground_x -= 2
        if self.ground_x <= -50:
            self.ground_x = 0

    def game_over(self):
        self.game_running = False

    def draw_background(self):
        # Sky gradient
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(SKY_COLOR_TOP[0] + (SKY_COLOR_BOTTOM[0] - SKY_COLOR_TOP[0]) * ratio)
            g = int(SKY_COLOR_TOP[1] + (SKY_COLOR_BOTTOM[1] - SKY_COLOR_TOP[1]) * ratio)
            b = int(SKY_COLOR_TOP[2] + (SKY_COLOR_BOTTOM[2] - SKY_COLOR_TOP[2]) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

    def draw_ground(self):
        # Ground
        pygame.draw.rect(self.screen, GROUND_COLOR,
                         (0, WINDOW_HEIGHT - self.ground_height, WINDOW_WIDTH, self.ground_height))

        # Ground pattern
        for i in range(int(WINDOW_WIDTH / 50) + 2):
            x = self.ground_x + i * 50
            pygame.draw.rect(self.screen, GROUND_DARK,
                             (x, WINDOW_HEIGHT - self.ground_height, 40, 10))
            pygame.draw.rect(self.screen, GROUND_DARK,
                             (x + 10, WINDOW_HEIGHT - self.ground_height + 15, 20, 10))

    def draw_text_with_outline(self, text, font, x, y, center=True):
        # Draw outline
        outline = font.render(text, True, TEXT_OUTLINE)
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    if center:
                        rect = outline.get_rect(center=(x + dx, y + dy))
                    else:
                        rect = outline.get_rect(topleft=(x + dx, y + dy))
                    self.screen.blit(outline, rect)

        # Draw text
        text_surface = font.render(text, True, TEXT_COLOR)
        if center:
            rect = text_surface.get_rect(center=(x, y))
        else:
            rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, rect)

    def draw_start_screen(self):
        self.draw_background()
        self.draw_ground()

        # Title
        self.draw_text_with_outline('FLAPPY BIRD', self.title_font, WINDOW_WIDTH // 2, 150)

        # Bird preview
        preview_bird = Bird(WINDOW_WIDTH // 2 - 17, 250)
        preview_bird.draw(self.screen)

        # Instructions
        self.draw_text_with_outline('Click or Press SPACE to Flap', self.instruction_font,
                                    WINDOW_WIDTH // 2, 350)
        self.draw_text_with_outline('Avoid the pipes!', self.small_font, WINDOW_WIDTH // 2, 390)
        self.draw_text_with_outline('Click to Start!', self.instruction_font, WINDOW_WIDTH // 2, 460)

    def draw_game(self):
        self.draw_background()

        # Draw pipes (polymorphic)
        for pipe in self.pipes:
            pipe.draw(self.screen, self.ground_height)

        # Draw ground
        self.draw_ground()

        # Draw bird
        if self.bird:
            self.bird.draw(self.screen)

        # Draw score
        self.draw_text_with_outline(str(self.score), self.score_font, WINDOW_WIDTH // 2, 70)
        self.draw_text_with_outline(f'Best: {self.best_score}', self.best_font, WINDOW_WIDTH // 2, 100)

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        self.draw_text_with_outline('GAME OVER', self.title_font, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        self.draw_text_with_outline(f'Score: {self.score}', self.instruction_font,
                                    WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        self.draw_text_with_outline(f'Best: {self.best_score}', self.instruction_font,
                                    WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        self.draw_text_with_outline('Click to Restart', self.small_font,
                                    WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)

    def draw(self):
        if not self.game_running and self.frame_count == 0:
            self.draw_start_screen()
        else:
            self.draw_game()
            if not self.game_running:
                self.draw_game_over()

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
                        if not self.game_running and self.frame_count == 0:
                            self.start()
                        elif not self.game_running:
                            self.start()
                        else:
                            self.flap()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_running and self.frame_count == 0:
                        self.start()
                    elif not self.game_running:
                        self.start()
                    else:
                        self.flap()

            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = FlappyBirdGame()
    game.run()
