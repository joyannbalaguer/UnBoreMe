"""
Games Routes
Game listing and access
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, abort
from app.models import Game, UserGame
from app.utils.decorators import login_required, active_required

games_bp = Blueprint('games', __name__)


@games_bp.route('/')
@login_required
@active_required
def index():
    """List all available games for user"""
    user_games = UserGame.get_user_games(session['user_id'])
    
    # Filter only enabled games
    enabled_games = [game for game in user_games if game['is_enabled'] == 1]
    
    return render_template('games/index.html', games=enabled_games)


@games_bp.route('/play/<slug>')
@login_required
@active_required
def play_game(slug):
    """Play a specific game"""
    game = Game.get_by_slug(slug)
    
    if not game:
        flash('Game not found!', 'danger')
        return redirect(url_for('games.index'))
    
    # Check if user has access to the game
    if not UserGame.is_game_enabled(session['user_id'], game['id']):
        flash('You do not have access to this game!', 'danger')
        return redirect(url_for('games.index'))
    
    # Render the specific game template
    return render_template(f'games/{slug}.html', game=game)
