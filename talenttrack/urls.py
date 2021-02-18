from django.urls import path


from .import views


app_name = 'Talent'


urlpatterns = [
    path('home/', views.ExperienceHome, name='Home'),
    path('capture/', views.EducationCaptureView, name='Capture'),
    path('education-edit/<slug:edt_slug>/', views.EducationEditView, name='EducationEdit'),
    path('popup/add/', views.CourseAddPopup, name="CourseAddPop"),
    path('popup/ajax/get_course_id/', views.get_course_id, name="AJAX_GetCourseID"),
    path('popup/coursetype/add/', views.CourseTypeAddPopup, name="CourseTypeAddPop"),
    path('popup/ajax/get_coursetype_id/', views.get_coursetype_id, name="AJAX_GetCourseTypeID"),
    path('popup/result/add/', views.ResultAddPopup, name="ResultAddPop"),
    path('popup/ajax/get_result_id/', views.get_result_id, name="AJAX_GetResultID"),
    path('popup/topic/add/', views.TopicAddPopup, name="TopicAddPop"),
    path('popup/ajax/get_topic_id/', views.get_topic_id, name="AJAX_GetTopicID"),
    path('lecturer/<slug:tex>/select/', views.LecturerSelectView, name='LecturerSelect'),
    path('lecturer/<slug:tex>/add/', views.LecturerAddView, name='LecturerAdd'),
    path('education/detail/<slug:tex>/', views.EducationDetail, name='EducationDetail'),
    path('lecturer/detail/<slug:lct>/', views.LecturerResponse, name='LecturerResponse'),
    path('classmate/<slug:tex>/select/', views.ClassMateSelectView, name='ClassMatesSelect'),
    path('classmate/<slug:tex>/add/', views.ClassMateAddView, name='ClassMatesAdd'),
    path('classmate/detail/<slug:cmt>/', views.ClassMatesResponse, name='ClassMatesResponse'),
    path('experience/capture/', views.WorkExperienceCaptureView, name="ExperienceCapture"),
    path('experience/edit/<slug:we_slug>/', views.WorkExperienceEditView, name="ExperienceEdit"),
    path('popup/designation/add/', views.DesignationAddPopup, name="DesignationAddPop"),
    path('popup/ajax/get_designation_id/', views.get_designation_id, name="AJAX_GetDesignationID"),
    path('profile-search/', views.profile_search, name="PflSearch"),
    path('experience/training-full-list/', views.TrainingListView, name="TrainingList"),
    path('experience/pre-experience-full-list/', views.PreExperienceListView, name="PreExperienceList"),
    path('experience/experience-full-list/', views.WorkExperienceListView, name="ExperienceList"),
    path('colleague/select/<int:pk>/', views.ColleagueSelectView, name='ColleagueSelect'),
    path('colleague/<slug:tex>/add/', views.ColleagueAddView, name='ColleagueAdd'),
    path('colleague/detail/<slug:clg>/', views.ColleagueResponseView, name='ColleagueResponse'),
    path('colleague/pre-detail/<slug:clg>/', views.ColleaguePreResponseView, name='ColleaguePreResponse'),
    path('superior/select/<slug:pk>/', views.SuperiorSelectView, name='SuperiorSelect'),
    path('superior/add/<slug:tex>/', views.SuperiorAddView, name='SuperiorAdd'),
    path('superior/detail/<slug:spr>/', views.SuperiorResponseView, name='SuperiorResponse'),
    path('superior/pre-detail/<slug:spr>/', views.SuperiorPreResponseView, name='SuperiorPreResponse'),
    path('collaborator/select/<int:pk>/', views.CollaboratorSelectView, name='CollaboratorSelect'),
    path('collaborator/add/<slug:tex>/', views.CollaboratorAddView, name='CollaboratorAdd'),
    path('collaborator/detail/<slug:clb>/', views.CollaboratorResponseView, name='CollaboratorResponse'),
    path('collaborator/pre-detail/<slug:clb>/', views.CollaboratorPreResponseView, name='CollaboratorPreResponse'),
    path('client/select/<slug:pk>/', views.ClientSelectView, name='ClientSelect'),
    path('client/add/<slug:tex>/', views.ClientAddView, name='ClientAdd'),
    path('client/detail/<slug:wkc>/', views.ClientResponseView, name='ClientResponse'),
    path('client/pre-detail/<slug:wkc>/', views.ClientPreResponseView, name='ClientPreResponse'),
    path('experience/detail/<slug:tex>/', views.ExperienceDetailView, name='ExperienceDetail'),
    path('experience/delete/<int:pk>/', views.ExperienceDeleteView, name='ExperienceDelete'),
    path('education/delete/<int:pk>/', views.EducationDetailDeleteView, name='EducationDetailDelete'),
    path('prelogged/capture/', views.PreLoggedExperienceCaptureView, name="PreloggedCapture"),
    path('prelogged/<slug:tex>/detail/', views.PreLogDetailView, name='PreLogDetail'),
    path('experience-detail/<slug:tlt>/', views.SumAllExperienceView, name='ExperienceSum'),
    path('skill-profile-detail/<slug:tlt>/', views.SkillProfileDetailView, name='SPDView'),
    path('dpc-detail/<slug:tlt>/', views.DPC_SummaryView, name='DPCSum'),
    path('dpcp-detail/<slug:tlt>/', views.DPCP_SummaryView, name='DPCPSum'),
    path('apv/<slug:tlt>/<slug:vac>/', views.ActiveProfileView, name='APV'),
    path('apv-lcm/<slug:tlt>/<slug:vac>/', views.LCMFVView, name='LCM_FV'),
    path('apv-bch/<slug:tlt>/<slug:vac>/', views.BCHView, name='BCH_FV'),
    path('apv-ach/<slug:tlt>/<slug:vac>/', views.AchievementsFVView, name='ACH_FV'),
    path('apv-awd/<slug:tlt>/<slug:vac>/', views.AwardsFVView, name='AWD_FV'),
    path('apv-pub/<slug:tlt>/<slug:vac>/', views.PublicationsFVView, name='PUB_FV'),
    path('apv-projects/<slug:tlt>/<slug:vac>/', views.ProjectsFVView, name='Projects_FV'),
    path('apv-edu/<slug:tlt>/<slug:vac>/', views.EduFVView, name='EDU_FV'),

    path('apv-l/<slug:tlt>/', views.profile_view, name='APV_L'),
    path('apv-c/<slug:cor>/<slug:tlt>/', views.profile_view_corp, name='APV_C'),
    path('apv-bch/<slug:tlt>/', views.BCHLView, name='BCH_L_FV'),
    path('apv-ach/<slug:tlt>/', views.AchievementsLView, name='ACH_L_FV'),
    path('apv-projects/<slug:tlt>/', views.ProjectsLFVView, name='Projects_L_FV'),
    path('apv-edu/<slug:tlt>/', views.EduLFVView, name='EDU_L_FV'),

    path('achievement-capture/', views.CaptureAchievementView, name='AchieveCap'),
    path('achievement-edit/<slug:ach>/', views.EditAchievementView, name='AchieveEdit'),
    path('achievement-del/<int:ach_i>/<slug:tlt>/', views.DeleteAchievementView, name='AchieveDelete'),
    path('award-capture/', views.CaptureAwardView, name='AwardCap'),
    path('award-edit/<slug:awd>/', views.EditAwardView, name='AwardEdit'),
    path('award-del/<int:awd_i>/<slug:tlt>/', views.DeleteAwardView, name='AwardDelete'),
    path('publication-capture/', views.CapturePublicationView, name='PublicationCap'),
    path('publication-edit/<slug:pub>/', views.EditPublicationView, name='PublicationEdit'),
    path('publication-del/<int:pub_i>/<slug:tlt>/', views.DeletePublicationView, name='PublicationDelete'),
    path('lcm-capture/', views.LicenseCertificationCaptureView, name='LCMCap'),
    path('lcm-edit/<slug:lcm>/', views.LicenseCertificationEditView, name='LCMEdit'),
    path('lcm-del/<int:pk>/<slug:tlt>/', views.LicenseCertificationDeleteView, name='LCMDelete'),
#    path('lcm-fv/<slug:tlt>/', views.LCMFullView, name='LCM_FV'),
    path('ple-del/<int:ple_pk>/', views.PreLoggedExperienceDeleteView, name='PLEDelete'),
    path('ple-del-full/<int:ple_pk>/', views.PreLoggedExperienceDeleteFullView, name='PLEFDelete'),
    path('we-del/<int:we_pk>/', views.WorkExperienceDeleteView, name='WEDelete'),
    path('we-del-full/<int:we_pk>/', views.WorkExperienceDeleteFullView, name='WEFDelete'),
    path('we-del-skill/<int:we_pk>/<int:skl>/', views.WorkExperienceDeleteSkillView, name='WESDelete'),
    path('we-del-skill-full/<int:we_pk>/<int:skl>/', views.WorkExperienceDeleteSkillFullView, name='WESFDelete'),
    path('edt-del/<int:edt_pk>/', views.EducationDeleteView, name='EDTDelete'),
    path('edt-del-full/<int:edt_pk>/', views.EducationDeleteFullView, name='EDTFDelete'),
    path('edt-del-skill/<int:edt_pk>/<int:skl>/', views.EducationDeleteSkillView, name='EDTSDelete'),
    path('edt-del-skill-full/<int:edt_pk>/<int:skl>/', views.EducationDeleteSkillFullView, name='EDTSFDelete'),
    # Help urls
    path('help/experience-home/', views.HelpExperienceHomeView, name='HelpExperienceHome'),
    path('help/experience-education/', views.HelpExperienceEducationView, name='HelpExperienceEducation'),
    path('help/experience-experience/', views.HelpExperienceExperienceView, name='HelpExperienceExperience'),
    path('help/experience-pre-experience/', views.HelpExperiencePreExperienceView, name='HelpExperiencePreExperience'),
    path('help/capture-education/', views.HelpCaptrueEducationView, name='HelpCaptureEducation'),
    path('help/capture-experience/', views.HelpCaptrueExperienceView, name='HelpCaptureExperience'),
    path('help/how-to-capture-skills/', views.HelpHowCaptrueSkillsView, name='HelpHowCaptureSkills'),
    #Talent Rating Details
    path('<slug:tlt>/rating/', views.TltRatingDetailView, name="TltRatingDetail"),
    #Confirmation review urlpatterns
    path('calect-list/', views.lecturer_conf_summary_list, name='CAsLectList'),
    path('cacm-list/', views.classmate_conf_summary_list, name='CAsCmList'),
    path('caclg-list/', views.colleague_conf_summary_list, name='CAsClgList'),
    path('casup-list/', views.superior_conf_summary_list, name='CAsSupList'),
    path('caclb-list/', views.collaborator_conf_summary_list, name='CAsClbList'),
    path('caclt-list/', views.client_conf_summary_list, name='CAsCltList'),
    path('reqlect-list/', views.lect_req_list, name='ReqLectList'),
    path('reqcm-list/', views.cm_req_list, name='ReqCmList'),
    path('reqclg-list/', views.clg_req_list, name='ReqClgList'),
    path('reqsup-list/', views.sup_req_list, name='ReqSupList'),
    path('reqclt-list/', views.clt_req_list, name='ReqCltList'),
    path('reqclb-list/', views.clb_req_list, name='ReqClbList'),
    #skills stats
    path('skill-stats-overview/<int:skl>/', views.skill_stats, name='SkillsStats'),
    path('profile-skill-stats-overview/<int:skl>/', views.profile_skill_stats, name='ProfileSkillsStats'),
    path('site-skill-stats-overview/<int:skl>/', views.site_skill_stats, name='SiteSkillsStats'),
    path('site-demand_skill-stats-overview/<int:skl>/', views.site_demand_skill_stats, name='SiteDemandSkillsStats'),
    path('skill-validation-list/<int:skl>/', views.skill_validate_list, name='SkillValidationList'),
    path('skill-education-list/<int:skl>/', views.skill_training_list_view, name='SkillEducationList'),
    path('skill-work-experience-list/<int:skl>/', views.skill_work_experience_list_view, name='SkillWorkExperienceList'),

    path('request-validate-experience/<int:skl>/<slug:tlt>/', views.email_reminder_validate, name='RequestValidateExperienceEmail'),
    path('request-validate-experience-list/<int:skl>/<slug:tlt>/', views.email_reminder_validate_list, name='RequestValidateExperienceEmailList'),
]
