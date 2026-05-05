from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

# Shared Flask extensions are initialized here and attached to the app in create_app().
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
