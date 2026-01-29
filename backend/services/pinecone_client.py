

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os

_model = None
_index = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        _index = pc.Index("insurance-policies")
    return _index

def search_policy(query: str):
    model = get_model()
    index = get_index()

    vector = model.encode(query).tolist()
    results = index.query(vector=vector, top_k=1, include_metadata=True)
    return results
