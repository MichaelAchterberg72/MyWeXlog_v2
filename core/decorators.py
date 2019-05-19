from django.core.exceptions import PermissionDenied

def company_role(cr):
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if request.user.permission <= int(cr):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrap
    return decorator

def package_required(pk):
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if request.user.permission <= int(pk):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrap
    return decorator
