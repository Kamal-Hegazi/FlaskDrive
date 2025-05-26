import os
import secrets
from datetime import datetime
from cryptography.fernet import Fernet
from flask import Flask, render_template, url_for, flash, redirect, request, abort, send_file, current_app
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import and_
import tempfile

from config import Config
from models import db, User, File, Folder, Activity, shares
from forms import (LoginForm, RegistrationForm, UploadFileForm, CreateFolderForm,
                  ShareFileForm, UpdateProfileForm, RenameFileForm)

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Context processors
@app.context_processor
def inject_shared_count():
    """Make shared file count available to all templates"""
    if current_user.is_authenticated:
        shared_count = File.query.join(shares).filter(
            shares.c.user_id == current_user.id,
            File.is_trashed == False
        ).count()
        return {'shared_count': shared_count}
    return {'shared_count': 0}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def get_encryption_key():
    """Get Fernet encryption key from config"""
    return Fernet(app.config['ENCRYPTION_KEY'].encode())

def encrypt_file(input_file_path):
    """Encrypt a file using Fernet symmetric encryption
    
    Args:
        input_file_path: Path to the file to encrypt
        
    Returns:
        Success status
    """
    try:
        # Read the file
        with open(input_file_path, 'rb') as f:
            data = f.read()
        
        # Encrypt the data
        fernet = get_encryption_key()
        encrypted_data = fernet.encrypt(data)
        
        # Write the encrypted data back to the file
        with open(input_file_path, 'wb') as f:
            f.write(encrypted_data)
            
        return True
    except Exception as e:
        print(f"Encryption error: {e}")
        return False

def decrypt_file(input_file_path, output_file_path=None):
    """Decrypt a file using Fernet symmetric encryption
    
    Args:
        input_file_path: Path to the encrypted file
        output_file_path: Optional path where to write the decrypted file
                          If None, a temp file will be created
        
    Returns:
        Path to the decrypted file (could be a temp file)
    """
    try:
        # Read the encrypted file
        with open(input_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt the data
        fernet = get_encryption_key()
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # If no output path provided, create a temporary file
        if not output_file_path:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            output_file_path = temp_file.name
            temp_file.close()
        
        # Write the decrypted data
        with open(output_file_path, 'wb') as f:
            f.write(decrypted_data)
            
        return output_file_path
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def save_file(file, owner, encrypt=True):
    # Generate a secure filename
    original_filename = secure_filename(file.filename)
    random_hex = secrets.token_hex(8)
    filename = f"{random_hex}_{original_filename}"
    file_path = filename
    
    # Save the file
    file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_location)
    
    # Encrypt the file if requested
    is_encrypted = False
    if encrypt:
        is_encrypted = encrypt_file(file_location)
    
    # Get file size
    file_size = os.path.getsize(file_location)
    
    # Update user's storage usage
    owner.storage_used += file_size
    
    # Create file record
    new_file = File(
        filename=filename,
        original_filename=original_filename,
        file_type=file.content_type if hasattr(file, 'content_type') else '',
        file_size=file_size,
        file_path=file_path,
        is_encrypted=is_encrypted,
        owner_id=owner.id
    )
    
    return new_file

def get_breadcrumbs(folder):
    """Generate breadcrumbs for navigation"""
    breadcrumbs = []
    current = folder
    
    while current:
        breadcrumbs.append(current)
        current = current.parent
    
    return reversed(breadcrumbs)

def record_activity(user, action, file=None, folder=None):
    """Record user activity"""
    activity = Activity(
        user_id=user.id,
        action=action,
        file_id=file.id if file else None,
        folder_id=folder.id if folder else None
    )
    db.session.add(activity)
    db.session.commit()

# Routes
@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        
        # Create root folder for the user
        root_folder = Folder(name='My Drive', owner_id=user.id)
        db.session.add(root_folder)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's root folder
    root_folder = Folder.query.filter_by(owner_id=current_user.id, parent_id=None).first()
    
    # If root folder doesn't exist, create it
    if not root_folder:
        root_folder = Folder(name='My Drive', owner_id=current_user.id)
        db.session.add(root_folder)
        db.session.commit()
    
    # Get stats
    total_files = File.query.filter_by(owner_id=current_user.id, is_trashed=False).count()
    recent_files = File.query.filter_by(owner_id=current_user.id, is_trashed=False).order_by(File.updated_at.desc()).limit(5).all()
    starred_files = File.query.filter_by(owner_id=current_user.id, is_starred=True, is_trashed=False).all()
    
    # Calculate storage
    storage_used = current_user.storage_used
    storage_limit = current_user.storage_limit
    storage_percent = (storage_used / storage_limit) * 100 if storage_limit > 0 else 0
    
    # Format storage for display
    storage_used_display = f"{storage_used / (1024 * 1024):.2f} MB" if storage_used < 1024 * 1024 * 1024 else f"{storage_used / (1024 * 1024 * 1024):.2f} GB"
    storage_limit_display = f"{storage_limit / (1024 * 1024 * 1024):.2f} GB"
    
    return render_template('dashboard.html', title='Dashboard',
                         root_folder=root_folder,
                         total_files=total_files,
                         recent_files=recent_files,
                         starred_files=starred_files,
                         storage_used=storage_used_display,
                         storage_limit=storage_limit_display,
                         storage_percent=storage_percent)

