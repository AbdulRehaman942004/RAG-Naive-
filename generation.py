from openai import OpenAI
import os
from dotenv import load_dotenv
import chromadb

client = chromadb.PersistentClient(path="chromadb_data")

# get the existing collection
collection = client.get_collection(name="Oxford-Guide-2022")

load_dotenv()

client_groq = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

user_query = "How old is Oxford University?"

context = collection.query(
    query_texts=user_query,
    n_results=10,
)

print(f" \n Context: {context['documents']}")

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

response = client_groq.responses.create(
    input=prompt,
    model="openai/gpt-oss-20b",
)

print(f"\nResponse: {response.output_text}")