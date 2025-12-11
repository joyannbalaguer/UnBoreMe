"""
Flask Application Factory
Creates and configures the Flask application instance
"""
from flask import Flask
import os
from app.config import config
from app.extensions import init_extensions
from app.database import init_db


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize database
    init_db(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register template globals
    register_template_globals(app)
    
    return app


def register_blueprints(app):
    """Register application blueprints"""
    
    # Main routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Auth routes
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Dashboard routes
    from app.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Admin routes
    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Blog routes
    from app.blog.routes import blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')
    
    # Games routes
    from app.games.routes import games_bp
    app.register_blueprint(games_bp, url_prefix='/games')


def register_error_handlers(app):
    """Register error handlers"""
    
    from flask import render_template
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


def register_template_filters(app):
    """Register custom Jinja2 template filters"""
    
    from datetime import datetime
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        """Format a datetime object"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%Y-%m-%d'):
        """Format a date"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('timeago')
    def timeago(value):
        """Convert datetime to 'time ago' format"""
        if value is None:
            return ""
        
        now = datetime.now()
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        
        diff = now - value
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return value.strftime('%Y-%m-%d')


def register_template_globals(app):
    """Register global variables available in all templates"""
    
    from datetime import datetime
    
    @app.context_processor
    def inject_now():
        """Make datetime.now available in all templates"""
        return {'now': datetime.now}
