from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout, login

from . import forms


def index(request):
    # Show login page if user is not logged
    title = "Přihlášení"
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                user = User.objects.get(email=form.cleaned_data["username"])
                login(request, user)
                return HttpResponseRedirect("/lobby")
            else:
                return render(request, "application/login.html", {"form": form, "title": title})
        else:
            form = forms.LoginForm()
            return render(request, "application/login.html", {"form": form, "title": title})
    else:
        # Redirect to lobby
        return HttpResponseRedirect("/lobby")


def register(request):
    # Show login page if user is not logged
    title = "Registrace"
    if not request.user.is_authenticated:
        form = forms.LoginForm()
        return render(request, "application/register.html", {"form": form, "title": title})
    else:
        # Redirect to lobby
        return HttpResponseRedirect("/lobby")


def log_out(request):
    # Log user out
    logout(request)
    # Redirect him to login page
    return HttpResponseRedirect('/login')

