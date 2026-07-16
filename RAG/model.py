import ollama
import os
import json
# read pdf_data.json file
with open("pdf_data.json", "r", encoding="utf-8") as f:
    pdf_data = json.load(f)
print(pdf_data.keys())
def extract_with_qwen(text):
    prompt = f"""
    Extract the following information from this research paper.

    Return ONLY valid JSON.

    Fields:
    - title
    - authors
    - abstract
    - summary

    Paper:

    {text}  # Limit to first 12000 characters to avoid exceeding token limits
    """

    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    ) 

    return response["message"]["content"]
for paper_id, paper in pdf_data.items():
    print(f"Processing paper: {paper_id}")
    extracted_info = extract_with_qwen(paper["text"])
    print(extracted_info)
 