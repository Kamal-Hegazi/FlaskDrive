# FlaskDrive Developer Guide

This guide provides detailed information for developers who want to understand, maintain, or extend the FlaskDrive application.

## Architecture Overview

FlaskDrive follows a standard Flask application structure:

```
flaskdrive/
├── app.py              # Main application file with routes
├── models.py           # Database models
├── config.py           # Application configuration
├── forms.py            # Form definitions
├── requirements.txt    # Project dependencies
├── static/             # Static assets (CSS, JS, images)
├── templates/          # HTML templates
├── uploads/            # Uploaded files (created automatically)
├── docs/               # Documentation
└── README.md           # Project overview
```

### Technology Stack

- **Backend**: Flask, SQLAlchemy, Werkzeug
- **Database**: SQLite (configurable to PostgreSQL or MySQL)
- **Frontend**: Bootstrap 5, Font Awesome, jQuery
- **Security**: Cryptography (Fernet), Flask-Login, CSRF protection

## Core Components

### Models (models.py)

The data models represent the database schema:

- **User**: User accounts with authentication
- **Folder**: Represents folders in the file hierarchy
- **File**: Metadata for uploaded files
- **Activity**: User activity logging
- **shares**: Association table for file sharing

### Routes (app.py)

The main application logic is organized into route functions:

- Authentication routes (register, login, logout)
- File management routes (upload, download, delete, etc.)
- Folder management routes (create, delete, navigate)
- Sharing routes (share, unshare)
- User profile and dashboard routes

### Forms (forms.py)

WTForms classes for form validation:

- **LoginForm**: User login
- **RegistrationForm**: New user registration
- **UploadFileForm**: File uploads
- **CreateFolderForm**: Folder creation
- **ShareFileForm**: File sharing
- **SearchForm**: Search functionality
- **UpdateProfileForm**: Profile updates
- **RenameFileForm**: File renaming

### Configuration (config.py)

Application settings loaded from environment variables:

- Security keys
- Database connection
- File upload settings
- Storage configuration

### Templates (templates/)

Jinja2 HTML templates with a base template inheritance structure:

- **base.html**: Common layout with navigation
- **dashboard.html**: User dashboard
- **folder.html**: Folder view with file listing
- Various other templates for specific functionality

## Key Features Implementation

### File Encryption

Files are encrypted using Fernet symmetric encryption:

```python
# Encryption (simplified)
def encrypt_file(input_file_path):
    with open(input_file_path, 'rb') as f:
        data = f.read()
    
    fernet = get_encryption_key()
    encrypted_data = fernet.encrypt(data)
    
    with open(input_file_path, 'wb') as f:
        f.write(encrypted_data)
```

### File Sharing

File sharing uses an association table to track shared files and permissions:

```python
# Association table for file sharing
shares = db.Table('shares',
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('permission', db.String(20), default='view'),
    db.Column('shared_on', db.DateTime, default=datetime.utcnow)
)
```

### Authentication

Authentication is handled using Flask-Login:

```python
# User authentication (simplified)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
```

## Extending the Application

### Adding New Features

To add new features to FlaskDrive:

1. Define models in models.py if needed
2. Create forms in forms.py if required
3. Implement routes in app.py
4. Create or modify templates in templates/
5. Add any necessary static assets in static/

### Modal File Preview Functionality

The application implements a Google Drive-like popup preview system that allows users to preview files without leaving their current page:

1. **Frontend Implementation**:
   - Modal dialog in base.html template:
   ```html
   <!-- File Preview Modal -->
   <div class="modal fade" id="previewModal" tabindex="-1" aria-labelledby="previewModalLabel" aria-hidden="true">
       <div class="modal-dialog modal-xl modal-dialog-centered modal-fullscreen-lg-down">
           <div class="modal-content">
               <!-- Modal header with title and action buttons -->
               <div class="modal-header py-2">
                   <h5 class="modal-title" id="previewModalLabel">File Preview</h5>
                   <div class="ms-auto me-2">
                       <a href="#" id="previewDownloadBtn" class="btn btn-primary btn-sm">
                           <i class="fas fa-download me-1"></i> Download
                       </a>
                       <a href="#" id="previewOpenNewTabBtn" class="btn btn-outline-primary btn-sm ms-1" target="_blank">
                           <i class="fas fa-external-link-alt me-1"></i> Open in New Tab
                       </a>
                   </div>
                   <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
               </div>
               <!-- Modal body where content is displayed -->
               <div class="modal-body p-1" id="previewModalBody"></div>
           </div>
       </div>
   </div>
   ```

2. **Backend Implementation**:
   - Enhanced preview_file route in app.py that handles different viewing modes:
   ```python
   @app.route('/preview/<int:file_id>')
   @login_required
   def preview_file(file_id):
       # Get parameters from query string
       direct = request.args.get('direct', type=int)  # For new tab viewing
       inline = request.args.get('inline', type=int)  # For inline content
       modal = request.args.get('modal', type=int)    # For modal popup
       
       # File access verification and processing...
       
       # Return JSON for modal preview
       if modal:
           return jsonify({
               'filename': file.original_filename,
               'file_type': file_type,
               'extension': file_extension[1:],
               'file_id': file.id,
               'content': file_content if file_type == 'text' else None
           })
       
       # File serving for direct/inline viewing
       if direct or inline:
           return send_file(path, download_name=filename, as_attachment=False)
   ```

3. **JavaScript Implementation**:
   - AJAX-based file content loading in script.js
   - Event handlers for preview buttons and file rows
   - Dynamic content rendering based on file type

4. **CSS Optimizations**:
   - Responsive design for different screen sizes
   - Content-specific styling for various file types
   - Optimized to avoid unnecessary scrollbars

This implementation creates a seamless user experience while maintaining proper access controls.

### Example: Adding File Versioning

To implement file versioning:

1. Add a FileVersion model in models.py:
   ```python
   class FileVersion(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
       version_number = db.Column(db.Integer, nullable=False)
       file_path = db.Column(db.String(255), unique=True, nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       file = db.relationship('File', backref='versions')
   ```

2. Update the File model to track the current version
3. Modify the upload route to handle versioning
4. Create a version history view template
5. Add version restoration functionality

### Changing Database Backend

To switch from SQLite to PostgreSQL:

1. Update your .env file with the PostgreSQL connection string:
   ```
   DATABASE_URI=postgresql://username:password@localhost/drive
   ```

2. Install the PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

3. Migrate your database:
   ```bash
   flask db migrate -m "Migrate to PostgreSQL"
   flask db upgrade
   ```

### Adding API Access

To implement a RESTful API:

1. Install Flask-RESTful:
   ```bash
   pip install flask-restful
   ```

2. Create api.py with resource definitions
3. Register API resources with your Flask application
4. Implement authentication for API access (e.g., using tokens)

## Testing

### Running Tests

FlaskDrive uses pytest for testing:

```bash
pytest tests/
```

### Writing Tests

Add tests in the tests/ directory:

```python
def test_file_upload(client, authenticated_user):
    # Test implementation
    response = client.post('/upload', data={'file': test_file, 'folder_id': 1})
    assert response.status_code == 302  # Redirect after successful upload
```

## Deployment

### Development

For development, use the Flask development server:

```bash
flask run --debug
```

### Production

For production, use Gunicorn with a process manager like Supervisor:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

Configure Nginx as a reverse proxy in front of Gunicorn.

## Coding Standards

- Follow PEP 8 for Python code style
- Use docstrings to document functions and classes
- Maintain test coverage for new features
- Use Git branches for feature development
