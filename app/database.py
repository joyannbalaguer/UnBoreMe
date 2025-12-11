"""
Database Utilities
Handles MySQL database connections and operations
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from flask import current_app, g


def get_db_config():
    """Get database configuration from app config"""
    config = {
        'host': current_app.config['DB_HOST'],
        'port': current_app.config['DB_PORT'],
        'user': current_app.config['DB_USER'],
        'database': current_app.config['DB_NAME'],
        'charset': 'utf8mb4',
        'cursorclass': DictCursor,
        'autocommit': False
    }
    # Only add password if it's not empty
    if current_app.config['DB_PASSWORD']:
        config['password'] = current_app.config['DB_PASSWORD']
    else:
        config['password'] = ''
    return config


def get_db():
    """
    Get database connection from Flask g object or create new one
    Connection is stored in g for request lifecycle
    """
    if 'db' not in g:
        g.db = pymysql.connect(**get_db_config())
    else:
        # Check if connection is still alive, reconnect if not
        try:
            g.db.ping(reconnect=True)
        except:
            # Connection is dead, create a new one
            g.db = pymysql.connect(**get_db_config())
    return g.db


def close_db(e=None):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database operations
    
    Args:
        commit: Whether to commit changes (default: False for SELECT, True for INSERT/UPDATE/DELETE)
    
    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO users ...")
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


def init_db(app):
    """Initialize database teardown for app"""
    app.teardown_appcontext(close_db)


def test_connection():
    """Test database connection"""
    try:
        conn = pymysql.connect(**get_db_config())
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


# Query helper functions
def execute_query(query, params=None, commit=False, fetchone=False, fetchall=True):
    """
    Execute a database query with parameters
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        commit: Whether to commit (for INSERT/UPDATE/DELETE)
        fetchone: Return single row
        fetchall: Return all rows
    
    Returns:
        Query results or affected row count
    """
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        
        if commit:
            return cursor.lastrowid or cursor.rowcount
        
        if fetchone:
            return cursor.fetchone()
        
        if fetchall:
            return cursor.fetchall()
        
        return None


def get_one(query, params=None):
    """Execute query and return single row"""
    return execute_query(query, params, fetchone=True, fetchall=False)


def get_all(query, params=None):
    """Execute query and return all rows"""
    return execute_query(query, params, fetchall=True)


def insert(query, params=None):
    """Execute INSERT query and return last insert ID"""
    return execute_query(query, params, commit=True, fetchall=False)


def update(query, params=None):
    """Execute UPDATE query and return affected rows"""
    return execute_query(query, params, commit=True, fetchall=False)


def delete(query, params=None):
    """Execute DELETE query and return affected rows"""
    return execute_query(query, params, commit=True, fetchall=False)
