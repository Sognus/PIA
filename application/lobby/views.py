from datetime import timedelta

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from game.models import Game
from .models import Friends, UserRequests

from online_users.models import OnlineUserActivity


# Redirect non-logged user to login page
@login_required(login_url='/')
def index(request):
    # Redirect to active game
    user = request.user
    game_object = Game.get_active_game(user)
    if game_object is not None:
        return HttpResponseRedirect("/game/")

    # Get user activity
    user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(minutes=3))
    online = list(user for user in user_activity_objects)
    online.sort(key=lambda x: x.user.email, reverse=False)

    # Get friendlist
    friendlist = Friends.get_friends_for(request.user)

    # Get unanswered requests
    userRequestList = UserRequests.get_unanswered_for(request.user)

    # Get gamelist
    gamelist = Game.objects.all()

    # Render page
    return render(request, "lobby/lobby.html", {"user": request.user, "onlinelist": online, "friendlist": friendlist, "userRequestList": userRequestList, "gamelist": gamelist})


#
# Ajax endpoints *****************************************************
#

@login_required
def ajax_friends(request):
    friendlist = Friends.get_friends_for(request.user)
    return render(request, "lobby/friends.html", {"friendlist": friendlist})


@login_required
def ajax_friend_remove(request, unfriend_id):
    id1 = request.user.id
    id2 = unfriend_id
    Friends.remove_friend(id1, id2)
    return HttpResponse(status=200)


@login_required
def ajax_online_list(request):
    # Get user activity
    user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(minutes=3))
    online = list(user for user in user_activity_objects)
    online.sort(key=lambda x: x.user.email, reverse=False)
    return render(request, "lobby/user-list.html", {"onlinelist": online, "currentUser": request.user})


@login_required
def ajax_game_list(request):
    # Get games
    games = list(Game.objects.all())
    games.sort(key=lambda x: x.id)
    return render(request, "lobby/game-list.html", {"gamelist": games})