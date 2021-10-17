from django.urls import path

from . import views

app_name = 'Skills'

urlpatterns = [
        path('<int:skl>/detail/', views.skill_detail, name="Skill_Detail"),
        path('<int:skl>/full-detail/', views.skill_detail_full, name="Skill_Detail_Full"),

]
