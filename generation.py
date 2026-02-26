import os
from typing import List, Tuple

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


client = chromadb.PersistentClient(path="chromadb_data")


def run_rag_query(
    user_query: str,
    collection_name: str = "Oxford-Guide-2022",
    n_results: int = 10,
    model_name: str = "openai/gpt-oss-20b",
) -> Tuple[str, List[str]]:
    """Run the RAG query using the existing ChromaDB collection and Groq client."""
    # get the existing collection
    collection = client.get_collection(name=collection_name)

    load_dotenv()

    client_groq = OpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

    context = collection.query(
        query_texts=[user_query],
        n_results=n_results,
    )

    documents = context.get("documents") or []
    context_chunks: List[str] = documents[0] if documents else []

    prompt = f"""
You are an assistant that answers questions based on provided context.

CONTEXT:
{context}

USER QUERY:
{user_query}

Instructions:
- Answer the query using ONLY the information in the CONTEXT.
- If the CONTEXT does not contain enough information, reply exactly: "I don't have this information yet."
- Keep the answer concise, clear, and relevant.
- Do not make assumptions beyond the CONTEXT.

Answer:
"""

    response = client_groq.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content or ""
    return answer, context_chunks


if __name__ == "__main__":
    # Preserve original behaviour when run directly
    answer, _ = run_rag_query("How old is Oxford University?")
    print(f"\nResponse: {answer}")

