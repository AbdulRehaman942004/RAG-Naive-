from typing import List

import PyPDF2

pdf_path = "Oxford-Guide-2022.pdf"
chunk_size = 500


def extract_bytes_to_chunks(
    file_bytes: bytes,
    size: int | None = None,
) -> List[str]:
    """Extract text from PDF bytes (e.g. uploaded file) and split into chunks."""
    import io

    target_chunk = size or chunk_size
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return [full_text[i : i + target_chunk] for i in range(0, len(full_text), target_chunk)]


def extract_pdf_to_chunks(
    path: str | None = None,
    size: int | None = None,
) -> List[str]:
    """Extract all text from a PDF and split into fixed-size chunks.

    This wraps the original script logic so both the CLI scripts and the
    Streamlit frontend use the same implementation.
    """
    target_path = path or pdf_path
    target_chunk = size or chunk_size

    full_text = ""
    with open(target_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    return [full_text[i : i + target_chunk] for i in range(0, len(full_text), target_chunk)]


# Preserve original behaviour for scripts that import text_list
try:
    text_list = extract_pdf_to_chunks()
except Exception:
    text_list = []

if __name__ == "__main__":
    # print a slice of chunks
    print(text_list[100:103])