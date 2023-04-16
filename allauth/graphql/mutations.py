import graphene
from django.contrib.auth import login
from allauth.account.forms import LoginForm
from graphene_django.forms.mutation import DjangoModelFormMutation

class AuthMutation(DjangoModelFormMutation):
    class Meta:
        form_class = LoginForm

    @classmethod
    def perform_mutate(cls, form, info):
        user = form.user_cache
        if user is not None:
            login(info.context, user)
            return cls(errors=None)
        else:
            return cls(errors=form.errors.get_json_data())


class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()