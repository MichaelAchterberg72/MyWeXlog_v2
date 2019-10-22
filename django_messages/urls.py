from django.urls import path, re_path
from django.views.generic import RedirectView
from django.conf.urls import url, include

from django_messages.views import *

urlpatterns = [
    path('', RedirectView.as_view(permanent=True, url='inbox/'), name='messages_redirect'),
    path('inbox/', inbox, name='messages_inbox'),
    path('outbox/', outbox, name='messages_outbox'),
    path('compose/', compose, name='messages_compose'),
    path('compose/<int:recipient>/', compose, name='messages_compose_to'),
    path('reply/<int:message_id>/', reply, name='messages_reply'),
    path('view/<int:message_id>/', view, name='messages_detail'),
    path('delete/<int:message_id>/', delete, name='messages_delete'),
    path('permanently_delete/<int:message_id>', permanently_delete, name='messages_permanently_delete'),
    path('undelete/<int:message_id>/', undelete, name='messages_undelete'),
    path('trash/', trash, name='messages_trash'),
]
