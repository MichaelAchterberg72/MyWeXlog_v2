from django.contrib.auth import get_user_model
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from django.db.models import Count, Sum, F, Q

from . models import Message, ChatRoomMembers, MessageRead, ChatGroup

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def update_message_read(self, data):
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        x = data['id']
        y = ''.join(map(str, x))
        z = int(y)
        message_id = Message.objects.get(pk=z)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        chatgroup_id = ChatGroup.objects.get(slug=chat_name)

        message = []
        message_instance = Message.objects.filter(Q(room_name=chat_name) & Q(pk=message_id.pk)).values_list('pk')
        messages_read = MessageRead.objects.filter(Q(message__id=message_id.id) & Q(message_read=False) & ~Q(talent=author_user)).count()
        messages_read_self = MessageRead.objects.filter(Q(message__id=message_id.id) & Q(message_read=False) & Q(talent=author_user)).count()

        result = {'message': message_instance, 'messages_read': messages_read, 'messages_read_self': messages_read_self}
        message.append(result)

        content = {
            'command': 'update_message',
            'message': self.message_check_to_json(message),
        }

        return self.send_message_update(content)

    def message_read_notification(self, data):
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        x = data['id']
        y = ''.join(map(str, x))
        z = int(y)
        message_id = Message.objects.get(pk=z)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        chatgroup_id = ChatGroup.objects.get(slug=chat_name)
        update_message_read = MessageRead.objects.filter(
            message=message_id,
            talent=author_user,
            chat_group=chatgroup_id,
            ).update(
            message_read=True,
            read_date=timezone.now()
            )

        #is it necessary to rebuild the menu with each message read - processor heavy
        groups_qs = ChatRoomMembers.objects.filter(talent=author_user).order_by('-date_modified').values_list('chat_group')

        chat_rooms = []
        for item in groups_qs:
            groups = ChatRoomMembers.objects.filter(Q(talent=author_user) & Q(chat_group=item)).values_list('room_name', 'date_modified', 'chat_group__slug')
            messages_received = MessageRead.objects.filter(Q(chat_group=item) & Q(message_read=False) & Q(talent=author_user)).count()

            result = {'group': groups, 'notification': messages_received}
            chat_rooms.append(result)

        content = {
            'command': 'fetch_menu',
            'menus': self.menus_to_json(chat_rooms),
        }
        return self.send_menu(content)

    def fetch_menu(self, data):
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        groups_qs = ChatRoomMembers.objects.filter(talent=author_user).order_by('-date_modified').values_list('chat_group')

        chat_rooms = []
        for item in groups_qs:
            groups = ChatRoomMembers.objects.filter(Q(talent=author_user) & Q(chat_group=item)).values_list('room_name', 'date_modified', 'chat_group__slug')
            messages_received = MessageRead.objects.filter(Q(chat_group=item) & Q(message_read=False) & Q(talent=author_user)).count()

            result = {'group': groups, 'notification': messages_received}
            chat_rooms.append(result)

        content = {
            'command': 'fetch_menu',
            'menus': self.menus_to_json(chat_rooms),
        }
        return self.send_menu(content)

    def fetch_previous_messages(self, data):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        x = data['id']
        y = ''.join(map(str, x))
        message_id = int(y)
        previous_messages_list = reversed(Message.objects.filter(room_name=chat_name, id__lt=message_id).order_by('-timestamp')[:100])

        messages = []
        for item in previous_messages_list:
            message_instance = Message.objects.filter(Q(room_name=chat_name) & Q(pk=item.pk)).values_list('pk', 'author__alias', 'room_name', 'content', 'timestamp')
            messages_read = MessageRead.objects.filter(Q(message__id=item.id) & Q(message_read=False) & ~Q(talent=author_user)).count()
            messages_read_self = MessageRead.objects.filter(Q(message__id=item.id) & Q(message_read=False) & Q(talent=author_user)).count()

            result = {'message': message_instance, 'messages_read': messages_read, 'messages_read_self': messages_read_self}
            messages.append(result)

        content = {
            'command': 'fetch_previous_messages',
            'messages': self.messages_to_json(messages),
        }
        return self.send_message(content)

    def fetch_messages(self, data):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        fetch_messages_list = Message.objects.filter(room_name=chat_name).order_by('-timestamp')[:20]

        messages = []
        for item in fetch_messages_list:
            message_instance = Message.objects.filter(Q(room_name=chat_name) & Q(pk=item.pk)).values_list('pk', 'author__alias', 'room_name', 'content', 'timestamp')
            messages_read = MessageRead.objects.filter(Q(message__id=item.id) & Q(message_read=False) & ~Q(talent=author_user)).count()
            messages_read_self = MessageRead.objects.filter(Q(message__id=item.id) & Q(message_read=False) & Q(talent=author_user)).count()

            result = {'message': message_instance, 'messages_read': messages_read, 'messages_read_self': messages_read_self}
            messages.append(result)

        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages),
        }
        return self.send_message(content)

    def new_message(self, data):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        message_item = Message.objects.create(
            room_name=chat_name,
            author=author_user,
            content=data['message'])

        latest_message = message_item.id
        message_id = Message.objects.get(pk=latest_message)
        chatgroup_id = ChatGroup.objects.get(slug=chat_name)
        message_talent = ChatRoomMembers.objects.filter(chat_group__slug=chat_name)

        for tlt in message_talent:
            create_message_read = MessageRead.objects.create(
                message=message_id,
                talent=tlt.talent,
                chat_group=chatgroup_id)

        update_group_modified = ChatRoomMembers.objects.filter(chat_group__slug=chat_name).update(
            date_modified=timezone.now()
        )

        message = []
        message_instance = Message.objects.filter(Q(room_name=chat_name) & Q(pk=message_item.pk)).values_list('pk', 'author__alias', 'room_name', 'content', 'timestamp')
        messages_read = MessageRead.objects.filter(Q(message__id=message_item.id) & Q(message_read=False) & ~Q(talent=author_user)).count()
        messages_read_self = MessageRead.objects.filter(Q(message__id=message_item.id) & Q(message_read=False) & Q(talent=author_user)).count()

        result = {'message': message_instance, 'messages_read': messages_read, 'messages_read_self': messages_read_self}
        message.append(result)

        content = {
            'command': 'new_message',
            'message': self.message_item_to_json(message)
        }

        return self.send_chat_message(content)

    def message_check_to_json(self, message):
        return {
            'id': message[0]['message'][0][0],
            'message_read': message[0]['messages_read'],
            'message_read_self': message[0]['messages_read_self'],
        }

    def messages_to_json(self, messages):
        result =[]
        for message in messages:
            result.append(self.message_to_json(message))
        result.reverse()
        return result

    def message_item_to_json(self, message):
        return {
            'id': message[0]['message'][0][0],
            'author': message[0]['message'][0][1],
            'content': message[0]['message'][0][3],
            'timestamp': str(message[0]['message'][0][4].strftime('%a, %b %d, %H:%M')),
            'message_read': message[0]['messages_read'],
            'message_read_self': message[0]['messages_read_self'],
        }

    def message_to_json(self, message):
        return {
            'id': message['message'][0][0],
            'author': message['message'][0][1],
            'content': message['message'][0][3],
            'timestamp': str(message['message'][0][4].strftime('%a, %b %d, %H:%M')),
            'message_read': message['messages_read'],
            'message_read_self': message['messages_read_self'],
        }

    def menus_to_json(self, menus):
        result=[]
        for menu in menus:
            result.append(self.menu_to_json(menu))
        return result

    def menu_to_json(self, menu):
