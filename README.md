## RAG Naive – PDF Question Answering

This project is a **minimal Retrieval-Augmented Generation (RAG)** pipeline built around a single PDF.  
It:
- **Extracts text** from a PDF (`extraction.py`)
- **Indexes it in ChromaDB** (`ingestion.py`)
- **Answers questions using Groq LLM** with context retrieved from ChromaDB (`generation.py`)

Everything is written in plain Python scripts so you can see each step clearly.

---

## 1. Project Structure

- **`extraction.py`**: Reads `Oxford-Guide-2022.pdf`, extracts all text, splits it into ~500‑character chunks, and exposes them as `text_list`.
- **`ingestion.py`**: Creates (or reuses) a **persistent ChromaDB collection** and inserts all chunks from `text_list`.
- **`generation.py`**:  
  - Loads the ChromaDB collection  
  - Retrieves the most relevant chunks for a user query  
  - Sends a prompt with that context to the Groq LLM via the OpenAI client
- **`requirements.txt`**: Python dependencies (ChromaDB, OpenAI client, PyPDF2, `python-dotenv`, etc.).

The Chroma database is stored on disk in the `chromadb_data` folder (created automatically).

---

## 2. Prerequisites

- **OS**: Windows 10 or later (tested on Windows 10)
- **Python**: 3.10+ recommended
- **Internet access**: Required to call the Groq API
- **Groq API key**:
  - You need a valid **`GROQ_API_KEY`** from Groq

---

## 3. Setup Instructions (Step by Step)

### 3.1. Clone or download the project

Place the project folder somewhere convenient, e.g.:

```text
c:\Users\DELL\Desktop\RAG\RAG Naive\
```

Make sure the scripts (`extraction.py`, `ingestion.py`, `generation.py`) and `requirements.txt` are inside this folder.

### 3.2. Place your PDF

By default, `extraction.py` expects a file named:

```text
Oxford-Guide-2022.pdf
```

Steps:
- Put your PDF file in the same folder as the scripts.
- If your PDF has a **different name**, either:
  - Rename the file to `Oxford-Guide-2022.pdf`, **or**
  - Change the `pdf_path` variable in `extraction.py`:

```python
pdf_path = "your-file-name.pdf"
```

### 3.3. Create and activate a virtual environment (Windows, PowerShell)

From the project folder:

