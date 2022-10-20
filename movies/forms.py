from django import forms
from users.models import UserMovie

class DateInput(forms.DateInput):
    input_type = 'date'

class UserMovieCreateForm(forms.ModelForm):
    class Meta:
        model = UserMovie
        fields = '__all__'
        widgets = {'date_watched': DateInput()}
