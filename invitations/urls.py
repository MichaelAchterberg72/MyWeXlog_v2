from django.urls import path

from . import views
from .views import ConfigureWorkerInvite

app_name = 'Invitation'

urlpatterns = [
    path('invite/<slug:tex>/', views.InvitationView, name="Invite2"),
    path('flatinvite/', views.FlatInviteview, name="FlatInvite"),
    path('profile_2_pdf/', views.profile_2_pdf, name="Profile2PDF"),
    path('invites-sent/', views.InvitationsSentView, name="InvitationsSent"),

    path('email-test/', views.email_test_view, name="EmailTest"),
    path('invite-detail/<slug:invs>/', views.invite_detail_view, name="InviteDetail"),
]

ConfigureWorkerInvite()
