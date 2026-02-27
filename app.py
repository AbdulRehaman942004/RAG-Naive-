import os
import streamlit as st
from dotenv import load_dotenv
import generation

load_dotenv()

@st.cache_resource
def get_chroma_client():
    import chromadb
    return chromadb.PersistentClient(path="chromadb_data")


def index_uploaded_pdf(
    file_bytes: bytes,
    collection_name: str,
    chunk_size: int,
) -> int:
    """Extract chunks from PDF bytes, replace collection in ChromaDB, and return chunk count."""
    import extraction
    import ingestion

    chunks = extraction.extract_bytes_to_chunks(file_bytes, size=chunk_size)
    if not chunks:
        return 0

    client = get_chroma_client()
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    ingestion.ingest_chunks_into_chromadb(chunks, collection_name=collection_name)
    return len(chunks)


def init_session_state() -> None:
    if "last_collection" not in st.session_state:
        st.session_state.last_collection = "Oxford-Guide-2022"
    if "indexed_pdf_name" not in st.session_state:
        st.session_state.indexed_pdf_name = None
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []


def main() -> None:
    st.set_page_config(
        page_title="RAG Naive – PDF Q&A",
        page_icon="📘",
        layout="wide",
    )

    init_session_state()

    st.title("RAG Naive – PDF Question Answering")
    st.caption(
        "Upload a PDF to index it into ChromaDB, then ask questions answered from that document using the Groq LLM."
    )

    with st.sidebar:
        st.header("Configuration")

        collection_name = st.text_input(
            "Chroma collection name",
            value=st.session_state.last_collection,
            help="Collection to create/overwrite when indexing, and to query when asking.",
        )

        chunk_size = st.slider(
            "Chunk size (characters)",
            min_value=200,
            max_value=1500,
            value=500,
            step=100,
            help="Used when indexing a new PDF.",
        )

        n_results = st.slider(
            "Number of chunks to retrieve",
            min_value=3,
            max_value=20,
            value=8,
            step=1,
            help="Chunks sent as context to the LLM per question.",
        )

        model_name = st.text_input(
            "Groq model name",
            value="openai/gpt-oss-20b",
            help="Model ID used via Groq's OpenAI-compatible API.",
        )

        st.markdown("---")
        st.subheader("Environment status")
        groq_key_present = bool(os.environ.get("GROQ_API_KEY"))
        st.write(f"**GROQ_API_KEY set:** {'✅' if groq_key_present else '❌'}")

    tab_overview, tab_index, tab_qa = st.tabs(["Overview", "Index PDF", "Ask Questions"])

    with tab_overview:
        st.subheader("How this app works")
        st.markdown(
            """
1. **Index PDF** (tab *Index PDF*): Upload a PDF. The app extracts text, splits it into chunks, and stores them in ChromaDB under the collection name in the sidebar. Any existing collection with that name is replaced.
2. **Ask questions** (tab *Ask Questions*): Type a question. The app retrieves relevant chunks from the current collection and answers using the Groq LLM with that context.
"""
        )
        if st.session_state.indexed_pdf_name:
            st.success(f"**Current document:** `{st.session_state.indexed_pdf_name}` in collection `{st.session_state.last_collection}`")
        else:
            st.info("Upload a PDF in the *Index PDF* tab to get started.")

    with tab_index:
        st.subheader("Upload and index a PDF")

        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

        if uploaded_file is not None:
            st.caption(f"Selected: **{uploaded_file.name}**")
            if st.button("Index PDF into ChromaDB", type="primary"):
                with st.spinner("Extracting text and indexing..."):
                    file_bytes = uploaded_file.read()
                    num_chunks = index_uploaded_pdf(
                        file_bytes=file_bytes,
                        collection_name=collection_name,
                        chunk_size=chunk_size,
                    )
                if num_chunks == 0:
                    st.warning("No text could be extracted from the PDF.")
                else:
                    st.session_state.last_collection = collection_name
                    st.session_state.indexed_pdf_name = uploaded_file.name
                    st.success(f"Indexed **{num_chunks}** chunks into collection `{collection_name}`. You can now ask questions in the *Ask Questions* tab.")
        else:
            st.info("Upload a PDF file to index it.")

    with tab_qa:
        st.subheader("Ask questions")

        if not st.session_state.indexed_pdf_name:
            st.info("Index a PDF in the *Index PDF* tab first, or use a collection that was already populated (e.g. via the CLI).")

        question = st.text_input("Your question", placeholder="e.g. How old is Oxford University?")

        if st.button("Get Answer", type="primary") and question.strip():
            with st.spinner("Retrieving context and generating answer..."):
                answer, context_chunks = generation.run_rag_query(
                    user_query=question.strip(),
                    collection_name=collection_name,
                    n_results=n_results,
                    model_name=model_name,
                )

            st.markdown("#### Answer")
            st.write(answer)

            st.session_state.last_collection = collection_name
            st.session_state.qa_history.insert(
                0,
                {
                    "question": question.strip(),
                    "answer": answer,
                    "collection": collection_name,
                },
            )

            with st.expander("Show retrieved context chunks"):
                for i, chunk in enumerate(context_chunks, start=1):
                    st.markdown(f"**Chunk {i}:**")
                    st.write(chunk)
                    st.markdown("---")

        if st.session_state.qa_history:
            st.markdown("#### Recent questions")
            for item in st.session_state.qa_history[:5]:
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f"**A:** {item['answer']}")
                st.caption(f"Collection: `{item['collection']}`")
                st.markdown("---")


if __name__ == "__main__":
    main()
