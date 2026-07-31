from django.shortcuts import render

from books.services.google_books import search_google_books


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