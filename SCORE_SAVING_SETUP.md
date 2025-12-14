# Score Saving Setup Guide

## Overview
This guide explains how to set up and use the new score saving feature that saves Pygame game scores to MySQL database via Flask API.

## What Was Implemented

### 1. Database Table (`game_scores`)
- Stores user game scores with automatic INSERT/UPDATE on duplicate
- Unique constraint on (user_id, game_id) ensures one score per user per game
- Foreign keys to users and games tables with cascade delete

### 2. Flask API Endpoint
- **Route:** `POST /games/api/save-score`
- **Accepts JSON:** `{"user_id": int, "game_id": int, "score": int}`
- **Returns:** Success/failure response with saved score data
- **Validates:** User exists, game exists, score is non-negative

### 3. Score API Helper Module (`py_games/score_api.py`)
- `send_score_to_api()` - Sends score to Flask endpoint via HTTP POST
- `get_user_and_game_from_env()` - Gets user_id and game_id from environment variables
- Uses Python's built-in urllib (no external dependencies)

### 4. Updated Games
- **Snake game** now sends scores to database on game over
- Environment variables (GAME_USER_ID, GAME_ID) passed when launching games

## Setup Instructions

### Step 1: Create Database Table

Run the SQL migration file in phpMyAdmin or MySQL client:

```bash
# Open phpMyAdmin and run:
game_scores_migration.sql
```

Or via command line:
```bash
mysql -u root final_project < game_scores_migration.sql
```

### Step 2: Verify Flask Server is Running

Make sure your Flask server is running on `http://localhost:5000`:

```bash
python run.py
```

### Step 3: Test Score Saving

1. Log in to your application
2. Navigate to Games section
3. Launch Snake game
4. Play and get a game over
5. Check console output for: `✓ Score saved to database: [score]`
6. Verify in database:
   ```sql
   SELECT * FROM game_scores WHERE user_id = YOUR_USER_ID AND game_id = 1;
   ```

## How It Works

### Flow Diagram
```
1. User clicks "Play Game" on Flask web interface
   ↓
2. Flask routes.py launches Pygame with environment variables:
   - GAME_USER_ID = session['user_id']
   - GAME_ID = game['id']
   ↓
3. Pygame game runs normally
   ↓
4. On game over:
   - Game calls get_user_and_game_from_env()
   - Game calls send_score_to_api(user_id, game_id, score)
   ↓
5. HTTP POST request sent to Flask API
   ↓
6. Flask API validates and saves to MySQL
   - INSERT if new record
   - UPDATE if user already has score for that game
   ↓
7. Success/failure logged in game console
```

## Adding Score Saving to Other Games

To add score saving to any Pygame game:

### Step 1: Import the helper module
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from score_api import send_score_to_api, get_user_and_game_from_env
```

### Step 2: Call on game over
```python
def game_over(self):
    # Your existing game over logic
    self.game_running = False
    
    # Send score to API
    user_id, game_id = get_user_and_game_from_env()
    if user_id and game_id:
        send_score_to_api(user_id, game_id, self.score)
```

### That's it! No direct MySQL connection needed from Pygame.

## API Reference

### POST /games/api/save-score

**Request Body:**
```json
{
  "user_id": 1,
  "game_id": 1,
  "score": 100
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Score saved successfully",
  "data": {
    "user_id": 1,
    "game_id": 1,
    "score": 100
  }
}
```

**Error Response (400/404/500):**
```json
{
  "success": false,
  "message": "Error description"
}
```

## Database Schema

```sql
CREATE TABLE `game_scores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `score` int(11) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_game_score` (`user_id`, `game_id`),
  CONSTRAINT `fk_game_scores_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_game_scores_game` FOREIGN KEY (`game_id`) REFERENCES `games` (`id`) ON DELETE CASCADE
);
```

## Game IDs Reference

Based on your database:
- 1: Snake
- 2: Pong
- 3: Tetris
- 4: Breakout
- 5: Space Invaders
- 6: Memory Match
- 7: 2048
- 8: Flappy Bird

## Troubleshooting

### Score not saving?

1. **Check Flask is running**: Ensure `http://localhost:5000` is accessible
2. **Check environment variables**: Print them in game to verify:
   ```python
   import os
   print(f"User ID: {os.environ.get('GAME_USER_ID')}")
   print(f"Game ID: {os.environ.get('GAME_ID')}")
   ```
3. **Check database table exists**: Verify `game_scores` table created
4. **Check API endpoint**: Test manually with curl:
   ```bash
   curl -X POST http://localhost:5000/games/api/save-score \
     -H "Content-Type: application/json" \
     -d '{"user_id":1,"game_id":1,"score":100}'
   ```

### Connection refused error?

- Flask server is not running
- Wrong port (should be 5000)
- Firewall blocking localhost connections

### User/Game not found error?

- Invalid user_id or game_id
- User not in database
- Game not in games table

## Files Modified

- ✅ `game_scores_migration.sql` - Database schema
- ✅ `app/models.py` - Added GameScore model
- ✅ `app/games/routes.py` - Added API endpoint and env variables
- ✅ `py_games/score_api.py` - Score submission helper
- ✅ `py_games/snake/snake.py` - Updated to send scores

## Next Steps

1. **Run the migration SQL** to create the game_scores table
2. **Test with Snake game** to verify functionality
3. **Update other games** using the same pattern
4. **Add leaderboard view** (optional future enhancement)

## Notes

- Scores are saved automatically on game over
- No authentication needed for API (relies on environment variables)
- API is accessible only from localhost by default
- Duplicate scores are updated, not inserted twice
- Console shows success/failure messages for debugging
