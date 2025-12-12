"""
Authentication Blueprint
Handles user registration, login, logout, OTP verification
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import User, OTPToken
from app.utils.decorators import guest_only, login_required
from app.utils.email_sender import send_otp_with_checks
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    """User registration with OTP verification"""
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        firstname = request.form.get('firstname', '').strip()
        middlename = request.form.get('middlename', '').strip()
        lastname = request.form.get('lastname', '').strip()
        birthday = request.form.get('birthday', '')
        contact = request.form.get('contact', '').strip()
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores')
        
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Invalid email address')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if not firstname or not lastname:
            errors.append('First name and last name are required')
        
        # Check if username exists
        if User.get_by_username(username):
            errors.append('Username already exists')
        
        # Check if email exists
        if User.get_by_email(email):
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create user (inactive until email verified)
        try:
            user_id = User.create(
                username=username,
                email=email,
                password=password,
                firstname=firstname,
                middlename=middlename,
                lastname=lastname,
                birthday=birthday if birthday else None,
                contact=contact,
                role='user',
                is_active=False
            )
            
            # Send OTP email
            success, message, cooldown = send_otp_with_checks(email)
            
            if success:
                flash('Registration successful! Please check your email for verification code.', 'success')
                # Store email in session for verification page
                session['pending_verification_email'] = email
                return redirect(url_for('auth.verify_email'))
            else:
                flash(f'Registration successful, but failed to send verification email: {message}', 'warning')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('auth/login.html')
        
        # Get user
        user = User.get_by_username(username)
        
        if not user:
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html')
        
        # Verify password
        if not User.verify_password(user, password):
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html')
        
        # Check if account is active
        if not user['is_active']:
            flash('Your account is not active. Please verify your email or contact an administrator.', 'warning')
            session['pending_verification_email'] = user['email']
            return redirect(url_for('auth.verify_email'))
        
        # Login successful - create session
        session['loggedin'] = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['is_active'] = user['is_active']
        session.permanent = True
        
        flash(f'Welcome back, {user["firstname"]}!', 'success')
        
        # Redirect based on role
        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Email verification with OTP"""
    email = request.args.get('email') or session.get('pending_verification_email')
    
    if not email:
        flash('No email found for verification', 'danger')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        
        if not token:
            flash('Please enter the verification code', 'danger')
            return render_template('auth/verify_email.html', email=email)
        
        # Verify token
        if OTPToken.verify(email, token):
            # Activate user account
            user = User.get_by_email(email)
            if user:
                User.activate(user['id'])
                OTPToken.delete_by_email(email)
                
                # Clear pending verification
                session.pop('pending_verification_email', None)
                
                flash('Email verified successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('User not found', 'danger')
        else:
            # Increment failed attempts
            otp_record = OTPToken.get_by_email(email)
            if otp_record:
                OTPToken.increment_attempts(otp_record['id'])
                attempts = otp_record['attempts'] + 1
                
                if attempts >= 3:
                    flash('Too many failed attempts. Please request a new code.', 'danger')
                else:
                    flash(f'Invalid or expired verification code. Attempts: {attempts}/3', 'danger')
            else:
                flash('Invalid or expired verification code', 'danger')
        
        return render_template('auth/verify_email.html', email=email)
    
    return render_template('auth/verify_email.html', email=email)


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP with cooldown check"""
    email = request.form.get('email') or session.get('pending_verification_email')
    
    if not email:
        return jsonify({'success': False, 'message': 'No email provided'}), 400
    
    success, message, cooldown = send_otp_with_checks(email)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message, 'cooldown': cooldown}), 429


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@guest_only
def forgot_password():
    """Forgot password - request reset"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address', 'danger')
            return render_template('auth/forgot_password.html')
        
        user = User.get_by_email(email)
        
        # Always show success message to prevent email enumeration
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        
        if user:
            # Send reset email
            from app.utils.email_sender import send_password_reset_email
            token, token_id = OTPToken.create(email, expiry_minutes=30)
            send_password_reset_email(email, token)
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@guest_only
def reset_password():
    """Reset password with token"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if not token or not email:
        flash('Invalid reset link', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('auth/reset_password.html', token=token, email=email)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/reset_password.html', token=token, email=email)
        
        # Verify token
        if OTPToken.verify(email, token):
            user = User.get_by_email(email)
            if user:
                User.update_password(user['id'], new_password)
                OTPToken.delete_by_email(email)
                flash('Password reset successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('User not found', 'danger')
        else:
            flash('Invalid or expired reset token', 'danger')
        
        return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/reset_password.html', token=token, email=email)
