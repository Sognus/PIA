from django.urls import path

from . import views

app_name = 'lobby'

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/friends', views.ajax_friends, name='ajax_friends'),
    path('ajax/onlinelist', views.ajax_online_list, name='ajax_online'),
    path('ajax/gamelist', views.ajax_game_list, name='ajax_games'),
    path("ajax/announcements", views.ajax_announcements, name="ajax_announcements"),
    path('ajax/friend/remove/<int:unfriend_id>', views.ajax_friend_remove, name='ajax_friends_unfriend'),
]