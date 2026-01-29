import os

def load_code_files(folder_path):
    documents = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                documents.append({
                    "file": file,
                    "content": content
                })

    return documents


if __name__ == "__main__":
    code_folder = "data/sample_code"
    docs = load_code_files(code_folder)

    print(f"Loaded {len(docs)} code files:\n")

    for doc in docs:
        print("FILE:", doc["file"])
        print(doc["content"])
        print("-" * 40)
