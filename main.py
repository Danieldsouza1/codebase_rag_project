import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


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


def create_embeddings(chunks):
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    embeddings = embedding_model.embed_documents(
        [chunk.page_content for chunk in chunks]
    )
    return embeddings


if __name__ == "__main__":
    code_folder = "data/sample_code"

    docs = load_code_files(code_folder)
    chunks = chunk_code(docs)
    embeddings = create_embeddings(chunks)

    print(f"Total chunks: {len(chunks)}")
    print(f"Embedding vector size: {len(embeddings[0])}")
