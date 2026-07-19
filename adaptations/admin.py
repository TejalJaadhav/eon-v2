from django.contrib import admin

# Register your models here.
from adaptations.models import Adaptation


@admin.register(Adaptation)
class AdaptationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "book",
        "adaptation_type",
        "release_year",
        "watch_status",
        "rating"
    ]


    list_filter = [
        "adaptation_type",
        "release_year",
        "watch_status"
    ]
    
    search_fields = [
        "title",
        "book__title" # To search connected book title.
    ]