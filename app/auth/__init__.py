"""
Authentication Blueprint
Handles user registration, login, logout, email verification, and password reset
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth import routes
