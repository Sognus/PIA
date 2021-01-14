import datetime
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from online_users.models import OnlineUserActivity

from game.models import Game, GameAction


class WinDetector(object):

    def __init__(self, x, y, game, player):
        self.game = game
        self.player = player
        self.x = x
        self.y = y

    def is_same_player_on_coords(self, x, y):
        game_action = GameAction.objects.filter(game=self.game, who=self.player, x=x, y=y).first()
        return game_action is not None

    def detected_win(self):
        # Detect how many same symbols is on all sides including itself
        left = 0
        right = 0
        top = 0
        bottom = 0
        top_left = 0
        top_right = 0
        bottom_left = 0
        bottom_right = 0

        # left
        for i in range(0, 5):
            x = self.x - i
            y = self.y
            if self.is_same_player_on_coords(x, y):
                left = left + 1
            else:
                break

        # Win by left
        if left == 5:
            return "left"

        # right
        for i in range(0, 5):
            x = self.x + i
            y = self.y
            if self.is_same_player_on_coords(x, y):
                right = right + 1
            else:
                break

        # Win by right
        if right == 5:
            return "right"

        # Win by left+right combo
        if left + right >= 6:
            return "left+right"

        # Top
        for i in range(0, 5):
            x = self.x
            y = self.y - i
            if self.is_same_player_on_coords(x, y):
                top = top + 1
            else:
                break

        # Win by top
        if top == 5:
            return "top"

        # Bottom
        for i in range(0, 5):
            x = self.x
            y = self.y + i
            if self.is_same_player_on_coords(x, y):
                bottom = bottom + 1
            else:
                break

        # Win by bottom:
        if bottom == 5:
            return "bottom"

        # Win by top+bottom column
        if top + bottom >= 6:
            return "top+bottom"

        # Diagonal top left
        for i in range(0, 5):
            x = self.x - i
            y = self.y - i
            if self.is_same_player_on_coords(x, y):
                top_left = top_left + 1
            else:
                break

        # Win by top left
        if top_left == 5:
            return "top_left"

        # Diagonal Bottom right
        for i in range(0, 5):
            x = self.x + i
            y = self.y + i
            if self.is_same_player_on_coords(x, y):
                bottom_right = bottom_right + 1
            else:
                break

        # Win by bottom right
        if bottom_right == 5:
            return "bottom_right"

        # Win by diagonal (top left) + (bottom right)
        if top_left + bottom_right >= 6:
            return "top_left+bottom_right"

        # Diagonal bottom left
        for i in range(0, 5):
            x = self.x - i
            y = self.y + i
            if self.is_same_player_on_coords(x, y):
                bottom_left = bottom_left + 1
            else:
                break

        # Win by diagonal bottom left
        if bottom_left == 5:
            return "bottom_left"

        # Diagonal top right
        for i in range(0, 5):
            x = self.x + i
            y = self.y - i
            if self.is_same_player_on_coords(x, y):
                top_right = top_right + 1
            else:
                break

        # Win by diagonal top right
        if top_right == 5:
            return "top_right"

        # Win by diagonal (bottom left) + (top right)
        if bottom_left + top_right >= 6:
            return "bottom_left+top_right"

        # No win Sadge
        return None


