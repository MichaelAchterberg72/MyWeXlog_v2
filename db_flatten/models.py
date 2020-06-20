from django.db import models


class PhoneNumberType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type

    def clean(self):
        self.skill = self.type.proper()


class SkillTag(models.Model):
    skill = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=6, null=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['skill',]),
        ]
        #ordering = ['skill',]

    def clean(self):
        self.skill = self.skill.proper()

    def __str__(self):
        return self.skill


class LanguageList(models.Model):
    language = models.CharField(max_length=30, unique=True, null=True)

    def clean(self):
        self.language = self.language.proper()

    def __str__(self):
        return self.language
