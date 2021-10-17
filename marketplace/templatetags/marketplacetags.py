from django import template

from ..models import VacancyViewed

register = template.Library()

@register.filter(name='vv_user')
def vv_user(self, aVal):
    fvv = aVal.filter(talent=request.user)
    return fvv


@register.filter(name='remove_names')
def removenames(text):

    return nltk(text)
