from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from books.models import Book
from books.forms import BookForm
from books.services.google_books import search_google_books

from django.db import transaction
from django.utils import timezone
from books.models import ReadingRecord

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

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            book = self.object

            if book.status in [Book.CURRENTLY_READING, Book.READ]:
                ReadingRecord.objects.create(
                    book=book,
                    current_page=book.current_page,
                    total_pages=book.total_pages,
                    started_at=book.started_at,
                    finished_at=(
                        book.finished_at
                        if book.status == Book.READ
                        else None
                    ),
                    is_finished=book.status == Book.READ,
                )

        return response
    
class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    
    
class BookUpdateView(UpdateView):
    model= Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url= reverse_lazy("books:book_list")
    
    @transaction.atomic
    def form_valid(self, form):
        saved_book = Book.objects.select_for_update().get(
            pk=self.object.pk
        )
        book = form.instance
        
        if saved_book.status != book.status:
            form.add_error(
                None,
                "Reading status changed. Reload this page and try again."
            )
            return self.form_invalid(form)
        
        if book.status == book.WANT_TO_READ:
            return super().form_valid(form)
        
        is_finished = book.status == Book.READ
        if not is_finished and book.finished_at:
            form.add_error(
                "finished_at",
                "Finish the book before entering a finish date."
            )
            
            return self.form_invalid(form)
        
        record = book.reading_records.filter(
            is_finished=is_finished
        ).first()
        
        if record is None:
            record = ReadingRecord(book=book)
            
        record.current_page = book.current_page
        record.total_pages = book.total_pages
        record.started_at = book.started_at
        record.finished_at = book.finished_at
        record.is_finished = is_finished
        
        try:
            record.full_clean()
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        record.save()
        
        return response
    
class BookDeleteView(DeleteView):
    model = Book
    template_name = "books/book_delete.html"
    success_url = reverse_lazy("books:book_list")
    
    
@require_POST
@transaction.atomic
def update_book_status(request, pk):
    book = get_object_or_404(
        Book.objects.select_for_update(),
        pk=pk,
    )
    new_status = request.POST.get("status")

    # These are the actions supported by the detail-page buttons.
    if new_status not in [Book.CURRENTLY_READING, Book.READ]:
        return redirect("books:book_detail", pk=book.pk)

    # Repeated clicks should not create extra reading records.
    if new_status == book.status:
        return redirect("books:book_detail", pk=book.pk)

    today = timezone.localdate()
    record = book.reading_records.filter(
        is_finished=False
    ).first()

    if new_status == Book.CURRENTLY_READING:
        if record is None:
            record = book.reading_records.create(
                current_page=0,
                total_pages=book.total_pages,
                started_at=today,
            )

        book.current_page = record.current_page
        book.started_at = record.started_at
        book.finished_at = None

    elif new_status == Book.READ:
        if record is None:
            record = book.reading_records.create(
                current_page=book.current_page,
                total_pages=book.total_pages,
                started_at=book.started_at,
            )

        record.total_pages = book.total_pages
        record.current_page = (
            book.total_pages
            if book.total_pages
            else book.current_page
        )
        record.is_finished = True
        record.finished_at = today
        record.save()

        book.current_page = record.current_page
        book.started_at = record.started_at
        book.finished_at = record.finished_at

    book.status = new_status
    book.save()

    return redirect("books:book_detail", pk=book.pk)

@require_POST
@transaction.atomic
def upadte_book_progress(request, pk):
    book = get_object_or_404(
        Book.objects.select_for_update(),
        pk=pk,
    )

    # Finished books must use "Read again" before updating progress.
    if book.status != Book.CURRENTLY_READING:
        return redirect("books:book_detail", pk=book.pk)

    page_field = forms.IntegerField(
        min_value=0,
        max_value=book.total_pages if book.total_pages else None,
        required=True,
    )

    try:
        current_page = page_field.clean(
            request.POST.get("current_page")
        )
    except ValidationError as error:
        return render(
            request,
            "books/book_detail.html",
            {
                "book": book,
                "progress_error": " ".join(error.messages),
            },
            status=400,
        )

    record = book.reading_records.filter(
        is_finished=False
    ).first()

    # Support books started through paths not connected yet.
    if record is None:
        record = book.reading_records.create(
            current_page=book.current_page,
            total_pages=book.total_pages,
            started_at=book.started_at,
        )

    record.current_page = current_page
    record.total_pages = book.total_pages

    book.current_page = current_page

    if book.total_pages and current_page == book.total_pages:
        record.is_finished = True
        record.finished_at = timezone.localdate()
        book.status = Book.READ
        book.finished_at = record.finished_at
    else:
        record.finished_at = None
        book.finished_at = None

    book.started_at = record.started_at

    record.save()
    book.save()

    return redirect("books:book_detail", pk=book.pk)