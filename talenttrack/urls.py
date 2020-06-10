from django.urls import path


from .import views


app_name = 'Talent'


urlpatterns = [
    path('home/', views.ExperienceHome, name='Home'),
    path('capture/', views.EducationCaptureView, name='Capture'),
    path('popup/add/', views.CourseAddPopup, name="CourseAddPop"),
    path('popup/ajax/get_course_id/', views.get_course_id, name="AJAX_GetCourseID"),
    path('popup/coursetype/add/', views.CourseTypeAddPopup, name="CourseTypeAddPop"),
    path('popup/ajax/get_coursetype_id/', views.get_coursetype_id, name="AJAX_GetCourseTypeID"),
    path('popup/result/add/', views.ResultAddPopup, name="ResultAddPop"),
    path('popup/ajax/get_result_id/', views.get_result_id, name="AJAX_GetResultID"),
    path('popup/topic/add/', views.TopicAddPopup, name="TopicAddPop"),
    path('popup/ajax/get_topic_id/', views.get_topic_id, name="AJAX_GetTopicID"),
    path('lecturer/select/', views.LecturerSelectView, name='LecturerSelect'),
    path('lecturer/<slug:tex>/add/', views.LecturerAddView, name='LecturerAdd'),
    path('education/detail/<slug:tex>/', views.EducationDetail, name='EducationDetail'),
    path('lecturer/detail/<slug:lct>/', views.LecturerResponse, name='LecturerResponse'),
    path('classmate/select/', views.ClassMateSelectView, name='ClassMatesSelect'),
    path('classmate/<slug:tex>/add/', views.ClassMateAddView, name='ClassMatesAdd'),
    path('classmate/detail/<slug:cmt>/', views.ClassMatesResponse, name='ClassMatesResponse'),
    path('experience/capture/', views.WorkExperienceCaptureView, name="ExperienceCapture"),
    path('popup/designation/add/', views.DesignationAddPopup, name="DesignationAddPop"),
    path('experience/capture/', views.WorkExperienceCaptureView, name="ExperienceCapture"),
    path('popup/ajax/get_designation_id/', views.get_designation_id, name="AJAX_GetDesignationID"),
    path('profile-search/', views.profile_search, name="PflSearch"),
    path('experience/training-full-list/', views.TrainingListView, name="TrainingList"),
    path('experience/pre-experience-full-list/', views.PreExperienceListView, name="PreExperienceList"),
    path('experience/experience-full-list/', views.WorkExperienceListView, name="ExperienceList"),

    path('colleague/select/', views.ColleagueSelectView, name='ColleagueSelect'),

    path('colleague/<slug:tex>/add/', views.ColleagueAddView, name='ColleagueAdd'),
    path('colleague/detail/<slug:clg>/', views.ColleagueResponseView, name='ColleagueResponse'),

    path('superior/select/<slug:pk>/', views.SuperiorSelectView, name='SuperiorSelect'),
    path('superior/add/<slug:tex>/', views.SuperiorAddView, name='SuperiorAdd'),
    path('superior/detail/<slug:spr>/', views.SuperiorResponseView, name='SuperiorResponse'),

    path('collaborator/select/<int:pk>/', views.CollaboratorSelectView, name='CollaboratorSelect'),
    path('collaborator/add/<slug:tex>/', views.CollaboratorAddView, name='CollaboratorAdd'),
    path('collaborator/detail/<slug:clb>/', views.CollaboratorResponseView, name='CollaboratorResponse'),

    path('client/select/<slug:pk>/', views.ClientSelectView, name='ClientSelect'),
    path('client/add/<slug:tex>/', views.ClientAddView, name='ClientAdd'),
    path('client/detail/<slug:wkc>/', views.ClientResponseView, name='ClientResponse'),

#    path('client/select/<int:pk>/', views.ClientSelectView, name='ClientSelect'),
#    path('client/add/<int:pk>/', views.ClientAddView, name='ClientAdd'),
#    path('client/detail/<int:pk>/', views.ClientResponseView, name='ClientResponse'),

    path('experience/detail/<slug:tex>/', views.ExperienceDetailView, name='ExperienceDetail'),


    path('prelogged/capture/', views.PreLoggedExperienceCaptureView, name="PreloggedCapture"),
    path('prelogged/<slug:tex>/detail/', views.PreLogDetailView, name='PreLogDetail'),
    path('experience-detail/<slug:tlt>/', views.SumAllExperienceView, name='ExperienceSum'),
    path('skill-profile-detail/<slug:tlt>/', views.SkillProfileDetailView, name='SPDView'),
    path('dpc-detail/<slug:tlt>/', views.DPC_SummaryView, name='DPCSum'),
    path('apv/<slug:tlt>/<slug:vac>/', views.ActiveProfileView, name='APV'),
    path('achievement-capture/', views.CaptureAchievementView, name='AchieveCap'),

    path('achievement-edit/<slug:ach>/', views.EditAchievementView, name='AchieveEdit'),
    path('achievement-del/<int:ach_i>/<slug:tlt>/', views.DeleteAchievementView, name='AchieveDelete'),

    path('lcm-capture/', views.LicenseCertificationCaptureView, name='LCMCap'),
    path('lcm-edit/<slug:lcm>/', views.LicenseCertificationEditView, name='LCMEdit'),
    path('lcm-del/<int:pk>/<slug:tlt>/', views.LicenseCertificationDeleteView, name='LCMDelete'),
    path('lcm-fv/<slug:tlt>/', views.LCMFullView, name='LCM_FV'),
    path('ple-del/<int:ple_pk>/', views.PreLoggedExperienceDeleteView, name='PLEDelete'),
    path('ple-del-full/<int:ple_pk>/', views.PreLoggedExperienceDeleteFullView, name='PLEFDelete'),
    path('we-del/<int:we_pk>/', views.WorkExperienceDeleteView, name='WEDelete'),
    path('we-del-full/<int:we_pk>/', views.WorkExperienceDeleteFullView, name='WEFDelete'),
    path('edt-del/<int:edt_pk>/', views.EducationDeleteView, name='EDTDelete'),
    path('edt-del-full/<int:edt_pk>/', views.EducationDeleteFullView, name='EDTFDelete'),
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
]
