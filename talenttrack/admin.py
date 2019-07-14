from django.contrib import admin

from .models import (
    Topic, Result, CourseType, Course, Education, Lecturer, ClassMates, WorkClient, WorkExperience, WorkColleague, Superior, WorkCollaborator, PreLoggedExperience, PreColleague, Designation
    )

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    pass

@admin.register(PreColleague)
class PreColleagueAdmin(admin.ModelAdmin):
    pass

@admin.register(PreLoggedExperience)
class PreLoggedExperienceAdmin(admin.ModelAdmin):
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

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    pass
