import streamlit as st
from dotenv import load_dotenv

from src.loaders.github_loader import clone_github_repo
from src.loaders.code_loader import load_code_files
from src.chunking.splitter import chunk_code
from src.vectorstore.faiss_store import build_vector_store
from src.llm.generator import generate_answer
from src.llm.analyzer import analyze_code_issues

load_dotenv()

st.set_page_config(
    page_title="Codebase RAG Assistant",
    layout="wide"
)

st.title("🧠 Codebase RAG Assistant")
st.write("Analyze any GitHub repository using RAG")

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("Repository Settings")

repo_url = st.sidebar.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/psf/requests"
)

mode = st.sidebar.radio(
    "Select Mode",
    ["Ask Questions", "Code Review"]
)

# ----------------------------
# Main input
# ----------------------------
st.subheader("Input")

if mode == "Ask Questions":
    user_query = st.text_area(
        "Ask a question about the codebase",
        placeholder="How does authentication work?"
    )
else:
    user_query = "Find potential issues in this codebase"

run_button = st.button("Run Analysis")

# ----------------------------
# Run pipeline
# ----------------------------
if run_button:
    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
    else:
        with st.spinner("Cloning and indexing repository..."):
            code_folder = clone_github_repo(repo_url)
            docs = load_code_files(code_folder)
            chunks = chunk_code(docs)
            vector_store = build_vector_store(chunks)

        with st.spinner("Running analysis..."):
            if mode == "Ask Questions":
                retrieved_docs = vector_store.similarity_search(user_query, k=3)
                answer = generate_answer(user_query, retrieved_docs)
            else:
                retrieved_docs = vector_store.similarity_search(
                    "Find potential issues in this codebase",
                    k=5
                )
                answer = analyze_code_issues(retrieved_docs)

        st.success("Done!")

        st.subheader("Result")
        st.write(answer)
