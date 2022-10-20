from django import forms
from movies.forms import DateInput
from users.models import UserSeason, UserTvShow


class UserTvShowCreateForm(forms.ModelForm):
    class Meta:
        model = UserTvShow
        fields = '__all__'

class UserSeasonEditForm(forms.ModelForm):
    class Meta:
        model = UserSeason
        fields = '__all__'
        widgets = {'date_started': DateInput(), 'date_finished': DateInput()}
