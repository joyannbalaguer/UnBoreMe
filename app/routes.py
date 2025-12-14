"""
Main Application Routes
Handles homepage and public routes
"""
from flask import Blueprint, render_template, session
from app.models import User, GameScore

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage - shows user info if logged in"""
    user = None
    if 'user_id' in session:
        user = User.get_by_id(session['user_id'])
    
    return render_template('index.html', user=user)


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/leaderboard')
def leaderboard():
    """Global leaderboard page"""
    leaderboards = GameScore.get_global_leaderboards(limit=5)
    return render_template('leaderboard.html', leaderboards=leaderboards)


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')
