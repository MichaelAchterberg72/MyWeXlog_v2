from random import random
from time import time

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from tinymce.models import HTMLField

from utils.utils import update_model, handle_m2m_relationship

from db_flatten.models import LanguageList, SkillTag
from enterprises.models import Branch
from locations.models import City, Currency
from Profile.utils import create_code8, create_code9
from talenttrack.models import Designation, Result
from users.models import CustomUser
from WeXlog.storage_backends import PrivateMediaStorage, PublicMediaStorage

from django.contrib.auth import get_user_model

User = get_user_model()


#This is the table that specifies the work configuration (Freelance, Remote Freelence, Consultant, Contractor, Employee, FIFO)
class WorkLocation(models.Model):
    WTPE = (
        ('Remote freelance','Remote freelance'),
        ('Freelance','Freelance'),
        ('Consultant','Consultant'),
        ('Contractor','Contractor'),
        ('Employee','Employee'),
        ('FiFo','FiFo'),
    )
    type = models.CharField(max_length=40, unique=True, choices=WTPE)
    description = models.TextField()
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    class Meta:
        pass

    def __str__(self):
        return self.type


#Function to randomise filename for Profile Upload
def BidTerms(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/bidterms\%s_%s.%s" % (instance.requested_by.id, str(time()).replace('.','_'), random(), ext)


RATE_UNIT = (
    ('H','per Hour'),
    ('D','per Day'),
    ('M','per Month'),
    ('A','per Annum'),
    ('L','Lump Sum'),
    ('I','Market Related'),
)

UNIT = (
    ('O','Once Off'),
    ('M','per Month'),
    ('D','per Day'),
    ('W','per Week'),
    ('P','Permanent Position'),
    ('S','Short Term Contract'),
    ('A','As and When Contract'),
)


class SkillLevel(models.Model):
    LEVEL = (
        (0,'Student'),
        (1,'Beginner'),
        (2,'Junior'),
        (3,'Intermediate'),
        (4,'Senior'),
        (5,'Lead'),
    )

    level = models.IntegerField(choices=LEVEL, default=0)
    min_hours = models.IntegerField()#Read hours (typically max hours, but for lead its greater than the amount of hours shown.)
    description = models.TextField()
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    class Meta:
        ordering = ['level']

    def __str__(self):
        if self.level <=4:
            return f'{self.get_level_display()} (<={self.min_hours}) hours'
        else:
            return f'{self.get_level_display()} (>{self.min_hours}) hours'


class TalentRequired(models.Model):
    STATUS = (
        ('O','Open'),
        ('C','Closed'),
    )
    WKFLOW = (
        ('S','Assigned'),#Vacancy has been assigned, but not yet accepted
        ('A','Accepted'),#Vacancy has been accepted
        ('I','Interviewing'),#Interviews have been requested
        ('L','Short-listed'),#People have been shortlisted
        ('P','Pending'),#No movement Yet
    )
    date_entered = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=250)
    ref_no = models.CharField("MyWeXlog Reference Number",max_length=10, unique=True, null=True, blank=True)#SlugField
    own_ref_no = models.CharField(max_length=100, unique=True, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Company")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_deadline = models.DateField('Work completed by', blank=True, null=True)
    permpos = models.BooleanField('Permanent Position?', default=False, blank=True)
    hours_required = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=1, choices=UNIT)
    experience_level = models.ForeignKey(SkillLevel, on_delete=models.PROTECT)
    language = models.ManyToManyField(LanguageList)
    worklocation = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)#Job configuration
    rate_offered = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    bid_open = models.DateTimeField(auto_now_add=True, null=True)
    bid_closes = models.DateTimeField('Applications Close', null=True)
    offer_status = models.CharField(max_length=1, choices=STATUS, default='O')
    certification = models.ManyToManyField(Result, verbose_name='Certifications Required', blank=True)
    scope = HTMLField()
    expectations = HTMLField()
    terms = models.FileField(storage=PublicMediaStorage(), upload_to=BidTerms, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='City, Town or Place')
    date_modified = models.DateTimeField(auto_now=True)
    vac_wkfl = models.CharField(max_length=1, choices=WKFLOW, default='P')
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        designation = kwargs.pop('designation', None)
        companybranch = kwargs.pop('companybranch', None)
        requested_by = kwargs.pop('requested_by', None)
        experience_level = kwargs.pop('experience_level', None)
        language = kwargs.pop('language', [])
        worklocation = kwargs.pop('worklocation', None)
        currency = kwargs.pop('currency', None)
        certification = kwargs.pop('certification', [])
        city = kwargs.pop('city', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if designation:
            instance.designation = Designation.update_or_create(id=designation.id, **designation)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)

        if requested_by:
            instance.requested_by = User.update_or_create(slug=requested_by.slug, **requested_by)

        if experience_level:
            instance.experience_level = SkillLevel.update_or_create(id=experience_level.id, **experience_level)

        if language:
            language_list_models_data = {
                    'model': LanguageList,
                    'manager': 'language',
                    'fields': ['language'],
                    'data': language,
                }
            instance = handle_m2m_relationship(instance, [language_list_models_data])

        if worklocation:
            instance.worklocation = WorkLocation.update_or_create(id=worklocation.id, **worklocation)

        if currency:
            instance.currency = Currency.update_or_create(id=currency.id, **currency)

        if certification:
            certification_models_data = {
                    'model': Result,
                    'manager': 'certification',
                    'fields': ['type'],
                    'data': certification,
                }
            instance = handle_m2m_relationship(instance, [certification_models_data])

        if city:
            instance.city = City.update_or_create(id=city.id, **city)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('companybranch','title', 'requested_by'),('companybranch', 'own_ref_no'),)

    def __str__(self):
        return f'{self.title}, {self.companybranch}'

    def save(self, *args, **kwargs):
        if self.ref_no is None or self.ref_no == "":
            self.ref_no = create_code8(self)
        super(TalentRequired, self).save(*args, **kwargs)

