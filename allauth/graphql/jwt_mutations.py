import graphene
from django.contrib.auth import authenticate
from allauth.account.forms import LoginForm
from graphql_jwt.shortcuts import create_refresh_token, get_token
from graphql_jwt.mixins import JSONWebTokenMixin


class AllauthJWT(JSONWebTokenMixin, graphene.Mutation):
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, email, password):
        user = authenticate(info.context, email=email, password=password)
        if user is not None:
            if user.is_active and user.emailaddress_set.filter(verified=True).exists():
                token = get_token(user)
                refresh_token = create_refresh_token(user)
                return cls(token=token, refresh_token=refresh_token)
            else:
                raise Exception('Email not verified.')
        else:
            raise Exception('Invalid email or password.')


class Mutation(graphene.ObjectType):
    token_auth = AllauthJWT.Field()