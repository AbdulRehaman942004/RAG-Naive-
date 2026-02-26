import PyPDF2

pdf_path = "Oxford-Guide-2022.pdf"

# Extract all text from PDF
full_text = ""
with open(pdf_path, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            # Combine all text into a single string
            full_text += text + "\n"

# Split text into chunks of ~500 characters
chunk_size = 500
text_list = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

#print a slice of chunks
print(text_list[100:103])