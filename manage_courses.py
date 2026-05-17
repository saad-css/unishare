import os
import sys
from dotenv import load_dotenv

# ------------------------------------------------------------------
# DYNAMIC PATH RESOLUTION & ENV LOADING (MUST BE FIRST)
# Locate and load the .env file immediately before initializing Flask.
# ------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Automatically injects project directories into python path to prevent ModuleNotFoundError.
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'backend'))
sys.path.append(os.path.join(current_dir, 'backend', 'app'))

# ------------------------------------------------------------------
# SECURE AND ADAPTIVE IMPORTS
# Using try/except fallbacks to handle the "app" subdirectory structure smoothly.
# ------------------------------------------------------------------
try:
    # Try importing using the standard factory pattern structure
    from backend import create_app, db
except (ModuleNotFoundError, ImportError):
    try:
        # Fallback if create_app is nested directly under backend/app
        from backend.app import create_app, db
    except (ModuleNotFoundError, ImportError):
        # Last resort: absolute import if sys.path is already injected
        from app import create_app, db

try:
    # Try importing from the nested app subdirectory
    from backend.app.models import User, Major, Course, SharedFile, FileReport
except (ModuleNotFoundError, ImportError):
    try:
        # Fallback to standard top-level package structure
        from backend.models import User, Major, Course, SharedFile, FileReport
    except (ModuleNotFoundError, ImportError):
         # Final fallback
        from models import User, Major, Course, SharedFile, FileReport

# Initialize the Flask application instance to load the active database connection context
app = create_app()

# ------------------------------------------------------------------
# CENTRAL DATA SOURCE (The list you control)
# Simply add, remove, or edit majors and courses here.
# ------------------------------------------------------------------
MAJORS_DATA = [
    "Computer Science",
    "Information Systems",
    "Software Engineering",
    "Cyber Security"
]

COURSES_DATA = [
    {"name": "Database Systems", "major": "Computer Science"},
    {"name": "Artificial Intelligence", "major": "Computer Science"},
    {"name": "Network Security", "major": "Cyber Security"},
    {"name": "Web Development", "major": "Information Systems"},
]

# ------------------------------------------------------------------
# THE SYNC ENGINE (How the programmer updates the DB)
# ------------------------------------------------------------------
def sync_database():
    """
    Core function to synchronize the PostgreSQL database with the lists defined above.
    It cleans up old data in a strict cascading order to satisfy FK constraints.
    """
    # Wrap database transactions inside Flask's application context to bind the PostgreSQL connection
    with app.app_context():
        print("[System] Connecting to PostgreSQL on Render...")
        
        try:
            # Step A: Clear child tables first to satisfy foreign key constraints
            # Deleting FileReport -> SharedFile -> Course -> Major prevents ForeignKeyViolation
            try:
                db.session.query(FileReport).delete()
                print("[Clean] Old File Reports wiped successfully.")
            except Exception as clean_err:
                print(f"[Clean Note] FileReport table skip/empty: {clean_err}")

            try:
                db.session.query(SharedFile).delete()
                print("[Clean] Old Shared Files wiped successfully.")
            except Exception as clean_err:
                print(f"[Clean Note] SharedFile table skip/empty: {clean_err}")

            # Step B: Clear parent academic tables safely
            db.session.query(Course).delete()
            db.session.query(Major).delete()
            db.session.commit()
            print("[Clean] Old Majors and Courses wiped successfully.")

            # Step C: Re-build Majors dynamically and store their IDs in a map
            major_map = {}
            for m_name in MAJORS_DATA:
                new_major = Major(name=m_name)
                db.session.add(new_major)
                db.session.flush() # Flushing retrieves the auto-generated ID from PostgreSQL before commit
                major_map[m_name] = new_major.id
                print(f"[Major] Created: {m_name}")

            # Step D: Re-build Courses and link them to their respective Majors
            for item in COURSES_DATA:
                c_name = item["name"]
                m_name = item["major"]
                
                if m_name in major_map:
                    new_course = Course(name=c_name, major_id=major_map[m_name])
                    db.session.add(new_course)
                    print(f"[Course] Linked: {c_name} -> {m_name}")

            # Commit the session to push all changes permanently to Render cloud
            db.session.commit()
            print("\n[Final] Database is now fully synchronized and LIVE on Render!")
            
        except Exception as e:
            # Rollback the session in case of any database failures to protect structural integrity
            db.session.rollback()
            print(f"[Critical Error] Database sync failed: {e}")

if __name__ == "__main__":
    # Execute the synchronization engine
    sync_database()