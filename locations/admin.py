from django.contrib import admin

from .models import City, Currency, Region, Suburb


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    search_fields = ['currency_name', 'currency_abv', 'country']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = ['region', 'country']

@admin.register(Suburb)
class SuburbAdmin(admin.ModelAdmin):
    search_fields = ['city__city', 'suburb']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ['region__region', 'city']
