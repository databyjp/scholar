import arxiv
from pathlib import Path

DL_DIR = Path("downloaded_papers")
DL_DIR.mkdir(exist_ok=True)


def download_latest_papers(query=None, max_results=10):
    # Create a search query for computer science papers
    search_query = (
        "abs:'rag' AND cat:cs.ai"  # 'cs' is the category for computer science
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
        dl_path = DL_DIR / f"{result.get_short_id()}.pdf"
        if not dl_path.exists():
            print(f"Downloading: {result.title}")
            result.download_pdf(
                dirpath=str(DL_DIR), filename=f"{result.get_short_id()}.pdf"
            )
        else:
            print(f"Already downloaded: {result.title}")


download_latest_papers(query="retrieval augmented generation", max_results=500)
