from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


from django.contrib.auth.decorators import login_required
from csp.decorators import csp_exempt


@login_required()
@csp_exempt
def index(request):
    return render(request, 'intmessages/index.html', {})


@login_required()
@csp_exempt
def room(request, room_name):
    return render(request, 'intmessages/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username': mark_safe(json.dumps(request.user.alias))
    })
