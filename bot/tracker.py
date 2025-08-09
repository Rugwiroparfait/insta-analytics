import instaloader
import time
import logging
from datetime import datetime
import schedule
from .db import (
    init_db, save_follower_data, get_latest_follower_count, 
    save_follower_change, log_tracking_event
)
from .notifier import send_notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tracker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class InstagramTracker:
    def __init__(self, username, password):
        self.loader = instaloader.Instaloader()
        self.username = username
        self.password = password
        self.logged_in = False
        self.last_follower_count = 0
        self.profile_cache = None
        
    def login(self):
        """Login to Instagram"""
        try:
            logger.info(f"Attempting to login as {self.username}")
            self.loader.login(self.username, self.password)
            self.logged_in = True
            logger.info("Successfully logged into Instagram")
            log_tracking_event('success', f'Logged in as {self.username}')
            return True
        except Exception as e:
            logger.error(f"Failed to login to Instagram: {str(e)}")
            log_tracking_event('error', 'Login failed', str(e))
            return False
    
    def get_profile_stats(self):
        """Get profile statistics"""
        try:
            if not self.logged_in:
                if not self.login():
                    return None
            
            profile = instaloader.Profile.from_username(self.loader.context, self.username)
            
            stats = {
                'followers': profile.followers,
                'following': profile.followees,
                'posts': profile.mediacount,
                'timestamp': datetime.now(),
                'username': profile.username,
                'full_name': profile.full_name,
                'bio': profile.biography,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private
            }
            
            logger.info(f"Retrieved stats: {stats['followers']} followers, {stats['following']} following, {stats['posts']} posts")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get profile stats: {str(e)}")
            log_tracking_event('error', 'Failed to get profile stats', str(e))
            return None
    
    def track_changes(self):
        """Track follower changes"""
        try:
            stats = self.get_profile_stats()
            if not stats:
                return False
            
            current_followers = stats['followers']
            previous_followers = get_latest_follower_count()
            
            # Save current stats
            save_follower_data(
                stats['followers'],
                stats['following'],
                stats['posts']
            )
            
            # Check for changes
            if previous_followers > 0:
                change = current_followers - previous_followers
                
                if change > 0:
                    message = f"Gained {change} follower{'s' if change > 1 else ''}"
                    save_follower_change('gain', change, message)
                    send_notification(f"🎉 {message}! Total: {current_followers}")
                    logger.info(f"Follower gain: +{change} (Total: {current_followers})")
                    
                elif change < 0:
                    lost = abs(change)
                    message = f"Lost {lost} follower{'s' if lost > 1 else ''}"
                    save_follower_change('loss', lost, message)
                    send_notification(f"😔 {message}. Total: {current_followers}")
                    logger.info(f"Follower loss: -{lost} (Total: {current_followers})")
                
                else:
                    logger.info(f"No follower change (Total: {current_followers})")
            else:
                logger.info(f"Initial tracking setup - Current followers: {current_followers}")
                send_notification(f"📊 Instagram Analytics started! Current followers: {current_followers}")
            
            self.last_follower_count = current_followers
            log_tracking_event('success', f'Tracking completed - {current_followers} followers')
            return True
            
        except Exception as e:
            logger.error(f"Error during tracking: {str(e)}")
            log_tracking_event('error', 'Tracking failed', str(e))
            return False
    
    def run_once(self):
        """Run tracking once"""
        logger.info("Starting single tracking run")
        return self.track_changes()
    
    def get_followers_list(self):
        """Get list of current followers"""
        try:
            if not self.logged_in:
                if not self.login():
                    return None
            
            profile = instaloader.Profile.from_username(self.loader.context, self.username)
            followers = set()
            
            logger.info("Fetching followers list...")
            for follower in profile.get_followers():
                followers.add(follower.username)
                # Limit to prevent rate limiting during development
                if len(followers) >= 100:  # Remove this limit in production
                    break
            
            logger.info(f"Retrieved {len(followers)} followers")
            return followers
            
        except Exception as e:
            logger.error(f"Failed to get followers list: {str(e)}")
            log_tracking_event('error', 'Failed to get followers list', str(e))
            return None
    
    def detect_follower_changes(self, current_followers, previous_followers):
        """Detect who followed/unfollowed"""
        if previous_followers is None:
            return [], []
        
        new_followers = current_followers - previous_followers
        unfollowers = previous_followers - current_followers
        
        return list(new_followers), list(unfollowers)
    
    def run_scheduled(self, interval_seconds=300):
        """Run scheduled tracking"""
        logger.info(f"Starting scheduled tracking (interval: {interval_seconds} seconds)")
        
        # Schedule the tracking job
        schedule.every(interval_seconds).seconds.do(self.track_changes)
        
        # Run initial tracking
        self.track_changes()
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Tracking stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduled tracking: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying

def create_tracker_from_session(session_data):
    """Create tracker instance from web session data"""
    username = session_data.get('instagram_username')
    password = session_data.get('instagram_password')
    
    if not username or not password:
        raise ValueError("Instagram credentials not found in session")
    
    return InstagramTracker(username, password)
