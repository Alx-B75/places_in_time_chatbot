# test_vector_search.py

from backend.database import get_chroma_retriever

def main():
    retriever = get_chroma_retriever()
    query = "Who built Hadrian's Wall?"
    results = retriever(query)

    print(f"\n🔍 Found {len(results)} results:\n")
    for i, result in enumerate(results, start=1):
        print(f"{i}. {result['content'][:200]}...\n   ↳ Metadata: {result['metadata']}")

if __name__ == "__main__":
    main()
