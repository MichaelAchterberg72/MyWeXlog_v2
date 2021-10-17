from django.contrib import admin
from treebeard.admin import TreeAdmin

from .models import NtWk


@admin.register(NtWk)
class NtWkAdmin(TreeAdmin):
    pass
