from django.db import models

from WeXlog.utils import update_model


class PhoneNumberType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type

    def clean(self):
        self.type = self.type.title()


class SkillTag(models.Model):
    skill = models.CharField(max_length=30, unique=True)
    code = models.CharField(max_length=6, null=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['skill',]),
        ]

    def clean(self):
        self.skill = self.skill.title()

    def __str__(self):
        return self.skill


class LanguageList(models.Model):
    language = models.CharField(max_length=30, unique=True, null=True)

    def clean(self):
        self.language = self.language.title()

    def __str__(self):
        return self.language
