# FlaskDrive Database Schema

This document outlines the database structure of FlaskDrive, including tables, relationships, and key fields.

## Entity-Relationship Diagram

```
┌─────────┐     ┌──────────┐     ┌─────────┐
│   User  │─1─┬─┤  Folder  │─1─┬─┤  File   │
└─────────┘   └┬┴──────────┘   └┬┴─────────┘
              │                 │
              │                 │
              │                 │
┌─────────────┴─┐     ┌────────┴───────┐
│   Activity    │     │     shares      │
└───────────────┘     └──────────────┬─┘
                                     │
                                     │
                                     │
                                  ┌──┴───┐
                                  │ User │
                                  └──────┘
```

## Tables

### User

Stores user account information and authentication data.

| Column         | Type             | Description                     |
|----------------|------------------|---------------------------------|
| id             | Integer (PK)     | Unique identifier               |
| username       | String(64)       | User's display name             |
| email          | String(120)      | User's email address            |
| password_hash  | String(128)      | Hashed password                 |
| storage_used   | BigInteger       | Storage used in bytes           |
| storage_limit  | BigInteger       | Storage limit in bytes (1GB default) |
| created_at     | DateTime         | Account creation timestamp      |

**Relationships:**
- One-to-many with File (as owner)
- One-to-many with Folder (as owner)
- Many-to-many with File (through shares)
- One-to-many with Activity

### Folder

Represents directories in the user's file structure.

| Column         | Type             | Description                     |
|----------------|------------------|---------------------------------|
| id             | Integer (PK)     | Unique identifier               |
| name           | String(255)      | Folder name                     |
| owner_id       | Integer (FK)     | Reference to User.id            |
| parent_id      | Integer (FK)     | Reference to Folder.id (self-reference) |
| created_at     | DateTime         | Creation timestamp              |
| updated_at     | DateTime         | Last modification timestamp     |

**Relationships:**
- Many-to-one with User (owner)
- Self-referential for parent-child relationship
- One-to-many with File (files in folder)
- One-to-many with Activity

### File

Stores metadata about uploaded files (not the actual file content).

| Column            | Type             | Description                     |
|-------------------|------------------|---------------------------------|
| id                | Integer (PK)     | Unique identifier               |
| filename          | String(255)      | Unique filename in storage      |
| original_filename | String(255)      | Original user's filename        |
| file_type         | String(100)      | MIME type                       |
| file_size         | BigInteger       | Size in bytes                   |
| file_path         | String(255)      | Path relative to uploads folder |
| is_starred        | Boolean          | If file is favorited            |
| is_trashed        | Boolean          | If file is in trash             |
| is_encrypted      | Boolean          | If file is encrypted            |
| owner_id          | Integer (FK)     | Reference to User.id            |
| folder_id         | Integer (FK)     | Reference to Folder.id          |
| created_at        | DateTime         | Upload timestamp                |
| updated_at        | DateTime         | Last modification timestamp     |

**Relationships:**
- Many-to-one with User (owner)
- Many-to-one with Folder (containing folder)
- Many-to-many with User (through shares)
- One-to-many with Activity

### Activity

Tracks user actions for audit and history purposes.

| Column         | Type             | Description                     |
|----------------|------------------|---------------------------------|
| id             | Integer (PK)     | Unique identifier               |
| user_id        | Integer (FK)     | Reference to User.id            |
| file_id        | Integer (FK)     | Reference to File.id (optional) |
| folder_id      | Integer (FK)     | Reference to Folder.id (optional) |
| action         | String(50)       | Type of action performed        |
| timestamp      | DateTime         | When the action occurred        |

**Relationships:**
- Many-to-one with User
- Many-to-one with File (optional)
- Many-to-one with Folder (optional)

### shares (Association Table)

Manages file sharing between users.

| Column         | Type             | Description                     |
|----------------|------------------|---------------------------------|
| file_id        | Integer (PK, FK) | Reference to File.id            |
| user_id        | Integer (PK, FK) | Reference to User.id            |
| permission     | String(20)       | Permission level (view, edit)   |
| shared_on      | DateTime         | When sharing was created        |

## Indexes

The following indexes are recommended for optimal performance:

### User Table
- Unique index on `email`
- Unique index on `username`

### File Table
- Index on `owner_id`
- Index on `folder_id`
- Index on `is_trashed`
- Index on `is_starred`
- Unique index on `file_path`
- Composite index on `owner_id, is_trashed, original_filename` for search

### Folder Table
- Index on `owner_id`
- Index on `parent_id`
- Composite index on `owner_id, parent_id`

### Activity Table
- Index on `user_id`
- Index on `timestamp`

## Schema Creation

The database schema is automatically created by SQLAlchemy when the application starts:

```python
with app.app_context():
    db.create_all()
```

## Migrations

For database migrations when schema changes, Flask-Migrate (based on Alembic) is used:

```bash
# Initialize migrations
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Data Relationships

### User Ownership
- Each User owns multiple Files and Folders
- When a User is deleted, all owned Files and Folders should be deleted

### Folder Hierarchy
- Folders can contain Files and other Folders (subfolders)
- The parent-child relationship is managed through the `parent_id` field
- Each User has a root folder (`parent_id` is NULL)

### File Sharing
- Files can be shared with multiple Users
- The `shares` table manages these many-to-many relationships
- Each share record includes permission level and sharing timestamp
