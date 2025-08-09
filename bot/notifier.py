import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .db import log_tracking_event

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if self.enabled:
            self.bot = Bot(token=self.bot_token)
        else:
            logger.warning("Telegram notifications disabled - missing token or chat ID")
    
    async def send_message_async(self, message):
        """Send message asynchronously"""
        try:
            if not self.enabled:
                logger.debug("Telegram not configured, skipping notification")
                return False
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Telegram notification sent: {message}")
            log_tracking_event('success', 'Telegram notification sent', message)
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {str(e)}")
            log_tracking_event('error', 'Telegram notification failed', str(e))
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {str(e)}")
            log_tracking_event('error', 'Telegram notification error', str(e))
            return False
    
    def send_message(self, message):
        """Send message synchronously"""
        if not self.enabled:
            return False
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.send_message_async(message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in sync message sending: {str(e)}")
            return False
    
    async def send_formatted_notification(self, title, message, emoji="📊"):
        """Send formatted notification"""
        formatted_message = f"{emoji} <b>{title}</b>\n\n{message}\n\n<i>Instagram Analytics Bot</i>"
        return await self.send_message_async(formatted_message)
    
    def test_connection(self):
        """Test Telegram connection"""
        if not self.enabled:
            return False, "Telegram not configured"
        
        try:
            test_message = "🧪 Instagram Analytics Bot - Connection Test"
            result = self.send_message(test_message)
            return result, "Test message sent successfully" if result else "Failed to send test message"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

# Global notifier instance
_notifier = None

def get_notifier():
    """Get global notifier instance"""
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier()
    return _notifier

def send_notification(message):
    """Send notification using global notifier"""
    notifier = get_notifier()
    return notifier.send_message(message)

def send_formatted_notification(title, message, emoji="📊"):
    """Send formatted notification"""
    notifier = get_notifier()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(notifier.send_formatted_notification(title, message, emoji))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error sending formatted notification: {str(e)}")
        return False

def test_telegram_connection():
    """Test Telegram connection"""
    notifier = get_notifier()
    return notifier.test_connection()
