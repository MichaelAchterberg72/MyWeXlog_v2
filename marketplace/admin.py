from django.contrib import admin

from .models import (BidInterviewList, BidShortList, DeclineAssignment,
                     Deliverables, SkillLevel, SkillRequired,
                     TalentAvailabillity, TalentRate, TalentRequired,
                     VacancyRate, VacancyViewed, WorkBid, WorkIssuedTo,
                     WorkLocation)


@admin.register(TalentRate)
class TalentRateAdmin(admin.ModelAdmin):
    pass


@admin.register(VacancyRate)
class VacancyRateAdmin(admin.ModelAdmin):
    pass


@admin.register(DeclineAssignment)
class DeclineAssignmentAdmin(admin.ModelAdmin):
    pass


@admin.register(BidInterviewList)
class BidInterviewListAdmin(admin.ModelAdmin):
    pass


@admin.register(BidShortList)
class BidShortListAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkIssuedTo)
class WorkIssuedToAdmin(admin.ModelAdmin):
    pass

@admin.register(TalentAvailabillity)
class TalentAvailabillityAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkBid)
class WorkBidAdmin(admin.ModelAdmin):
    pass

@admin.register(SkillRequired)
class SkillRequiredAdmin(admin.ModelAdmin):
    pass

@admin.register(SkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    pass

@admin.register(Deliverables)
class DeliverablesAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkLocation)
class WorkLocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'type']

@admin.register(VacancyViewed)
class VacancyViewedAdmin(admin.ModelAdmin):
    pass

@admin.register(TalentRequired)
class TalentRequiredAdmin(admin.ModelAdmin):
    pass
