from django.urls import path

from .import views

app_name = 'Feedback'

urlpatterns = [
    path('feedback/', views.FeedBackView, name='FeedBack'),
    path('notices/', views.NoticeListView, name='NoticesList'),
    path('notice-detail/<slug:nt>/', views.NoticeReadView, name='NoticeRead'),
]
