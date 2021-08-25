from django.core.exceptions import PermissionDenied
from django.db.models import Q

from mod_corporate.models import CorporateStaff

#Why will this now work

def corp_permission(cr):
    '''Decorator for access to the corporate module'''
    def decorator(func):
        def wrap(request, *args, **kwargs):
            talent = request.user
            cor = request.COOKIES['corp']

            role = CorporateStaff.objects.get(Q(talent=talent) & Q(corporate__slug=cor))
            if role.corp_access >= int(cr):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrap
    return decorator

def subscription(cs):
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if request.user.subscription >= int(cs):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrap
    return decorator
