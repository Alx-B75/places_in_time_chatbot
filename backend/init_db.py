import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_dir)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from backend.database import engine, engine_figure # Import both engines
from backend.models import Base

def init_db():
    """
    Creates all tables defined in the SQLAlchemy models for both databases.
    """
    print("📂 Current working directory:", os.getcwd())
    print("📄 Target CHAT DB path:", os.path.abspath("./data/chat_history.db"))
    print("📄 Target FIGURE DB path:", os.path.abspath("./data/figures.db"))

    # Create tables for the chat history database
    Base.metadata.create_all(bind=engine)
    print("✅ Initial chat history database tables created.")

    # Create tables for the historical figures database
    Base.metadata.create_all(bind=engine_figure)
    print("✅ Initial historical figures database tables created.")

if __name__ == "__main__":
    init_db()