```powershell
cd "c:\Users\DELL\Desktop\RAG\RAG Naive"

python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

You should now see `(.venv)` at the start of your PowerShell prompt.

### 3.4. Install dependencies

With the virtual environment activated:

```powershell
pip install -r requirements.txt
```

This installs:
- `PyPDF2` for PDF text extraction
- `chromadb` for vector storage
- `openai` client for talking to the Groq API
- `python-dotenv` for loading environment variables
- And other supporting libraries

### 3.5. Configure your Groq API key

`generation.py` reads `GROQ_API_KEY` from a `.env` file using `python-dotenv`.

1. In the project root (`RAG Naive`), create a file named `.env`.
2. Add this line (replace the placeholder with your key):

```text
GROQ_API_KEY=your_real_groq_api_key_here
```

3. Save the file.  

> **Security tip**: Do not commit `.env` to version control; it should stay private.

---

## 4. Running the Pipeline

Run the scripts **in this order**:

1. **Extract text from the PDF**
2. **Ingest chunks into ChromaDB**
3. **Ask questions using the LLM**

All commands below assume you are in:

```powershell
cd "c:\Users\DELL\Desktop\RAG\RAG Naive"
.\.venv\Scripts\Activate.ps1
```

### 4.1. Step 1 – Extract PDF text

```powershell
python extraction.py
```

What this does:
- Opens the PDF specified by `pdf_path`
- Uses `PyPDF2.PdfReader` to iterate over all pages and call `extract_text()`
- Concatenates all page text into a single string
- Splits the text into chunks of ~500 characters:

```python
chunk_size = 500
text_list = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
```

At the end, `text_list` is a list of string chunks that will be imported by `ingestion.py`.

> You may see a printed slice of the chunks in the console (e.g., `text_list[100:103]`) just to verify extraction worked.

### 4.2. Step 2 – Ingest chunks into ChromaDB

```powershell
python ingestion.py
```

What this does:
- Imports `text_list` from `extraction.py`
- Creates a **persistent** ChromaDB client in `chromadb_data`:

```python
client = chromadb.PersistentClient(path="chromadb_data")
collection = client.create_collection(name="Oxford-Guide-2022")
```

- Prepares:
  - `chunks = text_list`
  - `chunks_ids = [f"chunk_{i}" for i in range(len(chunks))]`
- Adds all chunks to the ChromaDB collection:

```python
collection.add(
    ids=chunks_ids,
    documents=chunks
)
```

- Optionally prints some chunk IDs and contents so you can visually inspect that ingestion worked.

> **Note**: Because the client is **persistent**, the `chromadb_data` directory is created and reused automatically. You can shut down and rerun later without losing the index.

### 4.3. Step 3 – Ask a question (RAG generation)

```powershell
python generation.py
```

What this does:
- Connects to the same persistent ChromaDB:

```python
client = chromadb.PersistentClient(path="chromadb_data")
collection = client.get_collection(name="Oxford-Guide-2022")
```

- Loads environment variables from `.env`:

```python
load_dotenv()
```

- Creates an OpenAI client **pointing to Groq’s API**:

```python
client_groq = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
```

- Defines a **user query** (you can edit this in the script):

```python
user_query = "How old is Oxford University?"
```

- Queries ChromaDB for the most relevant chunks:

```python
context = collection.query(
    query_texts=user_query,
    n_results=10,
)
```

- Builds a prompt that:
  - Includes the retrieved context
  - Instructs the model to:
    - Answer using only the provided context
    - Return `"I don't have this information yet."` if context is insufficient

- Calls the Groq model:

```python
response = client_groq.responses.create(
    input=prompt,
    model="openai/gpt-oss-20b",
)
```

- Prints:
  - The retrieved context (for debugging)
  - The final answer: `response.output_text`

To ask **a different question**, just edit the `user_query` string in `generation.py` and rerun the script.

---

## 5. Customization

### 5.1. Use a different PDF

If you want to index another PDF:
- Replace `Oxford-Guide-2022.pdf` with your own file
- Or change the `pdf_path` variable in `extraction.py`
- Rerun:
  1. `python extraction.py`
  2. `python ingestion.py`
  3. `python generation.py`

You may also want to:
- Change the Chroma collection name in both `ingestion.py` and `generation.py` to match your document, e.g.:

```python
collection = client.create_collection(name="my-new-pdf")
collection = client.get_collection(name="my-new-pdf")
```

### 5.2. Adjust chunk size

In `extraction.py`, you can change:

```python
chunk_size = 500
```

Larger chunks:
- Fewer items in Chroma
- More context per chunk, but might be less precise

Smaller chunks:
- More fine‑grained retrieval
- More items to store and retrieve

After changing chunk size, rerun the full pipeline.

### 5.3. Change the model

`generation.py` currently uses:

```python
model="openai/gpt-oss-20b"
```

If your Groq account supports other models, you can plug in a different model name here.  
Check Groq’s documentation for the list of available model IDs.

---

## 6. Troubleshooting

- **`FileNotFoundError` for the PDF**
  - Confirm the PDF is in the project root.
  - Confirm the `pdf_path` in `extraction.py` matches the file name exactly.

- **Chroma collection not found**
  - Ensure you ran `ingestion.py` before `generation.py`.
  - Make sure both scripts use the same collection name (`"Oxford-Guide-2022"` by default).

- **`GROQ_API_KEY` is None or unauthorized**
  - Confirm `.env` exists in the project root.
  - Confirm the line `GROQ_API_KEY=...` is correct (no quotes, no extra spaces).
  - Ensure `python-dotenv` is installed and `load_dotenv()` is called before using the key.

- **Dependencies missing**
  - Re-run:

```powershell
pip install -r requirements.txt
```

- **Permission issues on Windows when activating venv**
  - If PowerShell blocks script execution, you may need to relax the execution policy (as admin):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating the virtual environment again.

---

## 7. How This RAG Pipeline Works (Conceptual)

- **Retrieval**:
  - Converts your long PDF into many smaller text chunks.
  - Uses **ChromaDB** to store and retrieve the most relevant chunks for a user query.
- **Augmented Generation**:
  - The retrieved chunks are inserted into the LLM prompt as **context**.
  - The LLM is instructed to answer using only this context, avoiding hallucinations as much as possible.

This is a **naive but clear** implementation, ideal for learning and experimentation. From here you can extend it with:
- Better chunking (e.g., by sentences or headings instead of raw characters)
- Embeddings-based similarity search with custom embedding models
- A simple API or UI on top of `generation.py`

---

## 8. Summary of Typical Workflow

1. **Set up environment**: create venv, install `requirements.txt`, configure `.env` with `GROQ_API_KEY`.
2. **Prepare data**: place your PDF and adjust `pdf_path` if needed.
3. **Run extraction**: `python extraction.py`.
4. **Run ingestion**: `python ingestion.py`.
5. **Ask questions**: edit `user_query` in `generation.py` and run `python generation.py`.

You now have a working, minimal RAG pipeline over a single PDF.

