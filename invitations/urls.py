from django.urls import path


from .import views

app_name = 'Invitation'

urlpatterns = [
    path('invite/<slug:tex>/', views.InvitationView, name="Invite2"),
    path('flatinvite/', views.FlatInviteview, name="FlatInvite"),
    path('profile_2_pdf/', views.profile_2_pdf, name="Profile2PDF"),
    path('invites-sent/', views.InvitationsSentView, name="InvitationsSent"),
]
