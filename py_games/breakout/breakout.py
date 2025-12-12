"""
Breakout Game - Pygame Version (OOP Enhanced)
Classic brick-breaking game
Refactor: adds GameObject base, Paddle/Ball/Brick inherit and override update()/draw()
"""

import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (26, 26, 46)
PADDLE_COLOR = (0, 255, 136)
BALL_COLOR = (0, 217, 255)
TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (26, 26, 46)

BRICK_COLORS = [
    (255, 0, 110),   # Pink
    (255, 102, 0),   # Orange
    (255, 208, 0),   # Yellow
    (0, 255, 136),   # Green
    (0, 217, 255)    # Cyan
]


# ----------------------------
# Base class for polymorphism
# ----------------------------
class GameObject:
    def update(self, *args, **kwargs):
        """Optional per-frame update hook."""
        pass

    def draw(self, screen, *args, **kwargs):
        """Draw the object. Subclasses override this."""
        raise NotImplementedError("Subclasses must implement draw()")


# ----------------------------
# Paddle (inherits GameObject)
# ----------------------------
class Paddle(GameObject):
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.speed = 8

    def move_left(self):
        self.x = max(0, self.x - self.speed)

    def move_right(self, canvas_width):
        self.x = min(canvas_width - self.width, self.x + self.speed)

    def update(self, keys=None, canvas_width=None):
        """
        If keys is provided, paddle will handle player input.
        Signature kept extensible for future AI or scripted control.
        """
        if keys is None or canvas_width is None:
            return
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right(canvas_width)

    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, (int(self.x), int(self.y), self.width, self.height))


# ----------------------------
# Ball (inherits GameObject)
# ----------------------------
class Ball(GameObject):
    def __init__(self, x, y, radius):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.speed_x = 4.0
        self.speed_y = -4.0
        self.max_speed = 8.0

    def update(self, *args, **kwargs):
        # allow call signature update(canvas_width, canvas_height) though not required here
        self.x += self.speed_x
        self.y += self.speed_y

    def check_wall_collision(self, canvas_width, canvas_height):
        # Left and right walls
        if self.x - self.radius <= 0 or self.x + self.radius >= canvas_width:
            self.speed_x = -self.speed_x

        # Top wall
        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

    def check_paddle_collision(self, paddle):
        # paddle coordinates may be float
        px, py = paddle.x, paddle.y
        pw, ph = paddle.width, paddle.height

        if (self.y + self.radius >= py and
                self.y - self.radius <= py + ph and
                self.x >= px and
                self.x <= px + pw):

            # Calculate hit position for angle adjustment
            hit_pos = (self.x - px) / pw
            self.speed_x = (hit_pos - 0.5) * 10.0
            self.speed_y = -abs(self.speed_y)
            return True
        return False

    def is_out_of_bounds(self, canvas_height):
        return self.y - self.radius > canvas_height

    def reset(self, canvas_width, canvas_height):
        self.x = canvas_width / 2.0
        self.y = canvas_height - 50.0
        self.speed_x = 4.0
        self.speed_y = -4.0

    def draw(self, screen):
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           int(self.radius * 2), int(self.radius * 2))


# ----------------------------
# Brick (inherits GameObject)
# ----------------------------
class Brick(GameObject):
    def __init__(self, x, y, width, height, color, points):
        self.x = x
        self.y = y
        self.width = int(width)
        self.height = int(height)
        self.color = color
        self.points = points
        self.destroyed = False

    def check_collision(self, ball):
        if self.destroyed:
            return False

        # Axis-aligned bounding box vs circle approximation (same as original logic)
        if (ball.x + ball.radius >= self.x and
                ball.x - ball.radius <= self.x + self.width and
                ball.y + ball.radius >= self.y and
                ball.y - ball.radius <= self.y + self.height):

            # Determine collision side by overlap amounts
            overlap_left = ball.x + ball.radius - self.x
            overlap_right = (self.x + self.width) - (ball.x - ball.radius)
            overlap_top = ball.y + ball.radius - self.y
            overlap_bottom = (self.y + self.height) - (ball.y - ball.radius)

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left or min_overlap == overlap_right:
                ball.speed_x = -ball.speed_x
            else:
                ball.speed_y = -ball.speed_y

            self.destroyed = True
            return True
        return False

    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.rect(screen, BORDER_COLOR, (int(self.x), int(self.y), self.width, self.height), 2)