#    def get_current_user_views(self):
#        return self.vacancyviewed_set.filter(talent=self.request.user)

class VacancyViewed(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    vacancy = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False)
    date_viewed = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    read = models.BooleanField(default=False)
    date_read = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    closed = models.BooleanField(default=False)
    date_closed = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        vacancy = kwargs.pop('vacancy', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if vacancy:
            instance.vacancy = TalentRequired.update_or_create(id=vacancy.id, **vacancy)
        
        instance.save()
            
        return instance

    def __str__(self):
        return f'{self.vacancy}'


class Deliverables(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    deliverable = HTMLField()
    date_modified = models.DateField(auto_now=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        scope = kwargs.pop(['scope', None])
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if scope:
            instance.scope = TalentRequired.update_or_create(id=scope.id, **scope)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('scope','deliverable'),)

    def __str__(self):
        return '{}: {}'.format(self.scope, self.deliverable)


class SkillRequired(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    skills = models.ForeignKey(SkillTag, on_delete=models.PROTECT)
    date_modified = models.DateField(auto_now=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        scope = kwargs.pop('scope', None)
        skills = kwargs.pop('skills', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if scope:
            instance.scope = TalentRequired.update_or_create(id=scope.id, **scope)

        if skills:
            instance.skills = SkillTag.update_or_create(id=skills.id, **skills)

        instance.save()
            
        return instance

    def __str__(self):
        return f'{self.scope.title}'


BID = (
        ('A','Accepted'),
        ('P','Pending'),
        ('R','Unsuccessful'),
        ('S','Short-listed'),
        ('D','Talent Declined'),
        ('I','Interview'),
        ('Z','Declined'),
    )

class BidShortList(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='Shortlisted')
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    preferance_rating = models.SmallIntegerField(null=True, default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    status =  models.CharField(max_length=1, choices=BID, null=True, default='S')
    slug = models.SlugField(max_length=50, null=True, blank=True, unique=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        scope = kwargs.pop('scope', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if scope:
            instance.scope = TalentRequired.update_or_create(id=scope.id, **scope)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('talent', 'scope'),)

    def __str__(self):
        return f'{self.scope.title} shortlist {self.talent}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(BidShortList, self).save(*args, **kwargs)

#This table is also used to track all declined talent
class BidInterviewList(models.Model):
    OC = (
        ('P','Offer Pending'),
        ('I','Interview Pending'),
        ('S','Suitable'),
        ('N','Not Suitable'),
        ('D','Declined Offer'),
        ('A','Accepted Offer'),
    )
    RSP = (
        ('P','Interview Pending'),
        ('A','Accept Interview'),
        ('D','Decline Interview'),
        ('N','Not Interviewed'),
        ('Z', 'Offered Vacancy without Interview')
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='Interviewed')
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    date_listed = models.DateTimeField(auto_now_add=True)
    outcome = models.CharField(max_length=1, choices=OC, default='I')
    tlt_decline_reason = models.ForeignKey('DeclineAssignment', on_delete=models.PROTECT, null=True)
    comments_tlt = models.TextField(null=True)
    tlt_response = models.CharField(max_length=1, choices=RSP, default='P')
    tlt_reponded = models.DateTimeField(null=True)
    tlt_intcomplete = models.BooleanField(default=False)
    emp_intcomplete = models.BooleanField(default=False)
    comments_emp = models.TextField(null=True)
    slug = models.SlugField(max_length=50, null=True, blank=True, unique=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        scope = kwargs.pop('scope', None)
        tlt_decline_reason = kwargs.pop('tlt_decline_reason', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if scope:
            instance.scope = TalentRequired.update_or_create(id=scope.id, **scope)

        if tlt_decline_reason:
            instance.tlt_decline_reason = DeclineAssignment.update_or_create(id=tlt_decline_reason.id, **tlt_decline_reason)

        instance.save()
            
        return instance

    class Meta:
        unique_together = (('talent', 'scope'),)

    def __str__(self):
        return f'{self.scope.title}, {self.talent}, {self.get_outcome_display()}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(BidInterviewList, self).save(*args, **kwargs)


class WorkBid(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    #Completed by Talent
    work = models.ForeignKey(TalentRequired, on_delete=models.PROTECT)
    rate_bid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    motivation = models.TextField(blank=True, null=True)
    #Completed by CLient
    bidreview = models.CharField(max_length=1, choices=BID, null=True, default='P')
    date_applied = models.DateTimeField(auto_now_add=True)
    date_revised = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        work = kwargs.pop('work', None)
        currency = kwargs.pop('currency', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)

        if work:
            instance.work = TalentRequired.update_or_create(id=work.id, **work)

        if currency:
            instance.currency = Currency.update_or_create(id=currency.id, **currency)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('talent', 'work'),)

    def __str__(self):
        return'{}: {}'.format(self.work.title, self.talent)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(WorkBid, self).save(*args, **kwargs)


class TalentAvailabillity(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    freelance = models.BooleanField(default=False)
    remote_freelance = models.BooleanField(default=False)
    contract = models.BooleanField(default=False)
    part_time = models.BooleanField(default=False)
    permanent = models.BooleanField(default=False)
    date_modified = models.DateField(auto_now=True)
    
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
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance

    def __str__(self):
        return '{}'.format(self.talent)


#Reasons: No Available Capacity, Not Looking for work, Not suited to vacancy, Rate too low, Company Reputation, other (comment)
class DeclineAssignment(models.Model):
    option = models.CharField(max_length = 200, unique=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    def __str__(self):
        return f'{self.option}'


class WorkIssuedTo(models.Model):
    RSP = (
        ('P','Response Pending'),
        ('A','Accept Assignment'),
        ('D','Decline Assignment'),
        ('C','Clarification Requested'),
    )
    #completed by employer
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='Successful_talent')
    work = models.ForeignKey(TalentRequired, on_delete=models.PROTECT)
    tlt_response = models.CharField(max_length=1, choices = RSP, default= 'P')
    tlt_decline_reason = models.ForeignKey(DeclineAssignment, on_delete=models.PROTECT, null=True)
    tlt_response_date = models.DateTimeField(null=True)
    comments = models.TextField()#talent decline reasons
    clarification_required = models.TextField(null=True)
    #completed by employer
    rate_offered = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H', null=True)
    date_deliverable = models.DateTimeField(null=True)
    date_begin = models.DateTimeField(null=True)
    #autocompleted
    date_create = models.DateTimeField(auto_now_add=True)
    date_complete = models.DateTimeField(auto_now=True)
    #completed by talent
    #start_date = models.BooleanField()
    #rate_confirm = models.BooleanField()
    #deadline_confirm = models.BooleanField()
    #terms_accept = models.BooleanField()
    tlt_rated = models.BooleanField(default=False)
    assignment_complete_tlt = models.BooleanField(default=False)
    emp_rated = models.BooleanField(default=False)
    assignment_complete_emp = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, null=True, unique=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        work = kwargs.pop('work', None)
        tlt_decline_reason = kwargs.pop('tlt_decline_reason', None)
        currency = kwargs.pop('currency', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if work:
            instance.work = TalentRequired.update_or_create(id=work.id, **work)

        if tlt_decline_reason:
            instance.tlt_decline_reason = DeclineAssignment.update_or_create(id=tlt_decline_reason.id, **tlt_decline_reason)

        if currency:
            instance.currency = Currency.update_or_create(id=currency.id, **currency)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('talent', 'work'),)

    def __str__(self):
        return f'{self.work.title} assigned to {self.talent}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(WorkIssuedTo, self).save(*args, **kwargs)


#Employer rating the talent
class VacancyRate(models.Model):
    OPNS = (
        (1,'One'),
        (2,'Two'),
        (3,'Three'),
        (4,'Four'),
        (5,'Five'),
    )
    vacancy = models.ForeignKey(TalentRequired, on_delete=models.PROTECT)
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    rate_1 = models.SmallIntegerField('Talent Work Performance', choices=OPNS, default=3)
    rate_2 = models.SmallIntegerField('Completed on Time?', choices=OPNS, default=3)
    rate_3 = models.SmallIntegerField('Would you hire this person again?', choices=OPNS, default=3)
    date_rating = models.DateField(auto_now=True)
    comment = HTMLField(blank=True, null=True)
    personal_comment = HTMLField(blank=True, null=True)
    complete = models.BooleanField(null=True, default=False)
    suggestions = HTMLField(blank=True, null=True)
    slug = models.SlugField(max_length=50, null=True, unique=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        vacancy = kwargs.pop('vacancy', None)
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if vacancy:
            instance.vacancy = TalentRequired.update_or_create(id=vacancy.id, **vacancy)
            
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('vacancy','talent'), )

    def __str__(self):
        return f'Rating for {self.talent} on {self.vacancy.title}'

    def avg_rate(self):
        sum = self.rate_1+self.rate_2+self.rate_3
        return sum/3
    average = property(avg_rate)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(VacancyRate, self).save(*args, **kwargs)


#Talent rating the employer
class TalentRate(models.Model):
    OPNS = (
        (1,'One'),
        (2,'Two'),
        (3,'Three'),
        (4,'Four'),
        (5,'Five'),
    )

    PYMT = (
        (0,'Select'),
        (1,'Still Waiting!'),
        (2,'Within 60 days or more'),
        (3,'Within 30 days'),
        (4,'Within 14 days'),
        (5,'Within 5 days'),
    )

    vacancy = models.ForeignKey(TalentRequired, on_delete=models.PROTECT)
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    rate_1 = models.SmallIntegerField('Employer Performance', choices=OPNS, default=3)
    rate_2 = models.SmallIntegerField('Payment Receipt', choices=OPNS, default=3)
    rate_3 = models.SmallIntegerField('Would you work for this employer again?', choices=OPNS, default=3)
    payment_time = models.SmallIntegerField('Days from invoice to receipt of payment', choices=PYMT, default=0)
    date_rating = models.DateField(auto_now=True)
    comment = HTMLField(blank=True, null=True)
    suggestions = HTMLField(blank=True, null=True)
    complete = models.BooleanField(null=True, default=False)
    slug = models.SlugField(max_length=50, null=True, unique=True, blank=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        vacancy = kwargs.pop('vacancy', None)
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if vacancy:
            instance.vacancy = TalentRequired.update_or_create(id=vacancy.id, **vacancy)
            
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('vacancy','talent'), )

    def avg_rate(self):
        sum = self.rate_1+self.rate_2+self.rate_3+self.payment_time
        return sum/4
    average = property(avg_rate)

    def __str__(self):
        return f'Rating for {self.vacancy.title} by {self.talent}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(TalentRate, self).save(*args, **kwargs)
