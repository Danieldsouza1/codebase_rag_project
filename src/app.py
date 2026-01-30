from dotenv import load_dotenv
from src.loaders.code_loader import load_code_files
from src.loaders.github_loader import clone_github_repo
from src.chunking.splitter import chunk_code
from src.vectorstore.faiss_store import build_vector_store
from src.llm.generator import generate_answer

load_dotenv()


def main():
    use_github = True  # change to False to use sample_code

    if use_github:
        repo_url = "https://github.com/psf/requests"  # example repo
        code_folder = clone_github_repo(repo_url)
    else:
        code_folder = "data/sample_code"

    docs = load_code_files(code_folder)
    chunks = chunk_code(docs)
    vector_store = build_vector_store(chunks)

    query = "How does authentication work in this project?"
    retrieved_docs = vector_store.similarity_search(query, k=3)

    answer = generate_answer(query, retrieved_docs)
    print(answer)


if __name__ == "__main__":
    main()
