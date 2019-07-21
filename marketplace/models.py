from django.db import models
from django.conf import settings
from django.utils import timezone


from enterprises.models import Branch
from locations.models import Currency, City
from db_flatten.models import SkillTag
from talenttrack.models import Result


class WorkLocation(models.Model):
    type = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.type

#Function to randomise filename for Profile Upload
def BidTerms(instance, filename):
	ext = filename.split('.')[-1]
	return "bidterms\%s_%s.%s" % (str(time()).replace('.','_'), random(), ext)


RATE_UNIT = (
    ('H','per Hour'),
    ('D','per Day'),
    ('M','per Month'),
    ('L','Lump Sum'),
)

UNIT = (
    ('O','Once Off'),
    ('M','per Month'),
    ('D','perDay'),
    ('W','per Week'),
    ('S','Short Term Contract'),
    ('A','As and When Contract'),
)

class TalentRequired(models.Model):
    STATUS = (
        ('O','Open'),
        ('C','Closed'),
    )
    date_entered = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=250)
    enterprise = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="Company Branch")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_deadline = models.DateField('Work to be completed by')
    hours_required = models.IntegerField()
    unit = models.CharField(max_length=1, choices=UNIT)
    worklocation = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    rate_offered = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    bid_open = models.DateTimeField(default=timezone.now, null=True)
    bid_closes = models.DateTimeField(null=True)
    offer_status = models.CharField(max_length=1, choices=STATUS, default='O')
    certification = models.ManyToManyField(Result, verbose_name='Certifications Required', blank=True)
    scope = models.TextField()
    expectations = models.TextField()
    terms = models.FileField(upload_to=BidTerms, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='City, Town or Place')

    class Meta:
        unique_together = (('date_entered','enterprise','title', 'requested_by'),)

    def __str__(self):
        return '{}, {}, {}'.format(self.title, self.enterprise, self.date_entered)


class Deliverables(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    deliverable = models.CharField(max_length=255)

    class Meta:
        unique_together = (('scope','deliverable'),)

    def __str__(self):
        return '{}: {}'.format(self.scope, self.deliverable)


class SkillLevel(models.Model):
    LEVEL = (
        ('S','Student'),
        ('G','Graduate'),
        ('J','Junior'),
        ('I','Intermediate'),
        ('S','Senior'),
        ('L','Lead'),
    )

    level = models.CharField(max_length=1, choices=LEVEL)
    min_hours = models.SmallIntegerField()
    description = models.TextField()

    def __str__(self):
        return '{} (<={} hrs)'.format(self.level, self.min_hours)


class SkillRequired(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    skill = models.ForeignKey(SkillTag, on_delete=models.PROTECT)
    experience_level = models.ForeignKey(SkillLevel, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('skill','experience_level'),)

    def __str__(self):
        return self.scope


class WorkBid(models.Model):
    BID = (
        ('A','Accepted'),
        ('R','Rejected'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    #Completed by Talent
    work = models.ForeignKey(TalentRequired, on_delete=models.PROTECT)
    rate_bid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    #Completed by CLient
    bidreview = models.CharField(max_length=1, choices=BID)

    def __str__(self):
        return'{}: {}'.format(self.work, self.talent)

class TalentAvailabillity(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    hours_available = models.IntegerField()
    unit = models.CharField(max_length=1, choices=UNIT, default='D')

    def __str__(self):
        return '{} - {} {} ({})'.format(self.talent, self.hours_available, self.get_unit_display, self.date_to)

class WorkIssuedTo(models.Model):
    #completed by client
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Successful_talent')
    work = models.OneToOneField(TalentRequired, on_delete=models.PROTECT)
    rate_accepted = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    date_completion = models.DateField()
    date_begin = models.DateField()
    #autocompleted
    date_create = models.DateField(auto_now_add=True)
    date_complete = models.DateField(auto_now=True)
    #completed by talent
    start_confirm = models.BooleanField()
    rate_confirm = models.BooleanField()
    deadline_confirm = models.BooleanField()
    terms_accept = models.BooleanField()

    def __str__(self):
        return '{} assigned {}({})'.format(self.talent, self.work, self.terms_accept)
