from django.db import models
from books.models import Book, BaseModel

class Adaptation(BaseModel):
    class MediaType(models.TextChoices):
        MOVIE = "movie", "Movie"
        TV_SHOW = "tv", "TV SHOW"
        
    class WatchStatus(models.TextChoices):
        WANT_TO_WATCH = "want_to_watch", "Want to Watch"
        CURRENTLY_WATCHING = "currently_watching", "Currently Watching"
        WATCHED = "watched", "Watched"
        
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="adaptations",
    )
    
    title = models.CharField(
        max_length=255,
    )
    
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.MOVIE,
    )
    
    release_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=30,
        choices=WatchStatus.choices,
        default=WatchStatus.WANT_TO_WATCH,
    )
    
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )
    
    notes = models.TextField(
        blank=True
    )
    
    external_id = models.CharField(
        max_length=100,
        blank=True,
    )
    
    source = models.CharField(
        max_length=50,
        blank=True,
    )
    
    class Meta:
        ordering = ["-release_year", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["book", "title", "media_type", "release_year"],
                name="unique_adaptation_per_book",
            )
        ]
        
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"