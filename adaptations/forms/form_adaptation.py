from django import forms

from adaptations.models import Adaptation

class AdaptationForm(forms.ModelForm):
    class Meta:
        model = Adaptation
        
        fields = [
            "title",
            "adaptation_type",
            "release_year",
            "watch_status",
            "rating",
            "notes",
        ]