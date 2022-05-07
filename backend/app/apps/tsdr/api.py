import logging

from app.apps.tsdr import services
from ninja import Router
from django.http import HttpResponse
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

requestLogger = logging.getLogger('django.request')
router = Router()


@router.post('/trafficimg')
def login(request, image: UploadedFile = File(...)):
    requestLogger.info('tsdr traffic image: ' + image.name + ', bytesize: ' + str(image.size), extra={'request': request})

    if services.tsd() == 0:
        return HttpResponse('Test success', status=200)
    else:
        return HttpResponse('Test fail', status=200)


