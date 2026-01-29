from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_code(documents, chunk_size=800, chunk_overkap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overkap = chunk_overkap
    )
    return splitter.create_documents(documents)