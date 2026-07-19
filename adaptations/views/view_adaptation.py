from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from books.models import Book
from adaptations.models import Adaptation
from adaptations.forms import AdaptationForm

class AdaptationCreateView(CreateView):
    model = Adaptation
    form_class = AdaptationForm
    template_name = "adaptations/adaptation_form.html"
    
    def form_valid(self, form):
        book = get_object_or_404(Book, pk=self.kwargs["book_id"]) # find book using book_id from URL.
        form.instance.book = book
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("books:book_detail", kwargs={"pk": self.object.book.pk})
    