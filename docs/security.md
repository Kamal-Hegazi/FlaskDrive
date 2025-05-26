# FlaskDrive Security Guide

This document outlines the security features and best practices implemented in FlaskDrive.

## Overview

FlaskDrive implements multiple layers of security to protect user data:

1. **Authentication security**
2. **Data encryption**
3. **Access control**
4. **Web security measures**
5. **Configuration security**

## Authentication Security

### Password Security

- **Password Hashing**: User passwords are never stored in plaintext. They are hashed using Werkzeug's secure password hashing functions, which use PBKDF2 with SHA-256 hash.

  ```python
  # Password hashing (in models.py)
  @password.setter
  def password(self, password):
      self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
      return check_password_hash(self.password_hash, password)
  ```

- **Password Requirements**: The registration form enforces password complexity requirements.

### Session Security

- **Flask-Login**: Handles user session management securely.
- **Remember Me Functionality**: Implements secure persistent sessions when requested.
- **Session Expiry**: Sessions expire after a period of inactivity.

## Data Encryption

### File Encryption

Files are encrypted at rest using Fernet symmetric encryption, which provides:

- **AES-128** in CBC mode with PKCS7 padding
- **HMAC** using SHA-256 for authentication
- **Initialization vectors** (IV) to prevent repetition

```python
# Encryption (in app.py)
def encrypt_file(input_file_path):
    with open(input_file_path, 'rb') as f:
        data = f.read()
    
    fernet = get_encryption_key()
    encrypted_data = fernet.encrypt(data)
    
    with open(input_file_path, 'wb') as f:
        f.write(encrypted_data)
```

### Key Management

- **Environment Variables**: Encryption keys are stored in environment variables, not in the codebase.
- **Key Rotation**: Support for key rotation can be implemented by adding a key version column to the File model.

### Secure Downloads

When downloading encrypted files, they are:
1. Decrypted to a temporary file
2. Served to the user
3. Temporary file is deleted once the response is complete

## Access Control

### Permission System

- **Ownership**: Every file and folder has an explicit owner.
- **Share Permissions**: Granular sharing permissions (view, edit).
- **Authorization Checks**: All routes verify user permissions before allowing operations.

```python
# Example authorization check (in app.py)
@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user has permission to download this file
    is_owner = file.owner_id == current_user.id
    is_shared = current_user in file.shared_with
    
    if not (is_owner or is_shared):
        abort(403)
    
    # Continue with download...
```

### Route Protection

- **@login_required**: Ensures authenticated access to protected routes.
- **Function-level Checks**: Additional permission checks inside route functions.

## Web Security Measures

### CSRF Protection

- **Flask-WTF**: All forms include CSRF tokens to prevent cross-site request forgery.
- **Token Validation**: CSRF tokens are validated on form submission.

### Input Validation

- **WTForms Validation**: All user inputs are validated before processing.
- **File Type Checking**: Uploaded files are checked for type and size constraints.

### Secure File Handling

- **Secure Filenames**: Filenames are sanitized using `secure_filename()`.
- **Random Identifiers**: Files are stored with random identifiers, not original names.

### Error Handling

- **Custom Error Pages**: Prevents information leakage through error messages.
- **Exception Handling**: Proper exception handling to prevent application crashes.

## Configuration Security

### Environment Variables

- **Sensitive Information**: All sensitive configuration is stored in environment variables.
- **.env File**: For development, variables are loaded from a .env file (not committed to version control).

### Secure Defaults

- **Restrictive Permissions**: File and folder permissions are set restrictively.
- **Secure Headers**: Secure HTTP headers are set to prevent common attacks.

## Security Recommendations

### For Deployment

1. **HTTPS**: Always deploy FlaskDrive with HTTPS in production.
2. **Key Management**: Use a secure vault service for encryption keys in production.
3. **Regular Updates**: Keep all dependencies updated to patch security vulnerabilities.
4. **Firewall Configuration**: Configure a firewall to restrict access to the server.

### For Development

1. **Local Environment**: Only use the .env file for local development.
2. **Git Security**: Use .gitignore to prevent committing sensitive files.
3. **Dependency Scanning**: Regularly scan dependencies for vulnerabilities.

## Security Auditing

### Activity Logging

- All security-relevant user actions are logged in the Activity model.
- Logs include user ID, action type, and timestamp.

### Audit Trail

- File modifications, sharing changes, and authentication events are recorded.
- Administrators can review the audit trail for suspicious activity.

## Reporting Security Issues

If you discover a security vulnerability in FlaskDrive, please follow responsible disclosure practices:

1. **Do not disclose publicly**: Avoid posting about the vulnerability in public forums.
2. **Contact information**: Email security@example.com with details about the vulnerability.
3. **Provide details**: Include steps to reproduce, potential impact, and any possible mitigations.

## Security Roadmap

Future security enhancements planned for FlaskDrive:

1. **Two-factor authentication**
2. **End-to-end encryption for shared files**
3. **File integrity verification**
4. **Advanced audit logging**
5. **Automated security scanning**
