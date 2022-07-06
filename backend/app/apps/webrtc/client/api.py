from ninja import NinjaAPI
from app.apps.authentication.api import router as authentication_router
from app.apps.tsdr.api import router as tsdr_router
from django.http import HttpResponse
from ninja import Router
from asgiref.sync import sync_to_async

import os
import logging

requestLogger = logging.getLogger('django.request')
router = Router()


@router.get('/client.html', auth=None)
def index(request):
    requestLogger.info('index' + ', user:' + str(request.user), extra={'request': request})
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'client.html')
    content = open(file_path, "r").read()
    return HttpResponse(content, content_type='text/html')


@router.get('/client.js', auth=None)
def javascript(request):
    requestLogger.info('client.js' + ', user:' + str(request.user), extra={'request': request})
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'client.js')
    content = open(file_path, "r").read()
    return HttpResponse(content, content_type="application/javascript")
