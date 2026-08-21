from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from books.models import Book
from adaptations.models import Adaptation
from adaptations.forms import AdaptationForm


class AdaptationCreateView(CreateView):
    model = Adaptation
    form_class = AdaptationForm
    template_name = "adaptations/form_adaptation.html"

    def get_book(self):
        return get_object_or_404(Book, pk=self.kwargs["book_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book"] = self.get_book()
        return context

    def form_valid(self, form):
        form.instance.book = self.get_book()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("books:book_detail", kwargs={"pk": self.object.book.pk})