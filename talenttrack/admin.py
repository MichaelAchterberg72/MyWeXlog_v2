from django.contrib import admin

from .models import (Achievements, Awards, ClassMates, Course, CourseType,
                     Designation, EmailRemindValidate, Lecturer,
                     LicenseCertification, Publications, Result, Superior,
                     Topic, WorkClient, WorkCollaborator, WorkColleague,
                     WorkExperience)


@admin.register(EmailRemindValidate)
class EmailRemindValidateAdmin(admin.ModelAdmin):
    pass


@admin.register(LicenseCertification)
class LicenseCertificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Achievements)
class AchievementsAdmin(admin.ModelAdmin):
    pass


@admin.register(Awards)
class AwardsAdmin(admin.ModelAdmin):
    pass


@admin.register(Publications)
class PublicationsAdmin(admin.ModelAdmin):
    pass


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkCollaborator)
class WorkCollaboratorAdmin(admin.ModelAdmin):
    pass

@admin.register(Superior)
class SuperiorAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkColleague)
class WorkColleagueAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    filter_horizontal = ('skills',)

@admin.register(WorkClient)
class WorkClientAdmin(admin.ModelAdmin):
    pass

@admin.register(ClassMates)
class ClassMatesAdmin(admin.ModelAdmin):
    pass

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    pass

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    pass

@admin.register(CourseType)
class CourseTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass
