"""
Admin Routes
Administrative dashboard and user management
Patched: blueprint declared before heavy imports; relative imports to keep package context;
expose root endpoint name 'dashboard' so templates using admin.dashboard resolve.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, abort
from jinja2 import TemplateNotFound

# Create blueprint immediately so import-time failures later won't prevent it from existing
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Use relative imports to reduce circular-import risk (module is inside package 'app')
from ..models import User, Game, UserGame, AuditLog, Post
from ..utils.decorators import login_required, active_required, admin_required
from ..utils.validators import validate_profile_data


@admin_bp.route('/', endpoint='dashboard')
@login_required
@active_required
@admin_required
def index():
    """Admin dashboard home page"""
    users = User.get_all()
    games = Game.get_all()

    # Count statistics
    total_users = len(users) if users else 0
    active_users = len([u for u in users if u.get('is_active')]) if users else 0
    total_games = len(games) if games else 0

    # Get recent audit logs
    recent_logs = AuditLog.get_recent(10)

    return render_template(
        'admin/index.html',
        total_users=total_users,
        active_users=active_users,
        total_games=total_games,
        recent_logs=recent_logs
    )


@admin_bp.route('/users')
@login_required
@active_required
@admin_required
def users():
    """List all users"""
    users_list = User.get_all()
    return render_template('admin/users.html', users=users_list)


@admin_bp.route('/users/view/<int:user_id>')
@login_required
@active_required
@admin_required
def view_user(user_id):
    """View user details"""
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.users'))

    # Get user's games
    user_games = UserGame.get_user_games(user_id)

    # Get user's posts
    user_posts = Post.get_by_user(user_id)

    return render_template('admin/view_user.html', user=user, games=user_games, posts=user_posts)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@active_required
@admin_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        firstname = request.form.get('firstname', '').strip()
        middlename = request.form.get('middlename', '').strip()
        lastname = request.form.get('lastname', '').strip()
        birthday = request.form.get('birthday', '').strip()
        contact = request.form.get('contact', '').strip()
        role = request.form.get('role', 'user')
        is_active = request.form.get('is_active') == 'on'

        # Validation
        if not username or not email or not password or not firstname or not lastname:
            flash('Username, email, password, first name, and last name are required!', 'danger')
            return render_template('admin/create_user.html')

        # Check if username exists
        if User.get_by_username(username):
            flash('Username already exists!', 'danger')
            return render_template('admin/create_user.html')

        # Check if email exists
        if User.get_by_email(email):
            flash('Email already exists!', 'danger')
            return render_template('admin/create_user.html')

        # Create user
        user_id = User.create(username, email, password, firstname, lastname,
                             middlename, birthday, contact, role, is_active)

        if user_id:
            # Log action
            AuditLog.log(session['user_id'], 'USER_CREATE', f'Created user: {username}')
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('Failed to create user. Please try again.', 'danger')

    return render_template('admin/create_user.html')


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@active_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.users'))

    if request.method == 'POST':
        # Validate profile data using shared validation
        is_valid, field_errors, sanitized_data = validate_profile_data(request.form, require_password=False)
        
        if not is_valid:
            # Show validation errors
            for field, error in field_errors.items():
                flash(error, 'danger')
            return render_template('admin/edit_user.html', user=user, errors=field_errors)
        
        # Update user with sanitized data
        if User.update_profile(
            user_id,
            sanitized_data['firstname'],
            sanitized_data['middlename'],
            sanitized_data['lastname'],
            sanitized_data['birthday'],
            sanitized_data['contact']
        ):
            # Log action
            AuditLog.log(session['user_id'], 'USER_UPDATE', f"Updated user: {user.get('username')}")
            flash(f'User {user.get("username")} updated successfully!', 'success')
            return redirect(url_for('admin.view_user', user_id=user_id))
        else:
            flash('Failed to update user. Please try again.', 'danger')

    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/users/activate/<int:user_id>')
@login_required
@active_required
@admin_required
def activate_user(user_id):
    """Activate user account"""
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.users'))

    if User.activate(user_id):
        # Log action
        AuditLog.log(session['user_id'], 'USER_ACTIVATE', f'Activated user: {user.get("username")}')
        flash(f'User {user.get("username")} activated successfully!', 'success')
    else:
        flash('Failed to activate user.', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/deactivate/<int:user_id>')
@login_required
@active_required
@admin_required
def deactivate_user(user_id):
    """Deactivate user account"""
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.users'))

    # Prevent deactivating self
    if user_id == session['user_id']:
        flash('You cannot deactivate your own account!', 'danger')
        return redirect(url_for('admin.users'))

    if User.deactivate(user_id):
        # Log action
        AuditLog.log(session['user_id'], 'USER_DEACTIVATE', f'Deactivated user: {user.get("username")}')
        flash(f'User {user.get("username")} deactivated successfully!', 'success')
    else:
        flash('Failed to deactivate user.', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@active_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.users'))

    # Prevent deleting self
    if user_id == session['user_id']:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))

    username = user.get('username')
    if User.delete_user(user_id):
        # Log action
        AuditLog.log(session['user_id'], 'USER_DELETE', f'Deleted user: {username}')
        flash(f'User {username} deleted successfully!', 'success')
    else:
        flash('Failed to delete user.', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/games/play/<slug>')
@login_required
@active_required
@admin_required
def play_game(slug):
    """
    Serve embed-only game page (no header/footer) for iframe viewing.
    Returns templates/games/embed/<slug>.html
    """
    try:
        # This will render templates/games/embed/<slug>.html
        return render_template(f'games/embed/{slug}.html', slug=slug)
    except TemplateNotFound:
        abort(404)


@admin_bp.route('/games/toggle/<int:user_id>/<int:game_id>', methods=['POST'])
@login_required
@active_required
@admin_required
def toggle_game(user_id, game_id):
    """Enable/disable game for user"""
    user = User.get_by_id(user_id)
    game = Game.get_by_id(game_id)

    if not user or not game:
        flash('User or game not found!', 'danger')
        return redirect(url_for('admin.users'))

    action = request.form.get('action')

    if action == 'enable':
        if UserGame.enable_game(user_id, game_id):
            AuditLog.log(session['user_id'], 'GAME_ENABLE',
                        f'Enabled game "{game.get("name")}" for user {user.get("username")}')
            flash(f'Game "{game.get("name")}" enabled for {user.get("username")}!', 'success')
        else:
            flash('Failed to enable game.', 'danger')
    elif action == 'disable':
        if UserGame.disable_game(user_id, game_id):
            AuditLog.log(session['user_id'], 'GAME_DISABLE',
                        f'Disabled game "{game.get("name")}" for user {user.get("username")}')
            flash(f'Game "{game.get("name")}" disabled for {user.get("username")}', 'success')
        else:
            flash('Failed to disable game.', 'danger')

    return redirect(url_for('admin.view_user', user_id=user_id))


@admin_bp.route('/audit-logs')
@login_required
@active_required
@admin_required
def audit_logs():
    """View audit logs"""
    logs = AuditLog.get_recent(100)
    return render_template('admin/audit_logs.html', logs=logs)
