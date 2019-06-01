from django.shortcuts import render
from django.views.generic import TemplateView

class ProfileHome(TemplateView):
    template_name = 'Profile/profile_home.html'
    