#        print(menu['group'][0][0])
        return {
            'group': menu['group'][0][0],
            'group_url': menu['group'][0][2],
            'notification': menu['notification'],
            'notification_timestamp': str(menu['group'][0][1].strftime('%a, %d %b'))
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'fetch_menu': fetch_menu,
        'message_read_notification': message_read_notification,
        'fetch_previous_messages': fetch_previous_messages,
        'update_message': update_message_read,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope["user"]
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    def send_message_update(self, message):
        self.send(text_data=json.dumps(message))

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def send_menu(self, menu):
        self.send(text_data=json.dumps(menu))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))


class ChatConsumerv2(WebsocketConsumer):

    def fetch_messages(self, data):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        messages = Message.objects.filter(room_name=chat_name).order_by('-timestamp')[:20]
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages),
        }
        return self.send_message(content)

    def new_message(self, data):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        author = data['from']
        author_user = User.objects.get(alias=author)
        message = Message.objects.create(
            room_name=chat_name,
            author=author_user,
            content=data['message'])

        latest_message = Message.objects.latest('id').id
        message_id = Message.objects.get(pk=latest_message)
        chatgroup_id = ChatGroup.objects.get(slug=chat_name)
        message_talent = ChatRoomMembers.objects.filter(chat_group__slug=chat_name)

        for tlt in message_talent:
            create_message_read = MessageRead.objects.create(
                message=message_id,
                talent=tlt.talent,
                chat_group=chatgroup_id)

        update_group_modified = ChatRoomMembers.objects.filter(chat_group__slug=chat_name).update(
            date_modified=timezone.now()
        )
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result =[]
        for message in messages:
            result.append(self.message_to_json(message))
        result.reverse()
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.alias,
            'content': message.content,
            'timestamp': str(message.timestamp.strftime('%a, %b %d, %H:%M'))
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
#        data = json.loads(text_data)
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))



import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumerv1(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
