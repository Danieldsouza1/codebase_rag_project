from langchain_groq import ChatGroq


def generate_answer(query, retrieved_docs):
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt = f"""
You are a senior software engineer.

Use ONLY the code below to answer the question.
If the answer is not present, say "Not found in codebase".

CODE:
{context}

QUESTION:
{query}

ANSWER:
"""

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    response = llm.invoke(prompt)
    return response.content
