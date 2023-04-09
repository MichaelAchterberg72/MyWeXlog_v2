import os

import django
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WeXlog.settings')
django.setup()

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
  "https": AsgiHandler(),
})
