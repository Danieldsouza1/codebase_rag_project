# 🧠 Codebase RAG Assistant

A Retrieval-Augmented Generation system that ingests any GitHub repository and enables natural language interaction with the codebase — ask questions, run automated code reviews, or deploy an AI agent to reason across the entire project.

---

## What It Does

Point it at any GitHub repository and you get three modes of analysis:

- **Ask Questions** — natural language Q&A grounded in the actual source code, with source file citations
- **Code Review** — automated detection of bugs, security issues, and bad practices
- **Agent Mode** — an LLM agent that dynamically selects tools, performs multi-step reasoning, and self-directs its analysis based on query complexity


---

## Project Structure

```
rag_project/
├── streamlit_app.py              # Streamlit UI — three modes
├── app.py                        # CLI entry point
├── src/
│   ├── loaders/
│   │   ├── github_loader.py      # Clone repos, Windows-safe deletion
│   │   └── code_loader.py        # Load files as Documents with metadata
│   ├── chunking/
│   │   └── splitter.py           # split_documents (preserves metadata)
│   ├── embeddings/
│   │   └── embedder.py           # HuggingFace Sentence-Transformers
│   ├── vectorstore/
│   │   ├── faiss_store.py        # Persistent FAISS index per repo hash
│   │   └── retriever.py          # Score-threshold retrieval with fallback
│   ├── llm/
│   │   ├── generator.py          # Q&A with cached LLM instance
│   │   └── analyzer.py           # Code review with cached LLM instance
│   ├── agent/
│   │   └── codebase_agent.py     # Agentic workflow — tool-calling loop
│   └── database.py               # SQLite query logger
└── data/
    ├── github_repo/              # Cloned repository (auto-generated)
    ├── faiss_index_<hash>/       # Persisted FAISS index (auto-generated)
    └── query_log.db              # Query history (auto-generated)
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Embeddings | Sentence-Transformers `all-MiniLM-L6-v2` |
| Vector Store | FAISS (Facebook AI Similarity Search) |
| LLM | LLaMA 3.3 70B via Groq API |
| RAG Framework | LangChain 1.x |
| Frontend | Streamlit |
| Query Logging | SQLite |
| Repo Ingestion | GitPython / subprocess |

---

## Key Engineering Decisions

### 1. Metadata-Preserving Chunking
Rather than splitting raw strings, the loader returns `LangChain Document` objects with `source` (file path) and `language` metadata attached to every chunk. This means every retrieved chunk is traceable to its origin file — the UI shows exactly which files contributed to each answer.

### 2. Score-Threshold Retrieval
Replaced standard top-k similarity search with a distance-filtered function that drops chunks above an L2 threshold, improving answer grounding. Falls back to top-2 if nothing clears the threshold.

### 3. Persistent FAISS Index per Repository
Each repo URL is hashed (MD5, 8 chars) and used as a unique index path. Re-runs on the same repo skip re-embedding entirely. A Force Re-index checkbox in the UI allows manual override when the repo changes.

### 4. Agentic Workflow
Agent Mode uses LangChain's `bind_tools()` API with a custom reasoning loop — no dependency on `AgentExecutor`. The loop runs up to 6 iterations, feeding each tool result back into the message history so the LLM can decide whether to call another tool or produce a final answer.

### 5. Cached LLM Instances
Both `generator.py` and `analyzer.py` initialize the LLM client once at module level using a singleton pattern, avoiding re-instantiation on every call.

---

## Setup

### Prerequisites
- Python 3.10+
- Git installed and on PATH
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Run

```bash
streamlit run streamlit_app.py
```

---

## Requirements

```
streamlit
python-dotenv
langchain
langchain-core
langchain-community
langchain-groq
langchain-text-splitters
langchain-huggingface
sentence-transformers
faiss-cpu
gitpython
```

---

## License

MIT
