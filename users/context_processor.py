from WeXlog import app_config
from django.db.models import Count, Sum, F, Q

from .models import CustomUserSettings
from feedback.models import NoticeRead
from talenttrack.models import (
        Lecturer, ClassMates, WorkColleague, Superior, WorkCollaborator,  WorkClient,
)


def theme(request):
    if request.user.is_authenticated:
        theme = CustomUserSettings.objects.get(talent=request.user).theme
    else:
        theme = 0

    return {'theme': theme}


def notification_count(request):
    if request.user.is_authenticated:
        notification = NoticeRead.objects.filter(Q(talent=request.user) & Q(notice_read=False)).count()
    else:
        notification = 0

    return {'notification': notification}


def confirm_count(request):
    if request.user.is_authenticated:
        if app_config.switch_confirmation == 'off':
            wf1 = Lecturer.objects.filter(confirm__exact='S').count()
            cm1 = ClassMates.objects.filter(confirm__exact='S').count()
            wk1 = WorkColleague.objects.filter(confirm__exact='S').count()
            spr1 = Superior.objects.filter(confirm__exact='S').count()
            wclr1 = WorkCollaborator.objects.filter(confirm__exact='S').count()
            wc1 = WorkClient.objects.filter(confirm__exact='S').count()
        else:
            talent = request.user
            wf1 = Lecturer.objects.filter(Q(lecturer=talent) & Q(confirm__exact='S')).count()
            cm1 = ClassMates.objects.filter(Q(colleague=talent) & Q(confirm__exact='S')).count()
            wk1 = WorkColleague.objects.filter(Q(colleague_name=talent) & Q(confirm__exact='S')).count()
            spr1 = Superior.objects.filter(Q(superior_name=talent) & Q(confirm__exact='S')).count()
            wclr1 = WorkCollaborator.objects.filter(Q(collaborator_name=talent) & Q(confirm__exact='S')).count()
            wc1 = WorkClient.objects.filter(Q(client_name=talent) & Q(confirm__exact='S')).count()

        verifications = wf1 + cm1 + wk1 + spr1 + wclr1 + wc1
    else:
        verifications = 0

    return {'verifications': verifications}
