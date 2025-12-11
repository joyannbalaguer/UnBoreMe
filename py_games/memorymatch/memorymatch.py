"""
Memory Match Game - Pygame Version
Classic card matching memory game
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
BACKGROUND_COLOR = (44, 62, 80)
CARD_BACK_COLOR = (52, 152, 219)
CARD_BACK_DARK = (41, 128, 185)
CARD_BORDER = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
HOVER_COLOR = (255, 255, 255, 50)

CARD_COLORS = [
    (255, 107, 107),  # Red
    (78, 205, 196),   # Teal
    (69, 183, 209),   # Blue
    (249, 202, 36),   # Yellow
    (108, 92, 231),   # Purple
    (253, 121, 168),  # Pink
    (253, 203, 110),  # Orange
    (0, 184, 148),    # Green
    (255, 118, 117),  # Light Red
    (116, 185, 255),  # Light Blue
    (162, 155, 254),  # Light Purple
    (255, 234, 167),  # Light Yellow
    (223, 230, 233),  # Gray
    (250, 177, 160),  # Peach
    (129, 236, 236),  # Cyan
    (85, 239, 196)    # Mint
]

SYMBOLS = ['♠', '♥', '♦', '♣', '★', '♪', '☀', '☁', '♫', '☂', '☆', '♨', '✿', '◆', '▲', '●']

class Card:
    def __init__(self, x, y, width, height, value, card_id):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value
        self.card_id = card_id
        self.flipped = False
        self.matched = False
    
    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)
    
    def draw(self, screen, mouse_pos=None):
        if self.flipped or self.matched:
            # Draw card face
            pygame.draw.rect(screen, self.value['color'], 
                           (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, CARD_BORDER, 
                           (self.x, self.y, self.width, self.height), 3)
            
            # Draw symbol
            font = pygame.font.Font(None, 56)
            text = font.render(self.value['symbol'], True, TEXT_COLOR)
            text_rect = text.get_rect(center=(self.x + self.width // 2, 
                                             self.y + self.height // 2))
            screen.blit(text, text_rect)
            
            # Draw matched overlay
            if self.matched:
                overlay = pygame.Surface((self.width, self.height))
                overlay.set_alpha(76)
                overlay.fill((255, 255, 255))
                screen.blit(overlay, (self.x, self.y))
        else:
            # Draw card back
            pygame.draw.rect(screen, CARD_BACK_COLOR, 
                           (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, CARD_BACK_DARK, 
                           (self.x, self.y, self.width, self.height), 3)
            
            # Draw pattern
            for i in range(4):
                for j in range(5):
                    pygame.draw.rect(screen, CARD_BACK_DARK,
                                   (self.x + 10 + i * 18, self.y + 10 + j * 18, 8, 8))
            
            # Draw hover effect
            if mouse_pos and self.contains_point(mouse_pos[0], mouse_pos[1]):
                overlay = pygame.Surface((self.width, self.height))
                overlay.set_alpha(50)
                overlay.fill((255, 255, 255))
                screen.blit(overlay, (self.x, self.y))

class MemoryMatchGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Memory Match")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_running = False
        self.score = 0
        self.moves = 0
        self.matches = 0
        self.level = 1
        
        # Cards
        self.cards = []
        self.flipped_cards = []
        self.can_flip = True
        self.flip_timer = 0
        
        # Card settings
        self.card_width = 80
        self.card_height = 100
        self.card_padding = 10
        self.rows = 4
        self.cols = 4
        
        # Fonts
        self.ui_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 64)
        self.instruction_font = pygame.font.Font(None, 32)
    
    def create_cards(self):
        self.cards = []
        self.flipped_cards = []
        
        total_pairs = (self.rows * self.cols) // 2
        card_values = []
        
        # Create pairs
        for i in range(total_pairs):
            value = {
                'color': CARD_COLORS[i % len(CARD_COLORS)],
                'symbol': SYMBOLS[i % len(SYMBOLS)],
                'id': i
            }
            card_values.append(value)
            card_values.append(value)
        
        # Shuffle
        random.shuffle(card_values)
        
        # Create card objects
        start_x = (WINDOW_WIDTH - (self.cols * (self.card_width + self.card_padding))) // 2
        start_y = 80
        
        index = 0
        for row in range(self.rows):
            for col in range(self.cols):
                card = Card(
                    start_x + col * (self.card_width + self.card_padding),
                    start_y + row * (self.card_height + self.card_padding),
                    self.card_width,
                    self.card_height,
                    card_values[index],
                    index
                )
                self.cards.append(card)
                index += 1
    
    def handle_click(self, pos):
        if not self.can_flip:
            return
        
        # Find clicked card
        for card in self.cards:
            if card.contains_point(pos[0], pos[1]):
                if card.flipped or card.matched:
                    continue
                if len(self.flipped_cards) >= 2:
                    continue
                
                # Flip card
                card.flipped = True
                self.flipped_cards.append(card)
                
                # Check for match
                if len(self.flipped_cards) == 2:
                    self.moves += 1
                    self.can_flip = False
                    self.flip_timer = pygame.time.get_ticks()
                
                break
    
    def check_match(self):
        if len(self.flipped_cards) != 2:
            return
        
        card1, card2 = self.flipped_cards
        
        if card1.value['id'] == card2.value['id']:
            # Match found
            card1.matched = True
            card2.matched = True
            self.matches += 1
            self.score += 100
            
            # Check if all matched
            if all(card.matched for card in self.cards):
                self.next_level()
        else:
            # No match
            card1.flipped = False
            card2.flipped = False
        
        self.flipped_cards = []
        self.can_flip = True
    
    def next_level(self):
        self.level += 1
        self.score += 500  # Bonus for completing level
        
        # Increase difficulty
        if self.level == 2:
            self.rows = 4
            self.cols = 5
        elif self.level == 3:
            self.rows = 4
            self.cols = 6
        elif self.level >= 4:
            self.rows = 5
            self.cols = 6
        
        self.matches = 0
        self.create_cards()
    
    def update(self):
        if not self.game_running:
            return
        
        # Check flip timer
        if not self.can_flip and len(self.flipped_cards) == 2:
            if pygame.time.get_ticks() - self.flip_timer > 800:
                self.check_match()
    
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Title
        title = self.title_font.render('MEMORY MATCH', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            'Click cards to flip and match pairs',
            'Match all pairs to advance to the next level',
            '',
            'Click anywhere to start!'
        ]
        
        y_offset = WINDOW_HEIGHT // 2
        for instruction in instructions:
            if instruction:
                text = self.instruction_font.render(instruction, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 40
    
    def draw_game(self, mouse_pos):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw UI
        score_text = self.ui_font.render(f'Score: {self.score}', True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 30))
        
        moves_text = self.ui_font.render(f'Moves: {self.moves}', True, TEXT_COLOR)
        self.screen.blit(moves_text, (200, 30))
        
        level_text = self.ui_font.render(f'Level: {self.level}', True, TEXT_COLOR)
        level_rect = level_text.get_rect(topright=(WINDOW_WIDTH - 20, 30))
        self.screen.blit(level_text, level_rect)
        
        total_pairs = len(self.cards) // 2
        matches_text = self.ui_font.render(f'Matches: {self.matches}/{total_pairs}', True, TEXT_COLOR)
        matches_rect = matches_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(matches_text, matches_rect)
        
        # Draw cards
        for card in self.cards:
            card.draw(self.screen, mouse_pos)
    
    def start(self):
        self.game_running = True
        self.score = 0
        self.moves = 0
        self.matches = 0
        self.level = 1
        self.rows = 4
        self.cols = 4
        self.create_cards()
    
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_running:
                        self.start()
                    else:
                        self.handle_click(event.pos)
            
            self.update()
            
            if not self.game_running:
                self.draw_start_screen()
            else:
                self.draw_game(mouse_pos)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = MemoryMatchGame()
    game.run()
