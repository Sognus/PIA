from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout

from . import forms

def index(request):
    # Show login page if user is not logged
    if not request.user.is_authenticated:
        form = forms.LoginForm()
        return render(request, "application/login.html", {"form": form})
    else:
        # Redirect to lobby
        return HttpResponseRedirect("/lobby")


def register(request):
    # Shows register page
    return HttpResponse("Here will be register form")


def log_out(request):
    # Log user out
    logout(request)
    # Redirect him to login page
    return HttpResponseRedirect('/login')

