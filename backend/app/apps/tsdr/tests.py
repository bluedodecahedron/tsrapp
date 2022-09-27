from django.test import TestCase
from app.apps.tsdr import services
import cv2


class TsdrTestCase(TestCase):
    def test_tsdr_detects_many_classes(self):
        image = cv2.imread("resources/manytrafficsigns.jpg")
        class_ids = services.tsdr(image)
        assert len(class_ids) == 9

    def test_tsdr_detects_no_classes(self):
        image = cv2.imread("resources/notrafficsigns.jpg")
        class_ids = services.tsdr(image)
        assert len(class_ids) == 0
