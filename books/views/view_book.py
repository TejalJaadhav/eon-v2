from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from books.models import Book
from books.forms import BookForm
from books.services.google_books import search_google_books

class BookListView(ListView):
    model=Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        books = context["books"]
        query = self.request.GET.get("q", "").strip()
        selected_status = self.request.GET.get("status", "").strip()
        
        context["currently_reading"] = books.filter (
            status = Book.CURRENTLY_READING
        )
        
        context["want_to_read"] = books.filter (
            status = Book.WANT_TO_READ
        )
        
        context["read_books"] = books.filter (
            status = Book.READ
        )
        
        show_all_sections = not query and not selected_status
        
        context["show_currently_reading"] = (
            show_all_sections
            or 
            selected_status == Book.CURRENTLY_READING
            or (query and not selected_status and context["currently_reading"].exists())
        )
        
        context["show_want_to_read"] = (
            show_all_sections
            or 
            selected_status == Book.WANT_TO_READ
            or (query and not selected_status and context["want_to_read"].exists())
        )
        
        context["show_read_books"] = (
            show_all_sections
            or selected_status == Book.READ
            or (query and not selected_status and context["read_books"].exists())
        )
        
        context["query"] = query
        context["status_choices"] = Book.STATUS_CHOICES
        context["selected_status"] = selected_status
        
        context["google_results"] = []
        
        if query and not books.exists():
            context["google_results"] = search_google_books(query)
        
        return context
        
    def get_queryset(self):
        queryset= super().get_queryset()
        query = self.request.GET.get("q", "").strip() # Get the search text from URL.
        
        selected_status = self.request.GET.get("status", "").strip() # To get selected status
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(author__icontains=query)
            )
        
        if selected_status:
            queryset = queryset.filter(status=selected_status)
        return queryset
    
class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:book_list")
    
class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    
    
class BookUpdateView(UpdateView):
    model= Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url= reverse_lazy("books:book_list")
    
class BookDeleteView(DeleteView):
    model = Book
    template_name = "books/book_delete.html"
    success_url = reverse_lazy("books:book_list")
    
    
@require_POST
def update_book_status(request, pk):
    """
    Updates one saved book's reading status from the detail page.
    """
    
    book = get_object_or_404(Book, pk=pk)
    new_status = request.POST.get("status")
    
    valid_statuses = [value for value, label in Book.STATUS_CHOICES]
    
    if new_status in valid_statuses:
        book.status = new_status
        
        if new_status == Book.READ and book.total_pages:
            book.current_page = book.total_pages
            
        if new_status == Book.CURRENTLY_READING and book.current_page == book.total_pages:
            book.current_page = 0
            
        book.save()
        
        
    return redirect("books:book_detail", pk=book.pk)
    