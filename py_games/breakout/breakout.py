import pygame
import sys
import os

# --- SCORE API IMPORT ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env

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
    (255, 0, 110),
    (255, 102, 0),
    (255, 208, 0),
    (0, 255, 136),
    (0, 217, 255)
]


class GameObject:
    def update(self, *args, **kwargs):
        pass

    def draw(self, screen):
        raise NotImplementedError


class Paddle(GameObject):
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.speed = 8

    def update(self, keys, canvas_width):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(0, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(canvas_width - self.width, self.x + self.speed)

    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR,
                         (int(self.x), int(self.y), self.width, self.height))


class Ball(GameObject):
    def __init__(self, x, y, radius):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.speed_x = 4.0
        self.speed_y = -4.0

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def check_wall_collision(self, w, h):
        if self.x - self.radius <= 0 or self.x + self.radius >= w:
            self.speed_x *= -1
        if self.y - self.radius <= 0:
            self.speed_y *= -1

    def check_paddle_collision(self, paddle):
        if (self.y + self.radius >= paddle.y and
            paddle.x <= self.x <= paddle.x + paddle.width):
            hit_pos = (self.x - paddle.x) / paddle.width
            self.speed_x = (hit_pos - 0.5) * 10
            self.speed_y = -abs(self.speed_y)

    def is_out(self, h):
        return self.y - self.radius > h

    def reset(self):
        self.x = WINDOW_WIDTH / 2
        self.y = WINDOW_HEIGHT - 50
        self.speed_x = 4
        self.speed_y = -4

    def draw(self, screen):
        pygame.draw.circle(screen, BALL_COLOR,
                           (int(self.x), int(self.y)), self.radius)


class Brick(GameObject):
    def __init__(self, x, y, w, h, color, points):
        self.rect = pygame.Rect(x, y, int(w), int(h))
        self.color = color
        self.points = points
        self.destroyed = False

    def check_collision(self, ball):
        if self.destroyed:
            return False
        if self.rect.collidepoint(ball.x, ball.y):
            ball.speed_y *= -1
            self.destroyed = True
            return True
        return False

    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BORDER_COLOR, self.rect, 2)


class BreakoutGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()

        self.paddle = Paddle(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 30, 100, 10)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, 8)

        self.score = 0
        self.lives = 3
        self.running = False
        self.game_over = False
        self.game_won = False
        self.score_sent = False

        self.bricks = []
        self.create_bricks()

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 64)

    def create_bricks(self):
        self.bricks.clear()
        rows, cols = 5, 8
        bw = (WINDOW_WIDTH - 80) / cols
        for r in range(rows):
            for c in range(cols):
                x = 40 + c * (bw + 10)
                y = 60 + r * 30
                self.bricks.append(
                    Brick(x, y, bw, 20, BRICK_COLORS[r], (rows - r) * 10)
                )

    def send_score_once(self):
        if self.score_sent:
            return
        user_id, game_id = get_user_and_game_from_env()
        if user_id and game_id:
            send_score_to_api(user_id, game_id, self.score)
            print("✓ Breakout score saved:", self.score)
        self.score_sent = True

    def reset(self):
        self.__init__()

    def update(self, keys):
        if not self.running or self.game_over or self.game_won:
            return

        self.paddle.update(keys, WINDOW_WIDTH)
        self.ball.update()
        self.ball.check_wall_collision(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.ball.check_paddle_collision(self.paddle)

        for brick in self.bricks:
            if brick.check_collision(self.ball):
                self.score += brick.points

        if all(b.destroyed for b in self.bricks):
            self.game_won = True
            self.running = False
            self.send_score_once()

        if self.ball.is_out(WINDOW_HEIGHT):
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.running = False
                self.send_score_once()
            else:
                self.ball.reset()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        if not self.running and not self.game_over and not self.game_won:
            text = self.big_font.render("BREAKOUT", True, TEXT_COLOR)
            self.screen.blit(text, text.get_rect(center=(400, 200)))
            tip = self.font.render("Press SPACE to Start", True, TEXT_COLOR)
            self.screen.blit(tip, tip.get_rect(center=(400, 300)))
        else:
            for b in self.bricks:
                b.draw(self.screen)
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)

            self.screen.blit(self.font.render(f"Score: {self.score}", True, TEXT_COLOR), (20, 20))
            self.screen.blit(self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR), (680, 20))

            if self.game_over or self.game_won:
                overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay_surface.set_alpha(180)
                overlay_surface.fill((0, 0, 0))
                self.screen.blit(overlay_surface, (0, 0))
                
                msg = "YOU WIN!" if self.game_won else "GAME OVER"
                title = self.big_font.render(msg, True, TEXT_COLOR)
                self.screen.blit(title, title.get_rect(center=(400, 200)))
                
                score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
                self.screen.blit(score_text, score_text.get_rect(center=(400, 270)))
                
                restart_text = self.font.render("Press R to Restart", True, TEXT_COLOR)
                self.screen.blit(restart_text, restart_text.get_rect(center=(400, 330)))
                
                quit_text = self.font.render("Press ESC to Close Game", True, TEXT_COLOR)
                self.screen.blit(quit_text, quit_text.get_rect(center=(400, 380)))

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
                    elif event.key == pygame.K_SPACE and not self.running:
                        self.running = True
                    elif event.key == pygame.K_r and (self.game_over or self.game_won):
                        self.reset()

            # Only update when actively playing
            if self.running and not self.game_over and not self.game_won:
                self.update(keys)
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    BreakoutGame().run()
