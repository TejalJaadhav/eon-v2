from django import forms
from books.models import Book

class BookForm(forms.ModelForm):
    
    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get("status") == Book.READ
            and cleaned_data.get("total_pages")
        ):
            cleaned_data["current_page"] = cleaned_data["total_pages"]

        return cleaned_data
    
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "published_date",
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
        
        labels = {
            "published_date": "Published date",
            "total_pages": "Total pages",
            "current_page": "Current page",
            "started_at": "Started reading",
            "finished_at": "Finished reading",
        }
        
        help_texts = {
            "published_date": "Use a year or full date, like 2018 or 2018-10-16.", 
        }
    
    
