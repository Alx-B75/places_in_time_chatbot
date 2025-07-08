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
    It will create the collection if it doesn't already exist.
    """
    # This now creates the collection if it's missing, preventing the crash.
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection