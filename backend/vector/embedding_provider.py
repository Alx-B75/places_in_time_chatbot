# backend/vector/embedding_provider.py

import os
from typing import List
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# --- Model Configuration ---
# Read your existing environment variable. Defaults to 'false'.
USE_OPENAI = os.getenv("USE_OPENAI_EMBEDDING", "false").lower() == "true"

MODEL_CONFIG = {
    "local": {"model_name": "all-MiniLM-L6-v2", "dimension": 384},
    "openai": {"model_name": "text-embedding-3-small", "dimension": 1536}
}

# --- Initialize the Correct Model ---
print(f"--- Embedding Provider Initializing ---")
client = None
provider_key = "openai" if USE_OPENAI else "local"

try:
    if USE_OPENAI:
        client = OpenAI()
        print(f"Provider: OPENAI (model: {MODEL_CONFIG['openai']['model_name']})")
    else:
        client = SentenceTransformer(MODEL_CONFIG['local']['model_name'])
        print(f"Provider: LOCAL (model: {MODEL_CONFIG['local']['model_name']})")
except Exception as e:
    print(f"FATAL: Could not initialize embedding model client. Error: {e}")
    client = None

print("--- Embedding Provider Ready ---")

def get_embedding_dimension() -> int:
    """Returns the dimension of the currently configured embedding model."""
    return MODEL_CONFIG[provider_key]['dimension']

def get_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a single piece of text using the configured provider.
    """
    if not client or not text or not isinstance(text, str):
        return [0.0] * get_embedding_dimension()

    try:
        if USE_OPENAI:
            response = client.embeddings.create(
                input=text.replace("\n", " "),
                model=MODEL_CONFIG['openai']['model_name']
            )
            return response.data[0].embedding
        else: # Assumes local provider
            embedding = client.encode(text, convert_to_tensor=False)
            return embedding.tolist()
    except Exception as er:
        print(f"Error generating embedding for text: '{text[:50]}...'\n{er}")
        return [0.0] * get_embedding_dimension()