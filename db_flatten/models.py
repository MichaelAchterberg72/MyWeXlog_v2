from django.db import models

class PhoneNumberType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type
