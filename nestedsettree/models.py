from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from treebeard.mp_tree import MP_Node

from utils.utils import update_model, handle_m2m_relationship

from django.contrib.auth import get_user_model

User = get_user_model()


class NtWk(MP_Node):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    referral_code = models.CharField(max_length=42, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)

    node_order_by = ['talent']
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
        
        instance.save()
            
        return instance

    def __str__(self):
        return f'Talent: {self.talent}'
