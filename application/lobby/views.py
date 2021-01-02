from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Redirect non-logged user to login page
@login_required(login_url='/')
def index(request):
    return render(request, "lobby/lobby.html", {"user": request.user})
