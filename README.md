## RAG Naive – PDF Question Answering

A **minimal Retrieval-Augmented Generation (RAG)** pipeline over PDFs: upload a PDF, index it into ChromaDB, and ask questions answered by a Groq LLM using retrieved chunks.

- **Streamlit app** (`app.py`): Upload a PDF at runtime, index it into ChromaDB, then ask questions in the browser.
- **CLI scripts**: Same pipeline from the command line—`extraction.py` → `ingestion.py` → `generation.py`.

---

## 1. Project Structure

| File | Role |
|------|------|
| **`app.py`** | Streamlit UI: upload PDF → index into ChromaDB → ask questions (uses `extraction`, `ingestion`, `generation`). |
| **`extraction.py`** | PDF text extraction and chunking. Exposes `extract_pdf_to_chunks(path, size)` for files and `extract_bytes_to_chunks(file_bytes, size)` for uploads; defines `text_list` for CLI. |
| **`ingestion.py`** | ChromaDB ingestion. Exposes `ingest_chunks_into_chromadb(chunks, collection_name)`; uses persistent client in `chromadb_data`. |
| **`generation.py`** | RAG query. Exposes `run_rag_query(user_query, collection_name, n_results, model_name)`—retrieves chunks, builds prompt, calls Groq via OpenAI client (chat completions). |
| **`requirements.txt`** | Dependencies: Streamlit, ChromaDB, OpenAI client, PyPDF2, python-dotenv, etc. |

The Chroma database is stored in the **`chromadb_data`** folder (created automatically).

---

## 2. Prerequisites

- **Python**: 3.10+
- **OS**: Windows 10+ (tested on Windows 10)
- **Internet**: Required for the Groq API
- **Groq API key**: Get a valid **`GROQ_API_KEY`** from [Groq Console](https://console.groq.com)

---

## 3. Setup

### 3.1. Project folder

Place the project somewhere convenient, e.g.:

```text
c:\Users\DELL\Desktop\RAG\RAG Naive\
```

### 3.2. Virtual environment (PowerShell)

```powershell
cd "c:\Users\DELL\Desktop\RAG\RAG Naive"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in the prompt.

### 3.3. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs Streamlit, ChromaDB, PyPDF2, the OpenAI client (for Groq), python-dotenv, and supporting packages.

### 3.4. Groq API key

1. In the project root, create a file named **`.env`**.
2. Add (replace with your key):

```text
GROQ_API_KEY=your_real_groq_api_key_here
```

3. Save. Do not commit `.env` to version control.

---

## 4. Running the app (recommended)

With the venv activated:

```powershell
streamlit run app.py
```

A browser tab opens (usually http://localhost:8501).

1. **Index PDF**: Upload a PDF, set collection name and chunk size in the sidebar, click **Index PDF into ChromaDB**. The app extracts text, chunks it, and stores it in ChromaDB (replacing any existing collection with that name).
2. **Ask Questions**: Type a question and click **Get Answer**. The app retrieves relevant chunks and returns an answer from the Groq LLM. Use the expander to see retrieved context.

You can change **collection name**, **chunk size**, **number of chunks to retrieve**, and **Groq model** in the sidebar. If you get a 403 or “Permission denied”, try a model such as **`llama-3.1-8b-instant`** in the Groq model field.

---

## 5. Running the pipeline via CLI

You can run the same pipeline from the command line.

### 5.1. Optional: use a local PDF file

For CLI, `extraction.py` reads a file path. Default is `Oxford-Guide-2022.pdf` in the project folder. To use another file, set it in `extraction.py`:

```python
pdf_path = "your-file.pdf"
```

### 5.2. Extract and ingest

```powershell
python extraction.py
python ingestion.py
```

- **extraction.py**: Reads the PDF, extracts text, builds `text_list` (chunks of 500 characters by default). Prints a slice of chunks.
- **ingestion.py**: Imports `text_list`, calls `ingest_chunks_into_chromadb(text_list)` into the default collection `Oxford-Guide-2022` (or adjust the collection name in the script). Prints a sample of stored chunks.

### 5.3. Ask a question

Edit the query in `generation.py` if you want, then:

```powershell
python generation.py
```

- Loads the ChromaDB collection, runs `run_rag_query(...)`, prints the answer. Uses Groq via the OpenAI client (chat completions) and your `GROQ_API_KEY` from `.env`.

---

## 6. Customization

- **Chunk size**: In the app (sidebar) or in `extraction.py` (`chunk_size = 500`). Larger = more context per chunk; smaller = finer-grained retrieval.
- **Collection name**: In the app sidebar or in `ingestion.py` / `generation.py` when using CLI.
- **Groq model**: In the app sidebar or in `generation.py` (`model_name=...`). Use a valid [Groq model ID](https://console.groq.com/docs/models), e.g. `llama-3.1-8b-instant`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`.

---

## 7. Troubleshooting

- **403 / Permission denied / “Access denied. Check your network settings.”**  
  - The app uses the **Chat Completions** API (`chat.completions.create`). If you still see 403, try:
    - A known Groq model ID in the sidebar (e.g. `llama-3.1-8b-instant`).
    - Checking API key and permissions at [Groq Console](https://console.groq.com).
    - Network/proxy/firewall allowing access to `https://api.groq.com`.

- **Chroma collection not found**  
  - Index a PDF first (app: Index PDF tab; CLI: run `ingestion.py`). Use the same collection name when asking questions.

- **`GROQ_API_KEY` missing or invalid**  
  - Ensure `.env` exists in the project root with `GROQ_API_KEY=your_key` (no quotes, no extra spaces). `load_dotenv()` is called in `generation.py`.

- **`FileNotFoundError` for PDF (CLI)**  
  - Put the PDF in the project folder and set `pdf_path` in `extraction.py` to match the filename.

- **PowerShell won’t run the venv script**  
  - Run (as admin if needed):  
    `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## 8. How the RAG pipeline works

- **Retrieval**: PDF text is split into chunks and stored in ChromaDB. For each question, the most relevant chunks are retrieved.
- **Augmented generation**: Those chunks are passed to the Groq LLM as context; the model is instructed to answer only from that context and to say “I don’t have this information yet.” when the context is insufficient.

This is a minimal, readable implementation suitable for learning and extension (e.g. better chunking, custom embeddings, or extra UI).

---

## 9. Summary

1. **Setup**: Create venv, `pip install -r requirements.txt`, add `GROQ_API_KEY` to `.env`.
2. **Run app**: `streamlit run app.py` → upload PDF in **Index PDF** → ask questions in **Ask Questions**.
3. **Or use CLI**: Place PDF, set `pdf_path` in `extraction.py` → `python extraction.py` → `python ingestion.py` → edit query in `generation.py` → `python generation.py`.

You now have a working RAG pipeline: index a PDF (app or CLI) and ask questions against it.
