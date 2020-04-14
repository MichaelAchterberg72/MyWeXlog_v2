from django.db import models
from django.conf import settings
from django.utils import timezone
from Profile.utils import create_code9


class FeedBack(models.Model):
    OPTS = (
        ('X','Select'),
        ('T','Comment'),
        ('S','Suggestion'),
        ('F','Request Feature'),
        ('C','Complaint'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_captured = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=OPTS, default='X')
    details = models.TextField()
    optional_1 = models.TextField('What do you like about MyWexLog', blank=True, null=True)
    optional_2 = models.TextField('What don\'t you like about MyWexLog', blank=True, null=True)

    def __str__(self):
        return f'{self.talent.alias} on {self.date_captured}'

#admin mangement of feedback comments
class FeedBackActions(models.Model):
    item = models.ForeignKey(FeedBack, on_delete=models.PROTECT)
    review_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_reviewed = models.DateTimeField(auto_now_add=True)
    actions = models.TextField(null=True)

    def __str__(self):
        return f'{self.item} by {self.review_by.alias}'
