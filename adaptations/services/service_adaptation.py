from difflib import SequenceMatcher # To compare how similar two titles are.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from adaptations.services.tmdb import search_adaptations, get_tmdb_credits, get_tmdb_details

import re

story_model = SentenceTransformer("all-MiniLM-L6-v2")

# candidate = one movie or TV show that might be an adaptation of the book.

def normalize_text(text):
    """
    To clean a title or name so matching is easier
    """
    if not text:
        return ""
    
    text = text.lower()
    
    text = re.sub(r"[^a-z0-9\s]", " ", text) # re.sub(pattern, replacement, text) ^ - Not

    # Collapse repeated spaces into a single space.
    text = re.sub(r"\s+"," ", text).strip()

    # Return the cleaned text.
    return text

def extract_year(value):
    """
    To get a year out of date.
    
    """
    
    if not value:
        return None
    try:
        return int(value[:4])
    except ValueError:
        return None
    
def calculate_title_similarity(book_title, adaptation_title):
    """
    To compare a book title with an adaptation title.
    """
    
    clean_book_title = normalize_text(book_title)
    clean_adaptation_title = normalize_text(adaptation_title)
    
    # Here using basic similarity score as one signal.
    similarity = SequenceMatcher (
        None,
        clean_book_title,
        clean_adaptation_title,
    ).ratio()
    
    return similarity

def get_name_parts(name):
    """
    Convert a persons name into useful parts for comparison.
    """
    clean_name = normalize_text(name)
    parts = clean_name.split()
    
    return parts

def authors_match(book_author, credit_name):
    """
    To check whether two differently formatted names likely belong to the same author.
    """
    # Convert book authors name into spersate parts.
    book_parts = get_name_parts(book_author)
    
    # Convert the TMDb credit name into sperate parts.
    credit_parts = get_name_parts(credit_name)
    
    if not book_parts or not credit_parts:
        return False
    
    book_last_name = book_parts[-1]
    credit_last_name = credit_parts[-1]
    
    if book_last_name != credit_last_name:
        return False
    
    book_first = book_parts[0]
    credit_first = credit_parts[0]
    
    if book_first[0] != credit_first[0]:
        return False
    
    return True
    

def author_appears_in_credits(book_author, credits):
    """
    Check whether the book author appears in TMDbs crew credit.
    """
    
    if not book_author or not credits:
        return False
    
    for person in credits.get("crew", []):
        credit_name = person.get("name", "")
        credit_job = normalize_text(person.get("job", ""))
        writing_jobs = {
            "novel",
            "book",
            "author",
            "writer",
            "character",
            "characters",
            "original story",
            "story",
        }
        
        if credit_job not in writing_jobs:
            continue
        if authors_match(book_author, credit_name):
            return True
    
    return False
    

def calculate_story_similarity(book_description, adaptation_overview):
    """
    comapre the meaning of a book description with an adaption overview.
    """
    
    if not book_description or not adaptation_overview:
        return 0.0
    
    # both pieces of text into a list for the ML model
    texts = [
        book_description,
        adaptation_overview,
    ]
    
    # Convering both texts into semantic vectors
    embeddings = story_model.encode(
        texts, normalize_embeddings=True,
    )

    book_embedding = embeddings[0] # Get the vector representing book description
    adaptation_embedding = embeddings[1] # Get the vector represting the movie or TV overview.
    similarity = book_embedding @ adaptation_embedding # Calculating cosine similarity using the normalized vectors.
    
    return float(similarity) # Numpy value to float.
    

def calculate_confidence_score(book, candidate, details, credits):
    
    title_score = calculate_title_similarity(
        book.title, 
        candidate["title"],
    )
   
    author_score = 0.0
    
    # Full score if author is in TMDbcredits.
    if author_appears_in_credits(
        getattr(book,"author", ""), 
        credits
    ):
        author_score = 1.0
        
    year_score = 0.0
    
    # Get the og publication yea instead of the edition date.
    book_year = getattr(
        book,
        "original_publication_year",
        None,
    )
    
    adaptation_year = candidate.get("release_year")
    
    # Giving a year score when the adaptation came out after the book.
    if (
        book_year
        and adaptation_year
        and adaptation_year >= book_year
    ):
        year_score = 1.0
        
    book_description = getattr(
        book,
        "description",
        "",
    )
    
    adaptation_overview = details.get(
        "overview",
        "",
    ) if details else ""
    
    story_score = calculate_story_similarity(
        book_description,
        adaptation_overview,
    )
    
    confidence = (
        title_score * 0.35
        + author_score * 0.30
        + story_score * 0.25
        + year_score * 0.10
    )
    
    return {
        "confidence": confidence,
        "title_score": title_score,
        "author_score": author_score,
        "story_score": story_score,
        "year_score": year_score,
    }
        
def find_adaptations_for_book(book):
    if book is None:
        return []
    
    results = search_adaptations(book.title)
    
    matches = []
    
    for result in results:
        
        #Get details for candidate.
        details = get_tmdb_details(result["external_id"], result["media_type"])
        
        # Get details for credit.
        credits = get_tmdb_credits(result["external_id"], result["media_type"])
        
        scores = calculate_confidence_score(book, result, details, credits)
        
        result["match_score"] = scores["confidence"]
        result["title_score"] = scores["title_score"]
        result["author_score"] = scores["author_score"]
        result["story_score"] = scores["story_score"]
        result["year_score"] = scores["year_score"]
       
        
        # if result["match_score"] >= 0.70:
        #     matches.append(result)
        
        matches.append(result)
            
    matches.sort(
        key=lambda result: result["match_score"],
        reverse=True,
    )

    return matches
    





        