from django.urls import path


from .import views

app_name = 'Invitation'

urlpatterns = [
    path('invite/', views.InvitationView, name="Invite2"),
    path('flatinvite/', views.FlatInviteview, name="FlatInvite"),
]
