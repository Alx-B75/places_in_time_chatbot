# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -- Section commented to enable render path
"""PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

os.makedirs(DATA_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'chat_history.db')}" """

# --- Path Calculation for Render Disk ---
DATA_DIR = "/data"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'chat_history.db')}"

# --- Engine and Session Setup ---
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Dependency for getting a DB session ---
def get_db_chat():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()