from django.db import models

class PhoneNumberType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type

class SkillTag(models.Model):
    skill = models.CharField(max_length=60, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['skill',]),
        ]

    def __str__(self):
        return self.skill
