from django.db import models
from books.models import Book, BaseModel

class Adaptation(BaseModel):
    MOVIE = 'movie'
    TV_SHOW = "tv_show"
    
    ADAPTATION_TYPE_CHOICES = [
        (MOVIE, "movie"),
        (TV_SHOW, "TV Show"),
    ]
    
    WANT_TO_WATCH = "want_to_watch"
    CURRENTLY_WATCHING = "currently_watching"
    WATCHED = "watched"
    
    WATCH_STATUS_CHOICES = [
        (WANT_TO_WATCH, "Want to watch"),
        (CURRENTLY_WATCHING, "Currently watching"),
        (WATCHED, "watched")
    ]
    
    book = models.ForeignKey (
        Book,
        on_delete=models.CASCADE,
        related_name="adaptations"
    )
    
    title = models.CharField(
        max_length=255,
        null = False,
        blank = False
    )
    
    adaptation_type = models.CharField(
        max_length=20,
        choices=ADAPTATION_TYPE_CHOICES,
        default=MOVIE,
    )
    
    release_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    watch_status = models.CharField (
        max_length=20,
        choices=WATCH_STATUS_CHOICES,
        default=WANT_TO_WATCH
    )
    
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True
    )
    
    notes = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering=["title"] # sorts adaptions by title.
    
    def __str__(self):
        return self.title