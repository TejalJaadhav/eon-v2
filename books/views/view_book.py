from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from books.models import Book
from books.forms import BookForm
from django.urls import reverse_lazy
from django.db.models import Q

class BookListView(ListView):
    model=Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        books = context["books"]
        
        context["currently_reading"] = books.filter(
            status=Book.CURRENTLY_READING
        )
        
        context["want_to_read"] = books.filter(
            status=Book.WANT_TO_READ
        )
        context["read_books"] = books.filter(
            status=Book.READ
        )
        context["query"] = self.request.GET.get("q", "").strip()
        
        context["status_choices"] = Book.STATUS_CHOICES # sends choices to temp
        context["selected_status"] = self.request.GET.get("status", "").strip() # To remember selected status
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