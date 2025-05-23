"""pia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings

from pia import views

urlpatterns = [
    # Project URLS
    path('', views.index, name='index'),
    path('login', views.index, name='index'),
    path('register', views.register, name='register'),
    path('logout', views.log_out, name='logout'),
    path('password-reset/<str:uuid_input>', views.password_reset, name='password_reset'),
    path('password-reset', views.password_reset_form, name='password_reset_form'),
    # URLS of Applications
    path('admin/', include('administration.urls', namespace='api')),
    path('api/', include('api.urls', namespace='api')),
    path('lobby/', include('lobby.urls', namespace='lobby')),
    path('polls/', include('polls.urls', namespace='polls')),
    path('game/', include('game.urls', namespace='game')),
    path('chat/', include('chat.urls')),
    path('superadmin/', admin.site.urls),
]

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
