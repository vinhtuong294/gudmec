# forms.py
from django import forms
from .models import ERole

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    telephone = forms.CharField(max_length=15)
    fullname = forms.CharField(max_length=255)
    birthday = forms.DateField(widget=forms.SelectDateWidget)
    gender = forms.BooleanField(required=True)
    role = forms.ChoiceField(choices=ERole.choices, required=False)
