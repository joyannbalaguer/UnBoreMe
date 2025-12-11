"""
Email Utility
Handles sending OTP verification emails with rate limiting and cooldown
"""
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail
from app.models import OTPToken


def send_otp_email(email, token):
    """
    Send OTP verification email
    
    Args:
        email: Recipient email address
        token: OTP token to send
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Create verification URL (for web-based verification)
        # In production, use actual domain
        verification_url = f"http://localhost:5000/auth/verify-email?token={token}&email={email}"
        
        # Create email message
        msg = Message(
            subject="Email Verification - Final Project",
            recipients=[email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Email body (plain text)
        msg.body = f"""
Hello,

Thank you for registering! Please verify your email address to activate your account.

Your verification token is: {token}

Or click the link below:
{verification_url}

This token will expire in {current_app.config['OTP_EXPIRY_MINUTES']} minutes.

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
        .token {{ background: white; padding: 15px; margin: 20px 0; 
                 font-size: 24px; font-weight: bold; text-align: center; 
                 letter-spacing: 3px; border-radius: 8px; color: #667eea; 
                 border: 2px dashed #667eea; }}
        .button {{ display: inline-block; background: #667eea; color: white; 
                  padding: 12px 30px; text-decoration: none; border-radius: 8px; 
                  margin: 20px 0; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        .warning {{ color: #ef4444; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Verification</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Thank you for registering! Please verify your email address to activate your account.</p>
            
            <div class="token">{token}</div>
            
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email</a>
            </p>
            
            <p class="warning">
                ⚠️ This token will expire in {current_app.config['OTP_EXPIRY_MINUTES']} minutes.
            </p>
            
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
    
    # Generate and send OTP
    expiry_minutes = current_app.config['OTP_EXPIRY_MINUTES']
    token, token_id = OTPToken.create(email, expiry_minutes)
    
    success, message = send_otp_email(email, token)
    
    if success:
        # Update last_sent timestamp
        OTPToken.update_last_sent(token_id)
        return True, message, 0
    else:
        return False, message, 0


def send_password_reset_email(email, reset_token):
    """
    Send password reset email
    
    Args:
        email: Recipient email address
        reset_token: Password reset token
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        reset_url = f"http://localhost:5000/auth/reset-password?token={reset_token}&email={email}"
        
        msg = Message(
            subject="Password Reset Request - Final Project",
            recipients=[email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.body = f"""
Hello,

You requested a password reset for your account.

Your reset token is: {reset_token}

Or click the link below:
{reset_url}

This token will expire in 30 minutes.

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
        .token {{ background: white; padding: 15px; margin: 20px 0; 
                 font-size: 20px; font-weight: bold; text-align: center; 
                 letter-spacing: 2px; border-radius: 8px; color: #ef4444; 
                 border: 2px dashed #ef4444; }}
        .button {{ display: inline-block; background: #ef4444; color: white; 
                  padding: 12px 30px; text-decoration: none; border-radius: 8px; 
                  margin: 20px 0; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        .warning {{ color: #ef4444; font-size: 14px; margin-top: 20px; }}
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
            
            <div class="token">{reset_token}</div>
            
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            
            <p class="warning">
                ⚠️ This token will expire in 30 minutes.
            </p>
            
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
