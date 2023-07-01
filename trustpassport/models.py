from django.conf import settings
from django.db import models
from django.utils import timezone

from enterprises.models import Branch

from utils.utils import update_model

from django.contrib.auth import get_user_model

User = get_user_model()


SCORE = (
    (1,'One'),
    (2,'Two'),
    (3,'Three'),
    (4,'Four'),
    (5,'Five'),
)


class EnterprisePassport(models.Model):
    score_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='enterprise_scorer', null=True)
    enterprise = models.ForeignKey(Branch, on_delete=models.PROTECT)
    date_score = models.DateField(auto_now_add=True)
    payment_text = models.TextField('Comment', blank=True, null=True)
    payment_score = models.IntegerField('Score', choices=SCORE, default=3)
    cooperation_text = models.TextField('Comment', blank=True, null=True)
    cooperation_score = models.IntegerField('Score', choices=SCORE, default=3)
    treatment_text = models.TextField('Comment', blank=True, null=True)
    treatment_score = models.IntegerField('Score', choices=SCORE, default=3)
    information_text = models.TextField('Comment', blank=True, null=True)
    information_score = models.IntegerField('Score', choices=SCORE, default=3)
    engagement_text = models.TextField('Comment', blank=True, null=True)
    engagement_score = models.IntegerField('Score', choices=SCORE, default=3)
    accuracy_text = models.TextField('Comment', blank=True, null=True)
    accuracy_score = models.IntegerField('Score', choices=SCORE, default=3)

    class Meta:
        unique_together = (('score_by','enterprise','date_score'),)

    def __str__(self):
        return '{} scored by {} on {}'.format(self.enterprise, self.score_by, self.score_date)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        score_by = kwargs.pop('score_by', None)
        enterprise = kwargs.pop('enterprise', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if score_by:
            instance.score_by = User.objects.get(alias=score_by.alias)
            
        if enterprise:
            instance.enterprise = Branch.update_or_create(slug=enterprise.slug, **enterprise)
        
        instance.save()
            
        return instance


class TalentPassport(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    score_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='talent_scorer')
    date_score = models.DateField(auto_now_add=True)
    q1_text = models.TextField('Comment', blank=True, null=True)
    q1_score = models.IntegerField('Score', choices=SCORE, default=3)
    q2_text = models.TextField('Comment', blank=True, null=True)
    q2_score = models.IntegerField('Score', choices=SCORE, default=3)
    q3_text = models.TextField('Comment', blank=True, null=True)
    q3_score = models.IntegerField('Score', choices=SCORE, default=3)
    q4_text = models.TextField('Comment', blank=True, null=True)
    q4_score = models.IntegerField('Score', choices=SCORE, default=3)
    q5_text = models.TextField('Comment', blank=True, null=True)
    q5_score = models.IntegerField('Score', choices=SCORE, default=3)
    q6_text = models.TextField('Comment', blank=True, null=True)
    q6_score = models.IntegerField('Score', choices=SCORE, default=3)
    q7_text = models.TextField('Comment', blank=True, null=True)
    q7_score = models.IntegerField('Score', choices=SCORE, default=3)
    q8_text = models.TextField('Comment', blank=True, null=True)
    q8_score = models.IntegerField('Score', choices=SCORE, default=3)
    q9_text = models.TextField('Comment', blank=True, null=True)
    q9_score = models.IntegerField('Score', choices=SCORE, default=3)
    q10_text = models.TextField('Comment', blank=True, null=True)
    q10_score = models.IntegerField('Score', choices=SCORE, default=3)
    q12_text = models.TextField('Comment', blank=True, null=True)
    q12_score = models.IntegerField('Score', choices=SCORE, default=3)
    q13_text = models.TextField('Comment', blank=True, null=True)
    q13_score = models.IntegerField('Score', choices=SCORE, default=3)
    q14_text = models.TextField('Comment', blank=True, null=True)
    q14_score = models.IntegerField('Score', choices=SCORE, default=3)
    q15_text = models.TextField('Comment', blank=True, null=True)
    q15_score = models.IntegerField('Score', choices=SCORE, default=3)

    class Meta:
        unique_together = (('score_by','talent','date_score'),)

    def __str__(self):
        return '{} scored by {} on {}'.format(self.talent, self.score_by, self.score_date)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        score_by = kwargs.pop('score_by', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if score_by:
            instance.score_by = User.objects.get(alias=score_by.alias)
        
        instance.save()
            
        return instance
