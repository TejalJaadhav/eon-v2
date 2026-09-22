from django.db import models
from django.core.exceptions import ValidationError
from books.models.base import BaseModel

class ReadingRecord(BaseModel):
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="reading_records",
    )

    current_page = models.PositiveIntegerField(default=0)

    total_pages = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    started_at = models.DateField(null=True, blank=True)
    finished_at = models.DateField(null=True, blank=True)

    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.book.title} — reading {self.pk}"

    def clean(self):
        super().clean()

        if (
            self.total_pages is not None
            and self.current_page > self.total_pages
        ):
            raise ValidationError({
                "current_page": "Current page cannot exceed total pages."
            })

        if (
            self.started_at
            and self.finished_at
            and self.finished_at < self.started_at
        ):
            raise ValidationError({
                "finished_at": "Finish date cannot be before start date."
            })