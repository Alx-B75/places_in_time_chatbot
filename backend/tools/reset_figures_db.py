"""
reset_figures_db.py

Wipes and recreates all tables in the figures.db file under /data.
"""

import os
from sqlalchemy import create_engine
from backend.models import Base

# Ensure data directory exists
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "figures.db")

print(f"🔍 Resetting database at: {DB_PATH}")

# Ensure /data directory exists
os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)

# Recreate engine with absolute path
engine = create_engine(f"sqlite:///{DB_PATH}")

# Drop and recreate all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("✅ All tables dropped and recreated.")
