def retrieve_with_threshold(vector_store, query, k=5, score_threshold=0.5):
    results = vector_store.similarity_search_with_score(query, k=k)
    # FAISS returns L2 distance — lower is better
    filtered = [(doc, score) for doc, score in results if score < score_threshold]
    if not filtered:
        return [doc for doc, _ in results[:2]]  # fallback to top 2
    return [doc for doc, _ in filtered]