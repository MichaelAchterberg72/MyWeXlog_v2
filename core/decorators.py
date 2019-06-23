from django.core.exceptions import PermissionDenied

def app_role(cr):
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if request.user.role >= int(cr):
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
