import os
import re
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from sqlalchemy.exc import IntegrityError
from .extensions import db
from .models import User, Major, Course, SharedFile, FileReport
from .utils import allowed_file, build_storage_name, secure_original_filename
from .reviewer import review_file_content

api = Blueprint('api', __name__)

# Email validation regex.
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
ADMIN_EMAIL = 's3@gmail.com'


def serialize_file(row: SharedFile) -> dict:
    # Convert a SharedFile database row into a JSON-ready dictionary.
    return {
        'id': row.id,
        'filename': row.filename,
        'storage_name': row.storage_name,
        'course': row.course.name if row.course else '',
        'uploader': row.uploader.full_name if row.uploader else '',
        'status': row.status,
        'review_reason': row.review_reason,
        'created_at': row.created_at.isoformat(),
    }


def serialize_report(row: FileReport) -> dict:
    # Convert a FileReport database row into a JSON-ready dictionary.
    return {
        'id': row.id,
        'file_id': row.file_id,
        'filename': row.file.filename if row.file else '',
        'storage_name': row.file.storage_name if row.file else '',
        'course': row.file.course.name if row.file and row.file.course else '',
        'uploader': row.file.uploader.full_name if row.file and row.file.uploader else '',
        'reported_by': row.reporter.full_name if row.reporter else '',
        'reason': row.reason,
        'status': row.status,
        'admin_note': row.admin_note,
        'created_at': row.created_at.isoformat(),
    }


@api.route('/')
def home():
    # Simple health endpoint to confirm the API is running.
    return jsonify({'status': 'ok', 'message': 'UniShare API is running'})


@api.get('/health')
def health_check():
    # Used by hosting platforms to verify the service is alive.
    return jsonify({'status': 'ok'})


@api.post('/signup')
def signup():
    # Register a new user using email and password.
    payload = request.get_json(silent=True) or {}
    full_name = (payload.get('full_name') or '').strip()
    email = (payload.get('email') or '').strip().lower()
    password = (payload.get('password') or '').strip()

    # Validate required fields.
    if not all([full_name, email, password]):
        return jsonify({'error': 'Please fill in all fields'}), 400

    # Validate email format.
    if not re.match(EMAIL_REGEX, email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Grant admin access if the registered email matches the admin email.
    user = User(full_name=full_name, email=email, is_admin=(email == ADMIN_EMAIL))
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already registered'}), 409

    return jsonify({'message': 'Account created successfully'}), 201


@api.post('/login')
def login():
    # Authenticate user using email and password.
    payload = request.get_json(silent=True) or {}
    email = (payload.get('email') or '').strip().lower()
    password = (payload.get('password') or '').strip()

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Force the configured admin email to be admin even for old accounts.
    if email == ADMIN_EMAIL and not user.is_admin:
        user.is_admin = True
        db.session.commit()

    return jsonify({
        'user_id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'is_admin': user.is_admin,
    }), 200


@api.get('/user_info/<int:user_id>')
def user_info(user_id: int):
    # Return user profile info.
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'is_admin': user.is_admin,
        'files_count': len(user.files),
    })


@api.get('/majors')
def majors():
    # Return all majors.
    rows = Major.query.order_by(Major.name.asc()).all()
    return jsonify([{'id': row.id, 'name': row.name} for row in rows])


@api.get('/courses/<int:major_id>')
def courses(major_id: int):
    # Return all courses for a given major.
    rows = Course.query.filter_by(major_id=major_id).order_by(Course.name.asc()).all()
    return jsonify([{'id': row.id, 'name': row.name} for row in rows])


@api.get('/files/<int:course_id>')
def files(course_id: int):
    # Return only approved files for students.
    rows = SharedFile.query.filter_by(course_id=course_id, status='approved').order_by(SharedFile.created_at.desc()).all()
    return jsonify([serialize_file(row) for row in rows])


