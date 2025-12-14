"""
Email Utility
Handles sending OTP verification emails with rate limiting and cooldown
"""
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail
from app.models import OTPToken
import secrets
import hashlib
from datetime import datetime, timedelta
from app.database import insert


def send_otp_email(email, token):
    """
    Send OTP verification email
    
    Args:
        email: Recipient email address
        token: 6-digit numeric OTP token to send
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Create email message
        msg = Message(
            subject="Email Verification - UnBoreMe",
            recipients=[email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Email body (plain text)
        msg.body = f"""
Hello,

Thank you for registering! Please verify your email address to activate your account.

Your 6-digit verification code is:

{token}

Please enter this code on the verification page to complete your registration.

This code will expire in {current_app.config['OTP_EXPIRY_MINUTES']} minutes.

If you did not request this, please ignore this email.

Best regards,
Final Project Team
        """
        
        # Email body (HTML)
        msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .otp-code {{ background: white; padding: 25px; margin: 30px 0; 
                     font-size: 36px; font-weight: bold; text-align: center; 
                     letter-spacing: 8px; border-radius: 8px; color: #667eea; 
                     border: 3px solid #667eea; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        .warning {{ color: #ef4444; font-size: 14px; margin-top: 20px; 
                   background: #fee2e2; padding: 15px; border-radius: 8px; }}
        .instructions {{ background: #e0e7ff; padding: 15px; border-radius: 8px; 
                        margin: 20px 0; color: #3730a3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✉️ Email Verification</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Thank you for registering! Please verify your email address to activate your account.</p>
            
            <div class="instructions">
                <strong>📋 Your 6-digit verification code:</strong>
            </div>
            
            <div class="otp-code">{token}</div>
            
            <p style="text-align: center; font-size: 14px; color: #6b7280;">
                Enter this code on the verification page to complete your registration.
            </p>
            
            <div class="warning">
                ⚠️ <strong>Important:</strong> This code will expire in {current_app.config['OTP_EXPIRY_MINUTES']} minutes.
            </div>
            
            <p>If you did not request this verification, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 Final Project. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Send email
        mail.send(msg)
        return True, "Verification email sent successfully"
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False, f"Failed to send email: {str(e)}"


def send_otp_with_checks(email):
    """
    Send OTP with rate limiting and cooldown checks
    
    Args:
        email: Recipient email address
    
    Returns:
        tuple: (success: bool, message: str, cooldown_seconds: int)
    """
    # Check resend cooldown (5 minutes)
    cooldown_minutes = current_app.config['OTP_RESEND_COOLDOWN_MINUTES']
    can_resend, remaining = OTPToken.check_resend_cooldown(email, cooldown_minutes)
    
    if not can_resend:
        return False, f"Please wait {remaining} seconds before requesting another code", remaining
    
    # Check hourly limit
    hourly_limit = current_app.config['OTP_HOURLY_LIMIT']
    within_limit = OTPToken.check_hourly_limit(email, hourly_limit)
    
    if not within_limit:
        return False, f"Maximum {hourly_limit} verification emails per hour exceeded. Please try again later.", 0
    
    # Generate 6-digit numeric OTP
    expiry_minutes = current_app.config['OTP_EXPIRY_MINUTES']
    otp_code = str(secrets.randbelow(1000000)).zfill(6)  # Generate 6-digit numeric OTP
    
    # Hash the OTP for storage
    token_hash = hashlib.sha256(otp_code.encode()).hexdigest()
    expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
    
    # Store OTP in database
    query = """
        INSERT INTO otp_tokens (email, token_hash, created_at, expires_at, last_sent_at, attempts)
        VALUES (%s, %s, NOW(), %s, NOW(), 0)
    """
    token_id = insert(query, (email, token_hash, expires_at))
    
    # Send OTP email with 6-digit code
    success, message = send_otp_email(email, otp_code)
    
    if success:
        # Update last_sent timestamp
        OTPToken.update_last_sent(token_id)
        return True, message, 0
    else:
        return False, message, 0


def send_password_reset_email(email, otp_code):
    """
    Send password reset email with 6-digit OTP
    
    Args:
        email: Recipient email address
        otp_code: 6-digit numeric OTP code
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        msg = Message(
            subject="Password Reset Request - UnBoreMe",
            recipients=[email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.body = f"""
Hello,

You requested a password reset for your account.

Your 6-digit password reset code is:

{otp_code}

Please enter this code on the password reset page to continue.

This code will expire in 30 minutes.

If you did not request this, please ignore this email.

Best regards,
Final Project Team
        """
        
        msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .otp-code {{ background: white; padding: 25px; margin: 30px 0; 
                     font-size: 36px; font-weight: bold; text-align: center; 
                     letter-spacing: 8px; border-radius: 8px; color: #ef4444; 
                     border: 3px solid #ef4444; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        .warning {{ color: #ef4444; font-size: 14px; margin-top: 20px; 
                   background: #fee2e2; padding: 15px; border-radius: 8px; }}
        .instructions {{ background: #fef3c7; padding: 15px; border-radius: 8px; 
                        margin: 20px 0; color: #78350f; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Password Reset</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>You requested a password reset for your account.</p>
            
            <div class="instructions">
                <strong>🔑 Your 6-digit password reset code:</strong>
            </div>
            
            <div class="otp-code">{otp_code}</div>
            
            <p style="text-align: center; font-size: 14px; color: #6b7280;">
                Enter this code on the password reset page to continue.
            </p>
            
            <div class="warning">
                ⚠️ <strong>Important:</strong> This code will expire in 30 minutes.
            </div>
            
            <p>If you did not request this reset, please ignore this email and your password will remain unchanged.</p>
        </div>
        <div class="footer">
            <p>© 2024 Final Project. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        mail.send(msg)
        return True, "Password reset email sent successfully"
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False, f"Failed to send email: {str(e)}"
