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
    path('education/detail/<int:edu_id>/', views.EducationDetail, name='EducationDetail'),
    path('lecturer/detail/<int:pk>/', views.LecturerResponse, name='LecturerResponse'),
    path('classmate/select/', views.ClassMateSelectView, name='ClassMatesSelect'),
    path('classmate/detail/<int:pk>/', views.ClassMatesResponse, name='ClassMatesResponse'),
    path('experience/capture/', views.WorkExperienceCaptureView, name="ExperienceCapture"),
    path('popup/designation/add/', views.DesignationAddPopup, name="DesignationAddPop"),
    path('popup/ajax/get_designation_id/', views.get_designation_id, name="AJAX_GetDesignationID"),
    path('colleague/select/', views.ColleagueSelectView, name='ColleagueSelect'),
    path('superior/select/<int:pk>/', views.SuperiorSelectView, name='SuperiorSelect'),
    path('collaborator/select/<int:pk>/', views.CollaboratorSelectView, name='CollaboratorSelect'),
    path('client/select/<int:pk>/', views.ClientSelectView, name='ClientSelect'),
    path('experience/detail/<int:exp_id>/', views.ExperienceDetailView, name='ExperienceDetail'),
    path('colleague/detail/<int:pk>/', views.ColleagueResponseView, name='ColleagueResponse'),
    path('superior/detail/<int:pk>/', views.SuperiorResponseView, name='SuperiorResponse'),
    path('collaborator/detail/<int:pk>/', views.CollaboratorResponseView, name='CollaboratorResponse'),
    path('client/detail/<int:pk>/', views.ClientResponseView, name='ClientResponse'),
]
