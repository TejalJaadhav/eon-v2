import requests
from django.conf import settings
import string


GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

def search_google_books(query, max_results=10):
    """
    Search Google Books and return a list of book results.
    """
    
    response = requests.get(
        GOOGLE_BOOKS_URL,
        params = {
            "q": query, # Search text type by the user.
            "maxResults": max_results,
            "key": settings.GOOGLE_BOOKS_API_KEY,
        },
        timeout=10,
    )
    
    response.raise_for_status()
    
    data = response.json()
    items = data.get("items", [])
    
    return [normalize_google_book_item(item) for item in items]


def normalize_google_book_item(item):
    """
    To convert one google books item into clean format.
    """
    
    volume_info = item.get("volumeInfo", {})
    
    thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "")
    
    # Converting to https so browser more likely to load the images.
    if thumbnail.startswith("http://"):
        thumbnail = thumbnail.replace("http://", "https://", 1)
    
    book_details_map = {
        "google_book_id": item.get("id", ""),
        "title": volume_info.get("title", ""),
        "authors" : volume_info.get("authors", []),
        "page_count": volume_info.get("pageCount"),
        "published_date": volume_info.get("publishedDate", ""),
        "thumbnail": thumbnail,
        "description": volume_info.get("description", ""),
    }
    
    return book_details_map

def get_title_words(title):
    """
    Returns lowercase words from a title for similarity checks.
    """
    ignored_words = {"the", "a", "an", "and", "of", "to", "in", "for", "by"}
    
    # Creating translation table that turns punctuation to spaces.
    punctuation_to_spaces = str.maketrans(
        string.punctuation, 
        " " * len(string.punctuation),
    )
    
    cleaned_title = title.lower().translate(punctuation_to_spaces)
    
    words = cleaned_title.split()
    
    return {
        word
        for word in words
        if word not in ignored_words and len(word) > 2
    }

def get_google_book_by_id(google_book_id):
    """
    To fetch one exact book from Google Books using its Google book ID.
    """
    
    response = requests.get(
        f"{GOOGLE_BOOKS_URL}/{google_book_id}",
        params={"key":settings.GOOGLE_BOOKS_API_KEY,},
        timeout=10,
    )
    
    response.raise_for_status()
    item = response.json() # Converting google's json to py dict
    
    return normalize_google_book_item(item)
    
    
    