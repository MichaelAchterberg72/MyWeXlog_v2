from django.db import models

from WeXlog.utils import update_model


class PhoneNumberType(models.Model):
    type = models.CharField(max_length=50, unique=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        return instance

    def __str__(self):
        return self.type

    def clean(self):
        self.type = self.type.title()


class SkillTag(models.Model):
    skill = models.CharField(max_length=30, unique=True)
    code = models.CharField(max_length=6, null=True, unique=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        return instance

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
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        return instance

    def clean(self):
        self.language = self.language.title()

    def __str__(self):
        return self.language
