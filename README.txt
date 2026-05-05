UniShare Full Project
====================

This package contains:
- backend/  -> Flask API + SQLAlchemy + PostgreSQL-ready setup
- frontend/ -> KivyMD client app with separated screens, widgets, and core files

Backend quick start
-------------------
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
python run.py

Frontend quick start
--------------------
cd frontend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Update frontend/unishare/core/config.py with your backend URL
python main.py

Important notes
---------------
- For production, set DATABASE_URL to PostgreSQL.
- For production, run backend with Gunicorn using wsgi.py.
- All core operations include English comments inside the code as requested.
