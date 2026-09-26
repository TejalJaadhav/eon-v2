from django.shortcuts import render, redirect

from django.db import transaction
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST


from books.models import Book, ReadingRecord
from books.services.google_books import search_google_books, get_google_book_by_id, get_title_words
from books.services.open_library import find_original_publication_year

@require_POST
def import_google_book(request, google_book_id):
    selected_status = request.POST.get(
        "status", Book.WANT_TO_READ
    )

    valid_statuses = {
        value for value, label in Book.STATUS_CHOICES
    }
    if selected_status not in valid_statuses:
        return HttpResponseBadRequest("Invalid reading status.")

    # Importing an existing book must not reset its reading history.
    existing_book = Book.objects.filter(
        google_book_id=google_book_id
    ).first()

    if existing_book:
        return redirect("books:book_detail", pk=existing_book.pk)

    google_book = get_google_book_by_id(google_book_id)
    author_text = ", ".join(google_book["authors"])

    original_year = find_original_publication_year(
        google_book["title"],
        author_text,
    )

    total_pages = google_book["page_count"] or None
    current_page = (
        total_pages or 0
        if selected_status == Book.READ
        else 0
    )

    with transaction.atomic():
        book, created = Book.objects.get_or_create(
            google_book_id=google_book["google_book_id"],
            defaults={
                "title": google_book["title"],
                "status": selected_status,
                "author": author_text,
                "total_pages": total_pages,
                "current_page": current_page,
                "published_date": google_book["published_date"],
                "original_publication_year": original_year,
                "cover_url": google_book["thumbnail"],
                "description": google_book["description"],
            },
        )

        if created and selected_status in [
            Book.CURRENTLY_READING,
            Book.READ,
        ]:
            ReadingRecord.objects.create(
                book=book,
                current_page=current_page,
                total_pages=total_pages,
                is_finished=selected_status == Book.READ,
            )

    return redirect("books:book_detail", pk=book.pk)



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
    

