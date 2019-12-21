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
    ('D','per Day'),
    ('W','per Week'),
    ('S','Short Term Contract'),
    ('A','As and When Contract'),
)


class SkillLevel(models.Model):
    LEVEL = (
        (0,'Student'),
        (1,'Graduate'),
        (2,'Junior'),
        (3,'Intermediate'),
        (4,'Senior'),
        (5,'Lead'),
    )

    level = models.IntegerField(choices=LEVEL, unique=True)
    min_hours = models.IntegerField()
    description = models.TextField()

    def clean(self):
        self.level = self.level.capitalize()

    def __str__(self):
        return f'{self.get_level_display()} (>={self.min_hours})'


class TalentRequired(models.Model):
    STATUS = (
        ('O','Open'),
        ('C','Closed'),
    )
    date_entered = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=250)
    enterprise = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="Company Branch")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_deadline = models.DateField('Work completed by')
    hours_required = models.IntegerField()
    unit = models.CharField(max_length=1, choices=UNIT)
    experience_level = models.ForeignKey(SkillLevel, on_delete=models.PROTECT)
    worklocation = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    rate_offered = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    bid_open = models.DateTimeField(auto_now_add=True, null=True)
    bid_closes = models.DateTimeField('Vacancy Closes', null=True)
    offer_status = models.CharField(max_length=1, choices=STATUS, default='O')
    certification = models.ManyToManyField(Result, verbose_name='Certifications Required', blank=True)
    scope = models.TextField()
    expectations = models.TextField()
    terms = models.FileField(upload_to=BidTerms, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='City, Town or Place')

    class Meta:
        unique_together = (('enterprise','title', 'requested_by'),)

    def __str__(self):
        return '{}, {}, {}'.format(self.title, self.enterprise, self.date_entered)


class Deliverables(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    deliverable = models.TextField()

    class Meta:
        unique_together = (('scope','deliverable'),)

    def __str__(self):
        return '{}: {}'.format(self.scope, self.deliverable)


class SkillRequired(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    skills = models.ForeignKey(SkillTag, on_delete=models.PROTECT)

    class Meta:
        #unique_together = (('skill','scope'),)
        pass

    def __str__(self):
        return f'{self.scope}'


BID = (
        ('A','Accepted'),
        ('P','Pending'),
        ('R','Unsuccessful'),
        ('S','Short-listed'),
    )


class BidShortList(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    preferance_rating = models.SmallIntegerField(null=True, default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    status =  models.CharField(max_length=1, choices=BID, null=True, default='S')

    class Meta:
        unique_together = (('talent', 'scope'),)

    def __str__(self):
        return f'{self.scope} shortlist {self.talent}'


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
    #rate_accepted = models.DecimalField(max_digits=10, decimal_places=2)
    #currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    #rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    #date_completion = models.DateField()
    #date_begin = models.DateField()
    #autocompleted
    date_create = models.DateField(auto_now_add=True)
    date_complete = models.DateField(auto_now=True)
    #completed by talent
    #start_confirm = models.BooleanField()
    #rate_confirm = models.BooleanField()
    #deadline_confirm = models.BooleanField()
    #terms_accept = models.BooleanField()

    def __str__(self):
        return f'{self.talent} assigned to {self.work}'
