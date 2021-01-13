from django.contrib import admin
from lobby.models import Friends, UserRequests, PasswordResets

admin.site.register(Friends)
admin.site.register(UserRequests)
admin.site.register(PasswordResets)
