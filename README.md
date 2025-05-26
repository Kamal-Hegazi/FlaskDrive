# FlaskDrive

<div align="center">

![FlaskDrive Logo](static/images/cloud-storage.svg)

*A secure cloud storage platform built with Flask*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1-purple)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

## Overview

FlaskDrive is a secure cloud storage application that replicates the core functionality of Google Drive. Built with Flask and modern web technologies, it provides a clean, intuitive interface for file management with robust security features, including end-to-end file encryption.

## Features

### Core Functionality
- 📁 File and folder management (upload, download, rename, delete)
- 🔍 File search and filtering
- 🌐 File sharing with permission controls
- 👤 User authentication and profile management
- 📱 Responsive interface that works on mobile devices

### Security Features
- 🔒 File encryption at rest using Fernet symmetric encryption
- 🔑 Secure password hashing
- 🛡️ Permission-based access controls
- 🔐 CSRF protection

### User Experience
- 👁️ File preview for common formats (images, PDFs, text files)
- ⭐ Favorite/star important files
- 🗑️ Trash bin for deleted files
- 📊 Storage usage visualization
- 📱 Responsive design for all devices

## Screenshots

*(Insert screenshots here)*

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- A modern web browser

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/flaskdrive.git
   cd flaskdrive
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory with:
   ```
   # Application security
   SECRET_KEY=your_secure_secret_key
   
   # Database configuration
   DATABASE_URI=sqlite:///drive.db
   
   # File encryption
   # Generate a secure key using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ENCRYPTION_KEY=your_generated_encryption_key
   
   # Storage limits (optional)
   # DEFAULT_STORAGE_LIMIT=1073741824  # 1GB in bytes
   ```
   
   You can generate a secure SECRET_KEY using:
   ```bash
   python -c "import secrets; print(secrets.token_hex(24))"
   ```
   
   And a Fernet ENCRYPTION_KEY using:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   flask run
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`
   
   You can also access it from other devices on your network using your computer's IP address:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```
   (Replace YOUR_IP_ADDRESS with your actual network IP address, e.g., 192.168.1.100)

## Project Structure

```
flaskdrive/
├── app.py              # Main application file
├── models.py           # Database models
├── config.py           # Application configuration
├── forms.py            # Form definitions
├── requirements.txt    # Project dependencies
├── .env                # Environment variables (create this)
├── static/             # Static assets (CSS, JS, images)
├── templates/          # HTML templates
├── uploads/            # Uploaded files (created automatically)
├── instance/           # Instance-specific data (database)
├── docs/               # Documentation
│   ├── installation.md    # Installation guide
│   ├── user_guide.md      # User guide
│   ├── developer_guide.md # Developer guide
│   ├── api_reference.md   # API documentation
│   ├── security.md        # Security information
│   └── database_schema.md # Database structure
└── README.md           # This file
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Werkzeug
- **Database**: SQLite (easily configurable to use PostgreSQL or MySQL)
- **Frontend**: Bootstrap 5, Font Awesome, jQuery
- **Security**: Cryptography, Flask-Login, CSRF protection

## Future Enhancements

- [ ] API for third-party integrations (see [API Reference](docs/api_reference.md))
- [ ] Mobile application support
- [ ] Advanced file versioning

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Cryptography](https://cryptography.io/)
