import os
import requests


TMDB_BASE_URL = "https://api.themoviedb.org/3"


def search_tmdb(query):
    token = os.getenv("TMDB_READ_ACCESS_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }

    response = requests.get(
        f"{TMDB_BASE_URL}/search/multi",
        headers=headers,
        params={"query": query},
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def normalize_tmbd_result(result):
    """
    Function to convert one raw TMDb result into Eon's format.
    """
    
    media_type = result.get("media_type")
    if media_type not in ["movie", "tv"]:
        return None
    
    if media_type == "movie":
        title = result.get("title")
        date = result.get("release_date", "")
    else:
        title = result.get("name")
        date = result.get("first_air_date", "")
        
    release_year = None
    if date:
        try:
            release_year = int(date[:4])
        except ValueError:
            pass
    poster_path = result.get("poster_path")
    poster_url = None
    
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        
    return {
        "external_id":str(result["id"]),
        "title": title,
        "media_type": media_type,
        "release_year": release_year,
        "overview": result.get("overview", ""),
        "poster_url": poster_url,
        "source":"tmdb",
    }

def search_adaptations(query):
    """
    To search TMDb and eturn result based on the search query.
    """
    
    data= search_tmdb(query)
    adaptations = []
    
    results = data.get("results", [])
    
    for result in results:
        normalized = normalize_tmbd_result(result)
        if normalized:
            adaptations.append(normalized)
            
    return adaptations

def get_tmdb_credits(external_id, media_type):
    # Get the TMDb token from the environment.
    token = os.getenv("TMDB_READ_ACCESS_TOKEN")

    # Add the token to the request headers.
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }

    # Only allow movie or TV lookups.
    if media_type not in ["movie", "tv"]:
        return None

    # Build the credits endpoint URL.
    url = f"{TMDB_BASE_URL}/{media_type}/{external_id}/credits"

    # Ask TMDb for the credits data.
    response = requests.get(url, headers=headers, timeout=10)

    # Stop if TMDb returned an error.
    response.raise_for_status()

    # Return the JSON response.
    return response.json()


def get_tmdb_details(external_id, media_type):
    token = os.getenv("TMDB_READ_ACCESS_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "accept":"application/json",
    }
    
    if media_type not in ["movie", "tv"]:
        return None
    
    url = f"{TMDB_BASE_URL}/{media_type}/{external_id}"
    
    response = requests.get(
        url,
        headers=headers,
        timeout=10,
    )
    
    response.raise_for_status()
    return response.json()