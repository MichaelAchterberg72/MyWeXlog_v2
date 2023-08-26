import graphene
from users.graphql.input_types import UserInputType


class ChatGroupInputType(graphene.InputObjectType):
    id = graphene.ID()
    room_name = graphene.String()
    slug = graphene.String()
    description = graphene.String()
    date_created = graphene.DateTime()


class ChatRoomMembersInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument(UserInputType)
    chat_group = graphene.Argument(ChatGroupInputType)
    room_name = graphene.String()
    mute_notifications = graphene.Boolean()
    date_joined = graphene.DateTime()
    date_modified = graphene.DateTime()


class MessageInputType(graphene.InputObjectType):
    id = graphene.ID()
    author = graphene.Argument(UserInputType)
    room_name = graphene.String()
    message_read = graphene.List(UserInputType)
    content = graphene.String()
    reply_pk = graphene.String()
    initial_members_count = graphene.String()
    message_deleted = graphene.Boolean()
    timestamp = graphene.DateTime()


class MessageReadInputType(graphene.InputObjectType):
    id = graphene.ID()
    message = graphene.Argument(MessageInputType)
    talent = graphene.Argument(UserInputType)
    chat_group = graphene.Argument(ChatGroupInputType)
    message_read = graphene.Boolean()
    read_date = graphene.DateTime()