from ninja import NinjaAPI
from app.apps.authentication.api import router as authentication_router
from app.apps.tsdr.api import router as tsdr_router
from app.apps.webrtc.client.api import router as webrtc_client_router
from app.apps.webrtc.server.api import router as webrtc_server_router

import logging

requestLogger = logging.getLogger('django.request')


def authenticate(request):
    if request.user.is_authenticated:
        return True
    else:
        return False


api = NinjaAPI(auth=authenticate)
api.add_router('/api/authentication/', authentication_router)
api.add_router('/api/tsdr/', tsdr_router)
api.add_router('/api/webrtc/client/', webrtc_client_router)
api.add_router('/api/webrtc/server/', webrtc_server_router)
