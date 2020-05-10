from treebeard.mp_tree import MP_Node
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models


class NtWk(MP_Node):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    referral_code = models.CharField(max_length=42, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)

    node_order_by = ['talent']

    def __str__(self):
        return f'Talent: {self.talent}'
