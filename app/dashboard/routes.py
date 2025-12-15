"""
Dashboard Routes
User dashboard and profile management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models import User, Post, GameScore
from app.utils.decorators import login_required, active_required
from app.utils.validators import validate_profile_data
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
@active_required
def index():
    """User dashboard home page"""
    user = User.get_by_id(session['user_id'])
    
    posts = Post.get_by_user(session['user_id'])
    recent_posts = posts[:5] if posts else []
    
    game_stats = GameScore.get_user_game_stats(session['user_id'])
    
    return render_template('dashboard/index.html', user=user, recent_posts=recent_posts, game_stats=game_stats)


@dashboard_bp.route('/profile')
@login_required
@active_required
def profile():
    """View user profile"""
    user = User.get_by_id(session['user_id'])
    return render_template('dashboard/profile.html', user=user)


@dashboard_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@active_required
def edit_profile():
    """Edit user profile"""
    user = User.get_by_id(session['user_id'])
    
    if request.method == 'POST':
        # Run validation before saving to database
        is_valid, field_errors, sanitized_data = validate_profile_data(request.form, require_password=False)
        
        if not is_valid:
            for field, error in field_errors.items():
                flash(error, 'danger')
            return render_template('dashboard/profile.html', user=user, errors=field_errors)
        
        # Save the changes to database
        if User.update_profile(
            session['user_id'],
            sanitized_data['firstname'],
            sanitized_data['middlename'],
            sanitized_data['lastname'],
            sanitized_data['birthday'],
            sanitized_data['contact']
        ):
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard.profile'))
        else:
            flash('Failed to update profile. Please try again.', 'danger')
    
    return render_template('dashboard/profile.html', user=user)


@dashboard_bp.route('/change-password', methods=['POST'])
@login_required
@active_required
def change_password():
    """Change user password (POST only). Renders profile page on error so modal shows."""
    user = User.get_by_id(session.get('user_id'))
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    current_password = request.form.get('current_password', '').strip()
    
    # Make sure they know their current password before changing
    if not current_password:
        flash('Current password is required!', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)
    
    if not User.verify_password(user, current_password):
        flash('Current password is incorrect!', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)

    # Check if new password meets requirements
    password_data = {
        'password': request.form.get('new_password', ''),
        'confirm_password': request.form.get('confirm_new_password', '')
    }
    
    is_valid, field_errors, sanitized_data = validate_profile_data(password_data, require_password=False)
    
    if 'password' in field_errors or 'confirm_password' in field_errors:
        for field, error in field_errors.items():
            if field in ['password', 'confirm_password']:
                flash(error, 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)

    # Everything looks good, update the password
    try:
        success = User.update_password(session['user_id'], sanitized_data['password'])
        if success:
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard.profile'))
        else:
            flash('Failed to change password. Please try again.', 'danger')
            return render_template('dashboard/profile.html', user=user, show_password_modal=True)
    except Exception as e:
        flash('An error occurred while updating your password. Please try again later.', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)
