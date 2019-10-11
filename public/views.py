from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import (
        TemplateView
)
from django.urls import reverse

from .forms import ContactUsForm, SuggestionsForm

# Create your views here.
class LandingPageView(TemplateView):
    template_name = 'public/landing_page.html'


class AboutUsView(TemplateView):
    template_name = 'public/about_us.html'


class PrivacyView(TemplateView):
    template_name = 'public/privacy_statement.html'


class TermsConditionsView(TemplateView):
    template_name = 'public/user_agreement.html'


class CookieView(TemplateView):
    template_name = 'public/cookie_policy.html'


class RightToSayNoView(TemplateView):
    template_name = 'public/right_to_say_no.html'


def ContactUsView(request):
    form = ContactUsForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect(reverse('Public:ThankContactUs'))
    else:
        context = {'form':form}
        template = 'public/contact.html'
        return render(request, template, context)


def SuggestionsView(request):
    form = SuggestionsForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect(reverse('Public:ThankContactUs'))
    else:
        context = {'form':form}
        template = 'public/suggestions.html'
        return render(request, template, context)


class ThankContactView(TemplateView):
    template_name = 'public/thank_contact.html'


class HelpSupportView(TemplateView):
    template_name = 'public/help_support.html'
