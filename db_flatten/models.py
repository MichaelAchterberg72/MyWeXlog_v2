from django.db import models


class PhoneNumberType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type

    def clean(self):
        self.skill = self.type.capitalize()


class SkillTag(models.Model):
    skill = models.CharField(max_length=60, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['skill',]),
        ]
        #ordering = ['skill',]

    def clean(self):
        self.skill = self.skill.capitalize()

    def __str__(self):
        return self.skill
