import logging

from app.apps.tsdr import services
from ninja import Router
from ninja import File
from ninja.files import UploadedFile

requestLogger = logging.getLogger('django.request')
router = Router()


@router.post('/trafficimg/{id}')
def traffic_sign_detection(request, id: int, image_file: UploadedFile = File(...)):
    requestLogger.info('tsdr traffic image: ' + str(id) + ", name: " + image_file.name + ', bytesize: ' + str(image_file.size), extra={'request': request})
    services.tsd_file(image_file)
    return id


@router.get('/test', auth=None)
def test(request):
    requestLogger.info('test', extra={'request': request})

    return 0
