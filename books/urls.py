from django.urls import path
from books.views import BookListView, BookCreateView, BookDetailView, BookUpdateView, BookDeleteView

app_name = "books"

urlpatterns = [
    path("books/", BookListView.as_view(), name="book_list"),
    path("books/add/", BookCreateView.as_view(), name="book_create"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/<int:pk>/edit/", BookUpdateView.as_view(), name="book_update"),
    path("books/<int:pk>/delete/", BookDeleteView.as_view(), name="book_delete"),
]