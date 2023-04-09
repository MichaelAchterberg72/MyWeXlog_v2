from django.db.models import Count, F, Q, Sum
from django.utils import timezone

from talenttrack.models import PreLoggedExperience, WorkExperience

from .models import (Deliverables, SkillRequired, TalentAvailabillity,
                     TalentRequired, WorkBid)


def SuitedVacancies(talent):
    #Code for stacked lookup for talent's skills
    my_logged = WorkExperience.objects.filter(talent=talent).aggregate(myl=Sum('hours_worked'))
    my_prelogged = PreLoggedExperience.objects.filter(talent=talent).aggregate(mypl=Sum('hours_worked'))

    myli = my_logged.get('myl')
    mypli = my_prelogged.get('mypl')

    mye = myli+mypli

    req_experience = TalentRequired.objects.filter(Q(offer_status__iexact='O') & Q(experience_level__min_hours__lte=mye)).values_list('id', flat=True)

    skill_have = WorkExperience.objects.filter(talent=talent).values_list('skills', flat=True)

    match = []

    for key in req_experience:
        skill_list = SkillRequired.objects.filter(id=key).values_list('skill', flat=True).distinct()

        for sk in skill_list:
            if sk in skill_have:
                match.append(sk)

    for item in match:
        display = SkillRequired.objects.filter(
                Q(skill__in=[item])
                & Q(scope__bid_closes__gte=timezone.now())
                & Q(scope__offer_status__iexact='O')
                ).distinct().prefetch_related('scope')
