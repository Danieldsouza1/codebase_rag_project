from dotenv import load_dotenv
from src.loaders.code_loader import load_code_files
from src.loaders.github_loader import clone_github_repo
from src.chunking.splitter import chunk_code
from src.vectorstore.faiss_store import build_vector_store
from src.llm.generator import generate_answer
from src.llm.analyzer import analyze_code_issues
from src.vectorstore.retriever import retrieve_with_threshold


load_dotenv()


def main():
    use_github = True
    review_mode = True   # ✅ DEFINE IT HERE

    if use_github:
        repo_url = "https://github.com/psf/requests"
        code_folder = clone_github_repo(repo_url)
    else:
        code_folder = "data/sample_code"

    docs = load_code_files(code_folder)
    chunks = chunk_code(docs)
    vector_store = build_vector_store(chunks, repo_url=repo_url)

    if review_mode:
        query = "Find potential issues in this codebase"
        retrieved_docs = retrieve_with_threshold(vector_store, query, k=5)
        answer = analyze_code_issues(retrieved_docs)
    else:
        query = "How does authentication work in this project?"
        retrieved_docs = retrieve_with_threshold(vector_store, query, k=5)
        answer = generate_answer(query, retrieved_docs)

    print(answer)


if __name__ == "__main__":
    main()
