from pypdf import PdfReader
from pathlib import Path
from typing import List
import re

DL_DIR = Path("downloaded_papers")


def get_chunks(text: str, n_words: int = 150, overlap: float = 0.2) -> List[str]:
    words = re.findall(r'\S+|\n', text)
    chunk_size = int(n_words) + 1
    overlap_size = int(overlap * n_words)
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i : i + chunk_size + overlap_size]))
    return chunks


def pdf_to_chunks(pdf_file: Path) -> List[str]:
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n\n"
    return get_chunks(text)
