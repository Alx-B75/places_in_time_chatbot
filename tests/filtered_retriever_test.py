"""
Test filtered context retrieval by figure_slug from Chroma vector store.
"""

from backend.vector.context_retriever import search_figure_context


def run_test():
    query = "What battles did you fight in?"
    figure_slug = "richard-iii"
    top_k = 5

    results = search_figure_context(query, figure_slug, top_k)

    if not results:
        print("No results found.")
        return

    print(f"Top {len(results)} results for '{query}' with figure_slug='{figure_slug}':\n")
    for i, r in enumerate(results, 1):
        content = r["content"][:200].strip().replace("\n", " ")
        source = r["metadata"].get("source_name", "Unknown Source")
        print(f"{i}. [{source}] {content}...\n")


if __name__ == "__main__":
    run_test()
