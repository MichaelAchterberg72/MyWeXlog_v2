from django.urls import path


from .import views
from .views import *

app_name = 'Enterprise'

urlpatterns = [
    path('popup/add/', views.EnterpriseAddPopup, name="EnterpriseAddPop"),
    path('popup/ajax/get_enterprise_id/', views.get_enterprise_id, name="AJAX_GetEnterpriseID"),
]
