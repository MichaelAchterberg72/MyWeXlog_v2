from django.contrib.auth import get_user_model
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from django.db.models import Count, Sum, F, Q

from . models import Message, ChatRoomMembers, MessageRead, ChatGroup

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def message_read_notification(self, data):
        author = self.scope["user"]
        author_user = User.objects.get(alias=author.alias)
        message_id = Message.objects.get(pk=data['id'])
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        chat_name = self.room_name
        chatgroup_id = ChatGroup.objects.get(slug=chat_name)
        update_message_read = MessageRead.objects.update(
            message=message_id,
            talent=author_user,
            chat_group=chatgroup_id,
            message_read=True,
            read_date=timezone.now())

        #is it necessary to rebuild the menu with each message read - processor heavy
        groups_qs = ChatRoomMembers.objects.filter(talent=author_user).order_by('-date_modified').values_list('chat_group')

        chat_rooms = []
        for item in groups_qs:
            groups = ChatRoomMembers.objects.filter(Q(talent=author_user) & Q(chat_group=item)).values_list('room_name', 'date_modified', 'chat_group__slug')
            messages_received = MessageRead.objects.filter(Q(chat_group=item) & Q(message_read=False) & ~Q(talent=author_user)).count()

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
            messages_received = MessageRead.objects.filter(Q(chat_group=item) & Q(message_read=False) & ~Q(talent=author_user)).count()

            result = {'group': groups, 'notification': messages_received}
            chat_rooms.append(result)

        content = {
            'command': 'fetch_menu',
            'menus': self.menus_to_json(chat_rooms),
        }
        return self.send_menu(content)

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
            'id': message.pk,
            'author': message.author.alias,
            'content': message.content,
            'timestamp': str(message.timestamp.strftime('%a, %b %d, %H:%M'))
        }

    def menus_to_json(self, menus):
        result=[]
        for menu in menus:
            result.append(self.menu_to_json(menu))
        return result

    def menu_to_json(self, menu):
        print(menu['group'][0][0])
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
