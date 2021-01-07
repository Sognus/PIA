from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout, login

from . import forms


def index(request):
    title = "Přihlášení"
    if not request.user.is_authenticated:
        if request.method == "POST":
            # Form validation
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                # User login
                user = User.objects.get(email=form.cleaned_data["username"])
                login(request, user)
                return HttpResponseRedirect("/lobby")
            else:
                # Send forms with errors
                return render(request, "application/login.html", {"form": form, "title": title})
        else:
            # Send form
            form = forms.LoginForm()
            return render(request, "application/login.html", {"form": form, "title": title})
    else:
        # Redirect to lobby when user is logged
        return HttpResponseRedirect("/lobby")


def register(request):
    # Show login page if user is not logged
    title = "Registrace"
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = forms.RegisterForm(request.POST)
            if form.is_valid():
                # Register User
                user = User.objects.create_user(form.cleaned_data["username"], form.cleaned_data["username"], form.cleaned_data["password"])
                # Login User
                login(request, user)
                # Redirect User to lobby
                return HttpResponseRedirect("/lobby")
            else:
                return render(request, "application/register.html", {"form": form, "title": title})
        else:
            # Send form
            form = forms.RegisterForm()
            return render(request, "application/register.html", {"form": form, "title": title})
    else:
        # Redirect to lobby when user is logged
        return HttpResponseRedirect("/lobby")


def log_out(request):
    # Log user out
    logout(request)
    # Redirect him to login page
    return HttpResponseRedirect('/login')
