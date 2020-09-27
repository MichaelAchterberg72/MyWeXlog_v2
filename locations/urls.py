from django.urls import path

from .import views

app_name = 'Location'

urlpatterns = [
    path('popup/region/add/', views.RegionAddPopup, name="RegionAddPop"),
    path('popup/ajax/get_region_id/', views.get_region_id, name="AJAX_GetRegionID"),
    path('popup/city/add/', views.CityAddPopup, name="CityAddPop"),
    path('popup/vac-city/', views.CityVacPopup, name="CityVacPop"),
    path('popup/ajax/get_city_id/', views.get_city_id, name="AJAX_GetCityID"),
    path('popup/suburb/add/', views.SuburbAddPopup, name="SuburbAddPop"),
    path('popup/ajax/get_suburb_id/', views.get_suburb_id, name="AJAX_GetSuburbID"),
    path('popup/currency/add/', views.CurrencyAddPopup, name="CurrencyAddPop"),
    path('popup/ajax/get_currency_id/', views.get_currency_id, name="AJAX_GetCurrencyID"),
]
