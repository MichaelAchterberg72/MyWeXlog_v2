from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email
