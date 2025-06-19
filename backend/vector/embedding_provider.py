import os

USE_OPENAI = os.getenv("USE_OPENAI_EMBEDDING", "false").lower() == "true"

if USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_embedding(text: str) -> list[float]:
        """
        Get embedding from OpenAI API.
        """
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

else:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_embedding(text: str) -> list[float]:
        """
        Get embedding from local SentenceTransformer model.
        """
        return _model.encode(text).tolist()
