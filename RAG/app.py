from dotenv import load_dotenv
import os
import pdfplumber
import fitz   
import pymupdf
from pathlib import Path


# loads .env into environment
load_dotenv()   

## how to get api key from environment variable
"""
api_key = os.getenv("API_KEY")
print(api_key)

"""

#2. Extract raw text from a PDF
# extract file list from data folder 
files = os.listdir("data/")
"""
for file in files:
    if file.endswith(".pdf"):
        pdf_path = os.path.join("data", file)
        with fitz.open(pdf_path) as pdf:
            text = ""
            for page in pdf:
                text += page.get_text()
            print(f"Extracted text from {file}:")
            print(text)
"""
# Initialize a dictionary to hold the text for each page 
pdf_text = {} 

pdf_folder = Path("data/")  # Path to the folder containing PDF files
for pdf_file in pdf_folder.glob("*.pdf"):  # Iterate over all PDF files in the folder
    full_text = ""
    with fitz.open(pdf_file) as pdf:  # Open the PDF file 
        for page in pdf:  # Iterate over each page in the PDF
            full_text += page.get_text()  # Extract text from the page and append it to full_text
    pdf_text[pdf_file.name] = full_text  # Store the extracted text in the
with open("extracted_text.json", "w") as f:  # Open a JSON file to save the extracted text
    import json
    json.dump(pdf_text, f)  # Write the dictionary to the JSON file
