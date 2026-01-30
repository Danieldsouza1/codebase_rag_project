import os


def load_code_files(folder_path, extensions=(".py",".js", ".ts", ".java", ".go", ".cpp", ".md")):
    documents = []

    IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build",
    "__pycache__", ".venv", "venv"
}

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        documents.append(f.read())
                except Exception:
                    pass  # skip unreadable files

    return documents
