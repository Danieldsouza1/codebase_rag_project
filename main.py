import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


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

    chunks = splitter.create_documents(documents)
    return chunks


if __name__ == "__main__":
    code_folder = "data/sample_code"

    docs = load_code_files(code_folder)
    chunks = chunk_code(docs)

    print(f"Total chunks created: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        print(f"CHUNK {i+1}")
        print(chunk.page_content)
        print("-" * 40)
