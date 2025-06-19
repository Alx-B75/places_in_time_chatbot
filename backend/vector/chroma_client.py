import chromadb

chroma_client = chromadb.PersistentClient(path="./data/chroma")

def get_figure_context_collection():
    """
    Func returns a persistent collection for figure context chunks.
    Creates it if it doesn't already exist.
    """
    return chroma_client.get_or_create_collection(
        name="figure_contexts",
        metadata={"description": "Historical figure context chunks"}
    )