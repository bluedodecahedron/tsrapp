from django.http import HttpResponse


def index(request):
    if request.method == 'GET':
        return HttpResponse('This service provides an API for detecting and recognizing traffic signs in road images')
    else:
        return HttpResponse('Method not supported', status=405)
