# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-08-06

### Added
- **User Authentication System**: Complete login system implementation with comprehensive testing
- **Dashboard Interface**: New dashboard layout replacing the simple upload page
- **Video Download Feature**: Added download functionality to result page for processed videos
- **Responsive Sidebar**: Collapsible sidebar with desktop/mobile toggle functionality
- **Login-First Navigation**: Implemented secure navigation requiring authentication

### Changed
- **UI/UX Improvements**: Enhanced login and navigation UI with modern styling
- **Layout Responsiveness**: Improved responsive design across different screen sizes
- **Password Input**: Enhanced password field with toggle visibility functionality
- **Navigation Structure**: Renamed "Upload" to "Dashboard" for better user experience
- **Container Layout**: Adjusted height properties and padding for better container organization

### Fixed
- **Login Page Issues**: Removed redundant links and fixed password toggle styling
- **Dropdown Z-index**: Improved dropdown component layering and positioning
- **Flash Messages**: Removed success flash messages from login/logout for cleaner UX
- **Configuration**: Updated get_config function signature to handle None type

### Technical Improvements
- **Code Refactoring**: Extensive layout and functionality refactoring for better maintainability
- **Video Upload Enhancement**: Improved video upload functionality and processing
- **Dependency Updates**: Updated project dependencies to latest compatible versions
- **Styling Consistency**: Standardized Bootstrap styling and component usage

## [1.0.0] - 2025-08-05

### Added
- **Flask Web Application**: Complete transformation from simple script to full-featured Flask web application
- **Modern Web Interface**: Responsive Bootstrap 5 UI with drag-and-drop file upload functionality
- **Video Processing Service**: Core video file processing and validation system
- **RESTful API**: Developer-friendly API endpoints for video upload and processing
- **Application Factory Pattern**: Modular Flask application architecture with blueprint system
- **Pydantic Configuration**: Type-safe configuration management with environment variable support
- **Comprehensive Testing**: pytest-based test suite with coverage reporting
- **Development Tooling**: Pre-commit hooks, Ruff linting, and code formatting
- **Dependency Management**: UV lock file for reproducible builds
- **Environment Configuration**: .env.example template with comprehensive settings
- **Project Documentation**: Complete README with installation guide and usage instructions

### Changed
- **Project Structure**: Migrated to modern Python package structure with src/ layout
- **Entry Point**: Replaced simple print script with production-ready Flask application launcher
- **Dependencies**: Added Flask 3.1.1, Pydantic, and development tools
- **Build System**: Updated pyproject.toml with modern Python packaging configuration

### Removed
- **Legacy Code**: Removed obsolete app/ directory structure
- **Simple Script**: Replaced basic hello-world functionality

### Technical Details
- **Framework**: Flask 3.1.1 with application factory pattern
- **Frontend**: Bootstrap 5 with responsive design
- **Configuration**: Pydantic-based settings with environment variable support
- **Testing**: pytest with Flask-specific testing utilities
- **Code Quality**: Ruff linting and formatting, pre-commit hooks
- **File Support**: MP4, MKV, MOV video formats
- **Architecture**: Modular design with services, views, and extensions

[1.1.0]: https://github.com/monkiravn/tiktok_webapp/releases/tag/v1.1.0
[1.0.0]: https://github.com/monkiravn/tiktok_webapp/releases/tag/v1.0.0
