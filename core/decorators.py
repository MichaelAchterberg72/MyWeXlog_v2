from django.core.exceptions import PermissionDenied

from mod_corporate.models import CorporateStaff


def corp_permission(cr):
    '''Decorator for access to the corporate module'''
    def decorator(func):
        def wrap(request, *args, **kwargs):
            talent=request.user
            role = CorporateStaff.objects.get(talent=talent)
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
