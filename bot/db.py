import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'analytics.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    
    # Create followers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS followers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            follower_count INTEGER NOT NULL,
            following_count INTEGER NOT NULL,
            posts_count INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create follower_changes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS follower_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            change_type TEXT NOT NULL, -- 'gain' or 'loss'
            count INTEGER NOT NULL,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create settings table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create tracking_log table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tracking_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            status TEXT NOT NULL, -- 'success', 'error', 'warning'
            message TEXT,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def save_follower_data(follower_count, following_count, posts_count):
    """Save follower data to database"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO followers (timestamp, follower_count, following_count, posts_count)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now(), follower_count, following_count, posts_count))
    conn.commit()
    conn.close()

def get_latest_follower_count():
    """Get the latest follower count"""
    conn = get_db_connection()
    result = conn.execute('''
        SELECT follower_count FROM followers 
        ORDER BY timestamp DESC LIMIT 1
    ''').fetchone()
    conn.close()
    return result['follower_count'] if result else 0

def save_follower_change(change_type, count, message):
    """Save follower change event"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO follower_changes (timestamp, change_type, count, message)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now(), change_type, count, message))
    conn.commit()
    conn.close()

def get_recent_changes(limit=10):
    """Get recent follower changes"""
    conn = get_db_connection()
    results = conn.execute('''
        SELECT * FROM follower_changes 
        ORDER BY timestamp DESC LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in results]

def get_follower_timeline(days=30):
    """Get follower timeline for the last N days"""
    conn = get_db_connection()
    results = conn.execute('''
        SELECT DATE(timestamp) as date, 
               MAX(follower_count) as followers,
               MAX(following_count) as following,
               MAX(posts_count) as posts
        FROM followers 
        WHERE timestamp >= datetime('now', ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    ''', (f'-{days}',)).fetchall()
    conn.close()
    return [dict(row) for row in results]

def get_today_stats():
    """Get today's statistics"""
    conn = get_db_connection()
    
    # Get current count
    current = conn.execute('''
        SELECT follower_count, following_count, posts_count 
        FROM followers 
        ORDER BY timestamp DESC LIMIT 1
    ''').fetchone()
    
    # Get start of day count
    start_of_day = conn.execute('''
        SELECT follower_count 
        FROM followers 
        WHERE DATE(timestamp) = DATE('now')
        ORDER BY timestamp ASC LIMIT 1
    ''').fetchone()
    
    # Get changes today
    changes = conn.execute('''
        SELECT change_type, SUM(count) as total_count
        FROM follower_changes 
        WHERE DATE(timestamp) = DATE('now')
        GROUP BY change_type
    ''').fetchall()
    
    conn.close()
    
    current_followers = current['follower_count'] if current else 0
    start_followers = start_of_day['follower_count'] if start_of_day else current_followers
    
    gains = 0
    losses = 0
    for change in changes:
        if change['change_type'] == 'gain':
            gains = change['total_count']
        elif change['change_type'] == 'loss':
            losses = change['total_count']
    
    return {
        'current_followers': current_followers,
        'followers_gained_today': gains,
        'followers_lost_today': losses,
        'net_change_today': gains - losses,
        'start_of_day_followers': start_followers
    }

def save_setting(key, value):
    """Save a setting to database"""
    conn = get_db_connection()
    conn.execute('''
        INSERT OR REPLACE INTO settings (key, value, updated_at)
        VALUES (?, ?, ?)
    ''', (key, value, datetime.now()))
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """Get a setting from database"""
    conn = get_db_connection()
    result = conn.execute('''
        SELECT value FROM settings WHERE key = ?
    ''', (key,)).fetchone()
    conn.close()
    return result['value'] if result else default

def log_tracking_event(status, message, details=None):
    """Log a tracking event"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO tracking_log (timestamp, status, message, details)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now(), status, message, details))
    conn.commit()
    conn.close()

def get_tracking_logs(limit=50):
    """Get recent tracking logs"""
    conn = get_db_connection()
    results = conn.execute('''
        SELECT * FROM tracking_log 
        ORDER BY timestamp DESC LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in results]
