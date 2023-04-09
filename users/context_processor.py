from django.db.models import Count, F, Q, Sum

from feedback.models import NoticeRead
from marketplace.models import (BidInterviewList, BidShortList, TalentRate,
                                TalentRequired, VacancyRate, WorkBid,
                                WorkIssuedTo)
from talenttrack.models import (ClassMates, Lecturer, Superior, WorkClient,
                                WorkCollaborator, WorkColleague)
from intmessages.models import ChatRoomMembers, Message, MessageRead

from WeXlog import app_config

from .models import CustomUserSettings


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

        if wf1 + cm1 + wk1 + spr1 + wclr1 + wc1 == None:
            verifications = 0
        else:
            verifications = wf1 + cm1 + wk1 + spr1 + wclr1 + wc1
    else:
        verifications = 0

    return {'verifications': verifications}

def employer_interviews_count(request):
    if request.user.is_authenticated:
        talent = request.user
        interview_qs = BidInterviewList.objects.all().select_related('scope')
        interviews_emp = interview_qs.filter(Q(scope__requested_by=talent) & Q(emp_intcomplete=False))
        interviews_emp_count = interviews_emp.count()
    else:
        interviews_emp_count = 0

    return {'interviews_emp_count': interviews_emp_count}


def talent_interviews_count(request):
    if request.user.is_authenticated:
        talent = request.user
        interview_qs = BidInterviewList.objects.all().select_related('scope')
        interviews_tlt = interview_qs.filter(Q(talent=talent) & Q(tlt_intcomplete=False) & ~Q(tlt_response='R'))
        interviews_tlt_count = interviews_tlt.count()
    else:
        interviews_tlt_count = 0

    return {'interviews_tlt_count': interviews_tlt_count}


def employer_assignment_count(request):
    if request.user.is_authenticated:
        talent = request.user
        assigned_emp = WorkIssuedTo.objects.filter(Q(work__requested_by=talent) & Q(assignment_complete_emp=False))
        assigned_emp_count = assigned_emp.count()
    else:
        assigned_emp_count = 0

    return {'assigned_emp_count': assigned_emp_count}


def talent_assignment_count(request):
    if request.user.is_authenticated:
        talent = request.user
        assigned_tlt_qs = WorkIssuedTo.objects.filter(Q(talent=talent))
        assigned_tlt = assigned_tlt_qs.filter(Q(tlt_response='P') | Q(tlt_response='C'))
        assigned_tlt_count = assigned_tlt.count()
    else:
        assigned_tlt_count = 0

    return {'assigned_tlt_count': assigned_tlt_count}


def chat_group_unread_messages_count(request):
    if request.user.is_authenticated:
        talent = request.user
        user_rooms = ChatRoomMembers.objects.filter(talent=talent).values_list('chat_group__slug', flat=True).distinct()
        chat_group_messages = MessageRead.objects.filter(Q(chat_group__slug__in=user_rooms) & Q(message_read=False))
        chat_group_unread_messages_count = chat_group_messages.count()
    else:
        chat_group_unread_messages_count = 0

    return {'chat_group_unread_messages_count': chat_group_unread_messages_count}


def total_notification_count(request):
    if request.user.is_authenticated:
        talent = request.user
        if app_config.switch_confirmation == 'off':
            wf1 = Lecturer.objects.filter(confirm__exact='S').count()
            cm1 = ClassMates.objects.filter(confirm__exact='S').count()
            wk1 = WorkColleague.objects.filter(confirm__exact='S').count()
            spr1 = Superior.objects.filter(confirm__exact='S').count()
            wclr1 = WorkCollaborator.objects.filter(confirm__exact='S').count()
            wc1 = WorkClient.objects.filter(confirm__exact='S').count()
        else:
            wf1 = Lecturer.objects.filter(Q(lecturer=talent) & Q(confirm__exact='S')).count()
            cm1 = ClassMates.objects.filter(Q(colleague=talent) & Q(confirm__exact='S')).count()
            wk1 = WorkColleague.objects.filter(Q(colleague_name=talent) & Q(confirm__exact='S')).count()
            spr1 = Superior.objects.filter(Q(superior_name=talent) & Q(confirm__exact='S')).count()
            wclr1 = WorkCollaborator.objects.filter(Q(collaborator_name=talent) & Q(confirm__exact='S')).count()
            wc1 = WorkClient.objects.filter(Q(client_name=talent) & Q(confirm__exact='S')).count()

        verifications = wf1 + cm1 + wk1 + spr1 + wclr1 + wc1


        interview_qs = BidInterviewList.objects.all().select_related('scope')
        interviews_emp = interview_qs.filter(Q(scope__requested_by=talent) & Q(emp_intcomplete=False))
        interviews_emp_count = interviews_emp.count()

        interview_qs = BidInterviewList.objects.all().select_related('scope')
        interviews_tlt = interview_qs.filter(Q(talent=talent) & Q(tlt_intcomplete=False) & ~Q(tlt_response='R'))
        interviews_tlt_count = interviews_tlt.count()

        assigned_emp = WorkIssuedTo.objects.filter(Q(work__requested_by=talent) & Q(assignment_complete_emp=False))
        assigned_emp_count = assigned_emp.count()

        assigned_tlt_qs = WorkIssuedTo.objects.filter(Q(talent=talent))
        assigned_tlt = assigned_tlt_qs.filter(Q(tlt_response='P') | Q(tlt_response='C'))
        assigned_tlt_count = assigned_tlt.count()

        total_notification_count = verifications + interviews_emp_count + interviews_tlt_count + assigned_emp_count + assigned_tlt_count
    else:
        total_notification_count = 0

    return {'total_notification_count': total_notification_count}
