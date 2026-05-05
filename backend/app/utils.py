import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename: str) -> bool:
    # Validate the uploaded extension before saving the file on disk.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def build_storage_name(filename: str) -> str:
    # Generate a unique server-side filename to avoid collisions between users.
    ext = os.path.splitext(filename)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def secure_original_filename(filename: str) -> str:
    # Sanitize the visible filename to prevent unsafe path characters.
    return secure_filename(filename)
