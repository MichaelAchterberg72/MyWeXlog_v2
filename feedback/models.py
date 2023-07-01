from django.conf import settings
from django.db import models
from django.utils import timezone

from Profile.utils import create_code9

from utils.utils import update_model

from django.contrib.auth import get_user_model

User = get_user_model()


class FeedBack(models.Model):
    OPTS = (
        ('X','Select'),
        ('B','Bug'),
        ('T','Comment'),
        ('S','Suggestion'),
        ('F','Request Feature'),
        ('C','Complaint'),
        ('M','Compliance'),
        ('M','I Got A Job'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_captured = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=OPTS, default='X')
    details = models.TextField()
    optional_1 = models.TextField('What do you like about MyWeXlog', blank=True, null=True)
    optional_2 = models.TextField('What don\'t you like about MyWeXlog', blank=True, null=True)
    responded = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, null=True, unique=True, blank=True)
    
    def __str__(self):
        return f'{self.talent.alias} on {self.date_captured}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(FeedBack, self).save(*args, **kwargs)

    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
        
        instance.save()
            
        return instance
    

#admin mangement of feedback comments
class FeedBackActions(models.Model):
    item = models.ForeignKey(FeedBack, on_delete=models.PROTECT)
    review_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_reviewed = models.DateTimeField(auto_now_add=True)
    actions = models.TextField(null=True)
    
    def __str__(self):
        return f'{self.item} by {self.review_by.alias}'
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
        
        item = kwargs.pop('item', None)
        review_by = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if item:
            instance.item = FeedBack.update_or_create(slug=item.slug, **item)
        
        if review_by:
            instance.review_by = User.objects.get(alias=review_by.alias)
        
        instance.save()
            
        return instance


class Notices(models.Model):
    notice_date = models.DateTimeField()
    subject = models.CharField(max_length=200, null=True)
    notice = models.TextField(null=True)
    slug = models.SlugField(max_length=10, blank=True, null=True, unique=True)
    
    def __str__(self):
        return '{}, {}'.format(self.notice_date, self.subject)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Notices, self).save(*args, **kwargs)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        return instance


class NoticeRead(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notice = models.ForeignKey(Notices, on_delete=models.PROTECT, null=True)
    date_read = models.DateTimeField(auto_now_add=True)
    notice_read = models.BooleanField(default=False, null=True)
    
    def __str__(self):
        return f'{self.notice} {self.talent}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        notice = kwargs.pop('notice', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if notice:
            instance.notice = Notices.update_or_create(slug=notice.slug, **notice)
            
        instance.save()
            
        return instance