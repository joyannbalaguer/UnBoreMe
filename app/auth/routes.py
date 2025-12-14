"""
Authentication Blueprint
Handles user registration, login, logout, OTP verification
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import User, OTPToken
from app.utils.decorators import guest_only, login_required
from app.utils.email_sender import send_otp_with_checks
import re
from datetime import datetime, date

auth_bp = Blueprint('auth', __name__)


def validate_registration_data(form_data):
    
    field_errors = {}
    
    # Extract and sanitize form data
    username = form_data.get('username', '').strip()
    email = form_data.get('email', '').strip().lower()
    password = form_data.get('password', '')
    confirm_password = form_data.get('confirm_password', '')
    firstname = form_data.get('firstname', '').strip()
    middlename = form_data.get('middlename', '').strip()
    lastname = form_data.get('lastname', '').strip()
    birthday = form_data.get('birthday', '').strip()
    contact = form_data.get('contact', '').strip()
    
    #  USERNAME VALIDATION 
    if not username:
        field_errors['username'] = 'Username is required'
    elif not (4 <= len(username) <= 32):
        field_errors['username'] = 'Username must be between 4 and 32 characters long'
    elif not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        field_errors['username'] = 'Username must start with a letter and contain only letters, numbers, and underscores'
    elif username.lower() in ['admin', 'root', 'system', 'administrator', 'test', 'user', 'guest', 'null', 'undefined']:
        field_errors['username'] = 'This username is reserved and cannot be used'
    elif '__' in username:
        field_errors['username'] = 'Username cannot contain consecutive underscores'
    elif User.get_by_username(username):
        field_errors['username'] = 'Username already exists. Please choose another one'
    
    #  EMAIL VALIDATION
    if not email:
        field_errors['email'] = 'Email address is required'
    elif not (5 <= len(email) <= 40):  
        field_errors['email'] = 'Email address must be between 5 and 40 characters long'
    else:
        email_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._+-]*@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            field_errors['email'] = 'Invalid email format. Please enter a valid email address'
        elif '..' in email or email.startswith('.') or '@.' in email:
            field_errors['email'] = 'Email contains invalid character sequences'
        else:
            domain = email.split('@')[1]

            disposable_domains = {
                'tempmail.com',
                '10minutemail.com',
                'guerrillamail.com',
                'mailinator.com',
                'throwawaymail.com'
            }

            if domain in disposable_domains:
                field_errors['email'] = 'Disposable email addresses are not allowed'

            elif User.get_by_email(email):
                field_errors['email'] = 'Email address already registered. Please use another email or login'


    
    #  PASSWORD VALIDATION
    if not password:
        field_errors['password'] = 'Password is required'
    elif len(password) < 8:
        field_errors['password'] = 'Password must be at least 12 characters long'
    elif len(password) > 128:
        field_errors['password'] = 'Password is too long (maximum 128 characters)'
    else:
        
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password))
        
        if not has_upper:
            field_errors['password'] = 'Password must contain at least one uppercase letter'
        elif not has_lower:
            field_errors['password'] = 'Password must contain at least one lowercase letter'
        elif not has_digit:
            field_errors['password'] = 'Password must contain at least one number'
        elif not has_special:
            field_errors['password'] = 'Password must contain at least one special character (!@#$%^&*-_+=)'
       
    
    #  CONFIRM PASSWORD VALIDATION 
    if not confirm_password:
        field_errors['confirm_password'] = 'Please confirm your password'
    elif password != confirm_password:
        field_errors['confirm_password'] = 'Passwords do not match'
    
    #  FIRST NAME VALIDATION
    if not firstname:
        field_errors['firstname'] = 'First name is required'
    elif not (2 <= len(firstname) <= 50):
        field_errors['firstname'] = 'First name must be between 2 and 50 characters long'
    elif firstname != firstname.strip():
        field_errors['firstname'] = 'First name must not start or end with a space'
    elif not re.match(r'^[a-zA-Z\s\'-]+$', firstname):
        field_errors['firstname'] = (
        'First name can only contain letters, spaces, hyphens, and apostrophes'
    )
    elif re.search(r'(.)\1{2,}', firstname):
        field_errors['firstname'] = 'First name contains too many repeated characters'
    elif re.search(r'\s{2,}', firstname):
        field_errors['firstname'] = 'First name contains excessive spacing'

    #  MIDDLE NAME VALIDATION (optional)
    if middlename:
        if len(middlename) > 50:
            field_errors['middlename'] = 'Middle name is too long (maximum 50 characters)'

        elif middlename != middlename.strip():
            field_errors['middlename'] = 'Middle name must not start or end with a space'

        elif not re.match(r'^[a-zA-Z\s\'-]+$', middlename):
            field_errors['middlename'] = (
                'Middle name can only contain letters, spaces, hyphens, and apostrophes'
            )

        elif re.search(r'(.)\1{2,}', middlename):
            field_errors['middlename'] = 'Middle name contains too many repeated characters'

        elif re.search(r'\s{2,}', middlename):
            field_errors['middlename'] = 'Middle name contains excessive spacing'


    #  LAST NAME VALIDATION
    if not lastname:
        field_errors['lastname'] = 'Last name is required'
    elif len(lastname) < 2:
        field_errors['lastname'] = 'Last name must be at least 2 characters long'
    elif len(lastname) > 50:
        field_errors['lastname'] = 'Last name is too long (maximum 50 characters)'
    elif lastname != lastname.strip():
        field_errors['lastname'] = 'Last name must not start or end with a space'
    elif not re.match(r'^[a-zA-Z\s\'-]+$', lastname):
        field_errors['lastname'] = (
            'Last name can only contain letters, spaces, hyphens, and apostrophes'
        )
    elif re.search(r"([\'\-])\1+", lastname):
        field_errors['lastname'] = 'Last name contains consecutive punctuation characters'
    elif re.search(r'(.)\1{2,}', lastname):
        field_errors['lastname'] = 'Last name contains too many repeated characters'
    elif re.search(r'\s{2,}', lastname):
        field_errors['lastname'] = 'Last name contains excessive spacing'

    
    #  AGE/BIRTHDAY VALIDATION
    if birthday:
        try:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if birth_date > today:
                field_errors['birthday'] = 'Birthday cannot be in the future'
            elif age < 13:
                field_errors['birthday'] = 'You must be at least 13-100 years old to register'
            elif age > 90:
                field_errors['birthday'] = 'Invalid birth date. Please verify your date of birth'
        except ValueError:
            field_errors['birthday'] = 'Invalid date format. Please use YYYY-MM-DD format'
    
    #  CONTACT NUMBER VALIDATION
    if contact:
        if not re.match(r'^09\d{9}$', contact):
            field_errors['contact'] = 'Contact number must be in the format 09XXXXXXXXX'
        elif re.search(r'(\d)\1{3}', contact):
            field_errors['contact'] = 'Contact number contains too many repeated digits'

    
    is_valid = len(field_errors) == 0
    
    return is_valid, field_errors, {
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirm_password,
        'firstname': firstname,
        'middlename': middlename,
        'lastname': lastname,
        'birthday': birthday,
        'contact': contact
    }


@auth_bp.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    """User registration with enterprise-level validation"""
    if request.method == 'POST':
        # Validate registration data
        is_valid, field_errors, form_data = validate_registration_data(request.form)
        
        if not is_valid:
            # Return to form with errors and preserved data
            return render_template('auth/register.html', 
                                 errors=field_errors, 
                                 form_data=form_data)
        
        # Create user (inactive until email verified)
        try:
            user_id = User.create(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password'],
                firstname=form_data['firstname'],
                middlename=form_data['middlename'],
                lastname=form_data['lastname'],
                birthday=form_data['birthday'] if form_data['birthday'] else None,
                contact=form_data['contact'],
                role='user',
                is_active=False
            )
            
            # Send OTP email
            success, message, cooldown = send_otp_with_checks(form_data['email'])
            
            if success:
                flash('Registration successful! Please check your email for verification code.', 'success')
                # Store email in session for verification page
                session['pending_verification_email'] = form_data['email']
                return redirect(url_for('auth.verify_email'))
            else:
                flash(f'Registration successful, but failed to send verification email: {message}', 'warning')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('auth/register.html', 
                                 errors={}, 
                                 form_data=form_data)
    
    return render_template('auth/register.html', errors={}, form_data={})


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
    """Forgot password - request reset with 6-digit OTP"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address', 'danger')
            return render_template('auth/forgot_password.html')
        
        user = User.get_by_email(email)
        
        if user:
            # Generate 6-digit OTP
            import secrets
            import hashlib
            from datetime import datetime, timedelta
            from app.database import insert
            
            otp_code = str(secrets.randbelow(1000000)).zfill(6)
            token_hash = hashlib.sha256(otp_code.encode()).hexdigest()
            expires_at = datetime.now() + timedelta(minutes=30)
            
            # Store OTP in database
            query = """
                INSERT INTO otp_tokens (email, token_hash, created_at, expires_at, last_sent_at, attempts)
                VALUES (%s, %s, NOW(), %s, NOW(), 0)
            """
            insert(query, (email, token_hash, expires_at))
            
            # Send reset email with OTP
            from app.utils.email_sender import send_password_reset_email
            send_password_reset_email(email, otp_code)
            
            # Store email in session for reset page
            session['pending_password_reset_email'] = email
            flash('A 6-digit password reset code has been sent to your email.', 'info')
            return redirect(url_for('auth.reset_password'))
        else:
            # For security, still redirect but don't store email
            flash('If an account exists with that email, a password reset code has been sent.', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@guest_only
def reset_password():
    """Reset password with 6-digit OTP"""
    email = session.get('pending_password_reset_email')
    
    if not email:
        flash('Please request a password reset first', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code', '').strip()
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate OTP code
        if not otp_code:
            flash('Please enter the 6-digit verification code', 'danger')
            return render_template('auth/reset_password.html', email=email)
        
        if len(otp_code) != 6 or not otp_code.isdigit():
            flash('Verification code must be 6 digits', 'danger')
            return render_template('auth/reset_password.html', email=email)
        
        # Validate password
        if not new_password or len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('auth/reset_password.html', email=email)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/reset_password.html', email=email)
        
        # Verify OTP
        if OTPToken.verify(email, otp_code):
            user = User.get_by_email(email)
            if user:
                User.update_password(user['id'], new_password)
                OTPToken.delete_by_email(email)
                session.pop('pending_password_reset_email', None)
                flash('Password reset successfully! You can now log in.', 'success')
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
                    flash('Too many failed attempts. Please request a new reset code.', 'danger')
                    session.pop('pending_password_reset_email', None)
                    return redirect(url_for('auth.forgot_password'))
                else:
                    flash(f'Invalid or expired verification code. Attempts: {attempts}/3', 'danger')
            else:
                flash('Invalid or expired verification code', 'danger')
        
        return render_template('auth/reset_password.html', email=email)
    
    return render_template('auth/reset_password.html', email=email)
