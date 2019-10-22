from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import (
        TemplateView
    )

from csp.decorators import csp_exempt

from django.contrib.auth import get_user_model
User = get_user_model()


from db_flatten.models import SkillTag
from enterprises.models import Enterprise
from marketplace.models import TalentRequired

from django.urls import reverse

from .forms import ContactUsForm, SuggestionsForm, DataProtectionForm, DataPrivacyForm

# Create your views here.

def HomePageView(request):
    mcount = User.objects.all().count()
    scount = SkillTag.objects.all().count()
    ecount = Enterprise.objects.all().count()
    vcount = TalentRequired.objects.all().count()

    template_name = 'public/landing_page.html'
    context = {
            'mcount': mcount,
            'scount': scount,
            'ecount': ecount,
            'vcount': vcount
    }
    return render(request, template_name, context)


class HtmlTestView(TemplateView):
    template_name = 'public/html_test.html'


class LandingPage3View(TemplateView):
    template_name = 'public/landing_page3.html'


class LandingPage4View(TemplateView):
    template_name = 'public/landing_page4.html'


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


def DataProtectionView(request):
    form = DataProtectionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect(reverse('Public:ThankContactUs'))
    else:
        context = {'form':form}
        template = 'public/data_contact.html'
        return render(request, template, context)


def DataPrivacyView(request):
    form = DataPrivacyForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect(reverse('Public:ThankContactUs'))
    else:
        context = {'form':form}
        template = 'public/data_privacy.html'
        return render(request, template, context)


class ThankContactView(TemplateView):
    template_name = 'public/thank_contact.html'


class HelpSupportView(TemplateView):
    template_name = 'public/help_support.html'


class DataPrivacyView(TemplateView):
    template_name = 'public/data_privacy.html'


class CaptureView(TemplateView):
    template_name = 'public/capture.html'


class TrustPassportView(TemplateView):
    template_name = 'public/trust_passport.html'


class AdvertiseView(TemplateView):
    template_name = 'public/advertise.html'


class PostVacancyView(TemplateView):
    template_name = 'public/post_vacancy.html'


class SearchCandidatesView(TemplateView):
    template_name = 'public/search_candidates.html'


class ShortTermView(TemplateView):
    template_name = 'public/short_term.html'


class PermanentView(TemplateView):
    template_name = 'public/permanent.html'
