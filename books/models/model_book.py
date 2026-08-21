from django.db import models
from books.models.base import BaseModel
from django.core.exceptions import ValidationError


class Book(BaseModel):
    
    # Defining this so later we can reuse tehm later if we want.
    
    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    READ = "read"
    
    # Here, Each choice has two parts:
    # 1. databse value: WANT_TO_READ -> "want to read"
    # 2. human label: "want to read"
    
    STATUS_CHOICES = [
        (WANT_TO_READ, "want to read"),
        (CURRENTLY_READING, "currently reading"),
        (READ, "read")
    ]
    
    # Book info
    
    google_book_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )
    
    title = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    
    author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    
    cover_url = models.URLField(
        max_length=500,
        blank=True,
    )
    
    original_publication_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    
    published_date = models.CharField(
        max_length=20,
        blank=True,
    )
    
    description = models.TextField(
        blank=True,
    )
    
    # Book reading status
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=WANT_TO_READ
    )
    
    # Reading progress
    total_pages = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    current_page = models.PositiveIntegerField(
        default=0
    )
    
    # Personal rating you wanna give.
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True
    )
    
    # Notes for the book
    notes = models.TextField(
        blank=True
    )
    
    started_at = models.DateField(
        null=True, 
        blank=True,
    )
    
    finished_at = models.DateField(
        null=True, 
        blank=True,
    )
    
    class Meta:
        # Default order
        ordering = ["title"]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.total_pages and self.current_page > self.total_pages:
            raise ValidationError(
                "Current page cannot be greater than total pages"
            )
        
        if self.rating and not 1 <= self.rating <= 5:
            raise ValidationError(
                "Rating must be between 1 and 5."
            )
            
    # Note: we are keeping these fun as property because they answer a question
    @property
    def reading_progress_perc(self):
        if not self.total_pages:
            return 0
        percentage = round((self.current_page / self.total_pages) * 100)
        
        return percentage
    
    @property
    def is_finished(self):
         return self.status == self.READ
    
    @property
    def is_currently_reading(self):
        return self.status == self.CURRENTLY_READING
    
    # Not property because it changes the object
    def mark_as_read(self):
        self.status = self.READ
        
        if self.total_pages:
            self.current_page = self.total_pages
            
    @property
    def display_rating(self):
        if self.rating is None:
            return ""
        if self.rating % 1 == 0:
            return int(self.rating)
        
        return self.rating
        