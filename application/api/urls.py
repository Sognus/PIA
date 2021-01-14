from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('users', views.users, name='users'),
    path("users/promote/<int:id>",views.user_promote, name="promote"),
    path("users/demote/<int:id>", views.user_demote, name="demote"),
    path("users/reset-password/<int:id>", views.user_reset_password, name="password-reset"),
]