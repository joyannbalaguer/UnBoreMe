import re
from datetime import datetime, date


def validate_profile_data(form_data, require_password=False):
    """
    Validate profile edit data (used by both user and admin edit flows)
    
    Args:
        form_data: Dictionary containing form fields
        require_password: Boolean indicating if password fields are required
    
    Returns:
        tuple: (is_valid, field_errors, sanitized_data)
    """
    field_errors = {}
    
    # Extract and sanitize form data
    firstname = form_data.get('firstname', '').strip()
    middlename = form_data.get('middlename', '').strip()
    lastname = form_data.get('lastname', '').strip()
    birthday = form_data.get('birthday', '').strip()
    contact = form_data.get('contact', '').strip()
    password = form_data.get('password', '') if require_password else form_data.get('password', '')
    confirm_password = form_data.get('confirm_password', '') if require_password else form_data.get('confirm_password', '')
    
    # FIRST NAME VALIDATION
    if not firstname:
        field_errors['firstname'] = 'First name is required'
    elif not (2 <= len(firstname) <= 50):
        field_errors['firstname'] = 'First name must be between 2 and 50 characters long'
    elif firstname != firstname.strip():
        field_errors['firstname'] = 'First name must not start or end with a space'
    elif not re.match(r'^[a-zA-Z\s\'-]+$', firstname):
        field_errors['firstname'] = 'First name can only contain letters, spaces, hyphens, and apostrophes'
    elif re.search(r'(.)\1{2,}', firstname):
        field_errors['firstname'] = 'First name contains too many repeated characters'
    elif re.search(r'\s{2,}', firstname):
        field_errors['firstname'] = 'First name contains excessive spacing'
    
    # MIDDLE NAME VALIDATION (optional)
    if middlename:
        if len(middlename) > 50:
            field_errors['middlename'] = 'Middle name is too long (maximum 50 characters)'
        elif middlename != middlename.strip():
            field_errors['middlename'] = 'Middle name must not start or end with a space'
        elif not re.match(r'^[a-zA-Z\s\'-]+$', middlename):
            field_errors['middlename'] = 'Middle name can only contain letters, spaces, hyphens, and apostrophes'
        elif re.search(r'(.)\1{2,}', middlename):
            field_errors['middlename'] = 'Middle name contains too many repeated characters'
        elif re.search(r'\s{2,}', middlename):
            field_errors['middlename'] = 'Middle name contains excessive spacing'
    
    # LAST NAME VALIDATION
    if not lastname:
        field_errors['lastname'] = 'Last name is required'
    elif len(lastname) < 2:
        field_errors['lastname'] = 'Last name must be at least 2 characters long'
    elif len(lastname) > 50:
        field_errors['lastname'] = 'Last name is too long (maximum 50 characters)'
    elif lastname != lastname.strip():
        field_errors['lastname'] = 'Last name must not start or end with a space'
    elif not re.match(r'^[a-zA-Z\s\'-]+$', lastname):
        field_errors['lastname'] = 'Last name can only contain letters, spaces, hyphens, and apostrophes'
    elif re.search(r"([\'\-])\1+", lastname):
        field_errors['lastname'] = 'Last name contains consecutive punctuation characters'
    elif re.search(r'(.)\1{2,}', lastname):
        field_errors['lastname'] = 'Last name contains too many repeated characters'
    elif re.search(r'\s{2,}', lastname):
        field_errors['lastname'] = 'Last name contains excessive spacing'
    
    # AGE/BIRTHDAY VALIDATION
    if birthday:
        try:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if birth_date > today:
                field_errors['birthday'] = 'Birthday cannot be in the future'
            elif age < 13:
                field_errors['birthday'] = 'You must be at least 13-100 years old'
            elif age > 100:
                field_errors['birthday'] = 'Invalid birth date. Please verify your date of birth'
        except ValueError:
            field_errors['birthday'] = 'Invalid date format. Please use YYYY-MM-DD format'
    
    # CONTACT NUMBER VALIDATION
    if contact:
        if not re.match(r'^09\d{9}$', contact):
            field_errors['contact'] = 'Contact number must be in the format 09XXXXXXXXX'
        elif re.search(r'(\d)\1{3,}', contact):
            field_errors['contact'] = 'Contact number contains too many repeated digits'
    
    # PASSWORD VALIDATION (only when changing password)
    if password or confirm_password:
        if not password:
            field_errors['password'] = 'Password is required'
        elif len(password) < 8:
            field_errors['password'] = 'Password must be at least 8 characters long'
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
        
        # CONFIRM PASSWORD VALIDATION
        if not confirm_password:
            field_errors['confirm_password'] = 'Please confirm your password'
        elif password != confirm_password:
            field_errors['confirm_password'] = 'Passwords do not match'
    
    is_valid = len(field_errors) == 0
    
    sanitized_data = {
        'firstname': firstname,
        'middlename': middlename,
        'lastname': lastname,
        'birthday': birthday,
        'contact': contact,
        'password': password,
        'confirm_password': confirm_password
    }
    
    return is_valid, field_errors, sanitized_data
