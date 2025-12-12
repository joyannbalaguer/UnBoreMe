"""
Database Models
Defines model classes for database operations using raw SQL with PyMySQL
"""
from datetime import datetime, timedelta
from app.database import get_one, get_all, insert, update, delete
from app.extensions import bcrypt
import secrets
import hashlib


class User:
    """User model - represents a user account"""
    
    @staticmethod
    def create(username, email, password, firstname, lastname, middlename='', 
               birthday=None, contact='', role='user', is_active=False):
        """Create a new user"""
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Calculate age if birthday provided
        age = None
        if birthday:
            today = datetime.today()
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        query = """
            INSERT INTO users (username, email, password_hash, firstname, middlename, 
                             lastname, birthday, age, contact, role, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (username, email, password_hash, firstname, middlename, 
                 lastname, birthday, age, contact, role, is_active)
        return insert(query, params)
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        return get_one(query, (user_id,))
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        return get_one(query, (username,))
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        return get_one(query, (email,))
    
    @staticmethod
    def get_all():
        """Get all users"""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return get_all(query)
    
    @staticmethod
    def update_profile(user_id, firstname, middlename, lastname, birthday, contact):
        """Update user profile"""
        # Calculate age
        age = None
        if birthday:
            today = datetime.today()
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        query = """
            UPDATE users 
            SET firstname = %s, middlename = %s, lastname = %s, 
                birthday = %s, age = %s, contact = %s, updated_at = NOW()
            WHERE id = %s
        """
        params = (firstname, middlename, lastname, birthday, age, contact, user_id)
        return update(query, params)
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        query = "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s"
        return update(query, (password_hash, user_id))
    
    @staticmethod
    def activate(user_id):
        """Activate user account"""
        query = "UPDATE users SET is_active = 1, updated_at = NOW() WHERE id = %s"
        return update(query, (user_id,))
    
    @staticmethod
    def deactivate(user_id):
        """Deactivate user account"""
        query = "UPDATE users SET is_active = 0, updated_at = NOW() WHERE id = %s"
        return update(query, (user_id,))
    
    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        query = "DELETE FROM users WHERE id = %s"
        return delete(query, (user_id,))
    
    @staticmethod
    def verify_password(user, password):
        """Verify user password"""
        if not user:
            return False
        return bcrypt.check_password_hash(user['password_hash'], password)


class OTPToken:
    """OTP Token model - handles email verification tokens"""
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token):
        """Hash token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def create(email, expiry_minutes=10):
        """Create new OTP token"""
        token = OTPToken.generate_token()
        token_hash = OTPToken.hash_token(token)
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        
        query = """
            INSERT INTO otp_tokens (email, token_hash, created_at, expires_at, last_sent_at, attempts)
            VALUES (%s, %s, NOW(), %s, NOW(), 0)
        """
        token_id = insert(query, (email, token_hash, expires_at))
        return token, token_id
    
    @staticmethod
    def get_by_email(email):
        """Get latest OTP token for email"""
        query = """
            SELECT * FROM otp_tokens 
            WHERE email = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        return get_one(query, (email,))
    
    @staticmethod
    def verify(email, token):
        """Verify OTP token"""
        token_hash = OTPToken.hash_token(token)
        query = """
            SELECT * FROM otp_tokens 
            WHERE email = %s AND token_hash = %s 
            AND expires_at > NOW()
            ORDER BY created_at DESC 
            LIMIT 1
        """
        result = get_one(query, (email, token_hash))
        return result is not None
    
    @staticmethod
    def increment_attempts(token_id):
        """Increment failed attempts counter"""
        query = "UPDATE otp_tokens SET attempts = attempts + 1 WHERE id = %s"
        return update(query, (token_id,))
    
    @staticmethod
    def update_last_sent(token_id):
        """Update last sent timestamp"""
        query = "UPDATE otp_tokens SET last_sent_at = NOW() WHERE id = %s"
        return update(query, (token_id,))
    
    @staticmethod
    def check_resend_cooldown(email, cooldown_minutes=5):
        """Check if resend cooldown has passed"""
        query = """
            SELECT last_sent_at FROM otp_tokens 
            WHERE email = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        result = get_one(query, (email,))
        if not result or not result['last_sent_at']:
            return True, 0
        
        time_elapsed = datetime.now() - result['last_sent_at']
        cooldown = timedelta(minutes=cooldown_minutes)
        
        if time_elapsed < cooldown:
            remaining = (cooldown - time_elapsed).total_seconds()
            return False, int(remaining)
        
        return True, 0
    
    @staticmethod
    def check_hourly_limit(email, limit=3):
        """Check if hourly send limit exceeded"""
        query = """
            SELECT COUNT(*) as count FROM otp_tokens 
            WHERE email = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """
        result = get_one(query, (email,))
        return result['count'] < limit
    
    @staticmethod
    def delete_by_email(email):
        """Delete all OTP tokens for email"""
        query = "DELETE FROM otp_tokens WHERE email = %s"
        return delete(query, (email,))


