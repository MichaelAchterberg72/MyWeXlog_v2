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


def must_be_yours(func):
    def check_and_call(request, *args, **kwargs):
        #user = request.user
        #print user.id
        pk = kwargs["pk"]
        scene = Scene.objects.get(pk=pk)
        if not (scene.user.id == request.user.id):
            return HttpResponse("It is not yours ! You are not permitted !",
                        content_type="application/json", status=403)
        return func(request, *args, **kwargs)
    return check_and_call


def user_is_entry_author(function):
    def wrap(request, *args, **kwargs):
        entry = Entry.objects.get(pk=kwargs['entry_id'])
        if entry.created_by == request.user:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
