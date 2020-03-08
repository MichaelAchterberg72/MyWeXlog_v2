from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from Profile.utils import create_code9

from enterprises.models import Branch
from locations.models import Currency, City
from db_flatten.models import SkillTag
from talenttrack.models import Result

#This is the table that specifies the work configeration (Freelance, Remote Freelence, Consultant, Contractor, Employee, FIFO)
class WorkLocation(models.Model):
    type = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ['type']

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
        (1,'Beginner'),
        (2,'Junior'),
        (3,'Intermediate'),
        (4,'Senior'),
        (5,'Lead'),
    )

    level = models.IntegerField(choices=LEVEL, unique=True)
    min_hours = models.IntegerField()#Read max_hours
    description = models.TextField()

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
    date_entered = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=250)
    ref_no = models.CharField(max_length=10, unique=True, null=True)#SlugField
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
        return f'{self.title}, {self.enterprise}'


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
        unique_together = (('skills','scope'),)
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
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='Shortlisted')
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    preferance_rating = models.SmallIntegerField(null=True, default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    status =  models.CharField(max_length=1, choices=BID, null=True, default='S')
    slug = models.SlugField(max_length=50, null=True, blank=True, unique=True)

    class Meta:
        unique_together = (('talent', 'scope'),)

    def __str__(self):
        return f'{self.scope} shortlist {self.talent}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(BidShortList, self).save(*args, **kwargs)

class BidInterviewList(models.Model):
    OC = (
        ('P','Pending'),
        ('S','Suitable'),
        ('N','Not Suitable'),
        ('D','Candidate Declined'),
    )
    RSP = (
        ('P','Interview Pending'),
        ('A','Accept Interview'),
        ('D','Decline Interview'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='Interviewed')
    scope = models.ForeignKey(TalentRequired, on_delete=models.CASCADE)
    date_listed = models.DateTimeField(auto_now_add=True)
    outcome = models.CharField(max_length=1, choices=OC, default='P')
    tlt_decline_reason = models.ForeignKey('DeclineAssignment', on_delete=models.PROTECT, null=True)
    comments_tlt = models.TextField(null=True)
    tlt_response = models.CharField(max_length=1, choices=RSP, default='P')
    tlt_reponded = models.DateTimeField(null=True)
    tlt_intcomplete = models.BooleanField(default=False)
    emp_intcomplete = models.BooleanField(default=False)
    comments_emp = models.TextField(null=True)
    slug = models.SlugField(max_length=50, null=True, blank=True, unique=True)

    class Meta:
        unique_together = (('talent', 'scope'),)

    def __str__(self):
        return f'{self.scope}, {self.talent}, {self.get_outcome_display()}'

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

    class Meta:
        unique_together = (('talent', 'work'),)

    def __str__(self):
        return'{}: {}'.format(self.work, self.talent)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(WorkBid, self).save(*args, **kwargs)


class TalentAvailabillity(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    hours_available = models.IntegerField()
    unit = models.CharField(max_length=1, choices=UNIT, default='D')

    def __str__(self):
        return '{} - {} {} ({})'.format(self.talent, self.hours_available, self.get_unit_display, self.date_to)

#Reasons: No Available Capacity, Not Looking for work, Not suited to vacancy, Rate too low, Company Reputation, other (comment)
class DeclineAssignment(models.Model):
    option = models.CharField(max_length = 200, unique=True)

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
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Successful_talent')
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
    assignment_complete_tlt = models.BooleanField(default=False)
    assignment_complete_emp = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, null=True, unique=True)

    class Meta:
        unique_together = (('talent', 'work'),)

    def __str__(self):
        return f'{self.talent} assigned to {self.work}'

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
    rate_1 = models.SmallIntegerField('Talent Performance', choices=OPNS, default=3)
    rate_2 = models.SmallIntegerField('Work Performance', choices=OPNS, default=3)
    rate_3 = models.SmallIntegerField('Would you hire this person again?', choices=OPNS)
    date_rating = models.DateField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    complete = models.BooleanField(null=True)
    slug = models.SlugField(max_length=50, null=True, unique=True)

    def __str__(self):
        return f'Rating for {self.talent} on {self.vacancy}'

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
    vacancy = models.ForeignKey(TalentRequired, on_delete=models.PROTECT)
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    rate_1 = models.SmallIntegerField('Employer Performance', choices=OPNS, default=3)
    rate_2 = models.SmallIntegerField('Payment Receipt', choices=OPNS, default=3)
    rate_3 = models.SmallIntegerField('Would you work for this employer again?', choices=OPNS, default=3)
    date_rating = models.DateField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    complete = models.BooleanField(null=True)
    slug = models.SlugField(max_length=50, null=True, unique=True)

    def __str__(self):
        return f'Rating for {self.vacancy} by {self.talent}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(TalentRate, self).save(*args, **kwargs)
