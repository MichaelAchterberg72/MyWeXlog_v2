from django.urls import path


from .import views
from .views import *

app_name = 'Billing'

urlpatterns = [
#    path('home/', views.ProjectListHome, name='ProjectHome'),
    path('add/calendar-item/', views.create_calendar_entry_view, name='CalendarAddPop'),
]
