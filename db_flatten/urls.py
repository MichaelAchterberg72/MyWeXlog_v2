from django.urls import path

from . import views

app_name = 'Flatten'

urlpatterns = [
    path('popup/add/', views.PhoneNumberTypeAddPopup, name="TypeAddPop"),
    path('popup/ajax/get_numbertype_id/', views.get_numbertype_id, name="AJAX_GetNumberTypeID"),
    path('popup/skill/add/', views.SkillAddPopup, name="SkillAddPop"),
    path('popup/ajax/get_skill_id/', views.get_skill_id, name="AJAX_GetSkillID"),
    path('taglist/', views.ListTagsView, name="ListTags"),
]
