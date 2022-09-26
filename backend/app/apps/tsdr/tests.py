from django.test import TestCase
from app.apps.tsdr import services
import cv2


class TsdrTestCase(TestCase):
    def test_tsdr_produces_certain_classes(self):
        image = cv2.imread("resources/gtsdbtest21.jpg")
        services.tsdr(image)
        services.tsdr(image)
        services.tsdr(image)
        services.tsdr(image)
        services.tsdr(image)
