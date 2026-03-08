# 🧠 Codebase RAG Assistant

A Retrieval-Augmented Generation (RAG) system that dynamically ingests GitHub repositories, performs semantic code retrieval across large multi-language codebases, and generates grounded answers and automated code review insights using LLMs.

This project demonstrates how modern AI-powered developer tools (like Copilot Chat or Sourcegraph Cody) are built at a system level.

---

## 🚀 Features

- 🔗 **Dynamic GitHub Repository Ingestion**
  - Clone and analyze any public GitHub repository
- 🧠 **Semantic Code Search**
  - FAISS-based vector search over code and documentation
- ❓ **Code Q&A Mode**
  - Ask natural-language questions about the codebase
- 🔍 **Automated Code Review Mode**
  - Detect potential issues, code smells, and improvement suggestions
- 🌐 **Multi-Language Support**
  - Python, JavaScript, TypeScript, Java, Go, Markdown (configurable)
- 🖥️ **Interactive Streamlit UI**
  - Simple web interface for real-time analysis
- 🧱 **Modular, Production-Style Architecture**

---



## ⚙️ How It Works

1. The user provides a GitHub repository URL
2. The repository is cloned locally
3. Source and documentation files are loaded and chunked
4. Chunks are embedded using a sentence-transformer model
5. FAISS performs similarity-based retrieval
6. Retrieved context is passed to an LLM
7. The LLM generates grounded answers or review insights

---

## ▶️ Running the Project

### 1️⃣ Create & activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python -m src.app
streamlit run streamlit_app.py

## 🧠 Why RAG?
Large Language Models alone hallucinate when analyzing large codebases.
RAG ensures responses are grounded in retrieved source code, improving accuracy, transparency, and reliability.

### 🔮 Future Improvements

File-level citations in answers

Embedding cache for faster re-runs

Chat history & memory

Deployment to Streamlit Cloud / Hugging Face Spaces

Advanced reranking for improved retrieval quality
