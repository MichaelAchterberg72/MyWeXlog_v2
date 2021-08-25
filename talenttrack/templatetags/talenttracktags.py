import phonenumbers
from django import template

register = template.Library()


@register.filter
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.filter(name='phonenumber')
def phonenumber(value, country=None):
   return phonenumbers.parse(value, country)
