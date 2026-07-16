from dotenv import load_dotenv
import os
import pdfplumber
import fitz   
import pymupdf as fitz
from pathlib import Path


# loads .env into environment
load_dotenv()   

## how to get api key from environment variable
"""
api_key = os.getenv("API_KEY")
print(api_key)

"""


pdf_folder = Path("data")
pdf_data = {}

for pdf_file in pdf_folder.glob("*.pdf"):
    with fitz.open(pdf_file) as pdf:
        text = "".join(page.get_text() for page in pdf)

    title = next(
        (line.strip() for line in text.splitlines() if line.strip()),
        pdf_file.stem
    )

    pdf_data[pdf_file.stem] = {
        "id": pdf_file.stem,
        "title": title,
        "source": str(pdf_file),
        "text": text,
    }

print(pdf_data)
