from django.contrib import admin

# Register your models here.
from adaptations.models import Adaptation


@admin.register(Adaptation)
class AdaptationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "book",
        "media_type",
        "release_year",
        "status",
        "rating",
        "source",
    )

    list_filter = (
        "media_type",
        "release_year",
        "status",
        "source",
    )

    search_fields = (
        "title",
        "book__title",
    )