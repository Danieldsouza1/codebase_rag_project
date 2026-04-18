import os
from langchain_core.documents import Document

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build",
    "__pycache__", ".venv", "venv"
}

def load_code_files(folder_path, extensions=(".py", ".js", ".ts", ".java", ".go", ".cpp", ".md")):
    documents = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={"source": file_path, "language": file.split(".")[-1]}
                    ))
                except Exception:
                    pass
    return documents