from django.db import models
from django.conf import settings
from django.utils import timezone


from enterprises.models import Branch
from locations.models import Currency
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


class TalentRequired(models.Model):
    RATE_UNIT = (
        ('H','per Hour'),
        ('D','per Day'),
        ('M','per Month'),
        ('L','Lump Sum'),
    )

    UNIT = (
        ('O','Once Off'),
        ('M','per Month'),
        ('W','per Week'),
        ('S','Short Term Contract'),
        ('A','As and When Contract'),
    )

    STATUS = (
        ('O','Open'),
        ('C','Closed'),
    )
    date_entered = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=250)
    enterprise = models.ForeignKey(Branch, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_deadline = models.DateField('Work to be completed by')
    hours_required = models.IntegerField()
    unit = models.CharField(max_length=1, choices=UNIT)
    worklocation = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    rate_offered = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    bid_open = models.DateTimeField(default=timezone.now)
    bid_closes = models.DateTimeField()
    offer_status = models.CharField(max_length=1, choices=STATUS, default='O')
    certifications = models.ManyToManyField(Result, verbose_name='Certifications Required')
    scope = models.TextField()
    expectations = models.TextField()
    terms = models.FileField(upload_to=BidTerms)

    class Meta:
        unique_together = (('date_entered','enterprise','title', 'requested_by'),)

    def __str__(self):
        return '{}, {}, {}'.format(self.title, self.enterprise, self.date)


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
    description = models.TextField()

    def __str__(self):
        return self.level


class SkillRequired(models.Model):
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    skill = models.ForeignKey(SkillTag, on_delete=models.PROTECT)
    experience_level = models.ForeignKey(SkillLevel, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('skill','experience_level'),)

    def __str__(self):
        return self.scope
