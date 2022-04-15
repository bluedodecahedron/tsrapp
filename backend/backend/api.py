from ninja import NinjaAPI
from app.apps.authentication.api import router as authentication_router
from django.http import HttpResponse


def authenticate(request):
    if request.user.is_authenticated:
        return True
    else:
        return False


api = NinjaAPI(auth=authenticate)
api.add_router('/authentication/', authentication_router)


@api.get('/index', auth=None)
def index(request):
    return HttpResponse('This service provides an API for detecting and recognizing traffic signs in road images')
