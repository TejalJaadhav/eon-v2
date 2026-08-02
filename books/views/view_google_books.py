from django.shortcuts import render, redirect

from books.models import Book
from books.services.google_books import search_google_books, get_google_book_by_id

def import_google_book(request, google_book_id):
    """
    Save one google book result into local book model.
    """
    
    google_book = get_google_book_by_id(google_book_id)
    selected_status = request.POST.get("status", Book.WANT_TO_READ)
    author_text = ", ".join(google_book["authors"])
    
    book, created = Book.objects.get_or_create(
       google_book_id = google_book["google_book_id"],
       defaults={
           "title": google_book["title"],
           "status":selected_status,
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
    saved_google_book_ids = set()
    if query:
        results = search_google_books(query)
        
        saved_google_book_ids = set(
            Book.objects.filter(
                google_book_id__in = [book["google_book_id"] for book in results]
            ).values_list("google_book_id", flat=True)
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
    

