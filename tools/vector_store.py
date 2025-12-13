import chromadb
from sentence_transformers import SentenceTransformer
_client = None
_model = None
_collection = None

def get_vector_store():
    global _client, _model, _collection

    if _collection is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _client = chromadb.PersistentClient(path="storage/chroma")
        _collection = _client.get_collection(name="cities")

    return _collection, _model