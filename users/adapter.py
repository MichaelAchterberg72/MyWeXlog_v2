from django.conf import settings
#from django.contrib.auth.models import User
from django.shortcuts import resolve_url

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):

        if request.user.is_authenticated:
            url = '/Profile/'

        elif request.user.is_anonymous:
            url = settings.LOGIN_URL

        return url

    def get_logout_redirect_url(self, request):
        url = settings.LOGOUT_REDIRECT_URL
        return url
