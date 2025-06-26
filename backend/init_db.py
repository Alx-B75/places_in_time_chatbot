import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_dir)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from backend.database import engine
from backend.models import Base

def init_db():
    """
    Creates all tables defined in the SQLAlchemy models.
    """
    print("📂 Current working directory:", os.getcwd())
    print("📄 Target DB path:", os.path.abspath("./data/chat_history.db"))

    Base.metadata.create_all(bind=engine)
    print("✅ Initial database tables have been created.")

if __name__ == "__main__":
    init_db()


