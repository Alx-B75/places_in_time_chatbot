import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Dynamically resolve project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- CHAT DB SETUP ---
CHAT_DB_PATH = os.path.join(BASE_DIR, "data", "chat_history.db")
DATABASE_URL = f"sqlite:///{CHAT_DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- FIGURE DB SETUP ---
FIGURE_DB_PATH = os.path.join(BASE_DIR, "data", "figures.db")
FIGURE_DB_URL = f"sqlite:///{FIGURE_DB_PATH}"

engine_figure = create_engine(FIGURE_DB_URL, connect_args={"check_same_thread": False})
SessionLocalFigure = sessionmaker(autocommit=False, autoflush=False, bind=engine_figure)

Base = declarative_base()


def get_db_chat():
    """
    Dependency for getting a SQLAlchemy session for chat_history.db.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_figure():
    """
    Dependency for getting a SQLAlchemy session for figures.db.
    """
    db = SessionLocalFigure()
    try:
        yield db
    finally:
        db.close()


def get_chroma_retriever():
    """
    Returns the vector search function for figure context using ChromaDB.
    """
    from backend.vector.context_retriever import search_figure_context
    return search_figure_context
