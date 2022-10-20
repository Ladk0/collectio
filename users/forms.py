from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from users.models import UserProfile


class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = "users/image_widget.html"

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.all().exclude(pk=self.instance.pk)
        for user in users:
            if email == user.email:
                raise ValidationError('A user with that email already exists.')

        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('image',)
        widgets = {
            'image': ImageWidget
        }

class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_username(self):
        username = self.cleaned_data['username']
        users = User.objects.all().exclude(pk=self.instance.pk)
        for user in users:
            if username == user.username:
                raise ValidationError('A user with that username already exists.')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.all().exclude(pk=self.instance.pk)
        for user in users:
            if email == user.email:
                raise ValidationError('A user with that email already exists.')

        return email
