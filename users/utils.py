from Profile.models import BriefCareerHistory

def GetInfo(record):
    qs = BriefCareerHistory.objects.filter(talent=record)
    print(qs)
    current = qs.latest('date_captured')
    title = [current.companybranch.capitalize(), current.designation.capitalize()]
    print(current)