class Game:
    """Game model - represents available games"""
    
    @staticmethod
    def create(name, slug, description, enabled_by_default=True):
        """Create new game"""
        query = """
            INSERT INTO games (name, slug, description, enabled_by_default)
            VALUES (%s, %s, %s, %s)
        """
        return insert(query, (name, slug, description, enabled_by_default))
    
    @staticmethod
    def get_all():
        """Get all games"""
        query = "SELECT * FROM games ORDER BY id"
        return get_all(query)
    
    @staticmethod
    def get_by_id(game_id):
        """Get game by ID"""
        query = "SELECT * FROM games WHERE id = %s"
        return get_one(query, (game_id,))
    
    @staticmethod
    def get_by_slug(slug):
        """Get game by slug"""
        query = "SELECT * FROM games WHERE slug = %s"
        return get_one(query, (slug,))


class UserGame:
    """UserGame model - manages user access to games"""

    @staticmethod
    def enable_game(user_id, game_id):
        """Enable game for user (insert or update)."""
        query = """
            INSERT INTO user_games (user_id, game_id, enabled)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE enabled = VALUES(enabled)
        """
        try:
            insert(query, (user_id, game_id))
            return True
        except Exception as e:
            # Replace print with your logger if available
            print("enable_game error:", e)
            return False

    @staticmethod
    def disable_game(user_id, game_id):
        """Disable game for user (insert or update)."""
        query = """
            INSERT INTO user_games (user_id, game_id, enabled)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE enabled = VALUES(enabled)
        """
        try:
            insert(query, (user_id, game_id))
            return True
        except Exception as e:
            print("disable_game error:", e)
            return False

    @staticmethod
    def get_user_games(user_id):
        """Get all games with user's enabled status"""
        query = """
            SELECT g.*,
                   COALESCE(ug.enabled, g.enabled_by_default) as is_enabled
            FROM games g
            LEFT JOIN user_games ug ON g.id = ug.game_id AND ug.user_id = %s
            ORDER BY g.id
        """
        return get_all(query, (user_id,))

    
    @staticmethod
    def is_game_enabled(user_id, game_id):
        """Check if game is enabled for user"""
        query = """
            SELECT COALESCE(ug.enabled, g.enabled_by_default) as is_enabled
            FROM games g
            LEFT JOIN user_games ug ON g.id = ug.game_id AND ug.user_id = %s
            WHERE g.id = %s
        """
        result = get_one(query, (user_id, game_id))
        return result and result['is_enabled'] == 1


class Post:
    """Post model - blog posts"""
    
    @staticmethod
    def create(user_id, title, content):
        """Create new post"""
        query = """
            INSERT INTO posts (user_id, title, content, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        return insert(query, (user_id, title, content))
    
    @staticmethod
    def get_all():
        """Get all posts with user info"""
        query = """
            SELECT p.*, u.username, u.firstname, u.lastname
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """
        return get_all(query)
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID"""
        query = """
            SELECT p.*, u.username, u.firstname, u.lastname
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """
        return get_one(query, (post_id,))
    
    @staticmethod
    def get_by_user(user_id):
        """Get all posts by user"""
        query = """
            SELECT p.*, u.username, u.firstname, u.lastname
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
        """
        return get_all(query, (user_id,))
    
    @staticmethod
    def update_post(post_id, title, content):
        """Update post"""
        query = """
            UPDATE posts 
            SET title = %s, content = %s, updated_at = NOW()
            WHERE id = %s
        """
        return update(query, (title, content, post_id))
    
    @staticmethod
    def delete_post(post_id):
        """Delete post"""
        query = "DELETE FROM posts WHERE id = %s"
        return delete(query, (post_id,))


class AuditLog:
    """AuditLog model - tracks admin actions"""
    
    @staticmethod
    def log(admin_id, action, details=''):
        """Create audit log entry"""
        query = """
            INSERT INTO audit_logs (admin_id, action, details, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        return insert(query, (admin_id, action, details))
    
    @staticmethod
    def get_recent(limit=100):
        """Get recent audit logs"""
        query = """
            SELECT al.*, u.username as admin_username
            FROM audit_logs al
            JOIN users u ON al.admin_id = u.id
            ORDER BY al.created_at DESC
            LIMIT %s
        """
        return get_all(query, (limit,))
    
    @staticmethod
    def get_by_admin(admin_id, limit=50):
        """Get logs by admin"""
        query = """
            SELECT al.*, u.username as admin_username
            FROM audit_logs al
            JOIN users u ON al.admin_id = u.id
            WHERE al.admin_id = %s
            ORDER BY al.created_at DESC
            LIMIT %s
        """
        return get_all(query, (admin_id, limit))
