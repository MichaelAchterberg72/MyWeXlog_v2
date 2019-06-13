"""WeXlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path ('messages/', include('django_messages.urls')),
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
    ]

urlpatterns += staticfiles_urlpatterns()
