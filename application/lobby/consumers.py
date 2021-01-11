import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from .models import UserRequests, Friends


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

        # Route based on context
        if context == "request_accept":
            # Treat message as new request
            rtype = text_data_json["type"]

            if rtype == "game":
                pass
            if rtype == "friend":
                req_id = text_data_json["request_id"]
                req_object = UserRequests.objects.filter(id=req_id).first()

                if req_object is None:
                    self.send(text_data=json.dumps({"request_friend_new_ack": "accept_missing"}))
                    return

                if self.user_object != req_object.sender and self.user_object != req_object.recipient:
                    self.send(text_data=json.dumps({"request_friend_new_ack": "accept_permission"}))
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

                # Notify accepter to delete his record
                self.send(text_data=json.dumps({"request_friend_new_ack": "accept_success", "request_id": req_object.id}))
                return

        if context == "request_new":
            # Treat message as new request
            rtype = text_data_json["type"]

            # Further route based on type
            if rtype == "game":
                # Treat request as new game request
                pass
            if rtype == "friend":
                # Treat request as new friend request

                # Acknowledge request
                self.send(text_data=json.dumps({"request_friend_new_ack": "acknowledged"}))

                # Get recipient
                id = text_data_json["recipient"]
                recipient = User.objects.filter(id=id).first()
                target_group = "requests_user_" + str(recipient.id)

                # Check if user wants to friend himself
                if recipient == self.user_object:
                    self.send(text_data=json.dumps({"request_friend_new_ack": "friends_self"}))
                    return

                # Check if users are already friends
                if Friends.are_friends(self.user_object, recipient):
                    self.send(text_data=json.dumps({"request_friend_new_ack": "already_friends"}))
                    return

                # Check if recipient have pending request
                if UserRequests.has_pending_request(self.user_object, recipient, rtype):
                    self.send(text_data=json.dumps({"request_friend_new_ack": "already_pending"}))
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
                            "request_friend_new_ack": "merged",
                            "request_id": other_side_requests[0].id,
                        }
                    )
                    # Notify self
                    self.send(text_data=json.dumps({
                        "request_friend_new_ack": "merged",
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
                    }
                )

        if context == "request_response":
            # Treat message as request response
            pass

    def request_notify_merged(self, event):
        request_id = event["request_id"]

        self.send(text_data=json.dumps({
            "request_friend_new_ack": "merged",
            "request_id": request_id,
        }))

    def request_notify(self, event):
        sender_name = event['sender_name']
        request_id = event["request_id"]
        message = event["message"]
        sender = event["sender"]
        context = "request_new"
        type = "friend"

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sender_name': sender_name,
            "context": context,
            "sender": sender,
            "type": type,
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
