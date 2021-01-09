from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

from online_users.models import OnlineUserActivity


# Friends model
class Friends(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")

    @staticmethod
    def get_friends_for(target):
        # Get all friends relations
        friends = Friends.objects.all()

        # Get online users
        user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(minutes=5))
        onlinelist = (user for user in user_activity_objects)

        user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(minutes=10))
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
            if (id1 == friend.user1.id and id2 == friend.user2.id) or (id1 == friend.user2.id and id2 == friend.user1.id):
                friend.delete()
                return True

        return False

    def __str__(self):
        return "{} - {}".format(self.user1.email, self.user2.email)