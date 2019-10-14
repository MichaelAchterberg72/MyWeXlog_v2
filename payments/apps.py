from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = 'payments'

    def ready(self):
        # importing model classes
#        from .models import PayPalStandardBase
        import payments.signals

        # registering signals with the model's string label
#        pre_save.connect(receiver, sender='app_label.MyModel')
#        pre_save.connect(receiver, sender='show_me_the_money')
