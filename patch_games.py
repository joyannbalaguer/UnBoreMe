"""Quick patch script to add score saving to remaining games"""
import os
import re

games_to_patch = [
    ('py_games/breakout/breakout.py', 'self.game_over = True', 'self.game_running = False'),
    ('py_games/pong/pong.py', 'self.game_over = True', 'self.game_running = False'),
    ('py_games/spaceinvaders/spaceinvaders.py', 'def game_over(self):', 'self.game_running = False'),
    ('py_games/memorymatch/memorymatch.py', 'self.game_won = True', 'self.check_win()')
]

imports_block = """
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env
"""

score_send_code = """
                # Send score to API
                user_id, game_id = get_user_and_game_from_env()
                if user_id and game_id:
                    send_score_to_api(user_id, game_id, self.score)"""

for game_file, search_text, context in games_to_patch:
    print(f"Patching {game_file}...")
    
print("Done! Now manually apply patches to each game.")
