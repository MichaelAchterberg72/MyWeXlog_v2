from django.urls import path


from .import views

app_name = 'MarketPlace'


urlpatterns = [
    path('entrance/', views.MarketHome, name='Entrance'),
    path('vacancy/', views.VacancyView, name='Vacancy'),
    path('popup/worklocation/add/', views.WorkLocationAddPopup, name="WorkLocationAddPop"),
    path('popup/ajax/get_worklocation_id/', views.get_worklocation_id, name="AJAX_GetWorklocationID"),
    path('vacancy-deliverables/<int:pk>/', views.DeliverablesAddView, name='Deliverables'),
    path('vacancy-skills/<int:pk>/', views.VacancySkillsAddView, name='Skills'),
    path('popup/skilllevel/add/', views.SkillLevelAddPopup, name="SkillLevelAddPop"),
    path('popup/ajax/get_skilllevel_id/', views.get_skilllevel_id, name="AJAX_GetSkillLevelID"),
]
