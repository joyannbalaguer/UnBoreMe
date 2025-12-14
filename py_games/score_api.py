"""
Score API Helper for Pygame Games
Sends scores to Flask API endpoint
"""

import json
import urllib.request
import urllib.error
import os


def send_score_to_api(user_id, game_id, score, api_url="http://localhost:5000/games/api/save-score"):
    """
    Send game score to Flask API
    
    Args:
        user_id (int): User ID from session
        game_id (int): Game ID from database
        score (int): Final game score
        api_url (str): Flask API endpoint URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare data
        data = {
            'user_id': user_id,
            'game_id': game_id,
            'score': score
        }
        
        # Convert to JSON and encode
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            api_url,
            data=json_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # Send request
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('success'):
                print(f"✓ Score saved to database: {score}")
                return True
            else:
                print(f"✗ Failed to save score: {result.get('message', 'Unknown error')}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error saving score: {e.code} - {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"✗ URL Error saving score: {e.reason}")
        return False
    except Exception as e:
        print(f"✗ Error saving score: {str(e)}")
        return False


def get_user_and_game_from_env():
    """
    Get user_id and game_id from environment variables
    These should be set when launching the game from Flask
    
    Returns:
        tuple: (user_id, game_id) or (None, None) if not set
    """
    try:
        user_id = os.environ.get('GAME_USER_ID')
        game_id = os.environ.get('GAME_ID')
        
        if user_id and game_id:
            return int(user_id), int(game_id)
    except ValueError:
        pass
    
    return None, None
