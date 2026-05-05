from flask import Flask
from sqlalchemy import text

from .config import Config
from .extensions import db, cors, migrate
from .routes import api
from .seed import seed_data


def create_app() -> Flask:
    # Application factory used by local runs and production.
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask extensions.
    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # Register API routes.
    app.register_blueprint(api)

    with app.app_context():
        # Create missing tables if they do not exist.
        db.create_all()

        # Add missing columns/tables for old databases.
        try:
            # Add admin flag to users table.
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE NOT NULL"
            ))

            # Add review status to shared files.
            db.session.execute(text(
                "ALTER TABLE shared_files ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'pending_review' NOT NULL"
            ))

            # Add review reason to shared files.
            db.session.execute(text(
                "ALTER TABLE shared_files ADD COLUMN IF NOT EXISTS review_reason VARCHAR(255)"
            ))

            # Add admin note to reports table for old databases.
            db.session.execute(text(
                "ALTER TABLE file_reports ADD COLUMN IF NOT EXISTS admin_note VARCHAR(255)"
            ))

            db.session.commit()

        except Exception as e:
            # Roll back if a migration step fails.
            db.session.rollback()
            print("Migration warning:", e)

        # Seed majors/courses.
        seed_data()

    return app