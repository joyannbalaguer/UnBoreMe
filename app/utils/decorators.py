"""
Authentication Decorators
Provides decorators for route protection
"""
from functools import wraps
from flask import session, redirect, url_for, flash, abort


def login_required(f):
    """
    Decorator to require login for a route
    Redirects to login page if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session.get('loggedin'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role for a route
    Returns 403 if user is not an admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session.get('loggedin'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def active_required(f):
    """
    Decorator to require active account status
    Redirects if account is not activated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session.get('loggedin'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not session.get('is_active'):
            flash('Your account is not active. Please contact an administrator.', 'warning')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    """
    Decorator to allow only guests (not logged in users)
    Redirects to dashboard if user is already logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' in session and session.get('loggedin'):
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
