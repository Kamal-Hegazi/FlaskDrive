from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

db = SQLAlchemy()

# Association table for file sharing
shares = db.Table('shares',
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('permission', db.String(20), default='view'),  # view, edit
    db.Column('shared_on', db.DateTime, default=datetime.utcnow)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    storage_used = db.Column(db.BigInteger, default=0)  # Storage used in bytes
    storage_limit = db.Column(db.BigInteger, default=1073741824)  # 1GB default
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic', 
                          foreign_keys='File.owner_id')
    folders = db.relationship('Folder', backref='owner', lazy='dynamic',
                            foreign_keys='Folder.owner_id')
    shared_files = db.relationship('File', secondary=shares, 
                                 backref=db.backref('shared_with', lazy='dynamic'))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = db.relationship('File', backref='folder', lazy='dynamic')
    subfolders = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), 
                               lazy='dynamic')
    
    def __repr__(self):
        return f'<Folder {self.name}>'


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.BigInteger)  # Size in bytes
    file_path = db.Column(db.String(255), unique=True, nullable=False)
    is_starred = db.Column(db.Boolean, default=False)
    is_trashed = db.Column(db.Boolean, default=False)
    is_encrypted = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_unique_filename(self):
        """Generate a unique filename to prevent collisions"""
        return f"{uuid.uuid4().hex}_{self.original_filename}"
    
    def get_full_path(self, app_config):
        """Get the full path to the file"""
        return os.path.join(app_config.UPLOAD_FOLDER, self.file_path)
    
    def __repr__(self):
        return f'<File {self.original_filename}>'


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # upload, download, share, rename, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='activities')
    file = db.relationship('File', backref='activities')
    folder = db.relationship('Folder', backref='activities')
    
    def __repr__(self):
        return f'<Activity {self.action} by {self.user.username}>'
