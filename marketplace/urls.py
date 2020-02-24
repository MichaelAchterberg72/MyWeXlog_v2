from django.urls import path


from .import views

app_name = 'MarketPlace'


urlpatterns = [
    path('entrance/', views.MarketHome, name='Entrance'),
    path('vacancy/', views.VacancyView, name='Vacancy'),
    path('popup/worklocation/add/', views.WorkLocationAddPopup, name="WorkLocationAddPop"),
    path('popup/ajax/get_worklocation_id/', views.get_worklocation_id, name="AJAX_GetWorklocationID"),
    path('vacancy-deliverables/<slug:vac>/', views.DeliverablesAddView, name='Deliverables'),
    path('vacancy-deliverable/<slug:vac>/', views.DeliverablesAdd2View, name='Deliverables2'),
    path('vacancy-skills/<slug:vac>/', views.VacancySkillsAddView, name='Skills'),
    path('vacancy-skilla/<slug:vac>/', views.VacancySkillsAdd2View, name='Skillsa'),
    path('popup/skilllevel/add/', views.SkillLevelAddPopup, name="SkillLevelAddPop"),
    path('popup/ajax/get_skilllevel_id/', views.get_skilllevel_id, name="AJAX_GetSkillLevelID"),
    path('vacancy-edit/<slug:vac>/', views.VacancyEditView, name="VacancyEdit"),
    path('vacancy-edit-deliverables/<slug:vac>/', views.DeliverablesEditView, name='DeliverablesEdit'),
    path('vacancy-delete-deliverables/<int:pk>/', views.DeliverableDeleteView, name='DeliverablesDelete'),
    path('vacancy-delete-skill/<int:id>/', views.SkillDeleteView, name='SkillDelete'),

    path('interviewlist/<slug:vac>/<slug:tlt>/', views.AddToInterviewListView, name='InterviewList'),

    path('shortlist/<slug:vac>/<slug:tlt>/', views.AddToShortListView, name='ShortList'),

    path('availabillity/', views.TalentAvailabillityView, name='Availabillity'),
    path('v-detail/<slug:vac>/', views.VacancyDetailView, name='VacancyDetail'),
    path('vp-detail/<slug:vac>/', views.VacancyDetailView_Profile, name='VacancyDetail_Profile'),
    path('apply/<slug:vac>/', views.WorkBidView, name='WorkBid'),
    path('history/', views.ApplicationHistoryView, name='History'),
    path('postview/<slug:vac>/', views.VacancyPostView, name='VacancyPost'),

    path('shortlist-review/<slug:vac>/', views.ShortListView, name='ShortListView'),
    path('interviewlist/<slug:vac>/', views.InterviewListView, name='InterviewList'),

    path('vac-assign/<slug:vac>/<slug:tlt>/', views.TalentAssign, name='VacAssign'),

    path('vac-decline/<slug:vac>/<slug:tlt>/', views.TalentDecline, name='VacDecline'),

    path('all-vac/', views.AllPostedVacanciesView, name='AllPostedVac'),
    path('availabillity-remove/<int:avl_id>/', views.AvailabillityRemoveView, name='NotAvailable'),
    path('vac-interview/<slug:vac>/<slug:tlt>/', views.AddToInterviewListView, name='VacInterview'),
    path('suitable/<slug:vac>/<slug:tlt>/', views.InterviewSuitable, name='Suitable'),
    path('notsuitable/<slug:vac>/<slug:tlt>/', views.InterviewNotSuitable, name='NotSuitable'),

    path('int-decline/<int:int_id>/', views.InterviewDeclineView, name='InterviewDecline'),

    path('rfi-respond/<slug:slug>/', views.TalentRFIView, name='RFIView'),
    path('vacancy-search/', views.VacancySearch, name="VacSearch"),
    path('interview-history/<slug:tlt>/', views.TalentInterviewHistoryView, name="TalentInterviewHistory"),
    path('interview-history/<slug:tlt>/', views.EmployerInterviewHistoryView, name="EmployerInterviewHistory"),
]
