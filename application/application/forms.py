from django import forms


class LoginForm(forms.Form):
    username = forms.EmailField(label="Email", max_length=100)
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput())