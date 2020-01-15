from django.urls import path


from .import views

app_name = 'MarketPlace'


urlpatterns = [
    path('entrance/', views.MarketHome, name='Entrance'),
    path('vacancy/', views.VacancyView, name='Vacancy'),
    path('popup/worklocation/add/', views.WorkLocationAddPopup, name="WorkLocationAddPop"),
    path('popup/ajax/get_worklocation_id/', views.get_worklocation_id, name="AJAX_GetWorklocationID"),
    path('vacancy-deliverables/<slug:ref>/', views.DeliverablesAddView, name='Deliverables'),
    path('vacancy-deliverable/<slug:ref>/', views.DeliverablesAdd2View, name='Deliverables2'),
    path('vacancy-skills/<slug:ref>/', views.VacancySkillsAddView, name='Skills'),
    path('vacancy-skilla/<slug:ref>/', views.VacancySkillsAdd2View, name='Skillsa'),
    path('popup/skilllevel/add/', views.SkillLevelAddPopup, name="SkillLevelAddPop"),
    path('popup/ajax/get_skilllevel_id/', views.get_skilllevel_id, name="AJAX_GetSkillLevelID"),
    path('vacancy-edit/<slug:ref>/', views.VacancyEditView, name="VacancyEdit"),
    path('vacancy-edit-deliverables/<slug:refd>/', views.DeliverablesEditView, name='DeliverablesEdit'),
    path('vacancy-delete-deliverables/<int:pk>/', views.DeliverableDeleteView, name='DeliverablesDelete'),
    path('vacancy-delete-skill/<int:id>/', views.SkillDeleteView, name='SkillDelete'),

    path('interviewlist/<int:vac>/<int:tlt>/', views.AddToInterviewListView, name='InterviewList'),

    path('shortlist/<slug:ref><int:tlt>/', views.AddToShortListView, name='ShortList'),

    path('availabillity/', views.TalentAvailabillityView, name='Availabillity'),
    path('v-detail/<slug:ref_no>/', views.VacancyDetailView, name='VacancyDetail'),
    path('vp-detail/<slug:ref>/', views.VacancyDetailView_Profile, name='VacancyDetail_Profile'),
    path('apply/<slug:ref>/', views.WorkBidView, name='WorkBid'),
    path('history/', views.ApplicationHistoryView, name='History'),
    path('postview/<slug:ref>/', views.VacancyPostView, name='VacancyPost'),

    path('shortlist-review/<slug:ref>/', views.ShortListView, name='ShortListView'),
    path('interviewlist/<slug:ref>/', views.InterviewListView, name='InterviewList'),

    path('vac-assign/<int:vac>/<int:tlt>/', views.TalentAssign, name='VacAssign'),
    path('vac-decline/<int:vac>/<int:tlt>/', views.TalentDecline, name='VacDecline'),
    path('all-vac/', views.AllPostedVacanciesView, name='AllPostedVac'),
    path('availabillity-remove/<int:avl_id>/', views.AvailabillityRemoveView, name='NotAvailable'),
    path('vac-interview/<int:vac>/<int:tlt>/', views.AddToInterviewListView, name='VacInterview'),
    path('suitable/<int:vac_id>/<int:tlt_id>/', views.InterviewSuitable, name='Suitable'),
    path('notsuitable/<int:vac_id>/<int:tlt_id>/', views.InterviewNotSuitable, name='NotSuitable'),
    path('int-decline/<int:int_id>/', views.InterviewDeclineView, name='InterviewDecline'),
    path('rfi-respond/<slug:slug>/', views.TalentRFIView, name='RFIView'),
]