@app.route('/folder/<int:folder_id>')
@login_required
def view_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    
    # Check if user has permission to view the folder
    if folder.owner_id != current_user.id:
        abort(403)
    
    files = File.query.filter_by(folder_id=folder_id, is_trashed=False).all()
    subfolders = Folder.query.filter_by(parent_id=folder_id).all()
    
    # Get breadcrumbs for navigation
    breadcrumbs = get_breadcrumbs(folder)
    
    # Forms
    upload_form = UploadFileForm()
    folder_form = CreateFolderForm()
    
    # Set the current folder as parent_id for the create folder form
    folder_form.parent_id.data = folder.id
    
    # Get all user's folders for upload dropdown
    user_folders = Folder.query.filter_by(owner_id=current_user.id).all()
    upload_folder_choices = [(f.id, f.name if f.id != folder.id else f'Current Folder ({f.name})') for f in user_folders]
    upload_form.folder_id.choices = upload_folder_choices
    
    return render_template('folder.html', title=folder.name,
                         folder=folder,
                         files=files,
                         subfolders=subfolders,
                         breadcrumbs=breadcrumbs,
                         upload_form=upload_form,
                         folder_form=folder_form)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    form = UploadFileForm()
    folder_id = request.form.get('folder_id')
    
    # Set choices before validation
    if folder_id:
        form.folder_id.choices = [(int(folder_id), 'Folder')]
    
    # Validate form
    if form.validate_on_submit():
        folder_id = form.folder_id.data
        folder = Folder.query.get_or_404(folder_id)
        
        # Check if user has permission to upload to this folder
        if folder.owner_id != current_user.id:
            abort(403)
        
        # Check if user has enough storage
        file_size = request.content_length
        if current_user.storage_used + file_size > current_user.storage_limit:
            flash('Not enough storage space.', 'danger')
            return redirect(url_for('view_folder', folder_id=folder_id))
        
        # Save the file
        file = form.file.data
        new_file = save_file(file, current_user)
        new_file.folder_id = folder_id
        
        db.session.add(new_file)
        db.session.commit()
        
        # Record activity
        record_activity(current_user, 'upload', file=new_file)
        
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('view_folder', folder_id=folder_id))
    
    flash('Error uploading file.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/create_folder/<int:parent_id>', methods=['POST'])
