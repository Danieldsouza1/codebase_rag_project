import os


def load_code_files(folder_path, extensions=(".py",)):
    documents = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        documents.append(f.read())
                except Exception:
                    pass  # skip unreadable files

    return documents
