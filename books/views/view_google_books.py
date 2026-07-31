from django.shortcuts import render, redirect

from books.models import Book
from books.services.google_books import search_google_books, get_google_book_by_id

def import_google_book(request, google_book_id):
    """
    Save one google book result into local book model.
    """
    
    google_book = get_google_book_by_id(google_book_id)
    
    author_text = ", ".join(google_book["authors"])
    
    book, created = Book.objects.get_or_create(
       google_book_id = google_book["google_book_id"],
       defaults={
           "title": google_book["title"],
           "author":author_text,
           "total_pages": google_book["page_count"],
           "published_date": google_book["published_date"],
           "cover_url": google_book["thumbnail"],
        
       }
   )
    return redirect("books:book_detail", pk=book.pk) # Once saved, send the user back to their saved book list.

def google_book_search(request):
    query = request.GET.get("q", "").strip()
    results = []
    
    if query:
        results = search_google_books(query)
        
    return render(
        request,
        "books/google_book_search.html",
        {
            "query": query,
            "results": results,
        }
    )
    

