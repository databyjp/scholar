import arxiv
from pathlib import Path
import json

DL_DIR = Path("downloaded_papers")
DL_DIR.mkdir(exist_ok=True)


def download_latest_papers(query=None, max_results=10):
    # Create a search query for computer science papers
    search_query = (
        "(abs:'rag' AND cat:cs.ai) OR (abs:'vector database' AND cat:cs.ai)"  # 'cs' is the category for computer science
    )
    if query:
        search_query += f" AND {query}"

    # Create a search object
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    # Initialize the client
    client = arxiv.Client()

    # Fetch the results
    for result in client.results(search):
        print(
            f"Found {result.get_short_id()}, published on {result.published}: {result.title}"
        )

        pdf_dl_path = DL_DIR / f"{result.get_short_id()}.pdf"
        if not pdf_dl_path.exists():
            print(f"Downloading: {result.title}")
            result.download_pdf(
                dirpath=str(DL_DIR), filename=f"{result.get_short_id()}.pdf"
            )
        else:
            print(f"Already downloaded: {result.title}")

        metadata_dl_path = DL_DIR / f"{result.get_short_id()}.json"
        if not metadata_dl_path.exists():
            print(f"Saving metadata: {result.title}")
            metadata = {
                "title": result.title,
                "abstract": result.summary,
                "authors": [a.name for a in result.authors],
                "published": result.published.isoformat(),
                "arxiv_id": result.get_short_id(),
                "categories": [r for r in result.categories],
            }
            metadata_dl_path.write_text(json.dumps(metadata, indent=2))
        else:
            print(f"Already saved metadata: {result.title}")


download_latest_papers(query="retrieval augmented generation", max_results=1000)
