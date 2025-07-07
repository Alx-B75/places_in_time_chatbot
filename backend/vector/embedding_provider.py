# backend/vector/embedding_provider.py

from sentence_transformers import SentenceTransformer
from typing import List


MODEL_NAME = "all-MiniLM-L6-v2"

print(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
print("Embedding model loaded successfully.")


def get_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a single piece of text.
    """
    if not text or not isinstance(text, str):
        return [0.0] * model.get_sentence_embedding_dimension()

    embedding = model.encode(text, convert_to_tensor=False)

    return embedding.tolist()