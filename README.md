# TikTok Re-Upload WebApp

A modern Flask web application for processing and optimizing TikTok videos for re-upload.

## 🌟 Key Features

- **Video Upload**: Support for MP4, MKV, and MOV formats
- **Video Processing**: Optimize videos for better compatibility
- **TikTok Live Monitoring**: Monitor TikTok users and automatically record live streams
- **Telegram Integration**: Send recorded live streams to Telegram chats
- **RESTful API**: Developer-friendly API endpoints
- **Modern UI**: Clean, responsive Bootstrap 5 interface
- **Drag & Drop**: Intuitive file upload experience
- **Secure**: Automatic file cleanup and validation

## 📁 Project Structure

```
tiktok_reup_webapp/
├── src/                    # Application source code
│   ├── views/             # Web and API routes
│   ├── services/          # Business logic
│   ├── app.py            # Application factory
│   ├── config.py         # Configuration management
│   └── extensions.py     # Flask extensions
├── templates/             # Jinja2 templates
├── static/               # CSS, JavaScript, images
│   ├── css/
│   └── js/
├── tests/                # Test suite
├── uploads/              # Temporary file storage
├── main.py              # Application entry point
├── pyproject.toml       # Project configuration
└── README.md
```
## 🛠️ Technology Stack

- **Framework**: Flask
- **Package Management**: UV
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest with async support

## 📦 Installation & Deployment
- Python 3.12
- UV package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- Docker & Docker Compose (for containerized deployment)

### Quick Start with UV

1. **Clone the repository**

   ```bash
   git clone https://github.com/monkiravn/tiktok_webapp.git
   cd tiktok_webapp
   ```

2. **Install UV** (if not already installed)

   ```bash
   # On Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up development environment**

   ```bash
   # Copy development environment file
   cp .env.example .env

   # Install dependencies with UV
   uv sync --extra dev
   ```

4. **Start development server**
   ```bash
   # Using UV run
   uv run python -m main
   ```

The application will be available at http://localhost:5000

## 🔴 TikTok Live Monitoring & Recording

This application includes a powerful TikTok Live Monitoring feature that automatically detects when TikTok users go live and records their streams.

### Features

- **Monitor TikTok Users**: Add users by username (@username) or profile URL
- **Automatic Detection**: Continuously monitors users for live status
- **Stream Recording**: Automatically starts recording when a user goes live
- **Telegram Integration**: Sends recorded files to your Telegram chat when streams end
- **Real-time Dashboard**: View monitoring status and recording activity
- **Background Processing**: Runs monitoring in the background

### Setup TikTok Live Monitoring

1. **Configure Telegram Integration** (optional but recommended):
   ```bash
   # Get API credentials from https://my.telegram.org/apps
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   
   # Create a bot with @BotFather on Telegram
   TELEGRAM_BOT_TOKEN=your_bot_token
   
   # Get your chat ID (can be personal chat or group)
   TELEGRAM_CHAT_ID=your_chat_id
   ```

2. **Install FFmpeg** (required for recording):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Windows (using Chocolatey)
   choco install ffmpeg
   
   # macOS (using Homebrew)
   brew install ffmpeg
   ```

3. **Access the Feature**:
   - Navigate to the "TikTok Live" section in the web interface
   - Add TikTok users you want to monitor
   - The system will automatically start monitoring and recording

### Usage

1. **Add a User to Monitor**:
   - Enter a TikTok username (e.g., `@username`) or profile URL
   - Click "Add User" to start monitoring

2. **Monitor Live Status**:
   - View real-time status of all monitored users
   - See when users are live and recording

3. **Recorded Files**:
   - Files are saved to the `uploads/recordings/` directory
   - Automatically sent to Telegram if configured
   - Files include timestamp and username in the filename

### API Endpoints

- `POST /api/v1/tiktok-live/add-user` - Add user to monitoring
- `POST /api/v1/tiktok-live/remove-user` - Remove user from monitoring  
- `GET /api/v1/tiktok-live/monitored-users` - Get list of monitored users
- `POST /api/v1/tiktok-live/start-monitoring` - Start monitoring service
- `POST /api/v1/tiktok-live/stop-monitoring` - Stop monitoring service

### Technical Notes

- Based on the [tiktok-live-recorder](https://github.com/Michele0303/tiktok-live-recorder) implementation
- Uses advanced request handling to bypass TikTok restrictions
- Monitoring runs every 60 seconds by default
- Supports multiple users simultaneously
- Includes error handling and logging

### Troubleshooting

- **"Could not find user"**: Verify the username exists and is correctly formatted
- **Recording issues**: Ensure FFmpeg is installed and accessible
- **Telegram not working**: Check API credentials and chat ID configuration
- **Network errors**: Some regions may have restrictions accessing TikTok APIs
