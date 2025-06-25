from backend.vector.chroma_client import get_figure_context_collection
from backend.vector.embedding_provider import get_embedding


def search_figure_context(query: str, figure_slug: str, top_k: int = 5) -> list[dict]:
    """
    Search the Chroma vector store for context chunks most relevant to the query,
    filtered by a specific historical figure's slug.

    Args:
        query (str): The user's question or statement.
        figure_slug (str): Slug of the historical figure (e.g., "richard-iii").
        top_k (int): Number of most relevant results to return.

    Returns:
        List[dict]: A list of matching documents with their metadata.
    """
    print(f"[CHROMA] Queried for: '{query}' | figure_slug: '{figure_slug}'")
    collection = get_figure_context_collection()
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        where={"figure_slug": figure_slug},
        n_results=top_k
    )


    print(f"[CHROMA] Retrieved {len(results['documents'][0])} documents")

    return [
        {
            "content": doc,
            "metadata": meta
        }
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]