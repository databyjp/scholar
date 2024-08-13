# File: ./preprocessing/3_extract_pdf_text.py
import json
from pathlib import Path
from helpers import pdf_to_chunks

DL_DIR = Path("downloaded_papers")
EXTRACTED_DIR = Path("extracted_text")


def extract_and_save_text():
    EXTRACTED_DIR.mkdir(exist_ok=True)
    papers_list = list(DL_DIR.glob("*.pdf"))

    for paper in papers_list:
        print(f"Processing {paper.stem}...")
        chunks = pdf_to_chunks(paper)
        metadata = json.loads((DL_DIR / f"{paper.stem}.json").read_text())

        extracted_data = {"metadata": metadata, "chunks": chunks}

        output_file = EXTRACTED_DIR / f"{paper.stem}.json"
        with open(output_file, "w") as f:
            json.dump(extracted_data, f)

        print(f"Saved extracted text for {paper.stem}")


if __name__ == "__main__":
    extract_and_save_text()