# ----------------------------
# BreakoutGame orchestrator
# ----------------------------
class BreakoutGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()

        # Game objects
        self.paddle = Paddle(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 30, 100, 10)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, 8)
        self.bricks = []

        # Game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.game_running = False

        # Brick settings
        self.brick_rows = 5
        self.brick_cols = 8
        # compute brick width as float then pass to Brick which casts to int internally
        self.brick_width = (WINDOW_WIDTH - 80) / self.brick_cols
        self.brick_height = 20
        self.brick_padding = 10
        self.brick_offset_top = 60
        self.brick_offset_left = 40

        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.info_font = pygame.font.Font(None, 32)
        self.ui_font = pygame.font.Font(None, 28)

        self.create_bricks()

    def create_bricks(self):
        self.bricks = []
        for row in range(self.brick_rows):
            for col in range(self.brick_cols):
                x = col * (self.brick_width + self.brick_padding) + self.brick_offset_left
                y = row * (self.brick_height + self.brick_padding) + self.brick_offset_top
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                points = (self.brick_rows - row) * 10
                self.bricks.append(Brick(x, y, self.brick_width, self.brick_height, color, points))

    def start(self):
        self.game_running = True

    def reset(self):
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.game_running = False
        self.paddle.x = WINDOW_WIDTH // 2 - 50
        self.ball.reset(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.create_bricks()

    def update(self):
        if not self.game_running or self.game_over or self.game_won:
            return

        # Update ball (polymorphic)
        self.ball.update()
        self.ball.check_wall_collision(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.ball.check_paddle_collision(self.paddle)

        # Check brick collisions
        for brick in self.bricks:
            if brick.check_collision(self.ball):
                self.score += brick.points

        # Check if all bricks destroyed
        if all(brick.destroyed for brick in self.bricks):
            self.game_won = True
            self.game_running = False

        # Check if ball out of bounds
        if self.ball.is_out_of_bounds(WINDOW_HEIGHT):
            self.lives -= 1

            if self.lives <= 0:
                self.game_over = True
                self.game_running = False
            else:
                self.ball.reset(WINDOW_WIDTH, WINDOW_HEIGHT)
                self.paddle.x = WINDOW_WIDTH // 2 - 50

    def draw(self):
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)

        if not self.game_running and not self.game_over and not self.game_won:
            # Start screen
            title = self.title_font.render('BREAKOUT', True, TEXT_COLOR)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
            self.screen.blit(title, title_rect)

            instructions = [
                'Use Arrow Keys or A/D to move paddle',
                'Break all the bricks to win!',
                '',
                'Press SPACE to Start'
            ]

            y_offset = WINDOW_HEIGHT // 2
            for instruction in instructions:
                text = self.info_font.render(instruction, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40

        else:
            # Draw UI
            score_text = self.ui_font.render(f'Score: {self.score}', True, TEXT_COLOR)
            self.screen.blit(score_text, (20, 20))

            lives_text = self.ui_font.render(f'Lives: {self.lives}', True, TEXT_COLOR)
            lives_rect = lives_text.get_rect(topright=(WINDOW_WIDTH - 20, 20))
            self.screen.blit(lives_text, lives_rect)

            # Draw bricks (polymorphic)
            for brick in self.bricks:
                brick.draw(self.screen)

            # Draw paddle
            self.paddle.draw(self.screen)

            # Draw ball
            self.ball.draw(self.screen)

            # Draw game over or won overlay
            if self.game_over or self.game_won:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                result_text = 'YOU WIN!' if self.game_won else 'GAME OVER'
                result = self.title_font.render(result_text, True, TEXT_COLOR)
                result_rect = result.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
                self.screen.blit(result, result_rect)

                score_display = self.info_font.render(f'Score: {self.score}', True, TEXT_COLOR)
                score_rect = score_display.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
                self.screen.blit(score_display, score_rect)

                restart = self.info_font.render('Press R to Restart', True, TEXT_COLOR)
                restart_rect = restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
                self.screen.blit(restart, restart_rect)

    def handle_input(self, keys):
        # Delegate control to paddle.update (polymorphic)
        self.paddle.update(keys=keys, canvas_width=WINDOW_WIDTH)

    def run(self):
        running = True

        while running:
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and not self.game_running:
                        if not self.game_over and not self.game_won:
                            self.start()
                    elif event.key == pygame.K_r:
                        if self.game_over or self.game_won:
                            self.reset()

            self.handle_input(keys)
            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = BreakoutGame()
    game.run()
