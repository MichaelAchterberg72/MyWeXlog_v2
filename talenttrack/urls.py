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
    path('lecturer/<int:pk>/add/', views.LecturerAddView, name='LecturerAdd'),
    path('education/detail/<int:edu_id>/', views.EducationDetail, name='EducationDetail'),
    path('lecturer/detail/<int:pk>/', views.LecturerResponse, name='LecturerResponse'),
    path('classmate/select/', views.ClassMateSelectView, name='ClassMatesSelect'),
    path('classmate/<int:pk>/add/', views.ClassMateAddView, name='ClassMatesAdd'),
    path('classmate/detail/<int:pk>/', views.ClassMatesResponse, name='ClassMatesResponse'),
    path('experience/capture/', views.WorkExperienceCaptureView, name="ExperienceCapture"),
    path('popup/designation/add/', views.DesignationAddPopup, name="DesignationAddPop"),
    path('popup/ajax/get_designation_id/', views.get_designation_id, name="AJAX_GetDesignationID"),

    path('colleague/select/', views.ColleagueSelectView, name='ColleagueSelect'),
    path('colleague/<int:pk>/add/', views.ColleagueAddView, name='ColleagueAdd'),
    path('colleague/detail/<int:pk>/', views.ColleagueResponseView, name='ColleagueResponse'),

    path('superior/select/<int:pk>/', views.SuperiorSelectView, name='SuperiorSelect'),
    path('superior/add/<int:pk>/', views.SuperiorAddView, name='SuperiorAdd'),
    path('superior/detail/<int:pk>/', views.SuperiorResponseView, name='SuperiorResponse'),

    path('collaborator/select/<int:pk>/', views.CollaboratorSelectView, name='CollaboratorSelect'),
    path('collaborator/add/<int:pk>/', views.CollaboratorAddView, name='CollaboratorAdd'),
    path('collaborator/detail/<int:pk>/', views.CollaboratorResponseView, name='CollaboratorResponse'),

    path('client/select/<int:pk>/', views.ClientSelectView, name='ClientSelect'),
    path('client/add/<int:pk>/', views.ClientAddView, name='ClientAdd'),
    path('client/detail/<int:pk>/', views.ClientResponseView, name='ClientResponse'),
    
    path('experience/detail/<int:exp_id>/', views.ExperienceDetailView, name='ExperienceDetail'),


    path('prelogged/capture/', views.PreLoggedExperienceCaptureView, name="PreloggedCapture"),
    path('prelogged/<int:pre_id>/detail/', views.PreLogDetailView, name='PreLogDetail'),
    path('experience-detail/', views.SumAllExperienceView, name='ExperienceSum'),
    path('skill-profile-detail/<int:tlt_id>/', views.SkillProfileDetailView, name='SPDView'),
    path('dpc-detail/', views.DPC_SummaryView, name='DPCSum'),
    path('apv/<int:tlt_id>/<int:vac_id>/', views.ActiveProfileView, name='APV'),
    path('achievement-capture/', views.CaptureAchievementView, name='AchieveCap'),
    path('achievement-edit/<int:ach_pk>/', views.EditAchievementView, name='AchieveEdit'),
    path('achievement-del/<int:ach_pk>/', views.DeleteAchievementView, name='AchieveDelete'),
    path('lcm-capture/', views.LicenseCertificationCaptureView, name='LCMCap'),
    path('lcm-edit/<int:lcm_id>/', views.LicenseCertificationEditView, name='LCMEdit'),
    path('lcm-del/<int:lcm_id>/', views.LicenseCertificationDeleteView, name='LCMDelete'),
    path('lcm-fv/<int:tlt_id>/', views.LCMFullView, name='LCM_FV'),
    path('ple-del/<int:ple_pk>/', views.PreLoggedExperienceDeleteView, name='PLEDelete'),
    path('we-del/<int:we_pk>/', views.WorkExperienceDeleteView, name='WEDelete'),
    path('edt-del/<int:edt_pk>/', views.EducationDeleteView, name='EDTDelete'),
]