@api.post('/upload')
def upload():
    # Upload a file and store its metadata in the database.
    course_id = request.form.get('course_id', type=int)
    user_id = request.form.get('user_id', type=int)
    uploaded_file = request.files.get('file')

    # Validate request data.
    if not course_id or not user_id or not uploaded_file:
        return jsonify({'error': 'Missing upload data'}), 400

    course = Course.query.get(course_id)
    user = User.query.get(user_id)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Clean and validate filename.
    original_name = secure_original_filename(uploaded_file.filename or '')

    if not original_name:
        return jsonify({'error': 'Invalid filename'}), 400

    if not allowed_file(original_name):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        # Make sure the upload folder exists.
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the physical file with a unique server-side name.
        storage_name = build_storage_name(original_name)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], storage_name)
        uploaded_file.save(upload_path)

        # Review file content automatically.
        status, review_reason = review_file_content(upload_path, course.name)

        # Prevent invalid status values from breaking the app.
        if status not in ['approved', 'rejected', 'pending_review']:
            status = 'pending_review'
            review_reason = 'File needs manual admin review'

        record = SharedFile(
            course_id=course.id,
            user_id=user.id,
            filename=original_name,
            storage_name=storage_name,
            status=status,
            review_reason=review_reason,
        )

        db.session.add(record)
        db.session.commit()

        return jsonify({
            'message': 'File uploaded successfully',
            'file': serialize_file(record),
            'status': status,
            'review_reason': review_reason,
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Upload failed")

        return jsonify({
            'error': 'Upload failed',
            'details': str(e)
        }), 500


@api.get('/download/<path:storage_name>')
def download(storage_name: str):
    # Download an approved file by its stored name.
    record = SharedFile.query.filter_by(storage_name=storage_name).first_or_404()
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        record.storage_name,
        as_attachment=True,
        download_name=record.filename,
    )


@api.post('/files/<int:file_id>/report')
def report_file(file_id: int):
    # Allow users to report a file. The report appears immediately in Admin Panel.
    payload = request.get_json(silent=True) or {}
    user_id = payload.get('user_id')
    reason = (payload.get('reason') or 'Reported by user').strip()

    file_row = SharedFile.query.get_or_404(file_id)
    user = User.query.get_or_404(user_id)

    report = FileReport(file_id=file_row.id, user_id=user.id, reason=reason, status='open')
    db.session.add(report)
    db.session.commit()

    return jsonify({'message': 'Report submitted successfully', 'report': serialize_report(report)}), 201


@api.get('/admin/pending-files')
def admin_pending_files():
    # Return files that need manual admin review.
    rows = SharedFile.query.filter_by(status='pending_review').order_by(SharedFile.created_at.desc()).all()
    return jsonify([serialize_file(row) for row in rows])


@api.post('/admin/files/<int:file_id>/approve')
def admin_approve_file(file_id: int):
    # Approve a pending file manually.
    row = SharedFile.query.get_or_404(file_id)
    row.status = 'approved'
    row.review_reason = 'Approved by admin'
    db.session.commit()
    return jsonify({'message': 'File approved successfully', 'file': serialize_file(row)})


@api.post('/admin/files/<int:file_id>/reject')
def admin_reject_file(file_id: int):
    # Reject a pending file manually.
    row = SharedFile.query.get_or_404(file_id)
    row.status = 'rejected'
    row.review_reason = 'Rejected by admin'
    db.session.commit()
    return jsonify({'message': 'File rejected successfully', 'file': serialize_file(row)})


@api.get('/admin/reports')
def admin_reports():
    # Return reports that need admin decision.
    rows = FileReport.query.filter_by(status='open').order_by(FileReport.created_at.desc()).all()
    return jsonify([serialize_report(row) for row in rows])


@api.post('/admin/reports/<int:report_id>/accept')
def admin_accept_report(report_id: int):
    # Accept a report and reject the reported file.
    report = FileReport.query.get_or_404(report_id)
    report.status = 'accepted'
    report.admin_note = 'Accepted by admin'

    if report.file:
        report.file.status = 'rejected'
        report.file.review_reason = f'Report accepted: {report.reason}'

    db.session.commit()
    return jsonify({'message': 'Report accepted successfully', 'report': serialize_report(report)})


@api.post('/admin/reports/<int:report_id>/reject')
def admin_reject_report(report_id: int):
    # Reject a report and keep the file visible.
    report = FileReport.query.get_or_404(report_id)
    report.status = 'rejected'
    report.admin_note = 'Rejected by admin'
    db.session.commit()
    return jsonify({'message': 'Report rejected successfully', 'report': serialize_report(report)})

@api.get('/fix-db')
def fix_db():
    db.session.execute(db.text("ALTER TABLE shared_files DROP COLUMN IF EXISTS rating;"))
    db.session.commit()
    return jsonify({'message': 'Database fixed successfully'})