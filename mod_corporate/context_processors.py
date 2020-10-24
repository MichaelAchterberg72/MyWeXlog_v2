from .models import (
    CorporateStaff, OrgStructure
    )

def corp_selection(request):
    usr = request.user
    corp = CorporateStaff.objects.filter(talent=usr)

    corporates_link={}
    for item in corp:
        cor = item.corporate.slug
        branch = item.corporate.companybranch
        corporates_link[item]={'cor': cor, 'branch': branch}

    return {'cor': corporates_link}
