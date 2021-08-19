from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from pinax.referrals.models import Referral

from allauth.account.signals import user_signed_up
from nestedsettree.models import NtWk
from Profile.utils import create_code16


class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    PKG = (
        (0,'Free'),
        (1,'Passive'),
        (2,'Active'),
        (3,'MyWeXlog Management'),
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
    alias = models.CharField(max_length=30, null=True)
    display_text = models.CharField(max_length=250, null=True)
    public_profile_name = models.CharField(max_length=100, unique=True, null=True)
    permit_viewing_of_profile_as_reference = models.BooleanField(default=False, blank=True)
    subscription = models.IntegerField(choices=PKG, default=2)
    permission = models.IntegerField(choices=COMPANY, default=1)
    role = models.IntegerField(choices=ROLE, default=0)
    registered_date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=True, blank=True)
    free_month = models.BooleanField(default=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    paid_type = models.IntegerField(choices=PAID_TYPE, default=1)
    invite_code = models.CharField(max_length=42, null=True, blank=True)
    alphanum = models.SlugField(max_length=7, unique=True, null=True)

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.display_text}'


@receiver(user_signed_up)
def after_signup(request, user, **kwargs):

    referral = Referral.create(
            user=user,
            redirect_to = '/accounts/signup/'
    )

    if 'pinax-referral' in request.COOKIES:
        ref_biscuit = request.COOKIES['pinax-referral']
        ref_code, ref_session = ref_biscuit.split(":")
        CustomUser.objects.filter(email=user).update(invite_code=ref_code)

        get = lambda node_id: NtWk.objects.get(pk=node_id)
        pp = Referral.objects.get(code=ref_code)
        rt_n = CustomUser.objects.get(pk=pp.user.pk)
        root = NtWk.objects.get(talent=rt_n)
        node = get(root.pk).add_child(talent=user, referral_code=ref_code)

    else:
        get = lambda node_id: NtWk.objects.get(pk=node_id)
        root = NtWk.add_root(talent=user)


class CustomUserSettings(models.Model):
    THEMES = (
        (0, 'Light Theme'),
        (1, 'Dark Theme'),
    )
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    right_to_say_no = models.BooleanField('The right to say no to the sale of personal information', default=False)
    unsubscribe = models.BooleanField('Unsubscribe from all newsletters', default=False)
    receive_newsletter = models.BooleanField('Receive the newsletter', default=True)
    validation_requests = models.BooleanField('Receive validation requests', default=True)
    takeout = models.BooleanField('Export data to a csv file', default=False)
    dnt = models.BooleanField('Do Not Track', default=False)
    right_to_be_forgotten = models.BooleanField('Right to be forgotten / Permanently delete my account', default=False)
    payment_notifications = models.BooleanField('Receive subscription payment notifications', default=True)
    subscription_notifications = models.BooleanField('Receive subscription status notifications', default=True)
    privacy = models.BooleanField('Accept Privacy Policy', default=True)
    useragree = models.BooleanField('Accept User Agreement', default=True)
    theme = models.IntegerField(choices=THEMES, default=0)

    def __str__(self):
        return f"Settings for {self.talent}"

    def create_settings(sender, **kwargs):
        if kwargs['created']:
            create_settings = CustomUserSettings.objects.create(talent=kwargs['instance'])

    post_save.connect(create_settings, sender=CustomUser)

    def create_public_profile_name(sender, created, **kwargs):
        if created:
            instance = kwargs['instance']
            instance.public_profile_name = f'{create_code16(instance)}-{instance.first_name.lower()}{instance.last_name.lower()}'
            instance.save()

    post_save.connect(create_public_profile_name, sender=CustomUser)


class ExpandedView(models.Model):
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    intro_walkthrough = models.BooleanField('Don\'t view intro again', default=False)
    trial_expired = models.BooleanField('Don\'t view trial again', default=False)
    applicants_list = models.BooleanField(default=True)
    applicants_fl_list = models.BooleanField(default=True)
    talent_suited_list = models.BooleanField(default=True)
    talent_fl_suited_list = models.BooleanField(default=True)
    shortlist_list = models.BooleanField(default=True)
    pending_interviews_list = models.BooleanField(default=True)
    pending_fl_interviews_list = models.BooleanField(default=True)
    suitable_applicants_list = models.BooleanField(default=True)
    suitable_fl_applicants_list = models.BooleanField(default=True)
    unsuitable_applicants_list = models.BooleanField(default=True)
    unsuitable_fl_applicants_list = models.BooleanField(default=True)
    rejected_applicants_list = models.BooleanField(default=True)
    rejected_fl_applicants_list = models.BooleanField(default=True)
    vacancies_suited_list = models.BooleanField(default=True)
    vacancies_fl_suited_list = models.BooleanField(default=True)

    def __str__(self):
        return f"Expanded view for {self.talent}"

    def create_settings(sender, **kwargs):
        if kwargs['created']:
            create_settings = ExpandedView.objects.create(talent=kwargs['instance'])

    post_save.connect(create_settings, sender=CustomUser)
