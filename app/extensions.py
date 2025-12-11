"""
Flask Extensions
Initializes all Flask extensions used in the application
"""
from flask_mail import Mail
from flask_bcrypt import Bcrypt

# Initialize extensions
mail = Mail()
bcrypt = Bcrypt()


def init_extensions(app):
    """
    Initialize Flask extensions with app instance
    
    Args:
        app: Flask application instance
    """
    mail.init_app(app)
    bcrypt.init_app(app)
