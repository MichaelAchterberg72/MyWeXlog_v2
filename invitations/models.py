from django.db import models
from django.conf import settings


from enterprises.models import Branch


class Invitation(models.Model):
    WREL = (
        ('LR','Lecturer'),
        ('CM','Class Mate'),
        ('WC','Colleague'),
        ('WS','Superior'),
        ('WL','Collaborator'),
        ('WT','Client'),
        ('PC','Colleague'),
        ('AF','Acqaintance / Friend'),
    )
    name = models.CharField('First Name', max_length=45)
    surname = models.CharField('Surname', max_length=45)
    worked_for = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Who did they work for at the time', null=True)
    relationship = models.CharField(max_length=2, choices=WREL, null=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(unique=True)
    date_invited = models.DateTimeField(auto_now_add=True)
    accpeted = models.BooleanField(null=True, default=False)
    date_accepted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.surname} invited by {self.invited_by} on {self.date_invited} - {self.date_accepted}"
