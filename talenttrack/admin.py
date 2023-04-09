from django.contrib import admin

from .models import (Achievements, Awards, ClassMates, Course, CourseType,
                     Designation, EmailRemindValidate, Lecturer,
                     LicenseCertification, Publications, Result, Superior,
                     Topic, WorkClient, WorkCollaborator, WorkColleague,
                     WorkExperience)


@admin.register(EmailRemindValidate)
class EmailRemindValidateAdmin(admin.ModelAdmin):
    search_fields = ['sender__alias']


@admin.register(LicenseCertification)
class LicenseCertificationAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(Achievements)
class AchievementsAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(Awards)
class AwardsAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(Publications)
class PublicationsAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(WorkCollaborator)
class WorkCollaboratorAdmin(admin.ModelAdmin):
    search_fields = ['collaborator_name__alias', 'experience__slug', 'experience__talent__alias']

@admin.register(Superior)
class SuperiorAdmin(admin.ModelAdmin):
    search_fields = ['superior_name__alias', 'experience__slug', 'experience__talent__alias']

@admin.register(WorkColleague)
class WorkColleagueAdmin(admin.ModelAdmin):
    search_fields = ['colleague_name__alias', 'experience__slug', 'experience__talent__alias']

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    filter_horizontal = ['skills',]
    search_fields = ['talent__alias', 'slug']

@admin.register(WorkClient)
class WorkClientAdmin(admin.ModelAdmin):
    search_fields = ['client_name__alias', 'experience__slug', 'experience__talent__alias']

@admin.register(ClassMates)
class ClassMatesAdmin(admin.ModelAdmin):
    search_fields = ['colleague__alias', 'education__slug', 'education__talent__alias']

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    search_fields = ['lecturer__alias', 'education__slug', 'education__talent__alias']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ['topic']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    pass

@admin.register(CourseType)
class CourseTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ['name', 'company__ename']
