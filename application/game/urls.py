from django.urls import path

from . import views

app_name = 'game'
urlpatterns = [
    # Game router
    path('', views.index, name='index'),
    # Game room
    path("<int:game_id>", views.game, name="game")
]