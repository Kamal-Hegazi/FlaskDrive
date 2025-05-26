# FlaskDrive API Reference

This document provides a reference for the web routes and functions implemented in FlaskDrive. It can serve as a basis for future API development.

## Authentication Routes

### Register

- **URL**: `/register`
- **Method**: `GET`, `POST`
- **Description**: Creates a new user account
- **Form Parameters**:
  - `username`: User's display name
  - `email`: User's email address
  - `password`: User's password
  - `confirm_password`: Password confirmation
- **Returns**: Redirects to login page on success

### Login

- **URL**: `/login`
- **Method**: `GET`, `POST`
- **Description**: Authenticates a user
- **Form Parameters**:
  - `email`: User's email address
  - `password`: User's password
  - `remember_me`: Boolean to enable persistent session
- **Returns**: Redirects to dashboard on success

### Logout

- **URL**: `/logout`
- **Method**: `GET`
- **Description**: Logs out the current user
- **Returns**: Redirects to home page

## File Management Routes

### Dashboard

- **URL**: `/dashboard`
- **Method**: `GET`
- **Description**: Displays user's dashboard with recent and starred files
- **Authentication**: Required
- **Returns**: Dashboard page with file stats and listings

### View Folder

- **URL**: `/folder/<int:folder_id>`
- **Method**: `GET`
- **Description**: Displays contents of a specific folder
- **URL Parameters**:
  - `folder_id`: ID of the folder to view
- **Authentication**: Required
- **Returns**: Folder view with files and subfolders

### Upload File

- **URL**: `/upload`
- **Method**: `POST`
- **Description**: Uploads a new file
- **Form Parameters**:
  - `file`: File to upload
  - `folder_id`: Destination folder ID
- **Authentication**: Required
- **Returns**: Redirects to folder view on success

### Create Folder

- **URL**: `/create_folder`
- **Method**: `POST`
- **Description**: Creates a new folder
- **Form Parameters**:
  - `name`: Folder name
  - `parent_id`: Parent folder ID
- **Authentication**: Required
- **Returns**: Redirects to parent folder view on success

### Download File

- **URL**: `/download/<int:file_id>`
- **Method**: `GET`
- **Description**: Downloads a file, decrypting if necessary
- **URL Parameters**:
  - `file_id`: ID of the file to download
- **Authentication**: Required
- **Returns**: File download response

### Preview File

- **URL**: `/preview/<int:file_id>`
- **Method**: `GET`
- **Description**: Displays a preview of the file if possible
- **URL Parameters**:
  - `file_id`: ID of the file to preview
- **Authentication**: Required
- **Returns**: File preview or redirect to download

### Delete File

- **URL**: `/delete/<int:file_id>`
- **Method**: `POST`
- **Description**: Moves a file to trash
- **URL Parameters**:
  - `file_id`: ID of the file to delete
- **Authentication**: Required
- **Returns**: Redirects to folder view on success

### Delete Folder

- **URL**: `/delete_folder/<int:folder_id>`
- **Method**: `POST`
- **Description**: Deletes a folder and its contents
- **URL Parameters**:
  - `folder_id`: ID of the folder to delete
- **Authentication**: Required
- **Returns**: Redirects to parent folder or dashboard

### Star/Unstar File

- **URL**: `/star/<int:file_id>`
- **Method**: `POST`
- **Description**: Toggles the starred status of a file
- **URL Parameters**:
  - `file_id`: ID of the file to star/unstar
- **Authentication**: Required
- **Returns**: Redirects to folder view on success

### Rename File

- **URL**: `/rename/<int:file_id>`
- **Method**: `GET`, `POST`
- **Description**: Renames a file
- **URL Parameters**:
  - `file_id`: ID of the file to rename
- **Form Parameters**:
  - `filename`: New file name
- **Authentication**: Required
- **Returns**: Redirects to folder view on success

## File Sharing Routes

### Share File

- **URL**: `/share/<int:file_id>`
- **Method**: `GET`, `POST`
- **Description**: Shares a file with another user
- **URL Parameters**:
  - `file_id`: ID of the file to share
- **Form Parameters**:
  - `email`: Email of user to share with
  - `permission`: Permission level (view, edit)
- **Authentication**: Required
- **Returns**: Redirects to folder view or share management page

### Unshare File

- **URL**: `/unshare/<int:file_id>/<int:user_id>`
- **Method**: `POST`
- **Description**: Removes file sharing with a specific user
- **URL Parameters**:
  - `file_id`: ID of the shared file
  - `user_id`: ID of user to remove sharing with
