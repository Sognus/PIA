from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from game.models import Game


def index(request):
    user = request.user
    game_object = Game.get_active_game(user)
    if game_object is None:
        return HttpResponseRedirect("/lobby")
    else:
        return HttpResponseRedirect("/game/"+str(game_object.id))


def game(request, game_id):
    user = request.user
    game_object = Game.objects.filter(id=game_id).first()

    # Hra neexistuje
    if game_object is None:
        return HttpResponseRedirect("/game")

    # Redirect user to game router if hes not in game
    if game_object.player1 != user and game_object.player2 != user:
        return HttpResponseRedirect("/game")

    # Redirect user to lobby if game is completed
    if game_object.completed:
        return HttpResponseRedirect("/lobby")

    side = "o" if user == game_object.player1 else "x"

    # Render template
    return render(request, "game/game.html", {"game": game_object, "side": side})