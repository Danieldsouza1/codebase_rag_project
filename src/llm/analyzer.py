from langchain_groq import ChatGroq

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
    return _llm

def analyze_code_issues(retrieved_docs):
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt = f"""
You are a senior software engineer performing a code review.

Analyze the following code and list:
1. Potential bugs
2. Security concerns
3. Code smells or bad practices
4. Suggestions for improvement

Only use the code provided.
If nothing critical is found, say so clearly.

CODE:
{context}

REVIEW:
"""
    llm = get_llm()  # use cached instance
    response = llm.invoke(prompt)
    return response.content