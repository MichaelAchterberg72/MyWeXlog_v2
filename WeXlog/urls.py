"""WeXlog URL Configuration
"""
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import handler404, handler500, url  # noqa
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import TemplateView
from filebrowser.sites import site

from graphene_django.views import GraphQLView
from WeXlog import schema

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    #path('messages/', include('django_messages.urls')),
    path('select2/', include('django_select2.urls')),
    path('Profile/', include('Profile.urls', namespace='Profile')),
    path('flatten/', include('db_flatten.urls', namespace='Flatten')),
    path('location/', include('locations.urls', namespace='Location')),
    path('enterprise/', include('enterprises.urls', namespace='Enterprise')),
    path('project/', include('project.urls', namespace='Project')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payments/', include('payments.urls', namespace='Payments')),
    path('public/', include('public.urls', namespace='Public')),
    path('experience/booklist/', include('booklist.urls', namespace='BookList')),
    path('experience/', include('talenttrack.urls', namespace='Talent')),
    path('trust/', include('trustpassport.urls', namespace='Trust')),
    path('marketplace/', include('marketplace.urls', namespace='MarketPlace')),
    path('user/', include('users.urls', namespace='Users')),
    path('aliu8926kjak/', admin.site.urls),
    path('feedback/', include('feedback.urls', namespace='Feedback')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    path('referrals/', include("pinax.referrals.urls", namespace='pinax_referrals')),
    path('invitations/', include('invitations.urls', namespace='Invitation')),
    path('management/', include('management.urls', namespace='Management')),
    # path('notifications/', include("pinax.notifications.urls", namespace='pinax_notifications')),
    path('treeMP/', include('nestedsettree.urls', namespace='Structure')),
    path('chat/', include('intmessages.urls', namespace='Chat')),
    path('appcontrol/', include('AppControl.urls', namespace='AppControl')),
    path('corporate/', include('mod_corporate.urls', namespace='Corporate')),
    path('billing/', include('billing.urls', namespace='Billing')),
    path('calendar/', include('schedule.urls')),
    path('skills/', include('skills.urls', namespace='Skills')),
    path('tinymce/', include('tinymce.urls')),
    path('admin/filebrowser/', site.urls),
    path('error/', TemplateView.as_view(template_name="error_screen.html"), name='404Error'),
    path("robots.txt", TemplateView.as_view(template_name="users/robots.txt", content_type="text/plain")),
#    path('emoji/', include('emoji.urls')),
    path('graphql/', GraphQLView.as_view(schema=schema, graphiql=True)),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
