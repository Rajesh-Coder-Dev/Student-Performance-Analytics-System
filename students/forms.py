from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Student


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Admin Username",
            "autofocus": True,
            "autocomplete": "username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password",
            "autocomplete": "current-password",
        })
    )


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "student_id",
            "name",
            "email",
            "date_of_birth",
            "department",
        ]

        widgets = {
            "student_id": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Student ID",
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Student Name",
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email Address",
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Department",
            }),
        }