- **Authentication**: Required
- **Returns**: Redirects to share management page

### Shared With Me

- **URL**: `/shared`
- **Method**: `GET`
- **Description**: Displays files shared with the current user
- **Authentication**: Required
- **Returns**: Shared files listing page

## Trash Management Routes

### Trash

- **URL**: `/trash`
- **Method**: `GET`
- **Description**: Displays files in trash
- **Authentication**: Required
- **Returns**: Trash view with deleted files

### Restore File

- **URL**: `/restore/<int:file_id>`
- **Method**: `POST`
- **Description**: Restores a file from trash
- **URL Parameters**:
  - `file_id`: ID of the file to restore
- **Authentication**: Required
- **Returns**: Redirects to trash view on success

### Permanent Delete

- **URL**: `/permanent_delete/<int:file_id>`
- **Method**: `POST`
- **Description**: Permanently deletes a file
- **URL Parameters**:
  - `file_id`: ID of the file to permanently delete
- **Authentication**: Required
- **Returns**: Redirects to trash view on success

## Search Routes

### Search

- **URL**: `/search`
- **Method**: `GET`
- **Description**: Searches for files and folders
- **Query Parameters**:
  - `query`: Search term
- **Authentication**: Required
- **Returns**: Search results page

## User Profile Routes

### Profile

- **URL**: `/profile`
- **Method**: `GET`, `POST`
- **Description**: Displays and updates user profile
- **Form Parameters**:
  - `username`: New username
  - `email`: New email
- **Authentication**: Required
- **Returns**: Profile page or redirect on update

## Error Handlers

### 404 Not Found

- **URL**: Automatic
- **Method**: Any
- **Description**: Handles requests for non-existent resources
- **Returns**: Custom 404 page

### 403 Forbidden

- **URL**: Automatic
- **Method**: Any
- **Description**: Handles unauthorized access attempts
- **Returns**: Custom 403 page

### 500 Internal Server Error

- **URL**: Automatic
- **Method**: Any
- **Description**: Handles server errors
- **Returns**: Custom 500 page

## Helper Functions

### Record Activity

- **Function**: `record_activity(user, action, file=None, folder=None)`
- **Description**: Records user activity for auditing
- **Parameters**:
  - `user`: User performing the action
  - `action`: Action type
  - `file`: File being acted upon (optional)
  - `folder`: Folder being acted upon (optional)
- **Returns**: None

### Encrypt File

- **Function**: `encrypt_file(input_file_path)`
- **Description**: Encrypts a file using Fernet encryption
- **Parameters**:
  - `input_file_path`: Path to file to encrypt
- **Returns**: Boolean success status

### Decrypt File

- **Function**: `decrypt_file(input_file_path, output_file_path=None)`
- **Description**: Decrypts a file, optionally to a new location
- **Parameters**:
  - `input_file_path`: Path to encrypted file
  - `output_file_path`: Optional output path (if None, creates a temp file)
- **Returns**: Path to decrypted file

### Save File

- **Function**: `save_file(file, owner, encrypt=True)`
- **Description**: Saves an uploaded file to disk and database
- **Parameters**:
  - `file`: Uploaded file object
  - `owner`: User who owns the file
  - `encrypt`: Whether to encrypt the file
- **Returns**: Created File object

### Get Breadcrumbs

- **Function**: `get_breadcrumbs(folder)`
- **Description**: Generates navigation breadcrumbs for folder hierarchy
- **Parameters**:
  - `folder`: Folder to generate breadcrumbs for
- **Returns**: List of folders in path (reversed)

## Future API Development

This route documentation provides a foundation for developing a RESTful API. To implement a formal API:

1. Create new routes with `/api/` prefix
2. Implement JSON responses instead of HTML templates
3. Add authentication using tokens or OAuth
4. Document the API with Swagger/OpenAPI specifications

Example API endpoint:

```python
@app.route('/api/files', methods=['GET'])
@auth_required
def api_list_files():
    files = File.query.filter_by(owner_id=current_user.id, is_trashed=False).all()
    return jsonify({
        'files': [
            {
                'id': file.id,
                'name': file.original_filename,
                'size': file.file_size,
                'created_at': file.created_at.isoformat(),
                'updated_at': file.updated_at.isoformat(),
                'starred': file.is_starred,
                'folder_id': file.folder_id
            } for file in files
        ]
    })
```
