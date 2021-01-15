import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now

from online_users.models import OnlineUserActivity


class Announcements(models.Model):
    class Meta:
        verbose_name = 'Oznámení'
        verbose_name_plural = 'Oznámení'

    text = models.CharField(max_length=2048)
    time_sent = models.DateTimeField('time sent', default=now)

    @staticmethod
    def get_announcements_last_hour():
        now = timezone.now()
        time_threshold = timezone.now() - datetime.timedelta(hours=1)
        return Announcements.objects.filter(time_sent__range=(time_threshold, now)).order_by("-time_sent")


class PasswordResets(models.Model):
    class Meta:
        verbose_name = 'Reset hesla'
        verbose_name_plural = 'Reset hesla'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    uuid = models.UUIDField(default=uuid.uuid4)
    time_sent = models.DateTimeField('time sent', default=now)

class UserRequests(models.Model):
    class Meta:
        verbose_name = 'Požadavek uživatele'
        verbose_name_plural = 'Požadavky uživatelů'

    # ID is created by django
    # Sender user
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    # Recipient user
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipient")
    # Request type
    type = models.CharField(max_length=128)
    # Request text
    text = models.CharField(max_length=512)
    # Additional data
    data = models.JSONField(blank=True, null=True)
    # If request got reaction
    answered = models.BooleanField(default=False)
    # Reaction - Not reacted, accepted, rejected
    answer = models.NullBooleanField(default=None)
    # time
    time_sent = models.DateTimeField('time sent', default=now)

    @staticmethod
    def get_pending_request(sender, recipient, type):
        # Get request of said type from sender to recipient
        data_set = UserRequests.objects.filter(sender=sender, recipient=recipient, type=type, answered=False)

        # If request type is game, check if found request is recent
        filtered_data_set = list()
        if type == "game":
            for dato in data_set:
                if dato.is_recent:
                    filtered_data_set.append(dato)
        if type == "friend":
            filtered_data_set = list(data_set)

        # If we have more than 0 results, sender indeed has pending request
        return filtered_data_set

    @staticmethod
    def has_pending_request(sender, recipient, type):
        filtered_data_set = UserRequests.get_pending_request(sender,recipient,type)
        return len(filtered_data_set) > 0



    @staticmethod
    def create_request(sender, recipient, type, text, data=None):
        new_request = UserRequests()
        new_request.sender = sender
        new_request.recipient = recipient
        new_request.type = type
        new_request.text = text

        if data is not None:
            new_request.data = data

        new_request.save()
        return new_request

    @staticmethod
    def get_unanswered_for(recipient):
        gameSet = UserRequests.get_unanswered_for_game_online(recipient)
        friendSet = UserRequests.get_unanswered_for_friend(recipient)
        merged = gameSet + friendSet
        return merged

    # Returns unanswered requests for game only if sender is online
    @staticmethod
    def get_unanswered_for_game_online(recipient):
        userQuery = Q(recipient=recipient)
        answeredQuery = Q(answered=False)
        typeQuery = Q(type="game")

        # Check if user is online
        dataset = UserRequests.objects.filter(userQuery & answeredQuery & typeQuery).order_by("time_sent")
        result = list()
        # Get online users
        user_activity_objects = OnlineUserActivity.get_user_activities(datetime.timedelta(minutes=5))
        onlinelist = [user.user for user in user_activity_objects]
        # Filter online users
        for data in dataset:
            if data.sender in onlinelist and data.is_recent():
                result.append(data)

        return result

    # Returns if request time is less than 3 minutes old
    def is_recent(self):
        now = timezone.now()
        return now - datetime.timedelta(minutes=3) <= self.time_sent <= now

    # Get friend request for user
    @staticmethod
    def get_unanswered_for_friend(recipient):
        userQuery = Q(recipient=recipient)
        answeredQuery = Q(answered=False)
        typeQuery = Q(type="friend")
        return list(UserRequests.objects.filter(userQuery & answeredQuery & typeQuery).order_by("time_sent"))


# Friends model
class Friends(models.Model):
    class Meta:
        verbose_name = 'Přátelé'
        verbose_name_plural = 'Přátelé'

    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")


    @staticmethod
    def are_friends_id(id1, id2):
        friends = Friends.objects.all()

        for friend in friends:
            if (id1 == friend.user1.id and id2 == friend.user2.id) or (
                    id1 == friend.user2.id and id2 == friend.user1.id):
                return True

    @staticmethod
    def are_friends(user1, user2):
        return Friends.are_friends_id(user1.id, user2.id)

    @staticmethod
    def get_friends_for(target):
        # Get all friends relations
        friends = Friends.objects.all()

        # Get online users
        user_activity_objects = OnlineUserActivity.get_user_activities(datetime.timedelta(minutes=5))
        onlinelist = (user for user in user_activity_objects)

        user_activity_objects = OnlineUserActivity.get_user_activities(datetime.timedelta(minutes=10))
        awaylist = (user for user in user_activity_objects)

        # Prepare result
        result = dict()

        # Process relations
        for friend in friends:
            target = friend.user1 if target == friend.user2 else friend.user2

            status = None

            if not target.is_authenticated:
                status = "offline"

            if status is None:
                for online_user in onlinelist:
                    if online_user.user == target:
                        status = "online"
                        break

            if status is None:
                for away_user in awaylist:
                    if away_user.user == target:
                        status = "away"
                        break

            if status is None:
                status = "offline"

            result[target] = status

        # End result
        return result

    @staticmethod
    def remove_friend(id1, id2):
        friends = Friends.objects.all()

        for friend in friends:
            if (id1 == friend.user1.id and id2 == friend.user2.id) or (
                    id1 == friend.user2.id and id2 == friend.user1.id):
                friend.delete()
                return True

        return False

    def __str__(self):
        return "{} - {}".format(self.user1.email, self.user2.email)
