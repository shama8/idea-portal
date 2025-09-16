from sentence_transformers import SentenceTransformer
import numpy as np

# Load the pre-trained model once
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

def get_embedding(text):
    embedding = model.encode(text, convert_to_numpy=True)
    norm = np.linalg.norm(embedding)
    return embedding / norm if norm > 0 else embedding

def cosine_similarity(a, b):
    if a is None or b is None:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
