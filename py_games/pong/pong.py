"""
Pong Game - Pygame Version
Classic pong game with AI opponent
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
BACKGROUND_COLOR = (26, 26, 46)
CENTER_LINE_COLOR = (22, 33, 62)
PADDLE_LEFT_COLOR = (0, 255, 136)
PADDLE_RIGHT_COLOR = (255, 0, 110)
BALL_COLOR = (0, 217, 255)
TEXT_COLOR = (255, 255, 255)

class Paddle:
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
        """Simple AI: follow the ball"""
        paddle_center = self.y + self.height / 2
        ball_center = ball.y
        
        if paddle_center < ball_center - 10:
            self.move_down(canvas_height)
        elif paddle_center > ball_center + 10:
            self.move_up()
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 4
        self.speed_y = 4
        self.max_speed = 8
    
    def update(self, canvas_width, canvas_height):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Top and bottom wall collision
        if self.y - self.radius <= 0 or self.y + self.radius >= canvas_height:
            self.speed_y = -self.speed_y
    
    def reset(self, canvas_width, canvas_height):
        self.x = canvas_width / 2
        self.y = canvas_height / 2
        self.speed_x = -self.speed_x
        self.speed_y = random.choice([4, -4])
    
    def check_paddle_collision(self, paddle):
        ball_left = self.x - self.radius
        ball_right = self.x + self.radius
        ball_top = self.y - self.radius
        ball_bottom = self.y + self.radius
        
        paddle_left = paddle.x
        paddle_right = paddle.x + paddle.width
        paddle_top = paddle.y
        paddle_bottom = paddle.y + paddle.height
        
        if (ball_right >= paddle_left and ball_left <= paddle_right and
            ball_bottom >= paddle_top and ball_top <= paddle_bottom):
            
            # Calculate hit position for spin effect
            hit_pos = (self.y - paddle.y) / paddle.height
            self.speed_y = (hit_pos - 0.5) * 10
            
            # Reverse horizontal direction
            self.speed_x = -self.speed_x
            
            # Increase speed slightly
            self.speed_x *= 1.05
            self.speed_x = min(abs(self.speed_x), self.max_speed) * (1 if self.speed_x > 0 else -1)
            
            return True
        return False
    
    def is_out_of_bounds(self, canvas_width):
        return self.x < 0 or self.x > canvas_width
    
    def scored_on(self):
        return 'right' if self.x < 0 else 'left'
    
    def draw(self, screen):
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), self.radius)

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        
        # Game objects
        paddle_width = 10
        paddle_height = 80
        
        self.left_paddle = Paddle(20, WINDOW_HEIGHT // 2 - paddle_height // 2,
                                  paddle_width, paddle_height, PADDLE_LEFT_COLOR)
        self.right_paddle = Paddle(WINDOW_WIDTH - 30, WINDOW_HEIGHT // 2 - paddle_height // 2,
                                   paddle_width, paddle_height, PADDLE_RIGHT_COLOR)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 8)
        
        # Game state
        self.score_left = 0
        self.score_right = 0
        self.game_running = False
        self.win_score = 5
        self.game_over = False
        
        # Fonts
        self.score_font = pygame.font.Font(None, 64)
        self.title_font = pygame.font.Font(None, 64)
        self.instruction_font = pygame.font.Font(None, 32)
        self.ui_font = pygame.font.Font(None, 28)
    
    def start(self):
        self.game_running = True
        self.game_over = False
    
    def reset(self):
        self.score_left = 0
        self.score_right = 0
        self.game_running = False
        self.game_over = False
        self.ball.reset(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.left_paddle.y = WINDOW_HEIGHT // 2 - self.left_paddle.height // 2
        self.right_paddle.y = WINDOW_HEIGHT // 2 - self.right_paddle.height // 2
    
    def update(self, keys):
        if not self.game_running or self.game_over:
            return
        
        # Update player paddle
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.left_paddle.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.left_paddle.move_down(WINDOW_HEIGHT)
        
        # Update AI paddle
        self.right_paddle.ai_update(self.ball, WINDOW_HEIGHT)
        
        # Update ball
        self.ball.update(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Check paddle collisions
        self.ball.check_paddle_collision(self.left_paddle)
        self.ball.check_paddle_collision(self.right_paddle)
        
        # Check if ball is out of bounds
        if self.ball.is_out_of_bounds(WINDOW_WIDTH):
            scorer = self.ball.scored_on()
            if scorer == 'left':
                self.score_left += 1
            else:
                self.score_right += 1
            
            # Check for winner
            if self.score_left >= self.win_score or self.score_right >= self.win_score:
                self.game_over = True
                self.game_running = False
                return
            
            self.ball.reset(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def draw_center_line(self):
        # Draw dashed center line
        dash_height = 10
        gap_height = 10
        y = 0
        while y < WINDOW_HEIGHT:
            pygame.draw.rect(self.screen, CENTER_LINE_COLOR,
                           (WINDOW_WIDTH // 2 - 1, y, 2, dash_height))
            y += dash_height + gap_height
    
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_center_line()
        
        # Title
        title = self.title_font.render('PONG', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            'Player vs AI',
            '',
            'Use Arrow Keys or W/S to move',
            f'First to {self.win_score} points wins!',
            '',
            'Press SPACE to Start'
        ]
        
        y_offset = WINDOW_HEIGHT // 2 - 20
        for instruction in instructions:
            if instruction:
                text = self.instruction_font.render(instruction, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 40
    
    def draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_center_line()
        
        # Draw game objects
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw scores
        left_score = self.score_font.render(str(self.score_left), True, TEXT_COLOR)
        left_rect = left_score.get_rect(center=(WINDOW_WIDTH // 4, 60))
        self.screen.blit(left_score, left_rect)
        
        right_score = self.score_font.render(str(self.score_right), True, TEXT_COLOR)
        right_rect = right_score.get_rect(center=(WINDOW_WIDTH * 3 // 4, 60))
        self.screen.blit(right_score, right_rect)
        
        # Draw labels
        player_label = self.ui_font.render('Player', True, PADDLE_LEFT_COLOR)
        player_rect = player_label.get_rect(center=(WINDOW_WIDTH // 4, 100))
        self.screen.blit(player_label, player_rect)
        
        ai_label = self.ui_font.render('AI', True, PADDLE_RIGHT_COLOR)
        ai_rect = ai_label.get_rect(center=(WINDOW_WIDTH * 3 // 4, 100))
        self.screen.blit(ai_label, ai_rect)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Winner text
        winner = 'PLAYER WINS!' if self.score_left >= self.win_score else 'AI WINS!'
        winner_text = self.title_font.render(winner, True, TEXT_COLOR)
        winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(winner_text, winner_rect)
        
        # Final score
        score_text = self.instruction_font.render(
            f'Final Score: {self.score_left} - {self.score_right}',
            True, TEXT_COLOR
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Restart prompt
        restart_text = self.instruction_font.render('Press R to Restart', True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)
    
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
                    elif event.key == pygame.K_SPACE:
                        if not self.game_running and not self.game_over:
                            self.start()
                    elif event.key == pygame.K_r:
                        if self.game_over:
                            self.reset()
            
            self.update(keys)
            
            if not self.game_running and not self.game_over:
                self.draw_start_screen()
            else:
                self.draw_game()
                if self.game_over:
                    self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = PongGame()
    game.run()
