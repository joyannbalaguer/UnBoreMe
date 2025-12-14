"""
Dashboard Routes
User dashboard and profile management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models import User, Post, GameScore
from app.utils.decorators import login_required, active_required
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
@active_required
def index():
    """User dashboard home page"""
    user = User.get_by_id(session['user_id'])
    
    # Get user's recent posts
    posts = Post.get_by_user(session['user_id'])
    recent_posts = posts[:5] if posts else []
    
    # Get user's game statistics
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
        firstname = request.form.get('firstname', '').strip()
        middlename = request.form.get('middlename', '').strip()
        lastname = request.form.get('lastname', '').strip()
        birthday = request.form.get('birthday', '').strip()
        contact = request.form.get('contact', '').strip()
        
        # Validation
        if not firstname or not lastname:
            flash('First name and last name are required!', 'danger')
            return render_template('dashboard/edit_profile.html', user=user)
        
        # Update profile
        if User.update_profile(session['user_id'], firstname, middlename, lastname, birthday, contact):
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard.profile'))
        else:
            flash('Failed to update profile. Please try again.', 'danger')
    
    return render_template('dashboard/edit_profile.html', user=user)


@dashboard_bp.route('/change-password', methods=['POST'])
@login_required
@active_required
def change_password():
    """Change user password (POST only). Renders profile page on error so modal shows."""
    # Read form values (names match your profile.html)
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_new_password', '').strip()

    # Load user
    user = User.get_by_id(session.get('user_id'))
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    # Basic validation
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required!', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)

    if len(new_password) < 8:
        flash('New password must be at least 8 characters long!', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)

    if new_password != confirm_password:
        flash('New passwords do not match!', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)

    # Verify current password
    if not User.verify_password(user, current_password):
        flash('Current password is incorrect!', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)

    # Update password
    try:
        success = User.update_password(session['user_id'], new_password)
        if success:
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard.profile'))
        else:
            flash('Failed to change password. Please try again.', 'danger')
            return render_template('dashboard/profile.html', user=user, show_password_modal=True)
    except Exception as e:
        # Optional: log exception server-side for debugging (do not expose details to user)
        # print("change_password error:", e)
        flash('An error occurred while updating your password. Please try again later.', 'danger')
        return render_template('dashboard/profile.html', user=user, show_password_modal=True)
