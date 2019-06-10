from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
class ProfileHome(TemplateView):
    template_name = 'Profile/profile_home.html'


from .models import Profile, PhysicalAddress, Email


@login_required()
def ProfileView(request, pk):
    details=Profile.objects.all()
    email=Email.objects.filter(talent=pk)

    template='Profile/profile_view.html'
    context= {'details':details, 'email':email}
    return render(request, template, context)
