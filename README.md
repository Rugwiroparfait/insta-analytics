# 📊 Instagram Analytics Bot

A comprehensive Instagram follower tracking system with real-time notifications and a web dashboard for monitoring follower changes and analytics.

## 🚀 Features

- **📈 Real-time Follower Tracking**: Monitor follower count changes in real-time
- **🔔 Telegram Notifications**: Get instant alerts when followers are gained or lost
- **🌐 Web Dashboard**: Beautiful web interface to view analytics and trends
- **🔒 Secure Authentication**: Password-protected dashboard access
- **📊 Data Persistence**: SQLite database for storing historical data
- **📝 Comprehensive Logging**: Detailed logs for debugging and monitoring

## 🏗️ Project Structure

```
insta-analytics/
│
├── bot/                  # Tracker logic
│   ├── tracker.py        # Fetches followers & detects changes
│   ├── notifier.py       # Sends Telegram alerts
│   ├── db.py             # Database connection & queries
│   ├── config.py         # Config & secrets
│   └── __init__.py
│
├── web/                  # Web dashboard
│   ├── app.py            # Flask app entry point
│   ├── templates/        # HTML templates (Jinja2)
│   ├── static/           # CSS, JS, images
│   ├── routes.py         # Web routes & logic
│   └── auth.py           # Simple password login
│
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── run.sh               # Script to run tracker + web app
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Git
- Instagram account
- Telegram Bot Token (optional, for notifications)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rugwiroparfait/insta-analytics.git
   cd insta-analytics
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   cp bot/config.py.example bot/config.py
   ```
   
   Edit `bot/config.py` with your credentials:
   ```python
   # Instagram credentials
   INSTAGRAM_USERNAME = "your_username"
   INSTAGRAM_PASSWORD = "your_password"
   
   # Telegram bot settings (optional)
   TELEGRAM_BOT_TOKEN = "your_bot_token"
   TELEGRAM_CHAT_ID = "your_chat_id"
   
   # Web dashboard password
   WEB_PASSWORD = "your_secure_password"
   
   # Database settings
   DATABASE_PATH = "analytics.db"
   ```

5. **Initialize the database**
   ```bash
   python -c "from bot.db import init_db; init_db()"
   ```

## 🚀 Usage

### Quick Start

Run both the tracker and web dashboard:
```bash
chmod +x run.sh
./run.sh
```

### Individual Components

**Start the follower tracker:**
```bash
python -m bot.tracker
```

**Start the web dashboard:**
```bash
python -m web.app
```

The web dashboard will be available at `http://localhost:5000`

## 📱 Telegram Setup (Optional)

1. **Create a Telegram Bot**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token

2. **Get your Chat ID**
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

3. **Update configuration**
   - Add the bot token and chat ID to `bot/config.py`

## 🔧 Configuration

### Environment Variables

You can also use environment variables instead of editing `config.py`:

```bash
export INSTAGRAM_USERNAME="your_username"
export INSTAGRAM_PASSWORD="your_password"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export WEB_PASSWORD="your_secure_password"
```

### Tracking Frequency

Modify the tracking interval in `bot/tracker.py`:
```python
TRACKING_INTERVAL = 300  # 5 minutes (in seconds)
```

## 📊 Web Dashboard Features

- **📈 Follower Timeline**: Visual graphs showing follower growth over time
- **📊 Statistics**: Total followers, gains/losses, growth rate
- **📋 Recent Changes**: List of recent follower changes with timestamps
- **⚙️ Settings**: Configure tracking parameters and view logs

## 🗄️ Database Schema

The application uses SQLite with the following main tables:

- `followers`: Historical follower count data
- `changes`: Individual follower gain/loss events
- `sessions`: Web dashboard session management

## 📝 Logging

Logs are stored in the `logs/` directory:
- `tracker.log`: Follower tracking activities
- `web.log`: Web dashboard access and errors
- `notifier.log`: Telegram notification events

## 🔒 Security Considerations

- Never commit your `config.py` file with real credentials
- Use strong passwords for web dashboard access
- Consider using Instagram App Passwords if available
- Regularly rotate your credentials

## 🐛 Troubleshooting

### Common Issues

**Instagram Login Fails**
- Check your username and password
- Instagram may require 2FA - use app passwords
- You might be rate-limited - wait before retrying

**Telegram Notifications Not Working**
- Verify bot token and chat ID
- Check if the bot has permission to send messages
- Review `logs/notifier.log` for errors

**Web Dashboard Not Loading**
- Check if port 5000 is available
- Verify Flask is installed correctly
- Check `logs/web.log` for errors

### Debug Mode

Run with debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m bot.tracker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please respect Instagram's Terms of Service and rate limits. The authors are not responsible for any misuse of this software.

## 🙏 Acknowledgments

- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Flask Web Framework](https://flask.palletsprojects.com/)
- [Chart.js](https://www.chartjs.org/) for dashboard visualizations

---

**Made with ❤️ by [Rugwiroparfait](https://github.com/Rugwiroparfait)**

For support, please open an issue on GitHub or contact the maintainer.
