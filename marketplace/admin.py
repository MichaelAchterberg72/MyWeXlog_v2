from django.contrib import admin

from .models import (BidInterviewList, BidShortList, DeclineAssignment,
                     Deliverables, SkillLevel, SkillRequired,
                     TalentAvailabillity, TalentRate, TalentRequired,
                     VacancyRate, VacancyViewed, WorkBid, WorkIssuedTo,
                     WorkLocation)


@admin.register(TalentRate)
class TalentRateAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'vacancy__ref_no']


@admin.register(VacancyRate)
class VacancyRateAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'vacancy__ref_no']


@admin.register(DeclineAssignment)
class DeclineAssignmentAdmin(admin.ModelAdmin):
    pass


@admin.register(BidInterviewList)
class BidInterviewListAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'scope__ref_mo']


@admin.register(BidShortList)
class BidShortListAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'scope__ref_no']

@admin.register(WorkIssuedTo)
class WorkIssuedToAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'work__ref_no']

@admin.register(TalentAvailabillity)
class TalentAvailabillityAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']

@admin.register(WorkBid)
class WorkBidAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'work__ref_no']

@admin.register(SkillRequired)
class SkillRequiredAdmin(admin.ModelAdmin):
    search_fields = ['scope__ref_no']

@admin.register(SkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    pass

@admin.register(Deliverables)
class DeliverablesAdmin(admin.ModelAdmin):
    search_fields = ['scope__ref_no']

@admin.register(WorkLocation)
class WorkLocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'type']

@admin.register(VacancyViewed)
class VacancyViewedAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'vacancy__ref_no', 'vacancy__companybranch__company__ename']

@admin.register(TalentRequired)
class TalentRequiredAdmin(admin.ModelAdmin):
    search_fields = ['title', 'ref_no', 'companybranch__company__ename']
