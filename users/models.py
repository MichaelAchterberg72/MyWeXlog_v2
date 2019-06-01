from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

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
    subscription = models.IntegerField(choices=PKG, default=0)
    middle_name = models.CharField(max_length=60, null=True)
    permission = models.IntegerField(choices=COMPANY, default=1)

    objects = CustomUserManager()

    def __str__(self):
        return self.email
