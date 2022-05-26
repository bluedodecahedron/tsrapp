import logging

from app.apps.tsdr import services
from ninja import Router
from django.http import HttpResponse
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

requestLogger = logging.getLogger('django.request')
router = Router()


@router.post('/trafficimg')
def traffic_sign_detection(request, image_file: UploadedFile = File(...)):
    requestLogger.info('tsdr traffic image: ' + image_file.name + ', bytesize: ' + str(image_file.size), extra={'request': request})

    return services.tsd(image_file)


