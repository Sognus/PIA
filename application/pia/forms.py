from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class NewPasswordForm(forms.Form):
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                'placeholder': 'Heslo'}))
    password2 = forms.CharField(label="Heslo znovu", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                       'placeholder': 'Heslo znovu'}))

    def clean(self):
        data_password1 = self.cleaned_data["password"]
        data_password2 = self.cleaned_data["password2"]

        if data_password1 != data_password2:
            self.add_error("password", "Hesla nesouhlasí!")


class ResetForm(forms.Form):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                              'placeholder': 'Email'}))

class LoginForm(forms.Form):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                              'placeholder': 'Email'}))
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                'placeholder': 'Heslo'}))
    hidden = forms.CharField(label="Hidden", widget=forms.HiddenInput, required=False)

    def clean(self):
        # Get data
        data_username = self.cleaned_data.get("username", None)
        data_password = self.cleaned_data.get("password", None)

        if data_password is None or data_password is None:
            self.add_error("hidden", "Formulář nebyl vyplněn!")
        else:
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
                                                                              'placeholder': 'Email',
                                                                              "id": "username"}))
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                'placeholder': 'Heslo'}))
    password2 = forms.CharField(label="Heslo2", widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                  'placeholder': 'Heslo znovu'}))
    hidden = forms.CharField(label="Hidden", widget=forms.HiddenInput, required=False)

    def clean(self):
        # Get data
        data_username = self.cleaned_data.get("username", None)
        data_password = self.cleaned_data.get("password", None)
        data_password2 = self.cleaned_data.get("password2", None)

        if data_password is None or data_password is None or data_password2 is None:
            self.add_error("hidden", "Formulář nebyl vyplněn!")
            return self.cleaned_data
        else:
            # Check if user exists
            try:
                user = User.objects.get(email=data_username)
            except User.DoesNotExist:
                user = None

            if user is not None:
                self.add_error("username", "Zadaný e-mail byl již registrován!")

            # Check password match
            if data_password != data_password2:
                self.add_error("password2", "Hesla se neshodují!")

        return self.cleaned_data
