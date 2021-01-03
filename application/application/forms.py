from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                              'placeholder': 'Email'}))
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                'placeholder': 'Heslo'}))

    def clean(self):
        # Get data
        data_username = self.cleaned_data["username"]
        data_password = self.cleaned_data["password"]

        user = None

        # Check user exist
        try:
            user = User.objects.get(email=data_username)

            if not check_password(data_password, user.password):
                self.add_error("password", "Zadejte správné heslo!")

        except User.DoesNotExist:
            self.add_error("username", "Zadaný uživatel neexistuje!")

        # Return data
        return self.cleaned_data


class RegisterForm(forms.Form):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                              'placeholder': 'Email'}))
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                'placeholder': 'Heslo'}))
