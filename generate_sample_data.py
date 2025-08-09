#!/usr/bin/env python3
"""
Sample data generator for Instagram Analytics
This script adds some sample data to demonstrate the dashboard functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bot.db import (
    init_db, save_follower_data, save_follower_change, 
    log_tracking_event, save_setting
)
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample data for testing"""
    print("🔧 Generating sample data...")
    
    # Initialize database
    init_db()
    
    # Generate follower data for the last 30 days
    base_followers = 1000
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        # Simulate growth with some variation
        growth = random.randint(-2, 8)
        followers = base_followers + (i * 2) + growth
        following = 500 + random.randint(-10, 20)
        posts = 150 + random.randint(0, 3)
        
        # Manually set the timestamp in the database
        import sqlite3
        conn = sqlite3.connect('analytics.db')
        conn.execute('''
            INSERT INTO followers (timestamp, follower_count, following_count, posts_count)
            VALUES (?, ?, ?, ?)
        ''', (date, followers, following, posts))
        conn.commit()
        conn.close()
        
        # Add some follower changes
        if i > 0 and random.random() < 0.3:  # 30% chance of a change
            change_type = 'gain' if growth > 0 else 'loss'
            count = abs(growth) if growth != 0 else 1
            message = f"{'Gained' if change_type == 'gain' else 'Lost'} {count} follower{'s' if count > 1 else ''}"
            
            conn = sqlite3.connect('analytics.db')
            conn.execute('''
                INSERT INTO follower_changes (timestamp, change_type, count, message)
                VALUES (?, ?, ?, ?)
            ''', (date, change_type, count, message))
            conn.commit()
            conn.close()
    
    # Add some recent tracking logs
    log_events = [
        ('success', 'Application started', 'Instagram Analytics initialized'),
        ('success', 'Profile data retrieved', 'Followers: 1056, Following: 520, Posts: 153'),
        ('success', 'Follower gain detected', 'Gained 3 followers'),
        ('warning', 'Rate limit approached', 'Slowing down requests'),
        ('success', 'Data saved successfully', 'Updated follower count: 1059'),
    ]
    
    for i, (status, message, details) in enumerate(log_events):
        timestamp = datetime.now() - timedelta(hours=i)
        import sqlite3
        conn = sqlite3.connect('analytics.db')
        conn.execute('''
            INSERT INTO tracking_log (timestamp, status, message, details)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, status, message, details))
        conn.commit()
        conn.close()
    
    # Save some settings
    save_setting('last_update', datetime.now().isoformat())
    save_setting('tracking_enabled', 'true')
    
    print("✅ Sample data generated successfully!")
    print("📊 Generated 30 days of follower data")
    print("📈 Added follower change events")
    print("📝 Added tracking log entries")
    print("\n🌐 Visit http://localhost:5000 to see the dashboard!")

if __name__ == "__main__":
    generate_sample_data()
