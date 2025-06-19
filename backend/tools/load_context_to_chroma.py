import uuid
from backend.figures_database import FigureSessionLocal
from backend.models import FigureContext
from backend.vector.chroma_client import get_figure_context_collection
from backend.vector.embedding_provider import get_embedding




def load_context_to_chroma():
    session = FigureSessionLocal()
    collection = get_figure_context_collection()

    figure_contexts = session.query(FigureContext).all()
    print(f"Found {len(figure_contexts)} context entries.")

    for fc in figure_contexts:
        doc_id = f"{fc.figure_slug}-{fc.id}-{uuid.uuid4().hex[:6]}"
        metadata = {
            "figure_slug": fc.figure_slug,
            "content_type": fc.content_type,
            "source_name": fc.source_name or "",
        }

        collection.add(
            ids=[doc_id],
            documents=[fc.content],
            embeddings=[get_embedding(fc.content)],
            metadatas=[metadata],
        )

    print("Context data loaded into Chroma.")


if __name__ == "__main__":
    load_context_to_chroma()
