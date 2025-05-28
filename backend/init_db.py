from backend.database import engine
from backend.models import Base
import os

print("📂 Current working directory:", os.getcwd())
print("📄 Target DB path:", os.path.abspath("./data/chat_history.db"))

Base.metadata.create_all(bind=engine)

print("Initial database tables have been created.")