class GameConsumer(WebsocketConsumer):
    def connect(self):
        # Get connecting user
        self.user = self.scope["user"]
        # Get Users game
        self.game = Game.get_active_game(self.scope["user"])
        # Assign channels
        self.room_name = str(self.game.id) if self.game is not None else "none"
        self.room_group_name = 'game_%s' % self.room_name

        if self.room_name == "none":
            # Player doesnt have active game, close connection
            self.close()

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
        action = text_data_json["action"]

        # TODO: check time between last player action
        # Something like a hello message with answer everything is OK
        # and if not just stop game
        if action == "keep_alive":
            # Get all users active last 5 minutes
            user_activity_objects = OnlineUserActivity.get_user_activities(datetime.timedelta(minutes=5))
            onlinelist = [user.user for user in user_activity_objects]

            # Check if both users are still online
            if self.game.player1 not in onlinelist or self.game.player2 not in onlinelist:
                # Inform remaining players
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_notify_end',
                        'action': "game_completed",
                        "winner": "draw",
                    }
                )
                # End game - draw
                self.game.completed = True
                self.game.save()
            else:
                # Send OK
                self.send(text_data=json.dumps({
                    "keep_alive": "ok",
                }))

        # Notify game abandon
        if action == "game_abandon":
            # Winner of game is other user
            winner = self.game.player2 if self.user == self.game.player1 else self.game.player2

            # Notify everyone about end of game
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_notify_end',
                    'action': "game_completed",
                    "winner": winner.email,
                }
            )

            # Mark game as completed
            self.game.completed = True
            # Set winner
            self.game.winner = winner
            # Save game to database
            self.game.save()

        # Request game state action
        if action == "load":
            # Get all actions for game
            all_game_actions = GameAction.objects.filter(game=self.game).order_by("-date")

            all_game_actions_dict = dict()
            counter = 0
            for game_action in all_game_actions:
                symbol = "x" if game_action.who == self.game.player1 else "o"
                all_game_actions_dict[counter] = {
                    "x": game_action.x,
                    "y": game_action.y,
                    "symbol": symbol,
                }
                counter = counter + 1

            # Add action
            all_game_actions_dict["action"] = "load"

            # Send every action
            self.send(text_data=json.dumps(all_game_actions_dict))
            return

        # Claim field in grid action
        if action == "claim":
            # Get last game action
            last_action = GameAction.objects.filter(game=self.game).order_by("-date").first()
            player_turn = None
            player_turn_symbol = None

            # If there are no actions, player1 starts
            if last_action is None:
                player_turn = self.game.player1
                player_turn_symbol = "x"
            else:
                # Player1 played last so player2 play now
                if last_action.who == self.game.player1:
                    player_turn = self.game.player2
                    player_turn_symbol = "o"
                # Player2 played last so player1 play now
                else:
                    player_turn = self.game.player1
                    player_turn_symbol = "x"

            # Check if right player tries to CLAIM
            if self.user != player_turn:
                self.send(text_data=json.dumps({
                    "action": "claim_ack",
                    "status": "ERR",
                    "status_message": "Nejsi na řadě!",
                }))
                return

            # Its player turn - get info sent
            coordX = text_data_json["x"]
            coordY = text_data_json["y"]

            # Check if coords are not used yet
            coord_action = GameAction.objects.filter(game=self.game, x=coordX, y=coordY).first()
            if coord_action is not None:
                self.send(text_data=json.dumps({
                    "action": "claim_ack",
                    "status": "ERR",
                    "status_message": "Dané políčko je již zabráno!",
                }))
                return

            # Coords are not used, claim them
            new_action = GameAction()
            new_action.game = self.game
            new_action.x = coordX
            new_action.y = coordY
            new_action.who = self.user
            new_action.save()

            # Notify both players
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_notify_claimed',
                    'action': "claimed",
                    'x': coordX,
                    "y": coordY,
                    "symbol": player_turn_symbol,
                }
            )

            # Check if game ended - BFS from current location
            wd = WinDetector(coordX, coordY, self.game, self.user)
            win = wd.detected_win()

            if wd.detected_win() is not None:
                self.game.completed = True
                self.game.winner = self.user
                self.game.save()
                # Notify everyone of game end
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_notify_end',
                        'action': "game_completed",
                        "winner": self.user.email,
                    }
                )

    # Notify every player about winner of game
    def game_notify_end(self, event):
        winner = event["winner"]

        self.send(text_data=json.dumps({
            "action": "game_completed",
            "winner": winner,
        }))

    # Notify every player of new claimed action
    def game_notify_claimed(self, event):
        x = event["x"]
        y = event["y"]
        symbol = event["symbol"]

        self.send(text_data=json.dumps({
            "action": "claimed",
            "x": x,
            "y": y,
            "symbol": symbol,
        }))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"].email
        self.game = Game.get_active_game(self.scope["user"])
        self.room_name = "game_" + str(self.game.id) if self.game is not None else "game_none"
        self.room_group_name = 'chat_%s' % self.room_name

        if self.room_name == "game_none":
            self.close()
            return

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
