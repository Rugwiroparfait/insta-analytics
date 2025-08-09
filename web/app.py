from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime
import logging
from .auth import login_required, verify_instagram_credentials
from .routes import init_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    
    # Initialize routes
    init_routes(app)
    
    @app.route('/')
    def index():
        """Homepage with login check"""
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page with Instagram credentials"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password!', 'error')
                return render_template('login.html')
            
            # Verify Instagram credentials
            success, result = verify_instagram_credentials(username, password)
            
            if success:
                session['logged_in'] = True
                session['instagram_username'] = username
                session['instagram_password'] = password  # Store for tracking
                session['profile_data'] = result
                session['login_time'] = datetime.now().isoformat()
                
                logger.info(f"Successful Instagram login: {username}")
                flash(f'Welcome {result.get("full_name", username)}! Login successful.', 'success')
                return redirect(url_for('index'))
            else:
                logger.warning(f"Failed Instagram login attempt for: {username}")
                flash(f'Instagram login failed: {result}', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Logout and clear session"""
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error_code=404, error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('error.html', error_code=500, error_message="Internal server error"), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Instagram Analytics Web Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
