from django.contrib import admin

from .models import (
    WorkLocation, TalentRequired, Deliverables, SkillLevel, SkillRequired, WorkBid, TalentAvailabillity, WorkIssuedTo, BidShortList,
    )


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
    pass

@admin.register(TalentRequired)
class TalentRequiredAdmin(admin.ModelAdmin):
    pass
