from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum, Min, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse


from core.decorators import subscription

from db_flatten.models import SkillTag
from talenttrack.models import WorkExperience
from users.models import CustomUser
from marketplace.models import SkillRequired
from enterprises.models import Branch


@login_required()
@subscription(2)
def skill_detail(request, skl):
    skill = SkillTag.objects.get(id=skl)

    qs = CustomUser.objects.filter(workexperience__skills__id=skl,
                                          workexperience__score__gte=3,
                                          workexperience__edt=False)

    hours1 = qs.annotate(sum=Sum('workexperience__hours_worked'),
                       min=Min('workexperience__date_from'),
                       max=Max('workexperience__date_to'))
    hours = hours1[:5]
    tally = hours1.count()

    range = qs.aggregate(range_sum=Sum('workexperience__hours_worked'),
                       range_min=Min('workexperience__date_from'),
                       range_max=Max('workexperience__date_to'),
                      )
    qs_demand = Branch.objects.filter(talentrequired__skillrequired__skills__id=skl).annotate(demand_count=Count('talentrequired'))

    template = 'skills/skill_detail.html'
    context = {'hours': hours, 'skill': skill, 'range': range, 'tally': tally, 'qs_demand': qs_demand}
    return render (request, template, context)
