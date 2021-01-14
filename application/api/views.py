import json

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core import serializers
from django.contrib.auth.base_user import BaseUserManager


# Forcefully generate new password for user
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def user_reset_password(request, id):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "PUT":
        user = User.objects.filter(id=id).first()
        # Cannot change password for superuser
        if user.is_superuser:
            raise PermissionDenied

        # Change password
        password = BaseUserManager().make_random_password(16)
        user.set_password(password)  # replace with your real password
        user.save()

        # Logout user
        [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id]

        # Email notification
        send_mail(
            'KIV/PIA Piškvorky - Jakub Vítek - Reset hesla',
            "Vynucena změna hesla, nové heslo " + password,
            'viteja-pia@seznam.cz',
            [user.email],
            fail_silently=False,
        )

        return HttpResponse("ok")

    return HttpResponse("not put")


# Demote user from staff
@csrf_exempt
def user_demote(request, id):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "PUT":
        user = User.objects.filter(id=id).first()
        # Cannot demote superuser
        if user.is_superuser:
            raise PermissionDenied
        else:
            user.is_staff = False
            user.save()
            return HttpResponse()

    return HttpResponse()


# Promote user to staff
@csrf_exempt
def user_promote(request, id):
    if not request.user.is_staff:
        raise PermissionDenied

    # REST PUT
    if request.method == "PUT":
        user = User.objects.filter(id=id).first()
        user.is_staff = True
        user.save()
        return HttpResponse()

    return HttpResponse()


# Get list of users
@csrf_exempt
def users(request):
    if not request.user.is_staff:
        raise PermissionDenied

    # REST GET
    if request.method == "GET":
        users = User.objects.all()
        data = dict()

        for user in users:
            user_json = dict()
            user_json["id"] = user.id
            user_json["email"] = user.email
            user_json["is_staff"] = user.is_staff
            user_json["is_superuser"] = user.is_superuser
            data[user.id] = user_json

        return JsonResponse(data, safe=False)

    return HttpResponse()
