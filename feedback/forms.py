from django import forms

from .models import FeedBack, Notices, NoticeRead, FeedBackActions


class FeedBackForm(forms.ModelForm):
    class Meta:
        model = FeedBack
        fields = ('type', 'details', 'optional_1', 'optional_2',)


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notices
        fields = ('notice_date', 'subject', 'notice',)


class NoticeReadForm(forms.ModelForm):
    class Meta:
        model = NoticeRead
        fields = ('notice_read',)


class FeedBackRespondForm(forms.ModelForm):
    class Meta:
        model = FeedBackActions
        fields = ('actions',)