@login_required
def create_folder(parent_id):
    form = CreateFolderForm()
    
    # Always use the current folder as parent
    form.parent_id.data = parent_id
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data
        parent_folder = Folder.query.get_or_404(parent_id)
        
        # Check if user has permission to create folder here
        if parent_folder.owner_id != current_user.id:
            abort(403)
        
        new_folder = Folder(
            name=form.name.data,
            owner_id=current_user.id,
            parent_id=parent_id
        )
        
        db.session.add(new_folder)
        db.session.commit()
        
        # Record activity
        record_activity(current_user, 'create_folder', folder=new_folder)
        
        flash('Folder created successfully!', 'success')
        return redirect(url_for('view_folder', folder_id=parent_id))
    
    flash('Error creating folder.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to download this file
    is_owner = file.owner_id == current_user.id
    is_shared = current_user in file.shared_with
    
    if not (is_owner or is_shared):
        abort(403)
    
    # Record activity
    record_activity(current_user, 'download', file=file)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
    
    # If the file is encrypted, decrypt it first
    if file.is_encrypted:
        # Create a temporary file for the decrypted content
        decrypted_path = decrypt_file(file_path)
        if decrypted_path:
            # Send the decrypted file
            response = send_file(decrypted_path, 
                            as_attachment=True, 
                            download_name=file.original_filename)
            
            # Schedule temp file for deletion after response is sent
            @response.call_on_close
            def cleanup():
                try:
                    os.unlink(decrypted_path)
                except:
                    pass
                
            return response
        else:
            flash('Error decrypting file.', 'danger')
            return redirect(url_for('view_folder', folder_id=file.folder_id or 0))
    
    # If not encrypted, send directly
    return send_file(file_path, 
                   as_attachment=True, 
                   download_name=file.original_filename)

@app.route('/preview/<int:file_id>')
@login_required
def preview_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to preview this file
    is_owner = file.owner_id == current_user.id
    is_shared = current_user in file.shared_with
    
    if not (is_owner or is_shared):
        abort(403)
    
    # Record activity
    record_activity(current_user, 'preview', file=file)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
    file_extension = os.path.splitext(file.original_filename)[1].lower()
    
    # If file is encrypted, decrypt it to a temporary file for preview
    preview_path = file_path
    temp_file_created = False
    
    if file.is_encrypted:
        decrypted_path = decrypt_file(file_path)
        if decrypted_path:
            preview_path = decrypted_path
            temp_file_created = True
        else:
            flash('Error decrypting file for preview.', 'danger')
            return redirect(url_for('view_folder', folder_id=file.folder_id or 0))
    
    # Determine the file type
    if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        file_type = 'image'
    elif file_extension == '.pdf':
        file_type = 'pdf'
    elif file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
        file_type = 'text'
        # Read the file content for text files
        try:
            with open(preview_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            # If we can't decode as text, treat as binary
            file_type = 'binary'
            file_content = None
    else:
        file_type = 'binary'
        file_content = None
    
    # Clean up temporary decrypted file if text content was already read
    if temp_file_created and file_type == 'text':
        try:
            os.unlink(preview_path)
            temp_file_created = False
        except:
            pass
    
    # For direct file serving (images, PDFs)
    if file_type in ['image', 'pdf']:
        response = send_file(preview_path, download_name=file.original_filename, as_attachment=False)
        
        # Clean up temporary file after response is sent
        if temp_file_created:
            @response.call_on_close
            def cleanup():
                try:
                    os.unlink(preview_path)
                except:
                    pass
        
        return response
    
    return render_template('preview.html', 
                         title=f'Preview: {file.original_filename}',
                         file=file,
                         file_type=file_type,
                         file_content=file_content if file_type == 'text' else None)

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to delete this file
    if file.owner_id != current_user.id:
        abort(403)
    
    # Soft delete (move to trash)
    file.is_trashed = True
    db.session.commit()
    
    # Record activity
    record_activity(current_user, 'trash', file=file)
    
    flash('File moved to trash.', 'success')
    return redirect(url_for('view_folder', folder_id=file.folder_id or 0))

@app.route('/delete_folder/<int:folder_id>', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    
    # Check if user has permission to delete this folder
    if folder.owner_id != current_user.id:
        abort(403)
    
    # Get parent folder for redirect
    parent_id = folder.parent_id
    
    # Delete the folder and all its contents
    db.session.delete(folder)
    db.session.commit()
    
    # Record activity
    record_activity(current_user, 'delete_folder', folder=folder)
    
    flash('Folder deleted successfully.', 'success')
    return redirect(url_for('view_folder', folder_id=parent_id) if parent_id else url_for('dashboard'))

@app.route('/star/<int:file_id>', methods=['POST'])
@login_required
def star_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to star this file
    if file.owner_id != current_user.id:
        abort(403)
    
    # Toggle star status
    file.is_starred = not file.is_starred
    db.session.commit()
    
    # Record activity
    action = 'star' if file.is_starred else 'unstar'
    record_activity(current_user, action, file=file)
    
    flash(f"File {'starred' if file.is_starred else 'unstarred'} successfully.", 'success')
    return redirect(url_for('view_folder', folder_id=file.folder_id or 0))

@app.route('/rename/<int:file_id>', methods=['GET', 'POST'])
@login_required
def rename_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to rename this file
    if file.owner_id != current_user.id:
        abort(403)
    
    form = RenameFileForm()
    
    if form.validate_on_submit():
        # Update file name
        file.original_filename = form.filename.data
        file.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Record activity
        record_activity(current_user, 'rename', file=file)
        
        flash('File renamed successfully!', 'success')
        return redirect(url_for('view_folder', folder_id=file.folder_id or 0))
    elif request.method == 'GET':
        form.filename.data = file.original_filename
    
    return render_template('rename.html', title='Rename File',
                          file=file,
                          form=form)

@app.route('/share/<int:file_id>', methods=['GET', 'POST'])
@login_required
def share_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to share this file
    if file.owner_id != current_user.id:
        abort(403)
    
    form = ShareFileForm()
    
    if form.validate_on_submit():
        # Get user to share with
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('share_file', file_id=file_id))
        
        if user.id == current_user.id:
            flash('You cannot share with yourself.', 'danger')
            return redirect(url_for('share_file', file_id=file_id))
        
        # Check if already shared
        if user in file.shared_with:
            flash('File already shared with this user.', 'warning')
            return redirect(url_for('share_file', file_id=file_id))
        
        # Share the file
        statement = shares.insert().values(
            file_id=file.id,
            user_id=user.id,
            permission=form.permission.data
        )
        db.session.execute(statement)
        db.session.commit()
        
        # Record activity
        record_activity(current_user, 'share', file=file)
        
        flash(f'File shared with {user.email} successfully!', 'success')
        return redirect(url_for('view_folder', folder_id=file.folder_id or 0))
    
    # Get current shares
    shared_users = []
    for user in file.shared_with:
        # Get permission
        share = db.session.query(shares).filter_by(
            file_id=file.id,
            user_id=user.id
        ).first()
        
        shared_users.append({
            'username': user.username,
            'email': user.email,
            'permission': share.permission if share else 'view'
        })
    
    return render_template('share.html', title='Share File',
                         file=file,
                         form=form,
                         shared_users=shared_users)

@app.route('/unshare/<int:file_id>/<int:user_id>', methods=['POST'])
@login_required
def unshare_file(file_id, user_id):
    file = File.query.get_or_404(file_id)
    user = User.query.get_or_404(user_id)
    
    # Check if user has permission to unshare this file
    if file.owner_id != current_user.id:
        abort(403)
    
    # Remove share
    statement = shares.delete().where(
        and_(shares.c.file_id == file.id, shares.c.user_id == user.id)
    )
    db.session.execute(statement)
    db.session.commit()
    
    # Record activity
    record_activity(current_user, 'unshare', file=file)
    
    flash('File unshared successfully.', 'success')
    return redirect(url_for('share_file', file_id=file_id))

@app.route('/shared')
@login_required
def shared_with_me():
    # Get files shared with the current user
    shared_files = File.query.join(shares).filter(
        shares.c.user_id == current_user.id,
        File.is_trashed == False
    ).all()
    
    return render_template('shared.html', title='Shared with Me',
                         files=shared_files)

@app.route('/remove_shared/<int:file_id>', methods=['POST'])
@login_required
def remove_shared(file_id):
    # Get the file
    file = File.query.get_or_404(file_id)
    
    # Remove the share record for this user
    statement = shares.delete().where(
        and_(shares.c.file_id == file.id, shares.c.user_id == current_user.id)
    )
    db.session.execute(statement)
    db.session.commit()
    
    # Record activity
    record_activity(current_user, 'remove_shared', file=file)
    
    flash('File removed from your shared files.', 'success')
    return redirect(url_for('shared_with_me'))

@app.route('/trash')
@login_required
def trash():
    # Get files in trash
    trashed_files = File.query.filter_by(owner_id=current_user.id, is_trashed=True).all()
    
    return render_template('trash.html', title='Trash',
                         files=trashed_files)

@app.route('/restore/<int:file_id>', methods=['POST'])
@login_required
def restore_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to restore this file
    if file.owner_id != current_user.id:
        abort(403)
    
    # Restore from trash
    file.is_trashed = False
    db.session.commit()
    
    # Record activity
    record_activity(current_user, 'restore', file=file)
    
    flash('File restored successfully.', 'success')
    return redirect(url_for('trash'))

@app.route('/permanent_delete/<int:file_id>', methods=['POST'])
@login_required
def permanent_delete(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to delete this file
    if file.owner_id != current_user.id:
        abort(403)
    
    # Update user's storage usage
    current_user.storage_used -= file.file_size
    
    # Delete the file from disk
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file.file_path))
    except:
        pass  # File might not exist on disk
    
    # Delete from database
    db.session.delete(file)
    db.session.commit()
    
    # Record activity
    record_activity(current_user, 'permanent_delete', file=file)
    
    flash('File permanently deleted.', 'success')
    return redirect(url_for('trash'))

@app.route('/search')
@login_required
def search():
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('dashboard'))
    
    # Search files
    files = File.query.filter(
        File.owner_id == current_user.id,
        File.is_trashed == False,
        File.original_filename.ilike(f'%{query}%')
    ).all()
    
    # Search folders
    folders = Folder.query.filter(
        Folder.owner_id == current_user.id,
        Folder.name.ilike(f'%{query}%')
    ).all()
    
    return render_template('search.html', title='Search Results',
                         query=query,
                         files=files,
                         folders=folders)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    # Get recent activity
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).limit(10).all()
    
    # Format storage
    storage_used = current_user.storage_used
    storage_limit = current_user.storage_limit
    storage_percent = (storage_used / storage_limit) * 100 if storage_limit > 0 else 0
    
    storage_used_display = f"{storage_used / (1024 * 1024):.2f} MB" if storage_used < 1024 * 1024 * 1024 else f"{storage_used / (1024 * 1024 * 1024):.2f} GB"
    storage_limit_display = f"{storage_limit / (1024 * 1024 * 1024):.2f} GB"
    
    return render_template('profile.html', title='Profile',
                         form=form,
                         activities=activities,
                         storage_used=storage_used_display,
                         storage_limit=storage_limit_display,
                         storage_percent=storage_percent)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)