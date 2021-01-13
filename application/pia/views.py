import uuid
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout, login
from django.utils.timezone import make_aware
from django.core.mail import send_mail

from lobby.models import PasswordResets
from . import forms

from online_users.models import OnlineUserActivity

from .forms import ResetForm, NewPasswordForm


def password_reset(request, uuid_input):
    # Basically just get user
    reset_object_base = PasswordResets.objects.filter(uuid=uuid.UUID(uuid_input)).first()

    # UUID doesnt exist
    if str(reset_object_base.uuid) != uuid_input:
        return HttpResponseForbidden("1")

    reset_object = PasswordResets.objects.filter(user=reset_object_base.user).order_by("-time_sent").first()

    # UUID is not last
    if str(reset_object.uuid) != uuid_input:
        return HttpResponseForbidden("2")

    if request.method == "POST":
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            # Update password
            reset_object.user.set_password(form.cleaned_data["password"])
            reset_object.user.save()

            # Email notification
            send_mail(
                'KIV/PIA Piškvorky - Jakub Vítek - Reset hesla',
                "Vaše heslo bylo úspěšně změněno",
                'viteja-pia@seznam.cz',
                [reset_object.user.email],
                fail_silently=False,
            )

            message = "Heslo úspěšně změněno"
            return render(request, "pia/password-reset-new.html", {"form": form, "success_message": message})
            pass
        else:
            message = None
            return render(request, "pia/password-reset-new.html", {"form": form, "success_message": message})
    else:
        form = NewPasswordForm()
        message = None
        return render(request, "pia/password-reset-new.html", {"form": form, "success_message": message})

def password_reset_form(request):
    if request.method == "POST":
        form = forms.ResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["username"]
            message = "Odkaz pro obnovení hesla odeslán na e-mail adresu " + email
            user = User.objects.filter(email=email).first()

            # If user doesnt exist dont do anything but dont inform user - possible security breach
            if user is None:
                return render(request, "pia/password-reset-form.html", {"form": form, "success_message": message})

            reset_object = PasswordResets()
            reset_object.user = user
            reset_object.save()
            send_mail(
                'KIV/PIA Piškvorky - Jakub Vítek - Reset hesla',
                'Odkaz pro reset hesla: http://localhost/password-reset/'+str(reset_object.uuid),
                'viteja-pia@seznam.cz',
                [email],
                fail_silently=False,
            )
            return render(request, "pia/password-reset-form.html", {"form": form, "success_message": message})
        else:
            return render(request, "pia/password-reset-form.html", {"form": form, "success_message": None})
    else:
        form = ResetForm()

    return render(request, "pia/password-reset-form.html", {"form": form, "success_message": None})


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
                return render(request, "pia/login.html", {"form": form, "title": title})
        else:
            # Send form
            form = forms.LoginForm()
            return render(request, "pia/login.html", {"form": form, "title": title})
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
                user = User.objects.create_user(form.cleaned_data["username"], form.cleaned_data["username"],
                                                form.cleaned_data["password"])
                # Login User
                login(request, user)
                # Redirect User to lobby
                return HttpResponseRedirect("/lobby")
            else:
                return render(request, "pia/register.html", {"form": form, "title": title})
        else:
            # Send form
            form = forms.RegisterForm()
            return render(request, "pia/register.html", {"form": form, "title": title})
    else:
        # Redirect to lobby when user is logged
        return HttpResponseRedirect("/lobby")


@login_required(login_url='/')
def log_out(request):
    # Special logout
    activity = OnlineUserActivity.objects.filter(user=request.user).first()
    activity.last_activity = make_aware(datetime.fromtimestamp(0))
    activity.save()
    # Log user out
    logout(request)
    # Redirect him to login page
    return HttpResponseRedirect('/login')
