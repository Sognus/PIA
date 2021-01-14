from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


# Create your views here.
@login_required(login_url='/')
def index(request):
    # User has no permissions
    if not request.user.is_staff:
        return HttpResponseRedirect("/")
    return render(request, "administration/base.html", {"user": request.user})
