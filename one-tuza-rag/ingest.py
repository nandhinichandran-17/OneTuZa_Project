# ingest.py
import os
import re
from typing import List
from pypdf import PdfReader
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    id: str
    source: str
    text: str

# ------------------------
# Cleaning utility
# ------------------------
def clean_text(raw: str) -> str:
    """Remove HTML/Markdown tags and extra spaces from text."""
    # strip HTML tags
    text = re.sub(r"<[^>]+>", " ", raw)
    # remove markdown headers/symbols (#, *, >, etc.)
    text = re.sub(r"[#*_>`~\-]+", " ", text)
    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ------------------------
# Readers
# ------------------------
def read_pdf(path: str) -> str:
    text = []
    reader = PdfReader(path)
    for p in range(len(reader.pages)):
        page = reader.pages[p]
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        text.append(t)
    return clean_text("\n".join(text))

def read_md(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    return clean_text(raw)

# ------------------------
# Chunker
# ------------------------
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    n = len(tokens)
    while i < n:
        chunk = tokens[i : min(i + chunk_size, n)]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

# ------------------------
# Ingest function
# ------------------------
def ingest_local_documents(folder: str = "docs/"):
    chunks = []
    idx = 0
    for fn in sorted(os.listdir(folder)):
        path = os.path.join(folder, fn)
        if os.path.isdir(path):
            continue
        ext = fn.lower().split(".")[-1]
        try:
            if ext == "pdf":
                text = read_pdf(path)
            elif ext in ("md", "markdown", "txt"):
                text = read_md(path)
            else:
                # skip unknown file types
                continue
        except Exception as e:
            print(f"Error reading {path}: {e}")
            continue
        text = text.strip()
        if not text:
            continue
        for i, t in enumerate(chunk_text(text)):
            idx += 1
            chunks.append(DocumentChunk(id=f"{fn}__chunk_{i+1}", source=fn, text=t))
    print(f"[ingest] produced {len(chunks)} chunks from {folder}")
    return chunks

# ------------------------
# Debug run
# ------------------------
if __name__ == "__main__":
    c = ingest_local_documents("docs/")
    for x in c[:2]:
        print(x)
