from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.forms import PayPalEncryptedPaymentsForm
from paypal.standard.forms import PayPalSharedSecretEncryptedPaymentsForm
from django.utils.html import format_html
from django import forms

class ExtPayPalPaymentsForm(PayPalPaymentsForm):
    def render(self):
        form_open  = u'''<form action="%s" id="PayPalForm" method="post">''' % (self.get_endpoint())
        form_close = u'</form>'
        # format html as you need
        submit_elm = u'''<input type="submit" class="btn btn-success my-custom-class">'''
        return format_html(form_open+self.as_p()+submit_elm+form_close)


class ExtPayPalEncryptedPaymentsForm(PayPalEncryptedPaymentsForm):
    def render(self):
        form_open  = u'''<form action="%s" id="PayPalEncryptedForm" method="post">''' % (self.get_endpoint())
        form_close = u'</form>'
        # format html as you need
        submit_elm = u'''<input type="submit" class="btn btn-success my-custom-class">'''
        return format_html(form_open+self.as_p()+submit_elm+form_close)


class ExtPayPalSharedSecretEncryptedPaymentsForm(PayPalSharedSecretEncryptedPaymentsForm):
    def render(self):
        form_open  = u'''<form action="%s" id="PayPalSharedSecretEncryptedForm" method="post">''' % (self.get_endpoint())
        form_close = u'</form>'
        # format html as you need
        submit_elm = u'''<input type="submit" class="btn btn-success my-custom-class">'''
        return format_html(form_open+self.as_p()+submit_elm+form_close)

passive_subscription_options = [
    ('1-month', 'Standard Monthly ($3 USD/Mon)'),
    ('6-month', '6-Monthly ($16,50 USD)'),
    ('1-year', '1-Yearly ($44,60 USD)'),
]

class PassiveSubscriptionChoiceForm(forms.Form):
    passive_plans = forms.ChoiceField(choices=passive_subscription_options)


active_subscription_options = [
    ('1-month', 'Standard Monthly ($4 USD/Mon)'),
    ('6-month', '6-Monthly ($22,50 USD)'),
    ('1-year', '1-Yearly Save ($44,60 USD)'),
]

class ActiveSubscriptionChoiceForm(forms.Form):
    active_plans = forms.ChoiceField(choices=active_subscription_options)
