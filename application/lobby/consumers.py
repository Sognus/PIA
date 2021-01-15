import json
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from online_users.models import OnlineUserActivity

from game.models import Game
from .models import UserRequests, Friends, Announcements


class RequestConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"].email
        self.user_object = self.scope["user"]
        self.user_id = self.scope["user"].id
        self.room_group_name = "requests_user_" + str(self.user_id)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        sender = self.user
        context = text_data_json["context"]

        if context == "request_reject":
            # Treat message as rejecting request
            rtype = text_data_json["type"]

            if rtype == "game" or rtype == "friend":
                req_id = text_data_json["request_id"]
                req_object = UserRequests.objects.filter(id=req_id).first()

                if req_object is None:
                    self.send(text_data=json.dumps({"request_new_ack": "reject_missing"}))
                    return

                if self.user_object != req_object.recipient:
                    self.send(text_data=json.dumps({"request_new_ack": "reject_permission"}))
                    return

                # Reject request
                req_object.answered = True
                req_object.answer = False
                req_object.save()

                # Notify sender and recipient
                self.send(text_data=json.dumps({"request_new_ack": "request_reject", "request_id": req_object.id}))

                # Notify sender that request was rejected
                target_group = "requests_user_" + str(req_object.sender.id)
                req_type = ""

                if req_object.type == "friend":
                    req_type = "o přátelství"
                elif req_object.type == "game":
                    req_type = "o hru"

                async_to_sync(self.channel_layer.group_send)(
                    target_group,
                    {
                        "type": "request_notify_reject",
                        "message": "Tvůj požadavek " + req_type + " s " + req_object.recipient.email + " byl odmítnut",
                        "request_id": req_object.id,
                        "rtype": "friend",
                    }
                )

                return

        # Route based on context
        if context == "request_accept":
            # Treat message as accepting request
            rtype = text_data_json["type"]

            if rtype == "game":
                req_id = text_data_json["request_id"]
                req_object = UserRequests.objects.filter(id=req_id).first()

                # Request doesnt exist
                if req_object is None:
                    self.send(text_data=json.dumps({"request_new_ack": "accept_missing"}))
                    return

                # Request is wrong type
                if req_object.type != "game":
                    self.send(text_data=json.dumps({"request_new_ack": "wrong_type"}))
                    return

                # Block user from accepting request that isnt for him
                if self.user_object != req_object.recipient:
                    self.send(text_data=json.dumps({"request_new_ack": "accept_permission"}))
                    return

                # Get online users
                user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(minutes=3))
                online = (user.user.id for user in user_activity_objects)

                # User is not online
                if not req_object.recipient.id in online:
                    self.send(text_data=json.dumps({"request_new_ack": "not_online"}))
                    return

                # Check if sender is in game
                sending = self.user_object

                if Game.has_active_game(sending):
                    self.send(text_data=json.dumps({"request_new_ack": "already_game_self"}))
                    return

                # Check if recipient is in game
                if Game.has_active_game(req_object.recipient):
                    self.send(text_data=json.dumps({"request_new_ack": "already_game"}))
                    return

                # Create game
                game_object = Game.create_game(req_object.sender, req_object.recipient)

                # Notify players
                target_recipient = "requests_user_" + str(game_object.player1.id)
                target_sender = "requests_user_" + str(game_object.player2.id)

                async_to_sync(self.channel_layer.group_send)(
                    target_recipient,
                    {
                        "type": "request_notify_game",
                        "request_new_ack": "game_start",
                        "game_id": game_object.id,
                    }
                )

                async_to_sync(self.channel_layer.group_send)(
                    target_sender,
                    {
                        "type": "request_notify_game",
                        "request_new_ack": "game_start",
                        "game_id": game_object.id,
                    }
                )

                ann = Announcements()
                ann.text = "Uživatelé " + str(game_object.player1.email) + " a " + str(
                    game_object.player2.email) + " začali hru #" + str(game_object.id) + "."
                ann.save()

                return

            if rtype == "friend":
                req_id = text_data_json["request_id"]
                req_object = UserRequests.objects.filter(id=req_id).first()

                if req_object.type != "friend":
                    self.send(text_data=json.dumps({"request_new_ack": "wrong_type"}))
                    return

                if req_object is None:
                    self.send(text_data=json.dumps({"request_new_ack": "accept_missing"}))
                    return

                if self.user_object != req_object.sender and self.user_object != req_object.recipient:
                    self.send(text_data=json.dumps({"request_new_ack": "accept_permission"}))
                    return

                # Set request responded true and positive
                req_object.answered = True
                req_object.answer = True
                req_object.save()

                # Create friend
                friend = Friends()
                friend.user1 = req_object.sender
                friend.user2 = req_object.recipient
                friend.save()

                # Announcement create
                ann = Announcements()
                ann.text = "Uživatelé " + str(friend.user1.email) + " a " + str(friend.user2.email) + " se stali přáteli."
                ann.save()

                # Notify rejecter to delete his record
                self.send(text_data=json.dumps({"request_new_ack": "request_accept", "request_id": req_object.id}))
                return

        if context == "request_new":
            # Treat message as new request
            rtype = text_data_json["type"]

            # Further route based on type
            if rtype == "game":
                # Treat request as new game request

                # Acknowledge request
                self.send(text_data=json.dumps({"request_new_ack": "acknowledged"}))

                # Get recipient
                id = text_data_json["recipient"]
                recipient = User.objects.filter(id=id).first()
                target_group = "requests_user_" + str(recipient.id)

                # Check if user wants to play game with himself
                if recipient == self.user_object:
                    self.send(text_data=json.dumps({"request_new_ack": "game_self"}))
                    return

                # Get online users
                user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(minutes=3))
                online = (user.user.id for user in user_activity_objects)

                # User is not online
                if not recipient.id in online:
                    self.send(text_data=json.dumps({"request_new_ack": "not_online"}))
                    return

                # Check if recipient have pending request
                if UserRequests.has_pending_request(self.user_object, recipient, rtype):
                    self.send(text_data=json.dumps({"request_new_ack": "already_pending"}))
                    return

                other_side_requests = UserRequests.get_pending_request(recipient, self.user_object, rtype)

                # Check if sender is in game
                sending = self.user_object
                active_game_self = Game.get_active_game(sending)

                if active_game_self is not None:
                    self.send(text_data=json.dumps({"request_new_ack": "already_game_self", "game_id": active_game_self.id}))
                    return

                # Check if recipient is in game
                if Game.has_active_game(recipient):
                    self.send(text_data=json.dumps({"request_new_ack": "already_game"}))
                    return

                # Check pending request from other side
                if len(other_side_requests) > 0:
                    request_object = other_side_requests[0]

                    # Notify other user
                    async_to_sync(self.channel_layer.group_send)(
                        target_group,
                        {
                            "type": "request_notify_merged",
                            "request_new_ack": "merged",
                            "request_id": other_side_requests[0].id,
                            "rtype": "game",
                        }
                    )
                    # Notify self
                    self.send(text_data=json.dumps({
                        "request_new_ack": "merged",
                        "request_id": request_object.id,
                    }))

                    # Set request responded true and positive
                    request_object.answered = True
                    request_object.answer = True
                    request_object.save()

                    # Create game
                    game_object = Game.create_game(request_object.sender, request_object.recipient)

                    # Notify players
                    target_recipient = "requests_user_" + str(game_object.player1.id)
                    target_sender = "requests_user_" + str(game_object.player2.id)

                    async_to_sync(self.channel_layer.group_send)(
                        target_recipient,
                        {
                            "type": "request_notify_game",
                            "request_new_ack": "game_start",
                            "game_id": game_object.id,
                        }
                    )

                    async_to_sync(self.channel_layer.group_send)(
                        target_sender,
                        {
                            "type": "request_notify_game",
                            "request_new_ack": "game_start",
                            "game_id": game_object.id,
                        }
                    )

                    # Terminate rest of function
                    return

                # Actually create Request in database
                request_text = "Uživatel " + self.user + " tě požádal o hru!"
                request = UserRequests.create_request(self.user_object, recipient, "game", request_text)

                # Send request to recipient
                async_to_sync(self.channel_layer.group_send)(
                    target_group,
                    {
                        "type": "request_notify",
                        "message": request_text,
                        'sender_name': self.user,
                        "sender": self.user_id,
                        "request_id": request.id,
                        "rtype": "game",
                    }
                )
                return
            if rtype == "friend":
                # Treat request as new friend request

                # Acknowledge request
                self.send(text_data=json.dumps({"request_new_ack": "acknowledged"}))

                # Get recipient
                id = text_data_json["recipient"]
                recipient = User.objects.filter(id=id).first()
                target_group = "requests_user_" + str(recipient.id)

                # Check if user wants to friend himself
                if recipient == self.user_object:
                    self.send(text_data=json.dumps({"request_new_ack": "friends_self"}))
                    return

                # Check if users are already friends
                if Friends.are_friends(self.user_object, recipient):
                    self.send(text_data=json.dumps({"request_new_ack": "already_friends"}))
                    return

                # Check if recipient have pending request
                if UserRequests.has_pending_request(self.user_object, recipient, rtype):
                    self.send(text_data=json.dumps({"request_new_ack": "already_pending"}))
                    return

                other_side_requests = UserRequests.get_pending_request(recipient, self.user_object, rtype)

                # Check pending request from other side
                if len(other_side_requests) > 0:
                    request_object = other_side_requests[0]

                    # Notify other user
                    async_to_sync(self.channel_layer.group_send)(
                        target_group,
                        {
                            "type": "request_notify_merged",
                            "request_new_ack": "merged",
                            "request_id": other_side_requests[0].id,
                        }
                    )
                    # Notify self
                    self.send(text_data=json.dumps({
                        "request_new_ack": "merged",
                        "request_id": request_object.id,
                    }))

                    # Set request responded true and positive
                    request_object.answered = True
                    request_object.answer = True
                    request_object.save()

                    # Create friend
                    friend = Friends()
                    friend.user1 = self.user_object
                    friend.user2 = recipient
                    friend.save()

                    ann = Announcements()
                    ann.text = "Uživatelé " + str(friend.user1.email) + " a " + str(
                        friend.user2.email) + " se stali přáteli."
                    ann.save()

                    # Terminate rest of function
                    return

                # Actually create Request in database
                request_text = "Uživatel " + self.user + " tě požádal o přátelství!"
                request = UserRequests.create_request(self.user_object, recipient, "friend", request_text)

                # Send request to recipient
                async_to_sync(self.channel_layer.group_send)(
                    target_group,
                    {
                        "type": "request_notify",
                        "message": request_text,
                        'sender_name': self.user,
                        "sender": self.user_id,
                        "request_id": request.id,
                        "rtype": "friend",
                    }
                )

    def request_notify_game(self, event):
        game_id = event["game_id"]

        self.send(text_data=json.dumps({
            "request_new_ack": "game_start",
            "game_id": game_id,
        }))

    def request_notify_reject(self, event):
        request_id = event["request_id"]
        message = event["message"]
        rtype = event["rtype"]

        self.send(text_data=json.dumps({
            "request_new_ack": "request_reject_message",
            "message": message,
            "type": rtype,
            "request_id": request_id,
        }))

    def request_notify_merged(self, event):
        request_id = event["request_id"]

        self.send(text_data=json.dumps({
            "request_new_ack": "merged",
            "request_id": request_id,
        }))

    def request_notify(self, event):
        sender_name = event['sender_name']
        request_id = event["request_id"]
        message = event["message"]
        sender = event["sender"]
        context = "request_new"
        rtype = event["rtype"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sender_name': sender_name,
            "context": context,
            "sender": sender,
            "type": rtype,
            "message": message,
            "request_id": request_id,
        }))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"].email
        self.room_name = "global"
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sender': sender,
            'message': message
        }))
