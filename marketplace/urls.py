from django.urls import path


from .import views

app_name = 'MarketPlace'


urlpatterns = [
    path('entrance/', views.MarketHome, name='Entrance'),
    path('vacancy/', views.VacancyView, name='Vacancy'),
    path('popup/worklocation/add/', views.WorkLocationAddPopup, name="WorkLocationAddPop"),
    path('popup/ajax/get_worklocation_id/', views.get_worklocation_id, name="AJAX_GetWorklocationID"),
    path('vacancy-deliverables/<int:pk>/', views.DeliverablesAddView, name='Deliverables'),
    path('vacancy-deliverable/<int:pk>/', views.DeliverablesAdd2View, name='Deliverables2'),
    path('vacancy-skills/<int:pk>/', views.VacancySkillsAddView, name='Skills'),
    path('vacancy-skilla/<int:pk>/', views.VacancySkillsAdd2View, name='Skillsa'),
    path('popup/skilllevel/add/', views.SkillLevelAddPopup, name="SkillLevelAddPop"),
    path('popup/ajax/get_skilllevel_id/', views.get_skilllevel_id, name="AJAX_GetSkillLevelID"),
    path('vacancy-edit/<int:pk>/', views.VacancyEditView, name="VacancyEdit"),
    path('vacancy-edit-deliverables/<int:pk>/', views.DeliverablesEditView, name='DeliverablesEdit'),
    path('vacancy-delete-deliverables/<int:pk>/', views.DeliverableDeleteView, name='DeliverablesDelete'),
    path('vacancy-delete-skill/<int:pk>/', views.SkillDeleteView, name='SkillDelete'),
    path('interviewlist/<int:vac>/<int:tlt>/', views.AddToInterviewListView, name='InterviewList'),
    path('shortlist/<int:s_list>/<int:tlt>/', views.AddToShortListView, name='ShortList'),
    path('availabillity/', views.TalentAvailabillityView, name='Availabillity'),
    path('v-detail/<int:pk>/', views.VacancyDetailView, name='VacancyDetail'),
    path('apply/<int:pk>/', views.WorkBidView, name='WorkBid'),
    path('history/', views.ApplicationHistoryView, name='History'),
    path('postview/<int:pk>/', views.VacancyPostView, name='VacancyPost'),
    path('shortlist-review/<int:slv>/', views.ShortListView, name='ShortListView'),
    path('vac-assign/<int:vac>/<int:tlt>/', views.TalentAssign, name='VacAssign'),
    path('vac-decline/<int:vac>/<int:tlt>/', views.TalentDecline, name='VacDecline'),
    path('all-vac/', views.AllPostedVacanciesView, name='AllPostedVac'),
    path('availabillity-remove/<int:avl_id>/', views.AvailabillityRemoveView, name='NotAvailable'),

]
