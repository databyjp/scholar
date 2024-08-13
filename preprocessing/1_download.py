# File: ./preprocessing/1_download.py
import arxiv
from pathlib import Path
import json
import os

DL_DIR = Path("downloaded_papers")
DL_DIR.mkdir(exist_ok=True)


def download_latest_papers(query=None, max_results=10):
    search_query = "(abs:'rag' AND cat:cs.ai) OR (abs:'vector database' AND cat:cs.ai)"
    if query:
        search_query += f" AND {query}"

    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    client = arxiv.Client()

    for result in client.results(search):
        print(
            f"Found {result.get_short_id()}, published on {result.published}: {result.title}"
        )

        pdf_dl_path = DL_DIR / f"{result.get_short_id()}.pdf"
        metadata_dl_path = DL_DIR / f"{result.get_short_id()}.json"

        try:
            if not pdf_dl_path.exists():
                print(f"Downloading: {result.title}")
                result.download_pdf(
                    dirpath=str(DL_DIR), filename=f"{result.get_short_id()}.pdf"
                )
            else:
                print(f"Already downloaded: {result.title}")

            if not metadata_dl_path.exists():
                print(f"Saving metadata: {result.title}")
                metadata = {
                    "title": result.title,
                    "summary": result.summary,
                    "authors": [a.name for a in result.authors],
                    "published": result.published.isoformat(),
                    "arxiv_id": result.get_short_id(),
                    "categories": [r for r in result.categories],
                }
                metadata_dl_path.write_text(json.dumps(metadata, indent=2))
            else:
                print(f"Already saved metadata: {result.title}")

        except Exception as e:
            print(f"Error processing {result.get_short_id()}: {str(e)}")
            # Delete partially downloaded files
            if pdf_dl_path.exists():
                os.remove(pdf_dl_path)
            if metadata_dl_path.exists():
                os.remove(metadata_dl_path)
            print(f"Deleted partial files for {result.get_short_id()}")
            continue


if __name__ == "__main__":
    download_latest_papers(query="retrieval augmented generation", max_results=1000)
