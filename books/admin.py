from django.contrib import admin
from books.models import Book

# Register your models here.

@admin.register(Book)

class BookAdmin (admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "current_page",
        "total_pages",
        "rating",
    )
    
    list_filter = ("status", "rating")
    search_fields = ("title", "author")
    

