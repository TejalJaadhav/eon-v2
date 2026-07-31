import requests
from django.conf import settings


GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

def search_google_books(query, max_result=10):
    response = requests.get(
        GOOGLE_BOOKS_URL,
        params = {
            "q": query,
            "maxResults": max_result,
            "key": settings.GOOGLE_BOOKS_API_KEY,
        },
        timeout=10,
    )
    
    response.raise_for_status()
    
    data = response.json()
    items = data.get("items", [])
    
    return [normalize_google_book_item(item) for item in items]


def normalize_google_book_item(item):
    volume_info = item.get("volumeInfo", {})
    
    thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "")
    
    if thumbnail.startswith("http://"):
        thumbnail = thumbnail.replace("http://", "https://", 1)
    
    book_details_map = {
        "google_book_id": item.get("id", ""),
        "title": volume_info.get("title", ""),
        "authors" : volume_info.get("authors", []),
        "page_count": volume_info.get("pageCount"),
        "published_date": volume_info.get("publishedDate", ""),
        "thumbnail": thumbnail,
    }
    
    return book_details_map