import logging
import app.apps.webrtc.server.services as server

from ninja import Router
from django.http import HttpResponse
from app.apps.webrtc.server.schemas import OfferSchema, AnswerSchema, Detail
from asgiref.sync import sync_to_async
import asyncio

requestLogger = logging.getLogger('django.request')
router = Router()


def authenticate(request):
    if request.user.is_authenticated:
        return True
    else:
        return False


@router.api_operation(['POST'], '/offer', auth=None, response={200: AnswerSchema, 401: Detail})
async def offer(request, offer_schema: OfferSchema):
    # Cannot use standard auth method because method is declared async (will error)
    # Handle authentication manually
    if not await sync_to_async(authenticate)(request):
        return 401, {'detail': 'Unauthorized'}
    requestLogger.info('offer', extra={'request': request})
    return 200, await server.offer(offer_schema)


@router.api_operation(['OPTIONS'], '/offer')
def offer(request):
    requestLogger.info('offer', extra={'request': request})
    return HttpResponse("Successful Options")
