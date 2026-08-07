import os
import sys

# Add the backend directory to sys.path so we can import from models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import create_app
from models import db, Project
from sqlalchemy import text

app = create_app()

with app.app_context():
    # SQLite workaround: Since we just added a UNIQUE constraint to Project.name,
    # and SQLAlchemy's create_all won't alter existing tables in SQLite,
    # we will drop and recreate the projects table. Note: this drops existing projects.
    print("Dropping existing projects table...")
    Project.__table__.drop(db.engine, checkfirst=True)
    print("Creating updated projects table with unique constraint...")
    Project.__table__.create(db.engine, checkfirst=True)
    print("Projects table updated successfully.")
