from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.db.models import Q


class Game(models.Model):
    class Meta:
        verbose_name = 'Hra'
        verbose_name_plural = 'Hry'

    WINNERS = (
        (0, "noone"),
        (1, "player1"),
        (2, "player2"),
    )

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player2")
    completed = models.BooleanField(default=False)
    winner = models.IntegerField(default=0, choices=WINNERS)

    @staticmethod
    def create_game(sender, recipient):
        game_object = Game()
        game_object.player1 = sender
        game_object.player2 = recipient
        game_object.completed = False
        game_object.winner = 0
        game_object.save()
        return game_object

    @staticmethod
    def has_active_game(user):
        return Game.get_active_game(user) is not None

    @staticmethod
    def get_active_game(user):
        q_active = Q(completed=False)
        q1 = Q(player1=user)
        q2 = Q(player2=user)
        return Game.objects.all().filter((q1 | q2) & q_active).first()


class GameAction(models.Model):
    class Meta:
        verbose_name = 'Kolo hry'
        verbose_name_plural = 'Kola hry'

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game")
    date = models.DateTimeField('time')
    x = models.IntegerField()
    y = models.IntegerField()
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name="who")

    @staticmethod
    def get_actions_for(game):
        return Game.objects.all().filter(game=game).order_by("time")