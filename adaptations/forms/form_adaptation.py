from django import forms

from adaptations.models import Adaptation


class AdaptationForm(forms.ModelForm):
    class Meta:
        model = Adaptation
        fields = [
            "title",
            "media_type",
            "release_year",
            "status",
            "rating",
            "notes",
        ]