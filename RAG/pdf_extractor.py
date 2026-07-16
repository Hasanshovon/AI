from dotenv import load_dotenv
import os
import pymupdf as fitz
from pathlib import Path

load_dotenv()

pdf_folder = Path("data")
pdf_data = {}

HEADING_ABSTRACT = "abstract"
HEADING_INTRODUCTION = "introduction"
HEADING_CONCLUSION = "conclusion"
HEADING_REFERENCES = "references"

def find_heading(text, heading, start=0, last=False):
    """Return the character index of a case-insensitive match of `heading`
    at or after `start`. If last=True, return the LAST match at/after start
    instead of the first. Returns None if not found."""
    if not last:
        idx = text.lower().find(heading, start)
        return idx if idx != -1 else None
    else:
        idx = text.lower().rfind(heading)
        return idx if idx != -1 and idx >= start else None

def extract_title(text, fallback):
    for line in text.splitlines():
        line = line.strip()
        if len(line) >= 5 and not line.replace(" ", "").isdigit():
            return line
    return fallback

def extract_sections(text):
    abstract_pos = find_heading(text, HEADING_ABSTRACT)
    intro_pos = find_heading(text, HEADING_INTRODUCTION)
    conclusion_pos = find_heading(text, HEADING_CONCLUSION)
    # references heading is almost always the LAST occurrence in the doc
    # (earlier matches are usually just the word appearing in-text)
    references_pos = find_heading(text, HEADING_REFERENCES, last=True)

    sections = {}

    # Abstract: from "abstract" to "introduction"
    if abstract_pos is not None:
        end = intro_pos if intro_pos is not None else abstract_pos + 1500
        sections["abstract"] = text[abstract_pos:end].strip()
    else:
        sections["abstract"] = ""

    # Introduction: from "introduction" to "references"
    if intro_pos is not None:
        end = references_pos if references_pos is not None and references_pos > intro_pos else intro_pos + 3000
        sections["introduction"] = text[intro_pos:end].strip()
    else:
        sections["introduction"] = ""

    # Conclusion: from "conclusion" to the last "references" AFTER conclusion_pos.
    # Search for references starting from conclusion_pos so we never get
    # an end position earlier than the start position.
    if conclusion_pos is not None:
        refs_after_conclusion = find_heading(text, HEADING_REFERENCES, start=conclusion_pos, last=True)
        end = refs_after_conclusion if refs_after_conclusion is not None else conclusion_pos + 2000
        sections["conclusion"] = text[conclusion_pos:end].strip()
    else:
        sections["conclusion"] = ""

    found_count = sum(1 for v in sections.values() if v)
    if found_count == 0:
        status = "failed"
    elif found_count < 3:
        status = "partial"
    else:
        status = "success"

    trimmed_text = "\n\n".join(
        f"[{name.upper()}]\n{content}" for name, content in sections.items() if content
    )

    return trimmed_text, status

for pdf_file in pdf_folder.glob("*.pdf"):
    try:
        with fitz.open(pdf_file) as pdf:
            text = "\n".join(page.get_text() for page in pdf)

        title = extract_title(text, pdf_file.stem)
        trimmed_text, trimming_status = extract_sections(text)

        pdf_data[pdf_file.stem] = {
            "id": pdf_file.stem,
            "title": title,
            "source": str(pdf_file),
            "text": text,
            "trimmed_text": trimmed_text,
            "trimming_status": trimming_status,
        }
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

print(f"Processed {len(pdf_data)} PDF files.")
for k, v in pdf_data.items():
    print(f"{v['title'][:60]:<60} | trimming: {v['trimming_status']}")