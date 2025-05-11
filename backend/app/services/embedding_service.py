# app/services/embedding_service.py
from flask import current_app
# Option 1: Using LiteLLM for embeddings
from app.services.litellm_service import embedding as litellm_embedding

# Option 2: Using a library like sentence-transformers (example)
# from sentence_transformers import SentenceTransformer
# SBERT_MODEL = None

# def get_sbert_model():
#     global SBERT_MODEL
#     if SBERT_MODEL is None:
#         model_name = current_app.config.get('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
#         current_app.logger.info(f"Loading SentenceTransformer model: {model_name}")
#         SBERT_MODEL = SentenceTransformer(model_name)
#         current_app.logger.info("SentenceTransformer model loaded.")
#     return SBERT_MODEL

def get_embedding(texts: list[str], model_type: str = "litellm"): # or "sbert"
    """
    Generates embeddings for a list of texts.
    `model_type` can be used to switch between embedding providers if you have multiple.
    """
    if not texts:
        return []

    if model_type == "litellm":
        model_name = current_app.config.get('EMBEDDING_MODEL_NAME_LITELLM', 'gemini/text-embedding-004') # Example, configure as needed
        try:
            current_app.logger.info(f"Generating embeddings for {len(texts)} texts using LiteLLM model: {model_name}")
            response = litellm_embedding(model=model_name, input=texts)
            # LiteLLM embedding response is a ModelResponse object.
            # The embeddings are in response.data, which is a list of EmbeddingObject.
            # Each EmbeddingObject has an 'embedding' attribute (list of floats).
            embeddings = [item['embedding'] for item in response.data]
            # Convert to numpy array if your downstream code expects it, like in chunk_and_index.py
            import numpy as np
            return np.array(embeddings)
        except Exception as e:
            current_app.logger.error(f"Error generating embeddings with LiteLLM: {e}")
            raise
    # elif model_type == "sbert":
    #     model = get_sbert_model()
    #     current_app.logger.info(f"Generating embeddings for {len(texts)} texts using SentenceTransformer.")
    #     embeddings = model.encode(texts)
    #     return embeddings # Already a numpy array
    else:
        raise ValueError(f"Unsupported embedding model type: {model_type}")

# Your rag/embedding.py should be adapted to use this service function.
# For example, in rag/chunk_and_index.py, replace direct embedding calls:
# from app.services.embedding_service import get_embedding
# vectors = get_embedding(chunks) # This now returns a NumPy array