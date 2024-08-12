from pypdf import PdfReader
from pathlib import Path

DL_DIR = Path("downloaded_papers")

pdf_files = list(DL_DIR.glob("*.pdf"))

for pdf_file in pdf_files:
    reader = PdfReader(pdf_file)
    number_of_pages = len(reader.pages)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        texts.append(text)
    print(f"Number of words in {pdf_file}:", sum(len(text.split()) for text in texts))
