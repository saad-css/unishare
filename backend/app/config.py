import os
from pathlib import Path

# Resolve the base directory of the project to enable reliable local path fallbacks
BASE_DIR = Path(__file__).resolve().parent.parent

# Define and dynamically create the secure directory for physical file uploads
UPLOAD_FOLDER = BASE_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class Config:
    # Cryptographic key used to secure active user sessions and encrypt cookies safely
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')

    # Fetch the production database URL from the cloud host (Render environment)
    # Fallback to a local SQLite database file to ensure smooth offline testing
    _raw_db_url = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + str(BASE_DIR / 'unishare.db')
    )

    # SQLAlchemy 1.4+ strictly requires 'postgresql://' instead of the legacy 'postgres://'
    # This conditional block cleans the URL string provided dynamically by the Render cloud server
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)

    # Define the exact uppercase variable required by Flask-SQLAlchemy to establish a connection
    SQLALCHEMY_DATABASE_URI = _raw_db_url

    # Disable tracking modifications to save server memory resources and optimize execution speed
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Set a secure upper limit for HTTP multipart file uploads (restricted to 20 MB)
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # Convert the upload directory path to a standard string format for Flask compatibility
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)

    # Strict file extensions whitelist to defend the system from executing malicious code
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'ppt', 'pptx',
        'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'zip'
    }