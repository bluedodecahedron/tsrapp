import logging

from app.apps.tsdr import services
from ninja import Router
from ninja import File
from ninja.files import UploadedFile
from PIL import Image, ImageShow
from django.http import FileResponse, HttpResponse

requestLogger = logging.getLogger('django.request')
router = Router()


@router.post('/trafficimg/{id}')
def traffic_sign_detection(request, id: int, image_file: UploadedFile = File(...)):
    requestLogger.info('tsdr traffic image: ' + str(id) + ", name: " + image_file.name + ', bytesize: ' + str(image_file.size), extra={'request': request})
    result_image = services.tsd_file(image_file)
    response = FileResponse(result_image, content_type="image/jpeg")
    return response
