import logging

from ninja import Router
from django.http import HttpResponse
from app.apps.authentication.schemas import UserSchema
from django.contrib import auth

requestLogger = logging.getLogger('django.request')
router = Router()


@router.post('/login', auth=None)
def login(request, user: UserSchema):
    requestLogger.info('User login: ' + user.__str__(), extra={'request': request})
    if request.user.is_authenticated:
        return HttpResponse('User already logged in', status=403)

    user = auth.authenticate(request, username=user.username, password=user.password)

    if user is not None:
        auth.login(request, user)
        return HttpResponse('Successfully logged in', status=200)
    else:
        return HttpResponse('Login failed, wrong login credentials', status=401)


@router.get('/status')
def status(request):
    requestLogger.info('Login status check: ' + request.user.username, extra={'request': request})
    return HttpResponse('You are logged in as ' + request.user.username, status=200)
