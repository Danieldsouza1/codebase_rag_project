import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

load_dotenv()


def load_code_files(folder_path):
    documents = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    documents.append(f.read())

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


def generate_answer(query, retrieved_docs):
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt = f"""
You are a senior software engineer.

Use ONLY the code below to answer the question.
If the answer is not present, say "Not found in codebase".

CODE:
{context}

QUESTION:
{query}

ANSWER:
"""

    llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)



    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    code_folder = "data/sample_code"

    docs = load_code_files(code_folder)
    chunks = chunk_code(docs)
    vector_store = build_vector_store(chunks)

    query = "Explain how login works in this project"
    retrieved_docs = vector_store.similarity_search(query, k=2)

    answer = generate_answer(query, retrieved_docs)

    print("QUESTION:")
    print(query)
    print("\nANSWER:")
    print(answer)
