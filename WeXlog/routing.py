from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import intmessages.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)


})
