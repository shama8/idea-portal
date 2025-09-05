# from sentence_transformers import SentenceTransformer
# import numpy as np

# model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    # embedding = model.encode(text, convert_to_numpy=True)
    # norm = np.linalg.norm(embedding)
    # return embedding / norm if norm > 0 else embedding
    return None  # Placeholder return to avoid breaking calls

def cosine_similarity(a, b):
    return 0.0  # Return dummy similarity
