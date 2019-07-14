"""WeXlog URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('messages/', include('django_messages.urls')),
    path('Profile/', include('Profile.urls', namespace='Profile')),
    path('flatten/', include('db_flatten.urls', namespace='Flatten')),
    path('location/', include('locations.urls', namespace='Location')),
    path('enterprise/', include('enterprises.urls', namespace='Enterprise')),
    path('project/', include('project.urls', namespace='Project')),
    path('experience/booklist/', include('booklist.urls', namespace='BookList')),
    path('experience/', include('talenttrack.urls', namespace='Talent')),
    path('trust/', include('trustpassport.urls', namespace='Trust')),
    path('marketplace/', include('marketplace.urls', namespace='MarketPlace')),
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('notifications/', include('pinax.notifications.urls', namespace='pinax_notifications')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
