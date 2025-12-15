import pygame
import random
import sys
import os

# --- SCORE API ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env

pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (44, 62, 80)
CARD_BACK_COLOR = (52, 152, 219)
CARD_BACK_DARK = (41, 128, 185)
CARD_BORDER = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)

CARD_COLORS = [
    (255, 107, 107), (78, 205, 196), (69, 183, 209), (249, 202, 36),
    (108, 92, 231), (253, 121, 168), (253, 203, 110), (0, 184, 148)
]

SYMBOLS = ['♠', '♥', '♦', '♣', '★', '♪', '☀', '☁']


class GameObject:
    def update(self, *args, **kwargs):
        pass

    def draw(self, screen):
        raise NotImplementedError


class Card(GameObject):
    def __init__(self, x, y, w, h, value):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value
        self.flipped = False
        self.matched = False

    def draw(self, screen):
        if self.flipped or self.matched:
            pygame.draw.rect(screen, self.value['color'], self.rect)
            pygame.draw.rect(screen, CARD_BORDER, self.rect, 3)
            font = pygame.font.Font(None, 48)
            text = font.render(self.value['symbol'], True, TEXT_COLOR)
            screen.blit(text, text.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(screen, CARD_BACK_COLOR, self.rect)
            pygame.draw.rect(screen, CARD_BACK_DARK, self.rect, 3)


class MemoryMatchGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Memory Match")
        self.clock = pygame.time.Clock()

        self.cards = []
        self.flipped_cards = []
        self.can_flip = True
        self.flip_timer = 0

        self.score = 0
        self.moves = 0
        self.level = 1
        self.game_running = False
        self.score_sent = False

        self.rows = 4
        self.cols = 4

        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 64)

    def create_cards(self):
        self.cards.clear()
        values = []

        pairs = (self.rows * self.cols) // 2
        for i in range(pairs):
            value = {
                'color': CARD_COLORS[i % len(CARD_COLORS)],
                'symbol': SYMBOLS[i % len(SYMBOLS)],
                'id': i
            }
            values.extend([value, value])

        random.shuffle(values)

        start_x = (WINDOW_WIDTH - self.cols * 90) // 2
        start_y = 100
        index = 0

        for r in range(self.rows):
            for c in range(self.cols):
                self.cards.append(
                    Card(start_x + c * 90, start_y + r * 120, 80, 100, values[index])
                )
                index += 1

    def send_score_once(self):
        if self.score_sent:
            return
        user_id, game_id = get_user_and_game_from_env()
        if user_id and game_id:
            send_score_to_api(user_id, game_id, self.score)
            print("✓ Memory Match score saved:", self.score)
        self.score_sent = True

    def start(self):
        self.game_running = True
        self.score = 0
        self.moves = 0
        self.level = 1
        self.rows = 4
        self.cols = 4
        self.score_sent = False
        self.create_cards()

    def next_level(self):
        self.score += 500
        self.level += 1

        if self.level == 2:
            self.cols = 5
        elif self.level >= 3:
            self.rows = 5

        self.create_cards()

    def handle_click(self, pos):
        if not self.can_flip:
            return

        for card in self.cards:
            if card.rect.collidepoint(pos) and not card.flipped and not card.matched:
                card.flipped = True
                self.flipped_cards.append(card)
                if len(self.flipped_cards) == 2:
                    self.moves += 1
                    self.can_flip = False
                    self.flip_timer = pygame.time.get_ticks()
                break

    def update(self):
        if not self.game_running:
            return

        if not self.can_flip and len(self.flipped_cards) == 2:
            if pygame.time.get_ticks() - self.flip_timer > 800:
                c1, c2 = self.flipped_cards
                if c1.value['id'] == c2.value['id']:
                    c1.matched = c2.matched = True
                    self.score += 100
                    if all(c.matched for c in self.cards):
                        self.next_level()
                else:
                    c1.flipped = c2.flipped = False

                self.flipped_cards.clear()
                self.can_flip = True

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        if not self.game_running:
            title = self.big_font.render("MEMORY MATCH", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(400, 250)))
            tip = self.font.render("Click to Start", True, TEXT_COLOR)
            self.screen.blit(tip, tip.get_rect(center=(400, 320)))
        else:
            self.screen.blit(self.font.render(f"Score: {self.score}", True, TEXT_COLOR), (20, 20))
            self.screen.blit(self.font.render(f"Level: {self.level}", True, TEXT_COLOR), (680, 20))

            for card in self.cards:
                card.draw(self.screen)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.send_score_once()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_running:
                        self.start()
                    else:
                        self.handle_click(event.pos)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    MemoryMatchGame().run()
