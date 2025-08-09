from functools import wraps
from flask import session, redirect, url_for, flash
import os
import hashlib
import instaloader
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or 'instagram_username' not in session:
            flash('Please log in with your Instagram credentials to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_instagram_credentials(username, password):
    """Verify Instagram credentials by attempting to login"""
    try:
        loader = instaloader.Instaloader()
        loader.login(username, password)
        
        # Get basic profile info to verify access
        profile = instaloader.Profile.from_username(loader.context, username)
        
        profile_data = {
            'username': profile.username,
            'full_name': profile.full_name,
            'followers': profile.followers,
            'following': profile.followees,
            'posts': profile.mediacount,
            'is_verified': profile.is_verified,
            'is_private': profile.is_private,
            'biography': profile.biography
        }
        
        logger.info(f"Successfully authenticated Instagram user: {username}")
        return True, profile_data
        
    except Exception as e:
        logger.error(f"Instagram authentication failed for {username}: {str(e)}")
        return False, str(e)

def hash_password(password):
    """Hash a password using SHA256 (basic implementation)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return hash_password(password) == hashed
