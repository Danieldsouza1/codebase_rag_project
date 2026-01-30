from langchain_community.vectorstores import FAISS
from src.embeddings.embedder import get_embedding_model


def build_vector_store(chunks):
    embedding_model = get_embedding_model()
    return FAISS.from_documents(chunks, embedding_model)
