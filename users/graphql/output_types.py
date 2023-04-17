import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

User = get_user_model()


class UserOutputType(DjangoObjectType):
    class Meta:
        model = User
        fields = '__all__'
        convert_choices_to_enums = ['subscription', 'permission', 'role']
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'username': ['exact', ],
            'first_name': ['exact', 'icontains', 'startswith'],
            'last_name': ['exact', 'icontains', 'startswith'],
            'email': ['exact', 'icontains', 'startswith'],
            'is_staff': ['exact'],
            'is_active': ['exact'],
            'date_joined': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'alias': ['exact'],
            'display_text': ['exact'],
            'public_profile_name': ['exact'],
            'permit_viewing_of_profile_as_reference': ['exact'],
            'subscription': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'permission': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'role': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'registered_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'paid': ['exact'],
            'free_month': ['exact'],
            'paid_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'paid_type': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'invite_code': ['exact'],
            'alphanum': ['exact'],
        }