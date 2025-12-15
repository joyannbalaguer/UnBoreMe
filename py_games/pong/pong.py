import pygame
import random
import sys
import os

# SCORE API IMPORT (IMPORTANT)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (26, 26, 46)
CENTER_LINE_COLOR = (22, 33, 62)
PADDLE_LEFT_COLOR = (0, 255, 136)
PADDLE_RIGHT_COLOR = (255, 0, 110)
BALL_COLOR = (0, 217, 255)
TEXT_COLOR = (255, 255, 255)



# Base class

class GameObject:
    def update(self, *args, **kwargs):
        pass

    def draw(self, screen):
        raise NotImplementedError



# Paddle

class Paddle(GameObject):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 5

    def move_up(self):
        self.y = max(0, self.y - self.speed)

    def move_down(self, canvas_height):
        self.y = min(canvas_height - self.height, self.y + self.speed)

    def ai_update(self, ball, canvas_height):
        paddle_center = self.y + self.height / 2
        ball_center = ball.y

        if paddle_center < ball_center - 10:
            self.move_down(canvas_height)
        elif paddle_center > ball_center + 10:
            self.move_up()

    def update(self, keys=None, canvas_height=None, ball=None):
        if ball is not None:
            self.ai_update(ball, canvas_height)
        elif keys is not None:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.move_up()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.move_down(canvas_height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))



# Ball

class Ball(GameObject):
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 4.0
        self.speed_y = 4.0
        self.max_speed = 8.0

    def update(self, canvas_width, canvas_height):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.y - self.radius <= 0 or self.y + self.radius >= canvas_height:
            self.speed_y = -self.speed_y

    def reset(self, canvas_width, canvas_height):
        self.x = canvas_width / 2
        self.y = canvas_height / 2
        self.speed_x = -self.speed_x
        self.speed_y = random.choice([4.0, -4.0])

    def check_paddle_collision(self, paddle):
        if (
            self.x - self.radius <= paddle.x + paddle.width
            and self.x + self.radius >= paddle.x
            and self.y + self.radius >= paddle.y
            and self.y - self.radius <= paddle.y + paddle.height
        ):
            self.speed_x = -self.speed_x
            return True
        return False

    def is_out_of_bounds(self, canvas_width):
        return self.x < 0 or self.x > canvas_width

    def scored_on(self):
        return "right" if self.x < 0 else "left"

    def draw(self, screen):
        pygame.draw.circle(
            screen, BALL_COLOR, (int(self.x), int(self.y)), self.radius
        )



# Pong Game

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()

        paddle_height = 80
        self.left_paddle = Paddle(20, WINDOW_HEIGHT // 2 - 40, 10, paddle_height, PADDLE_LEFT_COLOR)
        self.right_paddle = Paddle(WINDOW_WIDTH - 30, WINDOW_HEIGHT // 2 - 40, 10, paddle_height, PADDLE_RIGHT_COLOR)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 8)

        self.score_left = 0
        self.score_right = 0
        self.win_score = 5

        self.game_running = False
        self.game_over = False
        self.score_saved = False  # IMPORTANT: prevents duplicate saves

        self.font = pygame.font.Font(None, 48)

    def start(self):
        self.game_running = True

    def update(self, keys):
        if not self.game_running or self.game_over:
            return

        self.left_paddle.update(keys=keys, canvas_height=WINDOW_HEIGHT)
        self.right_paddle.update(ball=self.ball, canvas_height=WINDOW_HEIGHT)
        self.ball.update(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.ball.check_paddle_collision(self.left_paddle)
        self.ball.check_paddle_collision(self.right_paddle)

        if self.ball.is_out_of_bounds(WINDOW_WIDTH):
            if self.ball.scored_on() == "left":
                self.score_left += 1
            else:
                self.score_right += 1

            if self.score_left >= self.win_score or self.score_right >= self.win_score:
                self.game_over = True
                self.game_running = False
                self.save_score()
                return

            self.ball.reset(WINDOW_WIDTH, WINDOW_HEIGHT)

    
    # SCORE SAVING LOGIC
    
    def save_score(self):
        if self.score_saved:
            return

        user_id, game_id = get_user_and_game_from_env()
        if user_id and game_id:
            send_score_to_api(user_id, game_id, self.score_left)
            print(f"✓ Pong score saved: {self.score_left}")

        self.score_saved = True

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)

        left = self.font.render(str(self.score_left), True, TEXT_COLOR)
        right = self.font.render(str(self.score_right), True, TEXT_COLOR)

        self.screen.blit(left, (WINDOW_WIDTH // 4, 20))
        self.screen.blit(right, (WINDOW_WIDTH * 3 // 4, 20))

        if self.game_over:
            text = self.font.render("GAME OVER", True, TEXT_COLOR)
            self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

    def run(self):
        running = True
        while running:
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not self.game_running and not self.game_over:
                        self.start()

            self.update(keys)
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    PongGame().run()
