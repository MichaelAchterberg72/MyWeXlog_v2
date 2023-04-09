from django.urls import path

from . import views

app_name = 'Skills'

urlpatterns = [
        path('<int:skl>/detail/', views.skill_detail, name="Skill_Detail"),
        path('<int:skl>/full-detail/', views.skill_detail_full, name="Skill_Detail_Full"),
        path('skill-filter/', views.skill_form_filter_view, name="SkillFilter"),
        path('ajax-region/', views.ajax_region_field, name="AjaxRegion"),
        path('ajax-skill/', views.ajax_skill_field, name="AjaxSkill"),

]
