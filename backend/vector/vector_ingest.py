import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from backend.models import FigureContext
from backend.database import SessionLocalFigure
from backend.vector.chroma_client import get_figure_context_collection
from backend.vector.embedding_provider import get_embedding


def ingest_all_context_chunks():
    """
    Embeds all FigureContext content and stores in Chroma with figure_slug metadata.
    """
    session = SessionLocalFigure()
    collection = get_figure_context_collection()
    count = 0

    try:
        contexts = session.query(FigureContext).all()
        for ctx in contexts:
            if ctx.content:
                embedding = get_embedding(ctx.content)
                collection.add(
                    documents=[ctx.content],
                    embeddings=[embedding],
                    metadatas=[{"figure_slug": ctx.figure_slug}],
                    ids=[f"{ctx.figure_slug}-{ctx.id}"]
                )
                count += 1
        print(f"✅ Ingested {count} FigureContext chunks into Chroma.")
    finally:
        session.close()


if __name__ == "__main__":
    ingest_all_context_chunks()
