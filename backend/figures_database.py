import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Robust Path Calculation ---
# This calculates the absolute path to the project's root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# This creates an absolute path to the data directory
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# Create the data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)
# This creates the final, absolute path to the database file
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'figures.db')}"

# --- Engine and Session Setup ---
engine_figure = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
FigureSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_figure)
FigureBase = declarative_base()