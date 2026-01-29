import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_code_files(folder_path):
    documents = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                documents.append(content)

    return documents


def chunk_code(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.create_documents(documents)


def build_vector_store(chunks):
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return FAISS.from_documents(chunks, embedding_model)


def query_vector_store(vector_store, query, k=2):
    results = vector_store.similarity_search(query, k=k)
    return results


if __name__ == "__main__":
    code_folder = "data/sample_code"

    docs = load_code_files(code_folder)
    chunks = chunk_code(docs)
    vector_store = build_vector_store(chunks)

    query = "Where is login implemented?"
    results = query_vector_store(vector_store, query)

    print(f"Query: {query}\n")

    for i, doc in enumerate(results):
        print(f"RESULT {i+1}")
        print(doc.page_content)
        print("-" * 40)
