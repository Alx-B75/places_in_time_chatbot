import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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


