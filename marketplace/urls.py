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

    path('availabillity/', views.TalentAvailabillityView, name='Availabillity'),
    path('v-detail/<slug:vac>/', views.VacancyDetailView, name='VacancyDetail'),
    path('vp-detail/<slug:vac>/', views.VacancyDetailView_Profile, name='VacancyDetail_Profile'),
    path('apply/<slug:vac>/', views.WorkBidView, name='WorkBid'),
    path('history/', views.ApplicationHistoryView, name='History'),
    path('postview/<slug:vac>/', views.VacancyPostView, name='VacancyPost'),
    path('vac-close/<slug:vac>/', views.VacancyCloseSwitch, name='VacClose'),


    path('interviewlist/<slug:vac>/', views.InterviewListView, name='InterviewList'),

    path('vac-assign/<slug:vac>/<slug:tlt>/', views.TalentAssign, name='VacAssign'),


    path('all-vac/', views.AllPostedVacanciesView, name="AllPostedVac"),
    path('all-vac/open/', views.AllPostedVacanciesOpenView, name='AllPostedVacOpen'),
    path('all-vac/closed/', views.AllPostedVacanciesClosedView, name='AllPostedVacClosed'),
    path('availabillity-remove/<int:avl_id>/', views.AvailabillityRemoveView, name='NotAvailable'),

    #ShortList URLs
    path('shortlist-review/<slug:vac>/', views.ShortListView, name='ShortListView'),
    path('shortlist/<slug:vac>/<slug:tlt>/', views.AddToShortListView, name='ShortList'),
    path('vac-decline/<slug:vac>/<slug:tlt>/', views.TalentDecline, name='VacDecline'),
    path('sl-notsuitable/<slug:bil>/<slug:tlt>/', views.EmpSlDeclineComment, name='SlNotSuitable'),

    #Interview URLs
    path('vac-interview/<slug:vac>/<slug:tlt>/', views.AddToInterviewListView, name='VacInterview'),
    path('int-decline/<int:int_id>/', views.InterviewDeclineView, name='InterviewDecline'),
        #InterviewList Views
    path('suitable/<slug:vac>/<slug:tlt>/', views.InterviewSuitable, name='Suitable'),
    path('not-suitable/<slug:vac>/<slug:tlt>/', views.InterviewNotSuitable, name='NotSuitable'),
        #InterView History
    path('interview-history/<slug:tlt>/', views.TalentInterviewHistoryView, name="TalentInterviewHistory"),
    path('interview-history/<slug:tlt>/', views.EmployerInterviewHistoryView, name="EmployerInterviewHistory"),
        #tlt int close URLs
    path('tlt-int-close/<slug:bil>/<slug:tlt>/', views.TltInterviewClose, name='TalentIntClose'),
    path('tlt-int-detail/<slug:bil>/<slug:tlt>/', views.TltIntFullDetail, name='TalentIntDetail'),
    path('tlt-int-comment/<slug:bil>/<slug:tlt>/', views.TltIntCommentView, name='TalentIntComment'),
        #emp int close URLs
    path('emp-int-close/<slug:bil>/<slug:tlt>/', views.EmpInterviewClose, name='EmployerIntClose'),
    path('emp-int-detail/<slug:bil>/<slug:tlt>/', views.EmpIntFullDetail, name='EmployerIntDetail'),
    path('emp-int-detail/<slug:vac>/', views.EmpIntDetailVacancy, name='VacancyIntDetail'),
    path('emp-int-comment/<slug:bil>/<slug:tlt>/', views.EmpIntCommentView, name='VacancyIntComment'),

    path('rfi-respond/<slug:wit>/', views.TalentRFIView, name='RFIView'),
    path('vacancy-search/', views.VacancySearch, name="VacSearch"),
    path('vacancy/vacancies-full-list/', views.VacanciesListView, name="VacanciesList"),
    path('vacancy/talent-suited-to-vacancy/<slug:vac>/', views.TalentSuitedVacancyListView, name='TalentSuitedToVacancy'),
    path('vacancy/applicants-for-vacancy/<slug:vac>/', views.ApplicantsForVacancyListView, name='ApplicantsForVacancy'),
    path('vacancy/application-history-full-list/', views.RolesAppliedForApplicationHistoryView, name='RolesAppliedForFullList'),
    path('vacancy/shortlisted-history-full-list/', views.RolesShortlistedForApplicationHistoryView, name='RolesShortlistedFullList'),
    path('vacancy/unsuccessful-applications-history-full-list/', views.UnsuccessfulApplicationHistoryView, name='UnsuccessfulApplicationsFullList'),
    path('vacancy/successful-applications-history-full-list/', views.SuccessfulApplicationHistoryView, name='SuccessfulApplicationsFullList'),

    #Help urls
    path('help/Experience-level/', views.ExperienceLevelHelpView, name="HelpExperienceLevel"),
    path('help/Work-Configeration/', views.WorkConfigerationHelpView, name="HelpWorkCOnfigeration"),
    path('help/vacancy-capture/', views.HelpPostVacancyView, name='HelpPostVacancy'),
    path('help/vacancies-suited-for-me-summary/', views.HelpVacancySuitedSummaryView, name='HelpVacanciesSuitedForMeSummary'),
    path('help/vacancies-suited-for-me-full-list/', views.HelpVacancySuitedFullView, name='HelpVacanciesSuitedForMeFull'),
    path('help/vacancies-advertised-open-summary/', views.HelpVacancyAdvertisedOpenSummaryView, name='HelpVacanciesAdvertisedOpenSummary'),
    path('help/vacancies-advertised-open-all/', views.HelpVacancyAdvertisedOpenAllView, name='HelpVacanciesAdvertisedOpenAll'),
    path('help/vacancies-advertised-full-list/', views.HelpVacancyAdvertisedFullView, name='HelpVacanciesAdvertisedFull'),
    path('help/vacancies-advertised-closed-all/', views.HelpVacancyAdvertisedClosedAllView, name='HelpVacanciesAdvertisedClosedAll'),
    path('help/vacancies-advertised-closed-summary/', views.HelpVacancyAdvertisedClosedSummaryView, name='HelpVacanciesAdvertisedClosedSummary'),
    path('help/my-availability/', views.HelpAvailabilityView, name='HelpAvailability'),
    path('help/application-history/roles-applied-for-summary/', views.HelpApplicationHistoryRolesAppliedForSummaryView, name='HelpRolesAppliedForSummary'),
    path('help/application-history/roles-applied-for-full-list/', views.HelpApplicationHistoryRolesAppliedForFullView, name='HelpRolesAppliedForFull'),
    path('help/application-history/roles-shortlisted-for-summary/', views.HelpApplicationHistoryRolesShortlistedForSummaryView, name='HelpRolesShortlistedForSummary'),
    path('help/application-history/roles-shortlisted-for-full-list/', views.HelpApplicationHistoryRolesShortlistedForFullView, name='HelpRolesShortlistedForFull'),
    path('help/application-history/unsuccessful-applications-summary/', views.HelpApplicationHistoryUnsuccessfulApplicationsSummaryView, name='HelpUnseccessfulApplicationsSummary'),
    path('help/application-history/unsuccessful-applications-full-list/', views.HelpApplicationHistoryUnsuccessfulApplicationsFullView, name='HelpUnseccessfulApplicationsFull'),
    path('help/application-history/successful-applications-summary/', views.HelpApplicationHistorySuccessfulApplicationsSummaryView, name='HelpSeccessfulApplicationsSummary'),
    path('help/application-history/successful-applications-full-list/', views.HelpApplicationHistorySuccessfulApplicationsFullView, name='HelpSeccessfulApplicationsFull'),
    path('help/vacancy-review/', views.HelpVacancyPostView, name='HelpVacancyPost'),
    path('help/vacancy-review/talent-suited-to-vacancy/', views.HelpTalentSuitedToVacancyView, name='HelpTalentSuitedVacancy'),
    path('help/vacancy-review/talent-suited-to-vacancy-full-list/', views.HelpTalentSuitedToVacancyFullView, name='HelpTalentSuitedVacancyFull'),
    path('help/vacancy-review/applicants-for-vacancy/', views.HelpApplicantsView, name='HelpApplicantsVacancy'),
    path('help/vacancy-review/applicants-for-vacancy-full-list/', views.HelpApplicantsFullView, name='HelpApplicantsVacancyFull'),
    path('help/interview-history-all/', views.HelpInterviewHistoryAllView, name='HelpInterviewHistoryAll'),
    path('help/interview-detail/', views.HelpInterviewDetailView, name='HelpInterviewDetail'),
    path('help/deliverable/', views.HelpDeliverable2View, name='HelpDeliverable2'),
    path('help/deliverables/', views.HelpDeliverablesView, name='HelpDeliverables'),




]
