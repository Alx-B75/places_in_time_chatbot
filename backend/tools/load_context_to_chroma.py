import chromadb
from chromadb.utils import embedding_functions
import os
import sys

# --- Robust Path Calculation ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_dir)
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from backend.vector.embedding_provider import get_embedding
from backend.figures_database import FigureSessionLocal
from backend.models import FigureContext

# This now calculates an absolute path to the chroma_db folder
CHROMA_DATA_PATH = os.path.join(project_root_dir, "data", "chroma_db")
COLLECTION_NAME = "figure_context_collection"


def load_context_to_chroma():
    """
    Loads historical figure context from the figures.db into ChromaDB.
    """
    print(f"Ensuring ChromaDB path exists at: {CHROMA_DATA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    session = FigureSessionLocal()
    try:
        all_context = session.query(FigureContext).all()
        if not all_context:
            print("No context found in figures.db to load into ChromaDB.")
            return

        print(f"Preparing {len(all_context)} documents for embedding...")

        documents = [context.content for context in all_context]
        embeddings = [get_embedding(doc) for doc in documents]

        metadatas = [{"figure_slug": context.figure_slug} for context in all_context]
        ids = [str(context.id) for context in all_context]

        if not ids:
            print("No documents to add to ChromaDB.")
            return

        print(f"Adding {len(ids)} documents to ChromaDB collection...")
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("✅ ChromaDB loading complete.")

    finally:
        session.close()


if __name__ == '__main__':
    load_context_to_chroma()