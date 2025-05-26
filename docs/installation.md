# FlaskDrive Installation Guide

This guide provides detailed instructions for setting up and running FlaskDrive on your system.

## Prerequisites

Before installing FlaskDrive, ensure you have the following prerequisites:

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)
- A modern web browser

## Installation Steps

### 1. Get the Code

Either clone the repository using Git:

```bash
git clone https://github.com/yourusername/flaskdrive.git
cd flaskdrive
```

Or download and extract the source code to your preferred location.

### 2. Set Up a Virtual Environment (Recommended)

Create and activate a virtual environment to isolate the project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following content:

```
# FlaskDrive Environment Configuration

# Application security
# Generate a random key for Flask sessions and CSRF protection
SECRET_KEY=your_secure_secret_key

# Database configuration
# SQLite database path - change to PostgreSQL URI for production
DATABASE_URI=sqlite:///drive.db

# File encryption
# Generate a secure key using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your_generated_encryption_key

# Storage limits (optional)
# DEFAULT_STORAGE_LIMIT=1073741824  # 1GB in bytes
```

Replace the placeholders with actual secure keys. You can generate a secure SECRET_KEY using:

```bash
python -c "import secrets; print(secrets.token_hex(24))"
```

And a Fernet ENCRYPTION_KEY using:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 5. Initialize the Database

Set up the database with the following commands:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Run the Application

Start the Flask development server:

```bash
flask run
```

Access the application at http://127.0.0.1:5000 in your web browser.

## Production Deployment

For production deployment, consider the following additional steps:

### Database

For production, it's recommended to use PostgreSQL instead of SQLite. Update your `DATABASE_URI` environment variable:

```
DATABASE_URI=postgresql://username:password@localhost/flaskdrive
```

### Web Server

Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 app:app
```

And a reverse proxy like Nginx to handle static files and SSL termination.

### Environment Variables

In production, set environment variables directly on the server rather than using a `.env` file.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: If you encounter import errors, ensure all packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**: If you have database errors, try removing the existing database file and re-initializing:
   ```bash
   rm instance/drive.db
   flask db upgrade
   ```

3. **Permission Issues**: Ensure the application has write permissions to the `uploads` directory.

For further assistance, please open an issue on the GitHub repository.
