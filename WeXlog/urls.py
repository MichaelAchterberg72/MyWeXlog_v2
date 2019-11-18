"""WeXlog URL Configuration
"""
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import handler404, handler500, include, url  # noqa

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('messages/', include('django_messages.urls')),
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
    path('admin/', admin.site.urls),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    path('select2/', include('django_select2.urls')),
    path('referrals/', include("pinax.referrals.urls", namespace='pinax_referrals')),
    path('invitations/', include('invitations.urls', namespace='Invitation')),
    path('notifications/', include("pinax.notifications.urls", namespace='pinax_notifications')),
    path('treeMP/', include('nestedsettree.urls', namespace='Structure')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
