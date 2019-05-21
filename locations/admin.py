from django.contrib import admin

from .models import (
    City, Suburb, Region
    )

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass

@admin.register(Suburb)
class SuburbAdmin(admin.ModelAdmin):
    pass

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass
