import os
import hashlib
from langchain_community.vectorstores import FAISS
from src.embeddings.embedder import get_embedding_model

BASE_INDEX_PATH = "data/faiss_index"

def build_vector_store(chunks, repo_url=None, force=False):
    embedding_model = get_embedding_model()

    if repo_url:
        repo_hash = hashlib.md5(repo_url.encode()).hexdigest()[:8]
        index_path = f"{BASE_INDEX_PATH}_{repo_hash}"
    else:
        index_path = BASE_INDEX_PATH

    if os.path.exists(index_path) and not force:
        print(f"Loading existing FAISS index from {index_path}...")
        return FAISS.load_local(index_path, embedding_model,
                                allow_dangerous_deserialization=True)

    print("Building new FAISS index...")
    vector_store = FAISS.from_documents(chunks, embedding_model)
    vector_store.save_local(index_path)
    return vector_store