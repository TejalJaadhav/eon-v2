from django.urls import path
from books.views.view_book import (
     BookListView, 
     BookCreateView, 
     BookDetailView, 
     BookUpdateView, 
     BookDeleteView,
     update_book_status,
     upadte_book_progress,
)
from books.views.view_google_books import google_book_search, import_google_book

app_name = "books"

urlpatterns = [
    path("books/", 
         BookListView.as_view(), 
         name="book_list"
    ),
    path("books/add/", 
         BookCreateView.as_view(), 
         name="book_create"
    ),
    path("books/<int:pk>/", 
         BookDetailView.as_view(), 
         name="book_detail"
    ),
    path("books/<int:pk>/edit/", 
         BookUpdateView.as_view(), 
         name="book_update"
    ),
    path(
        "books/<int:pk>/delete/", 
        BookDeleteView.as_view(), 
        name="book_delete"
    ),
    path(
        "books/google-search/", 
         google_book_search, 
         name="google_book_search"
    ),
    path(
        "books/google-import/<str:google_book_id>/",
        import_google_book,
        name="import_google_book"
    ),
    path(
         "books/<int:pk>/status/", 
         update_book_status, 
         name="update_book_status"
    ),
    path(
         "booka/<int:pk>/progress/", 
         upadte_book_progress, 
         name="update_book_progress"
    )
]