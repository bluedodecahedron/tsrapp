import django.contrib.auth as auth
import apps.authentication.schemas as schemas

from ninja import Router
from django.http import HttpResponse

router = Router()


@router.post('/login', auth=None)
def login(request, user: schemas.User):
    if request.user.is_authenticated:
        return HttpResponse('User already logged in', status=403)

    print(user.username, user.password)

    user = auth.authenticate(request, username=user.username, password=user.password)

    if user is not None:
        auth.login(request, user)
        return HttpResponse('Successfully logged in', status=200)
    else:
        return HttpResponse('Login failed, wrong login credentials', status=401)


@router.get('/status')
def status(request):
    return 'You are logged in as ' + request.user.username
