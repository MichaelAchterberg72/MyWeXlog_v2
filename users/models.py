from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

from pinax.referrals.models import Referral
from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from nestedsettree.models import NtWk


class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    PKG = (
        (0,'Free'),
        (1,'Passive'),
        (2,'Active'),
    )
    COMPANY = (
        (0,'Company Representative'),
        (1,'Individual'),
    )
    ROLE = (
        (0,'Talent'),
        (1,'Beta-Tester'),
        (2,'Industry Insider'),
    )
    PAID_TYPE = (
        (0,'Free'),
        (1,'Monthly'),
        (2,'Six-Monthly'),
        (3,'Twelve-Monthly'),
    )
    subscription = models.IntegerField(choices=PKG, default=0)
    permission = models.IntegerField(choices=COMPANY, default=1)
    role = models.IntegerField(choices=ROLE, default=0)
    paid = models.BooleanField(default=False, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    paid_type = models.IntegerField(choices=PAID_TYPE, default=0)
    invite_code = models.CharField(max_length=42, null=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email

@receiver(user_signed_up)
def after_signup(request, user, **kwargs):
    if 'pinax-referral' in request.COOKIES:
        ref_biscuit = request.COOKIES['pinax-referral']
        ref_code, ref_session = ref_biscuit.split(":")
        CustomUser.objects.filter(email=user).update(invite_code=ref_code)

        get = lambda node_id: NtWk.objects.get(pk=node_id)
        pp = Referral.objects.get(code=ref_code)
        rt_n = CustomUser.objects.get(pk=pp.user.pk)
        root = NtWk.objects.get(talent=rt_n)
        node = get(root.pk).add_child(talent=user, referral_code=ref_code)
        print("Child Created!!!!!!!!!!")
    else:
        get = lambda node_id: NtWk.objects.get(pk=node_id)
        root = NtWk.add_root(talent=user)
        print("Root Created!!!!!!!!!")
