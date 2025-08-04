# TikTok Re-Upload WebApp

A modern Flask web application for processing and optimizing TikTok videos for re-upload.

## 🌟 Key Features

- **Video Upload**: Support for MP4, MKV, and MOV formats
- **Video Processing**: Optimize videos for better compatibility
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
