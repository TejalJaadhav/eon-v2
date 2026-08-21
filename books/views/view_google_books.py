from django.shortcuts import render, redirect

from books.models import Book
from books.services.google_books import search_google_books, get_google_book_by_id, get_title_words
from books.services.open_library import find_original_publication_year
from adaptations.services.service_adaptation import find_adaptations_for_book

def import_google_book(request, google_book_id):
    """
    Save one google book result into local book model.
    """
    
    google_book = get_google_book_by_id(google_book_id)
    selected_status = request.POST.get("status", Book.WANT_TO_READ)
    author_text = ", ".join(google_book["authors"])
    
    original_publication_year = find_original_publication_year (
        google_book["title"],
        author_text,
    )
    
    book, created = Book.objects.get_or_create(
       google_book_id=google_book["google_book_id"],
       defaults={
           "title": google_book["title"],
           "status": selected_status,
           "author": author_text,
           "total_pages": google_book["page_count"],
           "published_date": google_book["published_date"],
           "original_publication_date": original_publication_year,
           "cover_url": google_book["thumbnail"],
           "description": google_book["description"],
        
       }
   )
    
    if created:
        find_adaptations_for_book(book)
        
    return redirect("books:book_detail", pk=book.pk) # Once saved, send the user to the saved book detail page.


def google_book_search(request):
    query = request.GET.get("q", "").strip()
    results = []
    saved_google_book_ids = set()
    if query:
        results = search_google_books(query)
        
        saved_books_by_google_id = {
            saved_book.google_book_id: saved_book 
            for saved_book in Book.objects.filter(
                google_book_id__in=[book["google_book_id"] for book in results]
            )
        }
        
        saved_google_book_ids = set(saved_books_by_google_id.keys())
        
        saved_title_words = [
            get_title_words(title)
            for title in Book.objects.exclude(title="").values_list("title", flat=True)
        ]
        
        for book in results:
            book["saved_book"] = saved_books_by_google_id.get(book["google_book_id"])
            google_title_words = get_title_words(book["title"])

            book["has_similar_saved_title"] = (
                book["google_book_id"] not in saved_google_book_ids
                and any(
                    len(google_title_words & saved_words) >=2
                    for saved_words in saved_title_words
                )
            )
        
    return render(
        request,
        "books/google_book_search.html",
        {
            "query": query,
            "results": results,
            "saved_google_book_ids": saved_google_book_ids,
        },
    )
    

