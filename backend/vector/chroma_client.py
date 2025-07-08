import chromadb
import os

# --- Robust Path Calculation ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels from chroma_client.py -> vector -> backend -> project_root
project_root_dir = os.path.dirname(os.path.dirname(current_dir))
CHROMA_DATA_PATH = os.path.join(project_root_dir, "data", "chroma_db")

COLLECTION_NAME = "figure_context_collection"

# Initialize the persistent client with the absolute path
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

def get_figure_context_collection():
    """
    Returns the singleton instance of the ChromaDB collection for figure context.
    """
    collection = client.get_collection(name=COLLECTION_NAME)
    return collection