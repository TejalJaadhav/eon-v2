from django import forms
from books.models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "status",
            "total_pages",
            "current_page",
            "rating",
            "notes",
            "started_at",
            "finished_at",
        ]
        
        widgets = {
            "started_at": forms.DateInput(attrs={"type": "date"}),
            "finished_at": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows":4}),
        }