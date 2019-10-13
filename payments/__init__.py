from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
#from .payments import app as payments_app

default_app_config = 'payments.apps.PaymentsAppConfig'
