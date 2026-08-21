import requests

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"

def find_original_publication_year(title, author):
    response = requests.get(
        OPEN_LIBRARY_SEARCH_URL,
        params={
            "title": title,
            "author": author,
            "limit":5,
        },
        timeout=10,
    )
    
    response.raise_for_status()
    data = response.json()
    results = data.get("docs", [])
    if not results:
        return None
    for result in results:
        first_publish_year = result.get("first_publish_year")
        if first_publish_year:
            return first_publish_year
    return None