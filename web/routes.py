from flask import render_template, jsonify, request, session
from .auth import login_required
import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from bot.db import get_today_stats, get_follower_timeline, get_recent_changes, get_tracking_logs
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def calculate_growth_rate(stats):
    """Calculate growth rate percentage"""
    if stats['start_of_day_followers'] > 0:
        return round((stats['net_change_today'] / stats['start_of_day_followers']) * 100, 2)
    return 0.0

def init_routes(app):
    """Initialize all application routes"""
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/api/stats')
    @login_required
    def api_stats():
        """API endpoint for follower statistics"""
        try:
            stats = get_today_stats()
            stats['growth_rate'] = calculate_growth_rate(stats)
            stats['last_updated'] = datetime.now().isoformat()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/timeline')
    @login_required
    def api_timeline():
        """API endpoint for follower timeline data"""
        try:
            timeline = get_follower_timeline(30)
            
            # If no data, return empty array instead of error
            if not timeline:
                return jsonify([])
            
            # Ensure data is properly formatted
            formatted_timeline = []
            for item in timeline:
                formatted_timeline.append({
                    'date': item['date'],
                    'followers': int(item['followers']) if item['followers'] else 0
                })
            
            return jsonify(formatted_timeline)
        except Exception as e:
            logger.error(f"Error getting timeline: {str(e)}")
            return jsonify([])  # Return empty array instead of error to prevent frontend issues
    
    @app.route('/api/recent-changes')
    @login_required
    def api_recent_changes():
        """API endpoint for recent follower changes"""
        try:
            changes = get_recent_changes(10)
            
            # If no data, return empty array
            if not changes:
                return jsonify([])
            
            # Format the changes properly
            formatted_changes = []
            for change in changes:
                formatted_changes.append({
                    'timestamp': change['timestamp'],
                    'change_type': change['change_type'],
                    'count': int(change['count']) if change['count'] else 0,
                    'message': change['message'] or ''
                })
            
            return jsonify(formatted_changes)
        except Exception as e:
            logger.error(f"Error getting recent changes: {str(e)}")
            return jsonify([])  # Return empty array instead of error
    
    @app.route('/settings')
    @login_required
    def settings():
        """Settings page"""
        profile_data = session.get('profile_data', {})
        user_config = {
            'instagram_username': session.get('instagram_username', ''),
            'instagram_password_set': bool(session.get('instagram_password')),
            'profile_data': profile_data,
            'login_time': session.get('login_time'),
            'tracking_available': True
        }
        return render_template('settings.html', config=user_config)
    
    @app.route('/api/config')
    @login_required
    def api_config():
        """API endpoint for configuration"""
        try:
            profile_data = session.get('profile_data', {})
            user_config = {
                'instagram_username': session.get('instagram_username', ''),
                'instagram_password_set': bool(session.get('instagram_password')),
                'profile_data': profile_data,
                'login_time': session.get('login_time'),
                'tracking_available': True
            }
            return jsonify(user_config)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/logs')
    @login_required
    def view_logs():
        """View application logs"""
        try:
            # Get tracking logs from database
            tracking_logs = get_tracking_logs(50)
            
            # Get file logs
            log_files = []
            log_dir = 'logs'
            
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith('.log'):
                        file_path = os.path.join(log_dir, file)
                        file_stat = os.stat(file_path)
                        log_files.append({
                            'name': file,
                            'size': file_stat.st_size,
                            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
            
            return render_template('logs.html', log_files=log_files, tracking_logs=tracking_logs)
        except Exception as e:
            return render_template('error.html', error_code=500, error_message=str(e))
    
    @app.route('/api/log/<filename>')
    @login_required
    def api_get_log(filename):
        """API endpoint to get log file content"""
        try:
            log_path = os.path.join('logs', filename)
            if not os.path.exists(log_path) or not filename.endswith('.log'):
                return jsonify({'error': 'Log file not found'}), 404
            
            with open(log_path, 'r') as f:
                # Get last 100 lines
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            return jsonify({'content': ''.join(recent_lines)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/start-tracking', methods=['POST'])
    @login_required
    def api_start_tracking():
        """API endpoint to start tracking"""
        try:
            from bot.tracker import create_tracker_from_session
            
            # Create tracker from session
            tracker = create_tracker_from_session(session)
            
            # Run one tracking cycle
            success = tracker.run_once()
            
            if success:
                return jsonify({
                    'message': 'Tracking completed successfully',
                    'status': 'success'
                })
            else:
                return jsonify({
                    'message': 'Tracking failed - check logs for details',
                    'status': 'error'
                }), 500
                
        except Exception as e:
            logger.error(f"Error starting tracking: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/profile-info')
    @login_required
    def api_profile_info():
        """Get current user's Instagram profile info"""
        try:
            profile_data = session.get('profile_data', {})
            return jsonify(profile_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-telegram', methods=['POST'])
    @login_required
    def api_test_telegram():
        """API endpoint to test Telegram connection"""
        try:
            from bot.notifier import test_telegram_connection
            success, message = test_telegram_connection()
            return jsonify({'success': success, 'message': message})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
