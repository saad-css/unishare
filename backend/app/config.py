import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder where uploaded files will be stored
UPLOAD_FOLDER = BASE_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


class Config:
    # Secret key used for sessions and security
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')

    # Get database URL from environment variables (Render provides this)
    db_url = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + str(BASE_DIR / 'unishare.db')  # fallback for local use
    )

    # Fix PostgreSQL URL format (Render use "postgres://")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Final database connection string
    SQLALCHEMY_DATABASE_URI = db_url

    # Disable tracking modifications (performance optimization)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Maximum upload size (20 MB)
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # Upload folder path
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)

    # Allowed file types
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'ppt', 'pptx',
        'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'zip'
    }    
