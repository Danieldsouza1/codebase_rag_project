import streamlit as st
from dotenv import load_dotenv

from src.loaders.github_loader import clone_github_repo
from src.loaders.code_loader import load_code_files
from src.chunking.splitter import chunk_code
from src.vectorstore.faiss_store import build_vector_store
from src.llm.generator import generate_answer
from src.llm.analyzer import analyze_code_issues
from src.vectorstore.retriever import retrieve_with_threshold
from src.database import log_query, fetch_recent_logs
from src.agent.codebase_agent import build_codebase_agent

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
    ["Ask Questions", "Code Review", "Agent Mode"]
)

# Mode descriptions in sidebar
if mode == "Ask Questions":
    st.sidebar.caption("Direct RAG — fast, single-pass retrieval and answer generation.")
elif mode == "Code Review":
    st.sidebar.caption("Fixed analysis pipeline — reviews sampled chunks for bugs, smells, and security issues.")
else:
    st.sidebar.caption("Agentic — the LLM decides which tools to use and can perform multi-step reasoning across the codebase.")

# Recent queries history
with st.sidebar.expander("🕘 Recent Queries"):
    logs = fetch_recent_logs()
    if logs:
        for ts, m, q in logs:
            st.caption(f"[{m}] {q[:60]}...")
    else:
        st.caption("No queries yet.")

run_button = st.button("Run Analysis")

# ----------------------------
# Main input
# ----------------------------
st.subheader("Input")

if mode == "Ask Questions":
    user_query = st.text_area(
        "Ask a question about the codebase",
        placeholder="How does the Session class manage cookies?"
    )
elif mode == "Code Review":
    user_query = "Find potential issues in this codebase"
    st.info("Code Review mode will automatically sample and review the codebase for bugs, security issues, and bad practices.")
else:
    user_query = st.text_area(
        "Ask the agent anything about the codebase",
        placeholder="Are there any security vulnerabilities in how this handles HTTP redirects?"
    )

# ----------------------------
# Run pipeline
# ----------------------------
if run_button:
    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
    elif mode in ["Ask Questions", "Agent Mode"] and not user_query.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Cloning and indexing repository..."):
            code_folder = clone_github_repo(repo_url)
            docs = load_code_files(code_folder)
            chunks = chunk_code(docs)
            vector_store = build_vector_store(chunks, repo_url=repo_url)

        # -------------------------
        # Mode 1: Ask Questions
        # -------------------------
        if mode == "Ask Questions":
            with st.spinner("Searching codebase and generating answer..."):
                retrieved_docs = retrieve_with_threshold(vector_store, user_query, k=5)
                answer = generate_answer(user_query, retrieved_docs)
                log_query(user_query, mode, answer)

            st.success("Done!")
            st.subheader("Answer")
            st.write(answer)

            with st.expander("📁 Source Files Used"):
                sources = list({doc.metadata.get("source", "unknown") for doc in retrieved_docs})
                for s in sources:
                    st.code(s)

        # -------------------------
        # Mode 2: Code Review
        # -------------------------
        elif mode == "Code Review":
            with st.spinner("Running code review..."):
                retrieved_docs = retrieve_with_threshold(
                    vector_store, "Find potential issues in this codebase", k=5
                )
                answer = analyze_code_issues(retrieved_docs)
                log_query(user_query, mode, answer)

            st.success("Done!")
            st.subheader("Code Review")
            st.write(answer)

            with st.expander("📁 Source Files Reviewed"):
                sources = list({doc.metadata.get("source", "unknown") for doc in retrieved_docs})
                for s in sources:
                    st.code(s)

        # -------------------------
        # Mode 3: Agent Mode
        # -------------------------
        else:
            with st.spinner("Agent is analyzing the codebase... this may take a moment."):
                run_agent = build_codebase_agent(vector_store)
                result = run_agent(user_query)

            answer = result.get("output", "Agent did not return a result.")
            intermediate_steps = result.get("intermediate_steps", [])
            log_query(user_query, mode, answer)

            st.success("Done!")
            st.subheader("Agent Answer")
            st.write(answer)

            # Show the agent's reasoning steps
            if intermediate_steps:
                with st.expander("🔍 Agent Reasoning Steps"):
                    for i, (tool_name, tool_input, observation) in enumerate(intermediate_steps, 1):
                        st.markdown(f"**Step {i} — Tool used: `{tool_name}`**")
                        st.caption(f"Input: {tool_input}")
                        st.text_area(
                            f"Result from {tool_name}",
                            value=observation[:1000] + ("..." if len(observation) > 1000 else ""),
                            height=150,
                            key=f"step_{i}"
                        )
                        st.divider()
