from django import forms
from books.models import Book

class BookForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["status"].disabled = True
            self.fields["status"].help_text = (
                "Use the reading-status buttons on the book's "
                "detail page to start, finish, or read again."
            )
    
    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get("status") == Book.READ
            and cleaned_data.get("total_pages")
        ):
            cleaned_data["current_page"] = cleaned_data["total_pages"]
            
        status = cleaned_data.get("status")
        started_at = cleaned_data.get("started_at")
        finished_at = cleaned_data.get("finished_at")

        if finished_at and status != Book.READ:
            self.add_error(
                "finished_at",
                "Only finished books can have a finish date.",
            )
        elif started_at and finished_at and finished_at < started_at:
            self.add_error(
                "finished_at",
                "Finish date cannot be before start date.",
            )

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
    
    
