from django.db import models
from django.conf import settings
from django.utils import timezone
from Profile.utils import create_code9

from Profile.utils import create_code9


class FeedBack(models.Model):
    OPTS = (
        ('X','Select'),
        ('B','Bug'),
        ('T','Comment'),
        ('S','Suggestion'),
        ('F','Request Feature'),
        ('C','Complaint'),
        ('M','Compliance'),
        ('M','I Got A Job'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_captured = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=OPTS, default='X')
    details = models.TextField()
    optional_1 = models.TextField('What do you like about MyWeXlog', blank=True, null=True)
    optional_2 = models.TextField('What don\'t you like about MyWeXlog', blank=True, null=True)
    responded = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, null=True, unique=True, blank=True)

    def __str__(self):
        return f'{self.talent.alias} on {self.date_captured}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(FeedBack, self).save(*args, **kwargs)

#admin mangement of feedback comments
class FeedBackActions(models.Model):
    item = models.ForeignKey(FeedBack, on_delete=models.PROTECT)
    review_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_reviewed = models.DateTimeField(auto_now_add=True)
    actions = models.TextField(null=True)

    def __str__(self):
        return f'{self.item} by {self.review_by.alias}'


class Notices(models.Model):
    notice_date = models.DateTimeField()
    subject = models.CharField(max_length=200, null=True)
    notice = models.TextField(null=True)
    slug = models.SlugField(max_length=10, blank=True, null=True, unique=True)

    def __str__(self):
        return '{}, {}'.format(self.notice_date, self.subject)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Notices, self).save(*args, **kwargs)


class NoticeRead(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notice = models.ForeignKey(Notices, on_delete=models.PROTECT, null=True)
    date_read = models.DateTimeField(auto_now_add=True)
    notice_read = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f'{self.notice} {self.talent}'
