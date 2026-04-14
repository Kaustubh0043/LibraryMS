from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'role', 'department', 'year', 'semester', 'mobile_number'
        )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'department', 'year', 'semester', 'isbn',
            'thumbnail', 'available_copies', 'content_file', 'content_url'
        ]