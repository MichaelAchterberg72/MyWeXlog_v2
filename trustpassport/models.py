from django.db import models
from django.conf import settings
from django.utils import timezone


from enterprises.models import Branch


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
