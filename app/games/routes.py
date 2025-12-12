"""
Games Routes
Game listing and access
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session, abort, current_app
from app.models import Game, UserGame
from app.utils.decorators import login_required, active_required
import subprocess
import sys
import os

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
    """
    Launch a pygame game by discovering its entrypoint inside py_games/<folder>.
    This will start the game on the server machine and then redirect back to the games list.
    """
    # Lookup game object and access control
    game = Game.get_by_slug(slug)
    if not game:
        flash('Game not found!', 'danger')
        return redirect(url_for('games.index'))

    if not UserGame.is_game_enabled(session['user_id'], game['id']):
        flash('You do not have access to this game!', 'danger')
        return redirect(url_for('games.index'))

    # Map site slug -> folder name in py_games
    slug_to_folder = {
        "snake": "snake",
        "pong": "pong",
        "tetris": "tetris",
        "breakout": "breakout",
        "space-invaders": "spaceinvaders",
        "spaceinvaders": "spaceinvaders",
        "flappy": "flappybird",
        "flappy-bird": "flappybird",
        "memory-match": "memorymatch",
        "memorymatch": "memorymatch",
        "2048": "2048",
    }

    folder = slug_to_folder.get(slug, slug.replace('-', '').lower())

    # Determine project root and py_games folder (py_games is sibling of app/)
    app_pkg_path = current_app.root_path
    project_root = os.path.abspath(os.path.join(app_pkg_path, ".."))
    py_games_root = os.path.join(project_root, "py_games")
    current_app.logger.debug(f"Searching for game '{folder}' in: {py_games_root}")

    # Build candidate entrypoint paths in preferred order
    candidates = [
        os.path.join(py_games_root, f"{folder}.py"),           # py_games/snake.py
        os.path.join(py_games_root, folder, "main.py"),       # py_games/snake/main.py
        os.path.join(py_games_root, folder, "run.py"),
        os.path.join(py_games_root, folder, "start.py"),
        os.path.join(py_games_root, folder, "__init__.py"),
        os.path.join(py_games_root, folder, f"{folder}.py"),  # py_games/snake/snake.py
        os.path.join(os.getcwd(), f"{folder}.py"),            # fallback in cwd
    ]

    # If user explicitly configured path, check it first
    cfg = current_app.config.get("PY_GAMES_PATH")
    if cfg:
        candidates.insert(0, os.path.join(cfg, folder + ".py"))

    # Also consider launcher.py (fallback)
    launcher_path = os.path.join(py_games_root, "launcher.py")
    candidates.append(launcher_path)

    # Normalize and deduplicate candidate list
    seen = set()
    uniq_candidates = []
    for p in candidates:
        ap = os.path.abspath(p)
        if ap not in seen:
            seen.add(ap)
            uniq_candidates.append(ap)

    # helper: check for __main__ guard
    def has_main_guard(path):
        try:
            with open(path, "r", encoding="utf8") as f:
                chunk = f.read(4096)
                return "if __name__" in chunk
        except Exception:
            return False

    selected_script = None
    use_launcher_with_arg = False

    # Select a script to run
    for p in uniq_candidates:
        if not os.path.exists(p):
            continue
        # if this is the launcher, mark fallback
        if os.path.abspath(p) == os.path.abspath(launcher_path):
            use_launcher_with_arg = True
            break
        name = os.path.basename(p).lower()
        if name in ("main.py", "run.py", "start.py", f"{folder}.py"):
            selected_script = p
            break
        # accept __init__.py only if it contains main guard
        if name == "__init__.py":
            if has_main_guard(p):
                selected_script = p
                break
            else:
                continue
        # accept any file that has a main guard
        if has_main_guard(p):
            selected_script = p
            break

    if not selected_script and not use_launcher_with_arg:
        current_app.logger.warning("Game entrypoint not found. Checked: %s", uniq_candidates)
        flash("Game script not found on server. Contact admin.", "danger")
        return redirect(url_for('games.index'))

    # Launch process
    try:
        if selected_script:
            current_app.logger.info("Launching game script: %s", selected_script)
            subprocess.Popen([sys.executable, selected_script],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             close_fds=True)
        else:
            current_app.logger.info("Launching launcher.py with arg: %s", folder)
            subprocess.Popen([sys.executable, launcher_path, folder],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             close_fds=True)
    except Exception as e:
        current_app.logger.exception("Failed to spawn game process")
        flash(f"Failed to launch game: {e}", "danger")
        return redirect(url_for('games.index'))

    # Notify and return to games list
    display_name = game['name'] if isinstance(game, dict) and 'name' in game else getattr(game, "name", slug)
    flash(f"{display_name} launched.", "success")
    return redirect(url_for('games.index'))
