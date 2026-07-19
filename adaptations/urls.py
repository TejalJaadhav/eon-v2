from django.urls import path

from adaptations.views import AdaptationCreateView

app_name = "adaptations"

urlpatterns = [
    path (
        "books/<int:book_id>/adaptations/add",
        AdaptationCreateView.as_view(),
        name="adaptation_create",
    ),
]