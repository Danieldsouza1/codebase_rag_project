# src/agent/codebase_agent.py

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


def build_codebase_agent(vector_store):
    """
    Builds a tool-calling agent that can search and analyze
    an indexed codebase using multiple strategies.
    """

    # ----------------------------------------------------------------
    # Tool 1 — Semantic search across the codebase
    # ----------------------------------------------------------------
    @tool
    def search_codebase(query: str) -> str:
        """
        Semantically search the indexed codebase for code relevant to the query.
        Use this for any question about how something works, where something is
        defined, or what a specific component does.
        """
        from src.vectorstore.retriever import retrieve_with_threshold
        docs = retrieve_with_threshold(vector_store, query, k=6, score_threshold=0.8)
        if not docs:
            return "No relevant code found for this query."
        return "\n\n".join(
            f"[File: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

    # ----------------------------------------------------------------
    # Tool 2 — List all indexed files
    # ----------------------------------------------------------------
    @tool
    def list_indexed_files() -> str:
        """
        List all source files that have been indexed from the repository.
        Use this when you need to understand the project structure or find
        which files exist before deciding where to look.
        """
        try:
            docs = vector_store.docstore._dict.values()
            sources = sorted({
                doc.metadata.get("source", "unknown")
                for doc in docs
            })
            if not sources:
                return "No files found in the index."
            return f"Indexed files ({len(sources)} total):\n" + "\n".join(sources)
        except Exception as e:
            return f"Could not retrieve file list: {str(e)}"

    # ----------------------------------------------------------------
    # Tool 3 — Summarize a specific file
    # ----------------------------------------------------------------
    @tool
    def summarize_file(file_path: str) -> str:
        """
        Retrieve and summarize the contents of a specific file from the index.
        Use this when you know which file is relevant and want a focused summary.
        Provide the full file path as shown in list_indexed_files.
        """
        try:
            docs = vector_store.docstore._dict.values()
            file_chunks = [
                doc for doc in docs
                if doc.metadata.get("source", "") == file_path
            ]
            if not file_chunks:
                file_chunks = [
                    doc for doc in docs
                    if file_path in doc.metadata.get("source", "")
                ]
            if not file_chunks:
                return f"File '{file_path}' not found in the index."

            content = "\n\n".join(chunk.page_content for chunk in file_chunks[:4])

            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
            summary_prompt = f"""Summarize what this file does in 3-5 sentences.
Focus on: its purpose, key functions/classes, and how it fits into the project.

FILE: {file_path}
CONTENT:
{content}

SUMMARY:"""
            response = llm.invoke(summary_prompt)
            return f"Summary of {file_path}:\n{response.content}"
        except Exception as e:
            return f"Error summarizing file: {str(e)}"

    # ----------------------------------------------------------------
    # Tool 4 — Security and bug review of retrieved code
    # ----------------------------------------------------------------
    @tool
    def review_code_for_issues(query: str) -> str:
        """
        Search for code related to the query and perform a targeted security
        and bug review on it. Use this specifically for questions about
        vulnerabilities, bugs, security risks, or code quality issues.
        """
        from src.vectorstore.retriever import retrieve_with_threshold
        docs = retrieve_with_threshold(vector_store, query, k=5, score_threshold=0.8)
        if not docs:
            return "No relevant code found to review."

        context = "\n\n".join(
            f"[File: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
        review_prompt = f"""You are a senior security engineer.
Review the following code specifically for:
1. Security vulnerabilities
2. Potential bugs or edge cases
3. Dangerous patterns or bad practices

Be specific - cite line content and file names where possible.
If nothing critical is found, say so clearly.

CODE:
{context}

REVIEW:"""
        response = llm.invoke(review_prompt)
        return response.content

    # ----------------------------------------------------------------
    # Tools list
    # ----------------------------------------------------------------
    tools = [
        search_codebase,
        list_indexed_files,
        summarize_file,
        review_code_for_issues
    ]

    # ----------------------------------------------------------------
    # Build the agent manually — works with LangChain 1.x
    # ----------------------------------------------------------------
    def run_agent(user_input: str) -> dict:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        llm_with_tools = llm.bind_tools(tools)

        messages = [
            SystemMessage(content="""You are an expert code analysis agent with access to a fully indexed GitHub repository.

You have four tools available:
- search_codebase: semantically search for relevant code
- list_indexed_files: see the full file structure
- summarize_file: get a summary of a specific file
- review_code_for_issues: targeted security and bug review

Always use tools to find evidence before answering. Cite file names in your answer."""),
            HumanMessage(content=user_input)
        ]

        intermediate_steps = []

        for _ in range(6):
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            # No tool calls means the agent has its final answer
            if not response.tool_calls:
                break

            # Execute each tool the agent requested
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]

                matched_tool = next((t for t in tools if t.name == tool_name), None)
                if matched_tool:
                    arg_value = list(tool_input.values())[0] if tool_input else ""
                    observation = matched_tool.invoke(arg_value)

                    intermediate_steps.append((tool_name, str(tool_input), str(observation)))

                    messages.append(ToolMessage(
                        content=str(observation),
                        tool_call_id=tool_call["id"]
                    ))

        return {
            "output": response.content,
            "intermediate_steps": intermediate_steps
        }

    return run_agent
