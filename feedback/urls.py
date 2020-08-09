from django.urls import path

from .import views

app_name = 'Feedback'

urlpatterns = [
    path('feedback/', views.FeedBackView, name='FeedBack'),
    path('notices/', views.NoticeListView, name='NoticesList'),
    path('notice-detail/<slug:nt>/', views.NoticeReadView, name='NoticeRead'),
    path('member-feedback-all/', views.feedback_list, name='FeedbackAll'),
    path('member-feedback-detail/<slug:fbd>/', views.feedback_detail, name='FeedbackDetail'),
    path('feedback/<slug:fbd>/respond/', views.feedback_respond, name='FeedbackRespond'),
]
